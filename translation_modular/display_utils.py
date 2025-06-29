class DisplayUtils:
    """Handles all display and printing operations"""
    
    def __init__(self):
        pass
    
    def print_welcome(self):
        """Print welcome message and instructions"""
        print("File-based Translation Tool")
        print("=" * 50)
        print("Instructions:")
        print("- Enter the path to a text file containing content to translate")
        print("- Language will be automatically detected")
        print("- Text will be split into chunks of approximately 2048 tokens")
        print("- Each chunk will be translated individually")
        print("-" * 50)
    
    def print_file_info(self, file_size_kb):
        """Print file information"""
        print(f"\nFile size: {file_size_kb:.2f} KB")
    
    def print_language_detection(self, source_lang, target_lang, error=None):
        """Print language detection results"""
        if error:
            print(f"Language detection error: {error}. Defaulting to English")
        else:
            # Convert language code to full name
            source_name = 'Hindi' if source_lang == 'hi' else 'English'
            print(f"Detected language: {source_name}")
    
    def print_text_analysis(self, text_length, num_chunks):
        """Print text analysis information"""
        print("\nSplitting text into chunks for translation... Please wait...")
        print(f"Total text length: {text_length} characters")  
        print(f"Will create {num_chunks} chunks")
    
    def print_chunk_info(self, chunk_num, chunk_size, start_pos, end_pos):
        """Print chunk creation information"""
        # Remove this debug print - no longer needed
        pass
    
    def print_chunks_summary(self, chunks):
        """Print summary of all chunks"""
        print(f"Split text into {len(chunks)} chunks")
        
        # Remove detailed chunk preview - no longer needed
    
    def print_chunk_separator(self, chunk_num, total_chunks):
        """Print chunk separator and info"""
        print("\n" + "=" * 80)
        print(f"CHUNK #{chunk_num}/{total_chunks}")
        print("-" * 80)
    
    def print_chunk_preview(self, chunk, source_lang):
        """Print preview of original chunk"""
        chunk_preview = (chunk[:100] + "..." + chunk[-100:]) if len(chunk) > 200 else chunk
        lang_name = 'Hindi' if source_lang == 'hi' else 'English'
        print(f"ORIGINAL ({lang_name}) Preview:")
        print(f"{chunk_preview}")
    
    def print_translation_debug(self, chunk_num, source_lang, target_lang):
        """Print translation debug information"""
        print(f"Translating chunk #{chunk_num} from {source_lang} to {target_lang}")
    
    def print_translation_preview(self, translation, target_lang, elapsed_time):
        """Print translation preview and timing"""
        translation_preview = (translation[:100] + "..." + translation[-100:]) if len(translation) > 200 else translation
        print(f"\nTRANSLATION ({target_lang}) Preview:")
        print(f"{translation_preview}")
        print(f"\nTime: {elapsed_time:.2f} seconds")
        print("=" * 80)
    
    def print_completion_summary(self, source_lang, file_path, output_path, clean_output_path, 
                                timing_path, total_chunks, total_time):
        """Print completion summary"""
        print("\n" + "=" * 60)
        print("CHUNK-BY-CHUNK TRANSLATION COMPLETE")
        print("=" * 60)
        print(f"Detected language: {'Hindi' if source_lang == 'hi' else 'English'}")
        print(f"Source file: {file_path}")
        print(f"Detailed translation saved to: {output_path}")
        print(f"Clean translation saved to: {clean_output_path}")
        print(f"Timing information saved to: {timing_path}")
        print(f"Total chunks: {total_chunks}")
        print(f"Total time taken: {total_time:.2f} seconds")
        print("=" * 60)
    
    def print_preview_prompt(self):
        """Print preview prompt"""
        print("\nWould you like to see a preview of the translation? (y/n)")
    
    def print_translation_previews(self, translated_chunks, clean_translations):
        """Print translation previews"""
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
    
    def print_error(self, error_msg):
        """Print error message"""
        print(f"Error: {error_msg}")
    
    def print_file_prompt(self):
        """Print file input prompt"""
        print("\nEnter the path to the text file (or 'quit' to exit):")
    
    def print_goodbye(self):
        """Print goodbye message"""
        print("Goodbye!")
    
    def print_interrupt(self):
        """Print interruption message"""
        print("\n\nProgram interrupted by user. Goodbye!")
    
    def print_generic_error(self, error):
        """Print generic error message"""
        print(f"An error occurred: {error}")
        print("Please try again.")
