import sys
import io
import time
from file_handler import FileHandler
from text_splitter import TextSplitter
from language_detector import LanguageDetector
from translation_prompts import TranslationPrompts
from display_utils import DisplayUtils


class TranslationService:
    """Main translation service that coordinates all modules"""
    
    def __init__(self):
        self.file_handler = FileHandler()
        self.text_splitter = TextSplitter()
        self.language_detector = LanguageDetector()
        self.translation_prompts = TranslationPrompts()
        self.display = DisplayUtils()
    
    def translate_from_file(self):
        """Main function to translate text from a file with chunking"""
        self.display.print_welcome()
        
        while True:
            try:
                # Get file path from user
                self.display.print_file_prompt()
                file_path = input("> ").strip()
                
                # Check if user wants to quit
                if file_path.lower() in ['quit', 'exit', 'q']:
                    self.display.print_goodbye()
                    break
                
                # Check if file exists
                if not self.file_handler.file_exists(file_path):
                    self.display.print_error(f"File '{file_path}' not found. Please check the path and try again.")
                    continue
                
                # Read the file content
                input_text, error = self.file_handler.read_file(file_path)
                if error:
                    self.display.print_error(f"Error reading file: {error}")
                    continue
                
                if not input_text:
                    self.display.print_error("The file is empty. Please choose a file with content.")
                    continue
                
                # Show file information
                file_size_kb = self.file_handler.get_file_size_kb(file_path)
                self.display.print_file_info(file_size_kb)
                
                # Start timing the whole process
                total_start_time = time.time()
                
                # Detect language
                source_lang, target_lang, lang_error = self.language_detector.detect_language(input_text)
                self.display.print_language_detection(source_lang, target_lang, lang_error)
                
                # Split text into chunks
                chunks = self.text_splitter.split_text_into_chunks(input_text, source_lang)
                
                # Print text analysis
                text_length = len(input_text)
                num_chunks = len(chunks)
                self.display.print_text_analysis(text_length, num_chunks)
                
                self.display.print_chunks_summary(chunks)
                
                # Prepare output files
                output_path, clean_output_path, timing_path = self.file_handler.create_output_paths(file_path, target_lang)
                
                # Process translations
                translated_chunks, clean_translations = self._process_chunks(
                    chunks, source_lang, target_lang, timing_path, file_path, total_start_time
                )
                
                # Record total time
                total_elapsed_time = time.time() - total_start_time
                
                # Save translations
                success, error = self.file_handler.save_translations(output_path, translated_chunks)
                if not success:
                    self.display.print_error(f"Error saving translation: {error}")
                    continue
                else:
                    print(f"Translation successfully saved to: {output_path}")
                
                # Save clean translations
                success, error = self.file_handler.save_clean_translations(clean_output_path, clean_translations)
                if not success:
                    self.display.print_error(f"Error saving clean translation: {error}")
                else:
                    print(f"Clean translation successfully saved to: {clean_output_path}")
                
                # Display completion summary
                self.display.print_completion_summary(
                    source_lang, file_path, output_path, clean_output_path, 
                    timing_path, len(chunks), total_elapsed_time
                )
                
                # Ask for preview
                self.display.print_preview_prompt()
                preview = input("> ").strip().lower()
                if preview in ['y', 'yes']:
                    self.display.print_translation_previews(translated_chunks, clean_translations)
                
            except KeyboardInterrupt:
                self.display.print_interrupt()
                break
            except Exception as e:
                self.display.print_generic_error(e)
    
    def _process_chunks(self, chunks, source_lang, target_lang, timing_path, file_path, total_start_time):
        """Process all chunks for translation"""
        translated_chunks = []
        clean_translations = []
        total_chunks = len(chunks)
        
        # Create timing file
        timing_f = self.file_handler.create_timing_file(timing_path, file_path, total_chunks)
        
        try:
            for i, chunk in enumerate(chunks, 1):
                # Display chunk information
                self.display.print_chunk_separator(i, total_chunks)
                self.display.print_chunk_preview(chunk, source_lang)
                
                # Start timing for this chunk
                chunk_start_time = time.time()
                
                # Debug information before translation
                self.display.print_translation_debug(i, source_lang, target_lang)
                
                # Translate the chunk
                translation, _, error = self.translation_prompts.translate_text(chunk, source_lang)
                if error:
                    self.display.print_error(f"Translation error for chunk {i}: {error}")
                
                # Calculate elapsed time
                chunk_elapsed_time = time.time() - chunk_start_time
                
                # Record timing
                self.file_handler.write_timing_entry(timing_f, i, chunk_elapsed_time)
                
                # Display translation preview
                self.display.print_translation_preview(translation, target_lang, chunk_elapsed_time)
                
                # Store results
                lang_name = 'Hindi' if source_lang == 'hi' else 'English'
                chunk_entry = f"Chunk {i}:\nOriginal ({lang_name}):\n{chunk}\n\nTranslation ({target_lang}):\n{translation}\n"
                translated_chunks.append(chunk_entry)
                clean_translations.append(translation)
            
            # Record total time
            total_elapsed_time = time.time() - total_start_time
            self.file_handler.write_total_time(timing_f, total_elapsed_time)
            
        finally:
            timing_f.close()
        
        return translated_chunks, clean_translations


def main():
    """Main entry point"""
    # Set default stdin/stdout encoding to UTF-8
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("Starting File Translation Service")
    
    # Create and run translation service
    service = TranslationService()
    service.translate_from_file()


if __name__ == "__main__":
    main()
