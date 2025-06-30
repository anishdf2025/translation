import sys
import io
import time
import re
from ollama import Client
from langdetect import detect

# Load Ollama client
ollama_client = Client()
options = {
    "num_gpu": 1, 
    "num_ctx": 16000, 
    "num_predict": 16000, 
    "temperature": 0.1
}

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
                prompt = f"""निम्नलिखित प्रश्न का उत्तर हिंदी में दें।

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
                model="gemma3n:e2b",
                prompt=prompt,
                options=options
            )
            
            # Extract the answer
            answer = response['response'].strip()
            answer = re.sub(r'^(Answer:|उत्तर:)', '', answer).strip()
            
            return answer, result_lang
        
        # For passage-based questions (not used in this service)
        else:
            # Default to general question mode for this service
            return answer_question(passage, question, is_general_question=True)
        
    except Exception as e:
        print(f"Error during question answering: {e}")
        return f"Error: {str(e)}", "unknown"

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

if __name__ == "__main__":
    # Set default stdin/stdout encoding to UTF-8
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("Starting General Knowledge Service")
    general_knowledge_mode()