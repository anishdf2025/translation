from langdetect import detect


class LanguageDetector:
    """Handles language detection for translation"""
    
    def __init__(self):
        pass
    
    def detect_language(self, text):
        """Detect the language of input text"""
        try:
            # Use first 1000 characters for detection if text is long
            sample_text = text[:1000] if len(text) > 1000 else text
            detected_lang = detect(sample_text)
            
            # Determine target language
            if detected_lang == 'hi':
                target_lang = "English"
            else:
                target_lang = "Hindi"
            
            return detected_lang, target_lang, None
            
        except Exception as e:
            # Default to English if detection fails
            return "en", "Hindi", str(e)
    
    def get_language_name(self, lang_code):
        """Get full language name from code"""
        if lang_code == 'hi':
            return 'Hindi'
        elif lang_code == 'en':
            return 'English'
        else:
            return 'Unknown'
