import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.analyzers import WhatsAppAnalyzer, Classifier, ResultValidator

async def test_analyzer():
    print("Testing WhatsAppAnalyzer...")
    
    analyzer = WhatsAppAnalyzer()
    
    test_urls = [
        "https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "https://chat.whatsapp.com/INVALID_HASH",
        "https://wa.me/1234567890",
        "https://t.me/testgroup",
        "https://youtube.com/watch?v=123"
    ]
    
    for url in test_urls:
        can_analyze = await analyzer.can_analyze(url)
        print(f"URL: {url}")
        print(f"Can analyze: {can_analyze}")
        
        if can_analyze:
            result = await analyzer.analyze(url)
            print(f"Result status: {result.status.value}")
            print(f"Confidence: {result.confidence.value}")
            print(f"Details: {result.details}")
        print("---")
    
    await analyzer.close()
    print("WhatsAppAnalyzer test passed")

async def test_classifier():
    print("\nTesting Classifier...")
    
    classifier = Classifier()
    
    test_data = [
        {
            "url": "https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "data": {"status_code": 200, "final_url": "https://chat.whatsapp.com/ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
        },
        {
            "url": "https://chat.whatsapp.com/INVALID_HASH",
            "data": {"status_code": 404, "final_url": "https://chat.whatsapp.com/INVALID_HASH"}
        },
        {
            "url": "https://chat.whatsapp.com/REQUEST_HASH",
            "data": {"status_code": 403, "final_url": "https://chat.whatsapp.com/REQUEST_HASH"}
        }
    ]
    
    for item in test_data:
        result = await classifier.classify(item["url"], item["data"])
        print(f"URL: {item['url']}")
        print(f"Status: {result['status'].value}")
        print(f"Confidence: {result['confidence'].value}")
        print("---")
    
    print("Classifier test passed")

async def test_validator():
    print("\nTesting ResultValidator...")
    
    validator = ResultValidator()
    
    test_results = [
        {"status": "DIRECT_JOIN", "confidence": "HIGH", "details": {"status_code": 200}},
        {"status": "INVALID", "confidence": "HIGH", "details": {"status_code": 404}},
        {"status": "UNKNOWN", "details": {}}
    ]
    
    for result in test_results:
        validated = await validator.validate(result)
        print(f"Original: {result}")
        print(f"Validated: {validated}")
        print("---")
    
    print("ResultValidator test passed")

async def main():
    print("=== Analyzer Component Tests ===\n")
    
    await test_analyzer()
    await test_classifier()
    await test_validator()
    
    print("\nAll tests passed successfully!")

if __name__ == "__main__":
    asyncio.run(main())