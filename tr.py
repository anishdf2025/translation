import os
from ollama import Client
import re
import time
from langdetect import detect  # Added import for language detection

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

def answer_question(passage, question, is_general_question=False):
    """
    Extract answers from a passage based on questions or answer general questions
    Supports both Hindi and English
    """
    try:
        # Ensure text is properly encoded
        if isinstance(passage, bytes) and passage:
            passage = passage.decode('utf-8', errors='replace')
        if isinstance(question, bytes):
            question = question.decode('utf-8', errors='replace')
        
        # Detect language of question
        question_lang = detect(question)
        
        # For general questions (not related to passage)
        if is_general_question:
            if question_lang == 'hi':
                # Hindi question, answer in Hindi
                prompt = f"""निम्नलिखित प्रश्न का विस्तृत उत्तर हिंदी में दें।

प्रश्न: {question}

उत्तर:"""
                result_lang = "Hindi"
            else:
                # English question, answer in English
                prompt = f"""Answer the following question in English with detailed information. Provide a comprehensive answer in 3-4 sentences.

Question: {question}

Answer:"""
                result_lang = "English"
                
            # Generate the answer
            response = ollama_client.generate(
                model="gemma3:4b",
                prompt=prompt,
                options=options
            )
            
            # Extract the answer
            answer = response['response'].strip()
            answer = re.sub(r'^(Answer:|उत्तर:)', '', answer).strip()
            
            return answer, result_lang
            
        # For passage-based questions
        else:
            # Detect language of passage if it exists
            passage_lang = detect(passage) if passage else "en"
            
            # Format the prompt based on detected languages
            if passage_lang == 'hi' and question_lang == 'hi':
                # Both Hindi - process directly
                prompt = f"""मैं आपको एक अनुच्छेद और एक प्रश्न दूंगा। अनुच्छेद से प्रश्न का उत्तर खोजें और केवल उत्तर ही दें।
                
अनुच्छेद: {passage}

प्रश्न: {question}

उत्तर:"""
                result_lang = "Hindi"
                
            elif passage_lang == 'hi' and question_lang != 'hi':
                # Hindi passage, English question - translate question to Hindi first
                translate_prompt = f"""Translate the following English text to Hindi. Provide only the Hindi translation:

English Text: {question}

Hindi Translation:"""
                
                response = ollama_client.generate(
                    model="gemma3:4b",
                    prompt=translate_prompt,
                    options=options
                )
                
                hindi_question = response['response'].strip()
                hindi_question = re.sub(r'^(Hindi Translation:|Translation:)', '', hindi_question).strip()
                
                prompt = f"""मैं आपको एक अनुच्छेद और एक प्रश्न दूंगा। अनुच्छेद से प्रश्न का उत्तर खोजें और केवल उत्तर ही दें।
                
अनुच्छेद: {passage}

प्रश्न: {hindi_question}

उत्तर:"""
                result_lang = "Hindi"
                
            elif passage_lang != 'hi' and question_lang == 'hi':
                # English passage, Hindi question - translate question to English first
                translate_prompt = f"""Translate the following Hindi text to English. Provide only the English translation:

Hindi Text: {question}

English Translation:"""
                
                response = ollama_client.generate(
                    model="gemma3:4b",
                    prompt=translate_prompt,
                    options=options
                )
                
                english_question = response['response'].strip()
                english_question = re.sub(r'^(English Translation:|Translation:)', '', english_question).strip()
                
                prompt = f"""I will give you a passage and a question. Find the answer to the question from the passage and provide only the answer.
                
Passage: {passage}

Question: {english_question}

Answer:"""
                result_lang = "English"
                
            else:
                # Both English - process directly
                prompt = f"""I will give you a passage and a question. Find the answer to the question from the passage and provide only the answer.
                
Passage: {passage}

Question: {question}

Answer:"""
                result_lang = "English"
            
            # Generate the answer
            response = ollama_client.generate(
                model="gemma3:4b",
                prompt=prompt,
                options=options
            )
            
            # Extract the answer
            answer = response['response'].strip()
            answer = re.sub(r'^(Answer:|उत्तर:)', '', answer).strip()
            
            return answer, result_lang
        
    except Exception as e:
        print(f"Error during question answering: {e}")
        return f"Error: {str(e)}", "unknown"

def main():
    """
    Main function for translation
    """
    print("Automatic Language Translation Tool")
    print("=" * 40)
    print("Instructions:")
    print("- Enter your text (English or Hindi) when prompted")
    print("- Language will be automatically detected")
    print("- Type 'quit' or 'exit' to stop the program")
    print("-" * 40)
    
    while True:
        try:
            # Get input from user
            print("\nEnter text to translate (English or Hindi):")
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
            print(f"Detected language: {'Hindi' if source_lang == 'hi' else 'English'}")
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

