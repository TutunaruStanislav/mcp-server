import logging
import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class MyMemoryAPIClient:
    """Client for MyMemory Translation API."""

    SUPPORTED_LANGUAGES = {
        'ENG': 'English',
        'RUS': 'Russian',
        'UKR': 'Ukrainian',
    }

    # Cyrillic letters specific to Ukrainian (absent in Russian).
    UKRAINIAN_CHARS = set('іїєґІЇЄҐ')

    def __init__(self):
        self.api_url = os.getenv(
            'MYMEMORY_API_URL',
            'https://api.mymemory.translated.net/get'
        )
        self.timeout = int(os.getenv('TRANSLATION_TIMEOUT', '10'))

    def check_health(self) -> bool:
        """Check if API is available."""
        try:
            response = requests.get(
                self.api_url,
                params={'q': 'test', 'langpair': 'en|ru'},
                timeout=self.timeout
            )
            logger.info('API health check: status=%d', response.status_code)
            return response.status_code == 200
        except Exception as e:
            logger.error('API health check failed: %s', str(e))
            return False

    def translate(
        self,
        text: str,
        lang_pair: str
    ) -> Dict[str, Any]:
        """
        Translate text using MyMemory API.

        Args:
            text: Text to translate
            lang_pair: Language pair in format 'lang1|lang2'

        Returns:
            Dictionary with translation result
        """
        try:
            response = requests.get(
                self.api_url,
                params={'q': text, 'langpair': lang_pair},
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            logger.info(
                'Translation request: text_length=%d, lang_pair=%s',
                len(text),
                lang_pair
            )

            if data.get('responseStatus') == 200:
                return {
                    'translated_text': data.get('responseData', {})
                    .get('translatedText'),
                    'is_translated': data.get('responseData', {})
                    .get('translatedText') is not None,
                    'status': 'success',
                }
            else:
                logger.warning(
                    'Translation failed: status=%s, message=%s',
                    data.get('responseStatus'),
                    data.get('responseDetails')
                )
                return {
                    'translated_text': None,
                    'is_translated': False,
                    'status': 'error',
                    'error': data.get('responseDetails'),
                }
        except Exception as e:
            logger.error('Translation error: %s', str(e))
            return {
                'translated_text': None,
                'is_translated': False,
                'status': 'error',
                'error': str(e),
            }

    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect language of the text via a Unicode-script heuristic.

        MyMemory has no detection endpoint, so we classify by script:
        Cyrillic with Ukrainian-specific letters -> UKR, other
        Cyrillic -> RUS, Latin -> ENG. Returns None if undetermined.
        """
        has_cyrillic = any('Ѐ' <= ch <= 'ӿ' for ch in text)
        has_latin = any('a' <= ch.lower() <= 'z' for ch in text)

        if has_cyrillic:
            if any(ch in self.UKRAINIAN_CHARS for ch in text):
                detected = 'UKR'
            else:
                detected = 'RUS'
        elif has_latin:
            detected = 'ENG'
        else:
            detected = None

        logger.info(
            'Language detection: text_length=%d, detected=%s',
            len(text),
            detected,
        )
        return detected

    @staticmethod
    def get_supported_languages() -> Dict[str, str]:
        """Return list of supported languages."""
        return MyMemoryAPIClient.SUPPORTED_LANGUAGES.copy()
