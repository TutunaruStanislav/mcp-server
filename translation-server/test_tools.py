#!/usr/bin/env python3
"""Test script for translation tools."""

import sys
import logging

from src.tools import (
    translate_text,
    translate_with_detection,
    detect_language,
    get_supported_languages,
    check_api_health,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_check_api_health():
    """Test API health check."""
    print('\n' + '='*60)
    print('TEST 1: check_api_health')
    print('='*60)
    try:
        result = check_api_health()
        print(f'[OK] Result: {result}')
        return True
    except Exception as e:
        print(f'[FAIL] Error: {e}')
        return False


def test_get_supported_languages():
    """Test getting supported languages."""
    print('\n' + '='*60)
    print('TEST 2: get_supported_languages')
    print('='*60)
    try:
        result = get_supported_languages()
        print(f'[OK] Result: {result}')
        return True
    except Exception as e:
        print(f'[FAIL] Error: {e}')
        return False


def test_translate_text():
    """Test basic translation."""
    print('\n' + '='*60)
    print('TEST 3: translate_text (ENG -> RUS)')
    print('='*60)
    try:
        result = translate_text(
            text='Hello, world!',
            source_lang='ENG',
            target_lang='RUS'
        )
        print(f'[OK] Input: "Hello, world!"')
        print(f'[OK] Output: "{result["translated_text"]}"')
        return True
    except Exception as e:
        print(f'[FAIL] Error: {e}')
        return False


def test_translate_text_rus_to_eng():
    """Test translation RUS -> ENG."""
    print('\n' + '='*60)
    print('TEST 4: translate_text (RUS -> ENG)')
    print('='*60)
    try:
        result = translate_text(
            text='Привет, мир!',
            source_lang='RUS',
            target_lang='ENG'
        )
        print(f'[OK] Input: "Привет, мир!"')
        print(f'[OK] Output: "{result["translated_text"]}"')
        return True
    except Exception as e:
        print(f'[FAIL] Error: {e}')
        return False


def test_translate_with_detection():
    """Test translation with auto-detection."""
    print('\n' + '='*60)
    print('TEST 5: translate_with_detection')
    print('='*60)
    try:
        result = translate_with_detection(
            text='Good morning!',
            target_lang='RUS'
        )
        print(f'[OK] Input: "Good morning!"')
        print(f'[OK] Detected source: {result["detected_source_lang"]}')
        print(f'[OK] Output: "{result["translated_text"]}"')
        return True
    except Exception as e:
        print(f'[FAIL] Error: {e}')
        return False


def test_detect_language():
    """Test language detection."""
    print('\n' + '='*60)
    print('TEST 6: detect_language')
    print('='*60)
    try:
        result = detect_language(text='Hello world')
        print(f'[OK] Input: "Hello world"')
        print(f'[OK] Result: {result}')
        return True
    except Exception as e:
        print(f'[FAIL] Error: {e}')
        return False


def main():
    """Run all tests."""
    print('\n' + '='*60)
    print('TRANSLATION MCP SERVER - TOOL TESTS')
    print('='*60)

    tests = [
        ('API Health', test_check_api_health),
        ('Supported Languages', test_get_supported_languages),
        ('Translate ENG->RUS', test_translate_text),
        ('Translate RUS->ENG', test_translate_text_rus_to_eng),
        ('Translate with Detection', test_translate_with_detection),
        ('Detect Language', test_detect_language),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f'[FAIL] Test failed with exception: {e}')
            results.append((name, False))

    print('\n' + '='*60)
    print('TEST SUMMARY')
    print('='*60)
    for name, passed in results:
        status = '[OK] PASS' if passed else '[FAIL] FAIL'
        print(f'{status}: {name}')

    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    print(f'\nTotal: {passed_count}/{total_count} tests passed')

    return 0 if passed_count == total_count else 1


if __name__ == '__main__':
    sys.exit(main())
