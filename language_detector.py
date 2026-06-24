from langdetect import detect, DetectorFactory, LangDetectException
from config import Config

# Set seed for reproducibility
DetectorFactory.seed = 0

class LanguageDetector:
    """Language detection and management"""
    
    LANGUAGE_CODES = Config.SUPPORTED_LANGUAGES.keys()
    FALLBACK_LANGUAGE = 'en'
    
    @staticmethod
    def detect_language(text):
        """Detect language from text"""
        try:
            if not text or len(text.strip()) < 2:
                return LanguageDetector.FALLBACK_LANGUAGE
            
            detected = detect(text)
            
            # Map to supported languages
            if detected in LanguageDetector.LANGUAGE_CODES:
                return detected
            
            # Handle language variants (e.g., pt-BR -> pt)
            base_lang = detected.split('-')[0]
            if base_lang in LanguageDetector.LANGUAGE_CODES:
                return base_lang
            
            return LanguageDetector.FALLBACK_LANGUAGE
        
        except LangDetectException:
            return LanguageDetector.FALLBACK_LANGUAGE
    
    @staticmethod
    def get_language_name(language_code):
        """Get language name from code"""
        return Config.SUPPORTED_LANGUAGES.get(language_code, 'Unknown')
    
    @staticmethod
    def detect_mixed_languages(text):
        """Detect if text contains multiple languages"""
        try:
            if not text or len(text.strip()) < 5:
                return [LanguageDetector.FALLBACK_LANGUAGE]
            
            from langdetect import detect_langs
            detected = detect_langs(text)
            
            languages = []
            for lang_prob in detected:
                lang_code = lang_prob.lang
                base_lang = lang_code.split('-')[0]
                
                if base_lang in LanguageDetector.LANGUAGE_CODES:
                    languages.append(base_lang)
            
            return list(set(languages)) if languages else [LanguageDetector.FALLBACK_LANGUAGE]
        
        except LangDetectException:
            return [LanguageDetector.FALLBACK_LANGUAGE]
    
    @staticmethod
    def is_supported_language(language_code):
        """Check if language is supported"""
        return language_code in LanguageDetector.LANGUAGE_CODES
