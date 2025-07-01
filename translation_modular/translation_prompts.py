import re
from ollama import Client


class TranslationPrompts:
    """Handles translation prompts and Ollama client interactions"""
    
    def __init__(self):
        # Load Ollama client
        self.ollama_client = Client()
        self.options = {
            "num_gpu": 0, 
            "num_ctx": 16000,
            "num_predict": 2048, 
            "temperature": 0.2,
            "repeat_penalty": 1.2
        }
    
    def create_translation_prompt(self, text, source_lang):
        """Create appropriate translation prompt based on source language"""
        if source_lang == 'hi':
            # Hindi to English
            prompt = f"""You are a translation assistant. Translate only the following Hindi text to English without explanation, rephrasing, or any added formatting. Output only the translated English text:

Hindi Text: {text}

English Translation:"""
            target_lang = "English"
        else:
            # Default to English to Hindi
            prompt = f"""You are a translation assistant. Translate only the following English text to Hindi without explanation, rephrasing, or any added formatting. Output only the translated Hindi text:

English Text: {text}

Hindi Translation:"""
            target_lang = "Hindi"
        
        return prompt, target_lang
    
    def translate_text(self, text, source_lang):
        """
        Translate text using Ollama with appropriate prompts
        """
        try:
            # Ensure text is properly encoded
            if isinstance(text, bytes):
                text = text.decode('utf-8', errors='replace')
            # Create prompt
            prompt, target_lang = self.create_translation_prompt(text, source_lang)
            
            # Get translation from Ollama
            response = self.ollama_client.generate(
                model="gemma3n:e2b",
                prompt=prompt,
                options=self.options
            )
            
            # Extract the translation from response
            translation = response['response'].strip()
            
            # Clean up the translation (remove any extra formatting)
            translation = re.sub(r'^(Hindi Translation:|English Translation:|Translation:)', '', translation).strip()
            
            return translation, target_lang, None
        
        except Exception as e:
            error_msg = f"Translation Error: {str(e)}"
            return error_msg, "unknown", str(e)
