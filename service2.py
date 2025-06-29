import sys
import io
import time
import re
from ollama import Client
from langdetect import detect

# Load Ollama client
ollama_client = Client()
options = {
    "num_gpu": 0, 
    "num_ctx": 16000, 
    "num_predict": 16000, 
    "temperature": 0.1
}

def translate_text(text):
    """
    Translate text between English and Hindi using Ollama
    by first detecting the language
    """
    try:
        # Ensure text is properly encoded
        if isinstance(text, bytes):
            text = text.decode('utf-8', errors='replace')
        
        # Detect language
        detected_lang = detect(text)
        
        if detected_lang == 'hi':
            # Hindi to English
            prompt = f"""Translate the following Hindi text to English. Provide only the English translation without any explanations or additional text:

Hindi Text: {text}

English Translation:"""
            target_lang = "English"
        else:
            # Default to English to Hindi
            prompt = f"""Translate the following English text to Hindi. Provide only the Hindi translation without any explanations or additional text:

English Text: {text}

Hindi Translation:"""
            target_lang = "Hindi"
        
        response = ollama_client.generate(
            model="gemma3:4b",
            prompt=prompt,
            options=options
        )
        
        # Extract the translation from response
        translation = response['response'].strip()
        
        # Clean up the translation (remove any extra formatting)
        translation = re.sub(r'^(Hindi Translation:|English Translation:|Translation:)', '', translation).strip()
        
        return translation, detected_lang, target_lang
    
    except Exception as e:
        print(f"Error during translation: {e}")
        return f"Translation Error: {str(e)}", "unknown", "unknown"

def translate_multiline():
    """
    Function for multi-line input translation
    """
    print("Automatic Language Translation Tool (Multi-line Mode)")
    print("=" * 50)
    print("Instructions:")
    print("- Enter your text (English or Hindi, can be multiple lines)")
    print("- Language will be automatically detected")
    print("- Press Enter twice (empty line) to finish input")
    print("- Type 'quit' on a new line to exit")
    print("-" * 50)
    
    while True:
        try:
            print("\nEnter text (press Enter twice when done):")
            lines = []
            
            while True:
                line = input()
                if line.lower().strip() in ['quit', 'exit']:
                    print("Goodbye!")
                    return
                if line == "":  # Empty line means end of input
                    break
                lines.append(line)
            
            input_text = "\n".join(lines).strip()
            
            if not input_text:
                print("Please enter some text to translate.")
                continue
            
            # Show processing message
            print("\nDetecting language and translating... Please wait...")
            
            # Start timing
            start_time = time.time()
            
            # Translate the text
            translation, source_lang, target_lang = translate_text(input_text)
            
            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            
            # Display results
            print("\n" + "=" * 50)
            print("TRANSLATION RESULT")
            print("=" * 50)
            print(f"Detected language: {'Hindi' if source_lang == 'hi' else 'English'}")
            print("Source:")
            print(input_text)
            print(f"\n{target_lang}:")
            print(translation)
            print(f"Time taken: {elapsed_time:.2f} seconds")
            print("=" * 50)
            
        except KeyboardInterrupt:
            print("\n\nProgram interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please try again.")

if __name__ == "__main__":
    # Set default stdin/stdout encoding to UTF-8
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("Starting Multi-line Translation Service")
    translate_multiline()