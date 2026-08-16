import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.userbot import (
    UserbotManager,
    SessionManager,
    SourceResolver,
    AccessChecker,
    MessageScanner,
    URLExtractor,
    URLNormalizer,
    Deduplicator
)

async def test_session_manager():
    print("Testing SessionManager...")
    manager = SessionManager()
    
    test_data = {
        "session_string": "test_session_string",
        "phone": "+1234567890",
        "user_id": 123456789
    }
    
    encrypted = manager.pack_session(
        session_string=test_data["session_string"],
        phone=test_data["phone"],
        user_id=test_data["user_id"]
    )
    
    print(f"Encrypted: {encrypted[:50]}...")
    
    decrypted = manager.get_session_data(encrypted)
    print(f"Decrypted: {decrypted}")
    
    print("SessionManager test passed")

async def test_source_resolver():
    print("\nTesting SourceResolver...")
    
    test_inputs = [
        "@testgroup",
        "https://t.me/testgroup",
        "https://t.me/+abcdef12345",
        "https://t.me/joinchat/abcdef12345",
        "-100123456789",
        "123456789"
    ]
    
    for input_text in test_inputs:
        parsed = SourceResolver.parse_input(input_text)
        print(f"Input: {input_text} -> Type: {parsed['type']}, Value: {parsed.get('value', 'N/A')}")
    
    print("SourceResolver test passed")

async def test_url_extractor():
    print("\nTesting URLExtractor...")
    
    extractor = URLExtractor()
    
    test_text = """
    Check these links:
    https://chat.whatsapp.com/abcdefghijklmnopqrstuvwxyz
    https://t.me/testgroup
    https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ
    https://wa.me/+1234567890
    https://youtube.com/watch?v=123
    """
    
    urls = extractor.extract_from_text(test_text)
    print(f"Extracted URLs: {urls}")
    
    whatsapp_urls = extractor.extract_whatsapp_urls(urls)
    print(f"WhatsApp URLs: {whatsapp_urls}")
    
    print("URLExtractor test passed")

async def test_url_normalizer():
    print("\nTesting URLNormalizer...")
    
    normalizer = URLNormalizer()
    
    test_urls = [
        "https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "http://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "https://CHAT.WHATSAPP.COM/ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ?text=test"
    ]
    
    for url in test_urls:
        normalized = normalizer.normalize(url)
        whatsapp_normalized = normalizer.normalize_whatsapp(url)
        print(f"Original: {url}")
        print(f"Normalized: {normalized}")
        print(f"WhatsApp Normalized: {whatsapp_normalized}")
        print("---")
    
    print("URLNormalizer test passed")

async def test_deduplicator():
    print("\nTesting Deduplicator...")
    
    deduplicator = Deduplicator()
    
    urls = [
        "https://chat.whatsapp.com/AAAAA",
        "https://chat.whatsapp.com/BBBBB",
        "https://chat.whatsapp.com/AAAAA",
        "https://chat.whatsapp.com/CCCCC",
        "https://chat.whatsapp.com/BBBBB"
    ]
    
    unique = deduplicator.deduplicate(urls)
    print(f"Original URLs: {urls}")
    print(f"Unique URLs: {unique}")
    
    stats = deduplicator.get_stats()
    print(f"Stats: {stats}")
    
    print("Deduplicator test passed")

async def main():
    print("=== Userbot Component Tests ===\n")
    
    await test_session_manager()
    await test_source_resolver()
    await test_url_extractor()
    await test_url_normalizer()
    await test_deduplicator()
    
    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    asyncio.run(main())