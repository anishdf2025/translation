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
            model="gemma3n:e2b",
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

if __name__ == "__main__":
    # Set default stdin/stdout encoding to UTF-8
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("Starting Question Answering Service")
    question_answering_mode()