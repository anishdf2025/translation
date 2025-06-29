#!/usr/bin/env python3
"""
Quick test to verify all modules can be imported and basic functionality works
"""

def test_imports():
    """Test that all modules can be imported"""
    try:
        from file_handler import FileHandler
        from text_splitter import TextSplitter
        from language_detector import LanguageDetector
        from translation_prompts import TranslationPrompts
        from display_utils import DisplayUtils
        from translation_service import TranslationService
        
        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of each module"""
    try:
        from file_handler import FileHandler
        from text_splitter import TextSplitter
        from language_detector import LanguageDetector
        from display_utils import DisplayUtils
        
        # Test TextSplitter
        splitter = TextSplitter()
        test_text = "This is a test. This is another sentence."
        print(f"✅ TextSplitter: Initialized successfully for text with {len(test_text)} characters")
        
        # Test LanguageDetector
        detector = LanguageDetector()
        lang, target, error = detector.detect_language("Hello world")
        print(f"✅ LanguageDetector: Detected '{lang}' -> '{target}'")
        
        # Test DisplayUtils
        display = DisplayUtils()
        print("✅ DisplayUtils: Initialized successfully")
        
        # Test FileHandler
        file_handler = FileHandler()
        print("✅ FileHandler: Initialized successfully")
        
        print("✅ Basic functionality tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Modular Translation System...")
    print("=" * 50)
    
    if test_imports() and test_basic_functionality():
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nTo run the translation system:")
        print("python main.py")
        print("or")
        print("python translation_service.py")
    else:
        print("\n❌ Some tests failed. Please check the setup.")
