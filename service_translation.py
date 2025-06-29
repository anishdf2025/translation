import sys
import io
import os
import time
import re
from ollama import Client
from langdetect import detect

# Load Ollama client
ollama_client = Client()
options = {
    "num_gpu": 0, 
    "num_ctx": 2048, 
    "num_predict": 2500, 
    "temperature": 0.1,
    "repeat_penalty": 1.2
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

def translate_from_file():
    """
    Function to translate text from a file with 2048 token chunking
    """
    print("File-based Translation Tool")
    print("=" * 50)
    print("Instructions:")
    print("- Enter the path to a text file containing content to translate")
    print("- Language will be automatically detected")
    print("- Text will be split into chunks of approximately 2048 tokens")
    print("- Each chunk will be translated individually")
    print("-" * 50)
    
    while True:
        try:
            # Get file path from user
            print("\nEnter the path to the text file (or 'quit' to exit):")
            file_path = input("> ").strip()
            
            # Check if user wants to quit
            if file_path.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            # Check if file exists
            if not os.path.isfile(file_path):
                print(f"Error: File '{file_path}' not found. Please check the path and try again.")
                continue
            
            # Read the file content
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    input_text = file.read()
            except Exception as e:
                print(f"Error reading file: {e}")
                continue
            
            if not input_text:
                print("The file is empty. Please choose a file with content.")
                continue
            
            # Show processing message and file size
            file_size_kb = os.path.getsize(file_path) / 1024
            print(f"\nFile size: {file_size_kb:.2f} KB")
            
            # Create output file name
            file_name = os.path.basename(file_path)
            file_base, file_ext = os.path.splitext(file_name)
            
            # Start timing the whole process
            total_start_time = time.time()
            
            # Detect language of the text
            try:
                sample_text = input_text[:1000] if len(input_text) > 1000 else input_text
                source_lang = detect(sample_text)
                target_lang = "English" if source_lang == "hi" else "Hindi"
                print(f"[DEBUG] Detected language: {source_lang}, will translate to {target_lang}")
            except Exception as e:
                print(f"[DEBUG] Language detection error: {e}. Defaulting to English")
                source_lang = "en"
                target_lang = "Hindi"
            
            # Function to estimate token count (rough approximation)
            def estimate_tokens(text):
                # Rough estimation: 4 characters per token for English, adjust for Hindi
                if source_lang == 'hi':
                    # Hindi might need different token estimation
                    return len(text) / 3  # Assuming Hindi uses ~3 chars per token on average
                else:
                    # For English text
                    return len(text) / 4  # Assuming English uses ~4 chars per token on average
            
            # Split text into chunks of approximately 2048 tokens
            print("\nSplitting text into chunks of approximately 2048 tokens for translation... Please wait...")
            
            # Determine chunk size in characters based on token estimation
            chars_per_chunk = 2048 * (3 if source_lang == 'hi' else 4)
            
            # Print total text length for debugging
            text_length = len(input_text)
            print(f"[DEBUG] Total text length: {text_length} characters")
            print(f"[DEBUG] Estimated total tokens: {estimate_tokens(input_text):.0f}")
            print(f"[DEBUG] Target characters per chunk: ~{chars_per_chunk:.0f} (for ~1024 tokens)")
            
            # Calculate the number of chunks needed
            num_chunks = (text_length + chars_per_chunk - 1) // chars_per_chunk
            print(f"[DEBUG] Will create approximately {num_chunks} chunks")
            
            # Split into chunks
            chunks = []
            current_pos = 0
            chunk_num = 1
            
            while current_pos < text_length:
                # Calculate end position for this chunk (or end of text)
                target_end = min(current_pos + int(chars_per_chunk), text_length)
                
                # If we're not at the end of the text, adjust to avoid breaking words
                if target_end < text_length:
                    # Look for word boundaries (space, newline, punctuation)
                    word_boundary_found = False
                    
                    # Define search window: look back up to 200 chars from target
                    search_start = max(current_pos + int(chars_per_chunk * 0.9), current_pos)
                    search_end = min(current_pos + int(chars_per_chunk * 1.1), text_length)
                    
                    # Look for paragraph breaks first (most natural)
                    for i in range(target_end, search_start, -1):
                        if i < text_length and input_text[i-1:i+1] == '\n\n':
                            target_end = i
                            word_boundary_found = True
                            print(f"[DEBUG] Chunk {chunk_num}: Found paragraph break at position {i}")
                            break
                    
                    # If no paragraph break, look for sentence endings
                    if not word_boundary_found:
                        for i in range(target_end, search_start, -1):
                            if i < text_length and input_text[i-1] in ['.', '!', '?', '।'] and (i == text_length or input_text[i] in [' ', '\n']):
                                target_end = i
                                word_boundary_found = True
                                print(f"[DEBUG] Chunk {chunk_num}: Found sentence end at position {i}")
                                break
                    
                    # If no sentence end, just find a space
                    if not word_boundary_found:
                        for i in range(target_end, search_start, -1):
                            if i < text_length and input_text[i-1] in [' ', '\n', '\t']:
                                target_end = i
                                word_boundary_found = True
                                print(f"[DEBUG] Chunk {chunk_num}: Found space at position {i}")
                                break
                    
                    # If still no boundary found, try to find one after the target point
                    if not word_boundary_found:
                        for i in range(target_end, search_end):
                            if i < text_length and input_text[i] in [' ', '\n', '\t']:
                                target_end = i + 1
                                word_boundary_found = True
                                print(f"[DEBUG] Chunk {chunk_num}: Found space after target at position {i}")
                                break
                    
                    # Last resort - just cut at target position
                    if not word_boundary_found:
                        print(f"[WARNING] Chunk {chunk_num}: No word boundary found near position {target_end}, may break mid-word")
                
                # Extract the chunk and add to our list
                chunk = input_text[current_pos:target_end]
                chunks.append(chunk)
                
                # Debug output
                print(f"[DEBUG] Chunk {chunk_num}: {len(chunk)} characters (~{estimate_tokens(chunk):.0f} tokens) from positions {current_pos}-{target_end}")
                
                # Update for next iteration
                current_pos = target_end
                chunk_num += 1
            
            print(f"[DEBUG] Split text into {len(chunks)} chunks")
            
            # Debug output - show first few characters of each chunk
            for i, chunk in enumerate(chunks, 1):
                preview = chunk[:50].replace('\n', '\\n')
                print(f"[DEBUG] Chunk {i} begins with: {preview}...")
            
            # Prepare output files
            output_file = f"{file_base}_chunks_{target_lang.lower()}{file_ext}"
            output_path = os.path.join(os.path.dirname(file_path), output_file)
            
            clean_output_file = f"{file_base}_clean_translation{file_ext}"
            clean_output_path = os.path.join(os.path.dirname(file_path), clean_output_file)
            
            translated_chunks = []
            clean_translations = []
            total_chunks = len(chunks)
            
            # Create a summary file for timing information
            timing_file = f"{file_base}_chunk_translation_timing.txt"
            timing_path = os.path.join(os.path.dirname(file_path), timing_file)
            
            with open(timing_path, 'w', encoding='utf-8') as timing_f:
                timing_f.write(f"Chunk-by-Chunk Translation Timing Information\n")
                timing_f.write(f"{'='*60}\n")
                timing_f.write(f"Source file: {file_path}\n")
                timing_f.write(f"Number of chunks: {total_chunks}\n\n")
                timing_f.write(f"{'Chunk #':<10} {'Size (chars)':<15} {'Est. Tokens':<15} {'Time (seconds)':<15}\n")
                timing_f.write(f"{'-'*60}\n")
                
                for i, chunk in enumerate(chunks, 1):
                    # Print a clear separator
                    print("\n" + "=" * 80)
                    print(f"CHUNK #{i}/{total_chunks} ({len(chunk)} characters, ~{estimate_tokens(chunk):.0f} tokens)")
                    print("-" * 80)
                    # Print the beginning and end of the chunk
                    chunk_preview = (chunk[:100] + "..." + chunk[-100:]) if len(chunk) > 200 else chunk
                    print(f"ORIGINAL ({('Hindi' if source_lang == 'hi' else 'English')}) Preview:")
                    print(f"{chunk_preview}")
                    
                    # Start timing for this chunk
                    chunk_start_time = time.time()
                    
                    # Debug information before translation
                    print(f"\n[DEBUG] Translating chunk #{i} from {source_lang} to {target_lang}")
                    
                    # Translate the chunk
                    translation, _, _ = translate_text(chunk)
                    
                    # Calculate and record elapsed time
                    chunk_elapsed_time = time.time() - chunk_start_time
                    timing_f.write(f"{i:<10} {len(chunk):<15} {estimate_tokens(chunk):<15.0f} {chunk_elapsed_time:.2f}\n")
                    
                    # Print a preview of the translation
                    translation_preview = (translation[:100] + "..." + translation[-100:]) if len(translation) > 200 else translation
                    print(f"\nTRANSLATION ({target_lang}) Preview:")
                    print(f"{translation_preview}")
                    print(f"\nTime: {chunk_elapsed_time:.2f} seconds")
                    print("=" * 80)
                    
                    # Add the original chunk and its translation
                    chunk_entry = f"Chunk {i}:\nOriginal ({('Hindi' if source_lang == 'hi' else 'English')}):\n{chunk}\n\nTranslation ({target_lang}):\n{translation}\n"
                    translated_chunks.append(chunk_entry)
                    clean_translations.append(translation)
                
                # Record total time
                total_elapsed_time = time.time() - total_start_time
                timing_f.write(f"\nTotal translation time: {total_elapsed_time:.2f} seconds\n")
            
            # Save all translated chunks to the output file
            try:
                with open(output_path, 'w', encoding='utf-8') as file:
                    file.write("\n" + "="*60 + "\n")
                    file.write(f"CHUNK-BY-CHUNK TRANSLATION\n")
                    file.write("="*60 + "\n\n")
                    
                    # Create the output content
                    output_content = ""
                    for item in translated_chunks:
                        # Make sure each item is a string
                        item_str = str(item)
                        output_content += item_str + "\n" + "-"*50 + "\n\n"
                    
                    file.write(output_content)
                print(f"Translation successfully saved to: {output_path}")
            except Exception as e:
                print(f"Error saving translation: {e}")
                continue
                
            # Save clean translations (just the translated text)
            try:
                with open(clean_output_path, 'w', encoding='utf-8') as file:
                    # Create output content without using join
                    clean_output = ""
                    for item in clean_translations:
                        # Make sure each item is a string
                        item_str = str(item)
                        clean_output += item_str + " "
                    
                    file.write(clean_output)
                print(f"Clean translation successfully saved to: {clean_output_path}")
            except Exception as e:
                print(f"Error saving clean translation: {e}")
            
            # Display results
            print("\n" + "=" * 60)
            print("CHUNK-BY-CHUNK TRANSLATION COMPLETE")
            print("=" * 60)
            print(f"Detected language: {'Hindi' if source_lang == 'hi' else 'English'}")
            print(f"Source file: {file_path}")
            print(f"Detailed translation saved to: {output_path}")
            print(f"Clean translation saved to: {clean_output_path}")
            print(f"Timing information saved to: {timing_path}")
            print(f"Total chunks: {total_chunks}")
            print(f"Total time taken: {total_elapsed_time:.2f} seconds")
            print("=" * 60)
            
            # Ask if user wants to see a preview
            print("\nWould you like to see a preview of the translation? (y/n)")
            preview = input("> ").strip().lower()
            if preview in ['y', 'yes']:
                print("\nPreview of chunk-by-chunk translation (first chunk):")
                print("-" * 50)
                if translated_chunks:
                    print(translated_chunks[0])
                print("-" * 50)
                
                print("\nPreview of clean translation (beginning):")
                print("-" * 50)
                if clean_translations:
                    preview_clean = clean_translations[0][:300]
                    print(f"{preview_clean}...")
                print("-" * 50)
            
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
    
    print("Starting File Translation Service")
    translate_from_file()