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
    "temperature": 0.1,
    "repeat_penalty": 1.1
}

def translate_text(text):
    """
    Translate text between English and Kannada using Ollama
    by first detecting the language
    """
    try:
        # Ensure text is properly encoded
        if isinstance(text, bytes):
            text = text.decode('utf-8', errors='replace')
        
        # Detect language
        detected_lang = detect(text)
        
        if detected_lang == 'kn':
            # Kannada to English
            prompt = f"""Translate the following Kannada text to English. Provide only the English translation without any explanations or additional text:

Kannada Text: {text}

English Translation:"""
            target_lang = "English"
        else:
            # Default to English to Kannada
            prompt = f"""Translate the following English text to Kannada. Provide only the Kannada translation without any explanations or additional text:

English Text: {text}

Kannada Translation:"""
            target_lang = "Kannada"
        
        response = ollama_client.generate(
            model="gemma3:4b",
            prompt=prompt,
            options=options
        )
        
        # Extract the translation from response
        translation = response['response'].strip()
        
        # Clean up the translation (remove any extra formatting)
        translation = re.sub(r'^(Kannada Translation:|English Translation:|Translation:)', '', translation).strip()
        
        return translation, detected_lang, target_lang
    
    except Exception as e:
        print(f"Error during translation: {e}")
        return f"Translation Error: {str(e)}", "unknown", "unknown"

def main():
    """
    Main function for translation
    """
    print("Automatic Language Translation Tool")
    print("=" * 40)
    print("Instructions:")
    print("- Enter your text (English or Kannada) when prompted")
    print("- Language will be automatically detected")
    print("- Type 'quit' or 'exit' to stop the program")
    print("-" * 40)
    
    while True:
        try:
            # Get input from user
            print("\nEnter text to translate (English or Kannada):")
            input_text = input("> ").strip()
            
            # Check if user wants to quit
            if input_text.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            # Check if input is empty
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
            print(f"Detected language: {'Kannada' if source_lang == 'kn' else 'English'}")
            print(f"Source: {input_text}")
            print(f"{target_lang}: {translation}")
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
    
    print("Starting Single-line Translation Service")
    main()