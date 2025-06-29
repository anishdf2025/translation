import os
import time


class FileHandler:
    """Handles file operations for translation process"""
    
    def __init__(self):
        pass
    
    def read_file(self, file_path):
        """Read content from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return content, None
        except Exception as e:
            return None, str(e)
    
    def file_exists(self, file_path):
        """Check if file exists"""
        return os.path.isfile(file_path)
    
    def get_file_size_kb(self, file_path):
        """Get file size in KB"""
        return os.path.getsize(file_path) / 1024
    
    def create_output_paths(self, file_path, target_lang):
        """Create output file paths"""
        file_name = os.path.basename(file_path)
        file_base, file_ext = os.path.splitext(file_name)
        
        output_file = f"{file_base}_chunks_{target_lang.lower()}{file_ext}"
        output_path = os.path.join(os.path.dirname(file_path), output_file)
        
        clean_output_file = f"{file_base}_clean_translation{file_ext}"
        clean_output_path = os.path.join(os.path.dirname(file_path), clean_output_file)
        
        timing_file = f"{file_base}_chunk_translation_timing.txt"
        timing_path = os.path.join(os.path.dirname(file_path), timing_file)
        
        return output_path, clean_output_path, timing_path
    
    def save_translations(self, output_path, translated_chunks):
        """Save detailed translations to file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write("\n" + "="*60 + "\n")
                file.write(f"CHUNK-BY-CHUNK TRANSLATION\n")
                file.write("="*60 + "\n\n")
                
                output_content = ""
                for item in translated_chunks:
                    item_str = str(item)
                    output_content += item_str + "\n" + "-"*50 + "\n\n"
                
                file.write(output_content)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def save_clean_translations(self, clean_output_path, clean_translations):
        """Save clean translations to file"""
        try:
            with open(clean_output_path, 'w', encoding='utf-8') as file:
                clean_output = ""
                for item in clean_translations:
                    item_str = str(item)
                    clean_output += item_str + " "
                
                file.write(clean_output)
            return True, None
        except Exception as e:
            return False, str(e)
    
    def create_timing_file(self, timing_path, file_path, total_chunks):
        """Create and return timing file handle"""
        timing_f = open(timing_path, 'w', encoding='utf-8')
        timing_f.write(f"Chunk-by-Chunk Translation Timing Information\n")
        timing_f.write(f"{'='*60}\n")
        timing_f.write(f"Source file: {file_path}\n")
        timing_f.write(f"Number of chunks: {total_chunks}\n\n")
        timing_f.write(f"{'Chunk #':<10} {'Time (seconds)':<15}\n")
        timing_f.write(f"{'-'*25}\n")
        return timing_f
    
    def write_timing_entry(self, timing_f, chunk_num, elapsed_time):
        """Write timing entry to file"""
        timing_f.write(f"{chunk_num:<10} {elapsed_time:.2f}\n")
    
    def write_total_time(self, timing_f, total_time):
        """Write total time to timing file"""
        timing_f.write(f"\nTotal translation time: {total_time:.2f} seconds\n")