def translate_multiline():
    """
    Alternative function for multi-line input
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

def question_answering_mode():
    """
    Question answering mode - extract answers from passages
    """
    print("Question Answering Tool (Supports Hindi and English)")
    print("=" * 60)
    print("Instructions:")
    print("- First enter a passage (can be in Hindi or English)")
    print("- Then ask questions about the passage (can be in Hindi or English)")
    print("- Type 'new passage' to enter a new passage")
    print("- Type 'general' to ask general questions not related to the passage")
    print("- Type 'quit' or 'exit' to stop the program")
    print("-" * 60)
    
    current_passage = ""
    mode = "passage"  # Can be "passage" or "general"
    
    while True:
        try:
            # If in passage mode and no passage is set, get one first
            if mode == "passage" and not current_passage:
                print("\nEnter a passage (Hindi or English, press Enter twice when done):")
                lines = []
                
                while True:
                    try:
                        line = input()
                        if line == "":  # Empty line means end of input
                            break
                        lines.append(line)
                    except UnicodeDecodeError as e:
                        print(f"Warning: Encountered encoding issue with input. Using replacement character.")
                        # Try to recover with a replacement strategy
                        lines.append("[Input with encoding issue]")
                
                current_passage = "\n".join(lines).strip()
                
                if not current_passage:
                    print("Please enter a valid passage.")
                    continue
                
                try:
                    # Detect language of passage
                    passage_lang = detect(current_passage)
                    print(f"\nPassage language detected: {'Hindi' if passage_lang == 'hi' else 'English'}")
                    print("You can now ask questions about this passage.")
                except Exception as e:
                    print(f"Warning: Could not detect language. Will process as English. Error: {e}")
                    print("You can now ask questions about this passage.")
                continue
            
            # Get questions
            if mode == "passage":
                print("\nEnter your question about the passage (or 'new passage' for a new passage, 'general' to switch to general questions, 'quit' to exit):")
            else:  # mode == "general"
                print("\nEnter your general question (or 'passage' to switch to passage mode, 'quit' to exit):")
                
            try:
                question = input("> ").strip()
            except UnicodeDecodeError:
                print("Warning: Encountered encoding issue with your question. Please try again.")
                question = "[Input with encoding issue]"
            
            # Check commands
            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
                
            if question.lower() == 'new passage' and mode == "passage":
                current_passage = ""
                print("Please enter a new passage.")
                continue
                
            if question.lower() == 'general' and mode == "passage":
                mode = "general"
                print("Switched to general question answering mode. You can ask any question not related to a passage.")
                continue
                
            if question.lower() == 'passage' and mode == "general":
                mode = "passage"
                if not current_passage:
                    print("Please enter a new passage.")
                else:
                    print("Switched back to passage question answering mode.")
                continue
            
            if not question or question == "[Input with encoding issue]":
                print("Please enter a valid question.")
                continue
            
            # Show processing message
            print("\nProcessing question... Please wait...")
            
            # Start timing
            start_time = time.time()
            
            try:
                # Get answer based on mode
                if mode == "passage":
                    answer, result_lang = answer_question(current_passage, question, is_general_question=False)
                else:  # mode == "general"
                    answer, result_lang = answer_question("", question, is_general_question=True)
                
                # Calculate elapsed time
                elapsed_time = time.time() - start_time
                
                # Display results
                print("\n" + "=" * 60)
                print("ANSWER")
                print("=" * 60)
                question_lang = detect(question)
                print(f"Question ({('Hindi' if question_lang == 'hi' else 'English')}): {question}")
                print(f"Answer ({result_lang}): {answer}")
                print(f"Time taken: {elapsed_time:.2f} seconds")
                print("=" * 60)
            except Exception as e:
                print(f"Error processing question: {e}")
                print("Please try again with a different question or passage.")
            
        except KeyboardInterrupt:
            print("\n\nProgram interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please try again.")

def general_knowledge_mode():
    """
    General knowledge question answering mode
    """
    print("General Knowledge Question Answering (Supports Hindi and English)")
    print("=" * 60)
    print("Instructions:")
    print("- Ask any general knowledge question in Hindi or English")
    print("- The system will automatically detect the language and answer in the same language")
    print("- Type 'quit' or 'exit' to stop the program")
    print("-" * 60)
    
    while True:
        try:
            print("\nEnter your general knowledge question:")
            try:
                question = input("> ").strip()
            except UnicodeDecodeError:
                print("Warning: Encountered encoding issue with your question. Please try again.")
                question = "[Input with encoding issue]"
            
            # Check commands
            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not question or question == "[Input with encoding issue]":
                print("Please enter a valid question.")
                continue
            
            # Show processing message
            print("\nProcessing question... Please wait...")
            
            # Start timing
            start_time = time.time()
            
            try:
                # Get answer for general question
                answer, result_lang = answer_question("", question, is_general_question=True)
                
                # Calculate elapsed time
                elapsed_time = time.time() - start_time
                
                # Display results
                print("\n" + "=" * 60)
                print("ANSWER")
                print("=" * 60)
                question_lang = detect(question)
                print(f"Question ({('Hindi' if question_lang == 'hi' else 'English')}): {question}")
                print(f"Answer ({result_lang}): {answer}")
                print(f"Time taken: {elapsed_time:.2f} seconds")
                print("=" * 60)
            except Exception as e:
                print(f"Error processing question: {e}")
                print("Please try again with a different question.")
            
        except KeyboardInterrupt:
            print("\n\nProgram interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please try again.")

def translate_from_file():
    """
    Function to translate text from a file
    """
    print("File-based Translation Tool")
    print("=" * 50)
    print("Instructions:")
    print("- Enter the path to a text file containing content to translate")
    print("- Language will be automatically detected")
    print("- Each sentence will be translated individually")
    print("- Debug information will be shown for each sentence")
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
            
            # Sentence-by-sentence translation with improved sentence detection
            print("\nSplitting text into paragraphs and sentences for better translation... Please wait...")
            
            # First split by paragraphs to maintain document structure
            paragraphs = input_text.split('\n\n')
            
            # If no paragraphs found (no double newlines), try splitting by single newlines
            if len(paragraphs) <= 1:
                paragraphs = input_text.split('\n')
            
            print(f"[DEBUG] Found {len(paragraphs)} paragraphs")
            
            # Now split each paragraph into sentences for more manageable translation
            all_sentences = []
            paragraph_boundaries = []  # To track where paragraphs begin and end
            
            # Try to use NLTK for better sentence splitting
            try:
                import nltk
                # Download punkt tokenizer if not already downloaded
                try:
                    nltk.data.find('tokenizers/punkt')
                except LookupError:
                    print("Downloading NLTK punkt tokenizer for better sentence detection...")
                    nltk.download('punkt', quiet=True)
                
                # Detect language for appropriate sentence tokenization
                sample_text = input_text[:1000] if len(input_text) > 1000 else input_text
                detected_lang = detect(sample_text)
                
                # Process each paragraph
                current_index = 0
                for para in paragraphs:
                    if not para.strip():
                        continue
                        
                    # Split paragraph into sentences
                    from nltk.tokenize import sent_tokenize
                    para_sentences = sent_tokenize(para, language='english' if detected_lang != 'hi' else 'hindi')
                    
                    # Too long sentences should be further split
                    processed_sentences = []
                    for sent in para_sentences:
                        if len(sent) > 300:  # If sentence is too long
                            # Try to split by conjunctions or other logical breaks
                            chunks = re.split(r'([,;] )', sent)
                            # Recombine chunks to maintain punctuation
                            current_chunk = ""
                            for i in range(0, len(chunks)-1, 2):
                                if i+1 < len(chunks):
                                    current_chunk += chunks[i] + chunks[i+1]
                                    if len(current_chunk) > 150:  # Reasonable chunk size
                                        processed_sentences.append(current_chunk)
                                        current_chunk = ""
                            # Add any remaining text
                            if current_chunk or (len(chunks) % 2 == 1 and chunks[-1]):
                                remaining = current_chunk + (chunks[-1] if len(chunks) % 2 == 1 else "")
                                if remaining.strip():
                                    processed_sentences.append(remaining)
                        else:
                            processed_sentences.append(sent)
                    
                    # Record the paragraph boundary
                    paragraph_boundaries.append((current_index, current_index + len(processed_sentences)))
                    current_index += len(processed_sentences)
                    
                    # Add the processed sentences to our collection
                    all_sentences.extend(processed_sentences)
                
                print(f"[DEBUG] Using NLTK, split into {len(all_sentences)} sentences across {len(paragraph_boundaries)} paragraphs")
                
            except ImportError:
                print("[DEBUG] NLTK not available, using custom paragraph and sentence detection")
                
                # Simple sentence splitter
                import re
                
                current_index = 0
                for para in paragraphs:
                    if not para.strip():
                        continue
                    
                    # Check language of paragraph
                    is_hindi = False
                    try:
                        is_hindi = detect(para) == 'hi'
                    except:
                        pass
                    
                    # Choose appropriate sentence splitting pattern
                    if is_hindi:
                        # Split on Hindi punctuation
                        parts = re.split(r'([।!?])', para)
                    else:
                        # Split on English punctuation
                        parts = re.split(r'([.!?])', para)
                    
                    # Recombine to maintain punctuation
                    para_sentences = []
                    current = ""
                    for i in range(0, len(parts)-1, 2):
                        if i+1 < len(parts):
                            current = parts[i] + parts[i+1]
                            # Check if we need to split long sentences further
                            if len(current) > 300:
                                # Split on commas, semicolons for long sentences
                                subparts = re.split(r'([,;] )', current)
                                subsentences = []
                                subtext = ""
                                for j in range(0, len(subparts)-1, 2):
                                    if j+1 < len(subparts):
                                        if len(subtext + subparts[j] + subparts[j+1]) > 150:
                                            if subtext:
                                                subsentences.append(subtext)
                                            subtext = subparts[j] + subparts[j+1]
                                        else:
                                            subtext += subparts[j] + subparts[j+1]
                                if subtext:
                                    subsentences.append(subtext)
                                if len(subparts) % 2 == 1 and subparts[-1].strip():
                                    if len(subsentences) > 0 and len(subsentences[-1] + subparts[-1]) < 200:
                                        subsentences[-1] += subparts[-1]
                                    else:
                                        subsentences.append(subparts[-1])
                                para_sentences.extend(subsentences)
                            else:
                                para_sentences.append(current)
                    
                    # Handle any trailing text
                    if len(parts) % 2 == 1 and parts[-1].strip():
                        para_sentences.append(parts[-1])
                    
                    # Record paragraph boundary
                    paragraph_boundaries.append((current_index, current_index + len(para_sentences)))
                    current_index += len(para_sentences)
                    
                    # Add processed sentences
                    all_sentences.extend(para_sentences)
            
            # Use the processed sentences for translation
            sentences = [s.strip() for s in all_sentences if s.strip()]
            
            print(f"[DEBUG] Final processing: {len(sentences)} sentences in {len(paragraph_boundaries)} paragraphs")
            
            # Detect language of the first non-empty sentence
            first_sent = next((s for s in sentences if s.strip()), "")
            if first_sent:
                source_lang = detect(first_sent)
                target_lang = "English" if source_lang == "hi" else "Hindi"
                print(f"[DEBUG] Detected language: {source_lang}, will translate to {target_lang}")
            else:
                source_lang = "unknown"
                target_lang = "unknown"
                print("[DEBUG] Could not detect language, source unknown")
            
            # Prepare output file with sentence-by-sentence format
            output_file = f"{file_base}_sentences_{target_lang.lower()}{file_ext}"
            output_path = os.path.join(os.path.dirname(file_path), output_file)
            
            # Also create a clean output file with just translations
            clean_output_file = f"{file_base}_clean_translation{file_ext}"
            clean_output_path = os.path.join(os.path.dirname(file_path), clean_output_file)
            
            translated_sentences = []
            clean_translations = []
            total_sentences = len(sentences)
            
            # Create a summary file for timing information
            timing_file = f"{file_base}_sentence_translation_timing.txt"
            timing_path = os.path.join(os.path.dirname(file_path), timing_file)
            
            with open(timing_path, 'w', encoding='utf-8') as timing_f:
                timing_f.write(f"Sentence-by-Sentence Translation Timing Information\n")
                timing_f.write(f"{'='*60}\n")
                timing_f.write(f"Source file: {file_path}\n")
                timing_f.write(f"Number of sentences: {total_sentences}\n\n")
                timing_f.write(f"{'Sentence #':<10} {'Size (chars)':<15} {'Time (seconds)':<15}\n")
                timing_f.write(f"{'-'*60}\n")
                
                for i, sentence in enumerate(sentences, 1):
                    if not sentence.strip():
                        # Skip empty sentences but maintain them in output
                        translated_sentences.append("")
                        clean_translations.append("")
                        print(f"[DEBUG] Skipping empty sentence #{i}")
                        continue
                        
                    # Print a clear separator
                    print("\n" + "=" * 80)
                    print(f"SENTENCE #{i}/{total_sentences} ({len(sentence)} characters)")
                    print("-" * 80)
                    # Print the full sentence
                    print(f"ORIGINAL ({('Hindi' if source_lang == 'hi' else 'English')}):")
                    print(f"{sentence}")
                    
                    # Start timing for this sentence
                    sent_start_time = time.time()
                    
                    # Debug information before translation
                    print(f"\n[DEBUG] Translating sentence #{i} from {source_lang} to {target_lang}")
                    
                    # Translate the sentence
                    translation, _, _ = translate_text(sentence)
                    
                    # Calculate and record elapsed time
                    sent_elapsed_time = time.time() - sent_start_time
                    timing_f.write(f"{i:<10} {len(sentence):<15} {sent_elapsed_time:.2f}\n")
                    
                    # Print the translation immediately after
                    print(f"\nTRANSLATION ({target_lang}):")
                    print(f"{translation}")
                    print(f"\nTime: {sent_elapsed_time:.2f} seconds")
                    print("=" * 80)
                    
                    # Add the original sentence and its translation
                    sent_entry = f"Sentence {i}:\nOriginal ({('Hindi' if source_lang == 'hi' else 'English')}):\n{sentence}\n\nTranslation ({target_lang}):\n{translation}\n"
                    translated_sentences.append(sent_entry)
                    clean_translations.append(translation)
                
                # Record total time
                total_elapsed_time = time.time() - total_start_time
                timing_f.write(f"\nTotal translation time: {total_elapsed_time:.2f} seconds\n")
            
            # Save all translated sentences to the output file
            try:
                with open(output_path, 'w', encoding='utf-8') as file:
                    file.write("\n" + "="*60 + "\n")
                    file.write(f"SENTENCE-BY-SENTENCE TRANSLATION\n")
                    file.write("="*60 + "\n\n")
                    
                    # Create the output content differently to avoid the join issue
                    output_content = ""
                    for item in translated_sentences:
                        # Make sure each item is a string
                        item_str = str(item)
                        output_content += item_str + "\n" + "-"*50 + "\n\n"
                    
                    file.write(output_content)
                print(f"Translation successfully saved to: {output_path}")
            except Exception as e:
                print(f"Error saving translation: {e}")
                print(f"Debug info - translated_sentences type: {type(translated_sentences)}")
                for i, item in enumerate(translated_sentences[:3]):
                    print(f"Item {i} type: {type(item)}, value: {repr(item)}")
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
                print(f"Debug info - clean_translations type: {type(clean_translations)}")
                for i, item in enumerate(clean_translations[:3]):
                    print(f"Item {i} type: {type(item)}, value: {repr(item)}")
            
            # Display results
            print("\n" + "=" * 60)
            print("SENTENCE-BY-SENTENCE TRANSLATION COMPLETE")
            print("=" * 60)
            print(f"Detected language: {'Hindi' if source_lang == 'hi' else 'English'}")
            print(f"Source file: {file_path}")
            print(f"Detailed translation saved to: {output_path}")
            print(f"Clean translation saved to: {clean_output_path}")
            print(f"Timing information saved to: {timing_path}")
            print(f"Total sentences: {total_sentences}")
            print(f"Total time taken: {total_elapsed_time:.2f} seconds")
            print("=" * 60)
            
            # Ask if user wants to see a preview
            print("\nWould you like to see a preview of the translation? (y/n)")
            preview = input("> ").strip().lower()
            if preview in ['y', 'yes']:
                print("\nPreview of sentence-by-sentence translation (first 3 sentences):")
                print("-" * 50)
                preview_text = "\n\n".join(translated_sentences[:3])
                print(preview_text)
                print("-" * 50)
                
                print("\nPreview of clean translation:")
                print("-" * 50)
                preview_clean = " ".join(clean_translations[:5])
                print(f"{preview_clean}{'...' if len(clean_translations) > 5 else ''}")
                print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n\nProgram interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please try again.")

if __name__ == "__main__":
    # Set default stdin/stdout encoding to UTF-8
    import sys
    import io
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("Choose mode:")
    print("1. Translation (single line)")
    print("2. Translation (multi-line)")
    print("3. Question Answering")
    print("4. General Knowledge")
    print("5. Translation from File")
    
    while True:
        choice = input("\nEnter your choice (1, 2, 3, 4, or 5): ").strip()
        
        if choice == "1":
            main()
            break
        elif choice == "2":
            translate_multiline()
            break
        elif choice == "3":
            question_answering_mode()
            break
        elif choice == "4":
            general_knowledge_mode()
            break
        elif choice == "5":
            translate_from_file()
            break
        else:
            print("Please enter a valid choice (1-5)")