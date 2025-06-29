import sys
import io
import time
import re
from ollama import Client

# Load Ollama client
ollama_client = Client()
options = {
    "num_gpu": 0,
    "num_ctx": 16000,
    "num_predict": 16000,
    "temperature": 0.1,
    "repeat_penalty": 1.1
}

def translate_english_to_kannada(text):
    """
    Translate English text to Kannada using Ollama
    """
    try:
        if isinstance(text, bytes):
            text = text.decode('utf-8', errors='replace')

        prompt = f"""Translate the following English text to Kannada. Provide only the Kannada translation without any explanations or extra text:

English Text: {text}

Kannada Translation:"""

        response = ollama_client.generate(
            model="gemma3:4b",
            prompt=prompt,
            options=options
        )

        # Clean response
        translation = response['response'].strip()
        translation = re.sub(r'^(Kannada Translation:|Translation:)', '', translation).strip()

        return translation

    except Exception as e:
        print(f"Translation Error: {e}")
        return f"Error: {str(e)}"

def main():
    print("🟢 English ➡ Kannada Translator")
    print("=" * 40)
    print("Enter English sentences to translate them into Kannada.")
    print("Type 'exit' or 'quit' to stop.")
    print("=" * 40)

    while True:
        try:
            input_text = input("\nEnter English text:\n> ").strip()

            if input_text.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break

            if not input_text:
                print("⚠️ Please enter some text.")
                continue

            print("Translating... Please wait...")
            start_time = time.time()

            translation = translate_english_to_kannada(input_text)
            elapsed_time = time.time() - start_time

            print("\n✅ Kannada Translation:")
            print(translation)
            print(f"⏱️ Time taken: {elapsed_time:.2f} seconds")

        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Exiting...")
            break
        except Exception as e:
            print(f"Unexpected Error: {e}")

if __name__ == "__main__":
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    main()
