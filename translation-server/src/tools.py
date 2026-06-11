import logging
from typing import Any
from mcp.types import Tool, TextContent
from .api_client import MyMemoryAPIClient

logger = logging.getLogger(__name__)

client = MyMemoryAPIClient()


def get_tools() -> list[Tool]:
    """Return list of available tools."""
    return [
        Tool(
            name='translate_text',
            description=(
                'Translate text from one language to another. '
                'Requires explicit language specification.'
            ),
            inputSchema={
                'type': 'object',
                'properties': {
                    'text': {
                        'type': 'string',
                        'description': 'Text to translate',
                    },
                    'source_lang': {
                        'type': 'string',
                        'enum': ['ENG', 'RUS', 'UKR'],
                        'description': 'Source language code',
                    },
                    'target_lang': {
                        'type': 'string',
                        'enum': ['ENG', 'RUS', 'UKR'],
                        'description': 'Target language code',
                    },
                },
                'required': ['text', 'source_lang', 'target_lang'],
            },
        ),
        Tool(
            name='translate_with_detection',
            description=(
                'Translate text with automatic language detection. '
                'Only requires specifying the target language.'
            ),
            inputSchema={
                'type': 'object',
                'properties': {
                    'text': {
                        'type': 'string',
                        'description': 'Text to translate',
                    },
                    'target_lang': {
                        'type': 'string',
                        'enum': ['ENG', 'RUS', 'UKR'],
                        'description': 'Target language code',
                    },
                },
                'required': ['text', 'target_lang'],
            },
        ),
        Tool(
            name='detect_language',
            description=(
                'Detect the language of the given text. '
                'Returns the detected language code.'
            ),
            inputSchema={
                'type': 'object',
                'properties': {
                    'text': {
                        'type': 'string',
                        'description': 'Text to detect language for',
                    },
                },
                'required': ['text'],
            },
        ),
        Tool(
            name='get_supported_languages',
            description='Get list of supported languages for translation.',
            inputSchema={
                'type': 'object',
                'properties': {},
                'required': [],
            },
        ),
        Tool(
            name='check_api_health',
            description=(
                'Check if the translation API is available and healthy.'
            ),
            inputSchema={
                'type': 'object',
                'properties': {},
                'required': [],
            },
        ),
    ]


def translate_text(
    text: str,
    source_lang: str,
    target_lang: str,
) -> dict[str, Any]:
    """
    Translate text from source to target language.
    """
    logger.info(
        'Tool called: translate_text | text_length=%d, '
        'source_lang=%s, target_lang=%s',
        len(text),
        source_lang,
        target_lang,
    )

    if source_lang not in MyMemoryAPIClient.SUPPORTED_LANGUAGES:
        logger.error('Unsupported source language: %s', source_lang)
        raise ValueError(f'Unsupported source language: {source_lang}')

    if target_lang not in MyMemoryAPIClient.SUPPORTED_LANGUAGES:
        logger.error('Unsupported target language: %s', target_lang)
        raise ValueError(f'Unsupported target language: {target_lang}')

    if source_lang == target_lang:
        logger.warning('Source and target languages are the same')
        translated = text
    else:
        lang_pair = f'{source_lang.lower()}|{target_lang.lower()}'
        result = client.translate(text, lang_pair)

        logger.info(
            'Tool result: translate_text | status=%s, is_translated=%s',
            result.get('status'),
            result.get('is_translated'),
        )

        if not (result['status'] == 'success' and result['is_translated']):
            error_msg = result.get('error', 'Unknown error')
            logger.error('Translation failed: %s', error_msg)
            raise RuntimeError(f'Translation failed: {error_msg}')

        translated = result['translated_text']

    return {
        'source_lang': source_lang,
        'target_lang': target_lang,
        'original_text': text,
        'translated_text': translated,
    }


def translate_with_detection(
    text: str,
    target_lang: str,
) -> dict[str, Any]:
    """
    Translate text with automatic language detection.
    """
    logger.info(
        'Tool called: translate_with_detection | text_length=%d, '
        'target_lang=%s',
        len(text),
        target_lang,
    )

    if target_lang not in MyMemoryAPIClient.SUPPORTED_LANGUAGES:
        logger.error('Unsupported target language: %s', target_lang)
        raise ValueError(f'Unsupported target language: {target_lang}')

    source_lang = client.detect_language(text)
    if source_lang is None:
        logger.error('Could not detect source language')
        raise RuntimeError('Could not detect source language of the text')

    logger.info('Detected source language: %s', source_lang)

    if source_lang == target_lang:
        logger.warning('Detected source equals target language')
        translated = text
    else:
        lang_pair = f'{source_lang.lower()}|{target_lang.lower()}'
        result = client.translate(text, lang_pair)

        logger.info(
            'Tool result: translate_with_detection | status=%s, '
            'is_translated=%s',
            result.get('status'),
            result.get('is_translated'),
        )

        if not (result['status'] == 'success' and result['is_translated']):
            error_msg = result.get('error', 'Unknown error')
            logger.error('Translation failed: %s', error_msg)
            raise RuntimeError(f'Translation failed: {error_msg}')

        translated = result['translated_text']

    return {
        'detected_source_lang': source_lang,
        'target_lang': target_lang,
        'original_text': text,
        'translated_text': translated,
    }


def detect_language(text: str) -> dict[str, Any]:
    """
    Detect language of the given text.
    """
    logger.info(
        'Tool called: detect_language | text_length=%d',
        len(text),
    )

    detected = client.detect_language(text)

    result = {
        'detected_language': detected,
        'supported_languages': list(
            MyMemoryAPIClient.SUPPORTED_LANGUAGES.keys()
        ),
    }

    logger.info(
        'Tool result: detect_language | detected=%s',
        detected,
    )

    return result


def get_supported_languages() -> dict[str, str]:
    """
    Get list of all supported languages.
    """
    logger.info('Tool called: get_supported_languages')

    languages = MyMemoryAPIClient.get_supported_languages()

    logger.info(
        'Tool result: get_supported_languages | '
        'count=%d, languages=%s',
        len(languages),
        list(languages.keys()),
    )

    return languages


def check_api_health() -> dict[str, Any]:
    """
    Check if translation API is available.
    """
    logger.info('Tool called: check_api_health')

    is_healthy = client.check_health()

    result = {
        'api_available': is_healthy,
        'status': 'healthy' if is_healthy else 'unavailable',
    }

    logger.info(
        'Tool result: check_api_health | api_available=%s',
        is_healthy,
    )

    return result
