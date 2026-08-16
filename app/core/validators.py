import re
from typing import Optional, List
from urllib.parse import urlparse

from app.core.exceptions import ValidationError

class Validators:
    @staticmethod
    def validate_telegram_username(username: str) -> bool:
        pattern = re.compile(r'^@?[a-zA-Z][a-zA-Z0-9_]{4,31}$')
        return bool(pattern.match(username))

    @staticmethod
    def validate_telegram_id(chat_id: str) -> bool:
        pattern = re.compile(r'^-?100?\d+$')
        return bool(pattern.match(chat_id))

    @staticmethod
    def validate_telegram_url(url: str) -> bool:
        patterns = [
            re.compile(r'^https?://t\.me/[a-zA-Z][a-zA-Z0-9_]{4,31}$'),
            re.compile(r'^https?://t\.me/joinchat/[a-zA-Z0-9_-]+$'),
            re.compile(r'^https?://t\.me/\+[a-zA-Z0-9_-]+$')
        ]
        return any(p.match(url) for p in patterns)

    @staticmethod
    def validate_whatsapp_url(url: str) -> bool:
        patterns = [
            re.compile(r'^https?://chat\.whatsapp\.com/[a-zA-Z0-9_-]{22,}$'),
            re.compile(r'^https?://wa\.me/\+\d+$'),
            re.compile(r'^https?://api\.whatsapp\.com/send\?phone=\+\d+$')
        ]
        return any(p.match(url) for p in patterns)

    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        pattern = re.compile(r'^\+?[0-9]{7,15}$')
        return bool(pattern.match(phone))

    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(pattern.match(email))

    @staticmethod
    def validate_url(url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def validate_language_code(code: str) -> bool:
        valid_codes = ['ar', 'en', 'fr', 'es', 'de', 'ru']
        return code in valid_codes

    @staticmethod
    def validate_pagination(page: int, per_page: int) -> tuple:
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 20
        if per_page > 100:
            per_page = 100
        return page, per_page

    @staticmethod
    def validate_input(input_text: str, max_length: int = 4096) -> str:
        if not input_text:
            raise ValidationError("Input cannot be empty")
        if len(input_text) > max_length:
            raise ValidationError(f"Input exceeds maximum length of {max_length}")
        return input_text.strip()

    @staticmethod
    def validate_export_format(format_type: str) -> bool:
        valid_formats = ['txt', 'csv', 'json', 'xlsx']
        return format_type.lower() in valid_formats

    @staticmethod
    def validate_category(category: str) -> bool:
        valid_categories = ['direct_join', 'request_join']
        return category in valid_categories

validators = Validators()