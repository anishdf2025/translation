import os
import time
from html_parser import HTMLParser
from ocr_handler import OCRHandler


class FileHandler:
    """Handles file operations for translation process"""
    
    def __init__(self):
        self.html_parser = HTMLParser()
        self.ocr_handler = OCRHandler()
    
    def read_file(self, file_path, keep_temp_html=True):
        """Read content from a file - automatically process HTML and OCR files"""
        try:
            # Check if it's an HTML file
            if self._is_html_file(file_path):
                # Process HTML and return the path to the generated .md file
                md_file_path = self._process_html_to_md_file(file_path)
                if md_file_path:
                    # Read the generated .md file
                    with open(md_file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                    return content, None
                else:
                    return None, "Failed to process HTML file"
            # Check if it's an OCR file (PDF, PNG, JPG, JPEG)
            elif self._is_ocr_file(file_path):
                # Process OCR and return the path to the generated .md file
                md_file_path = self._process_ocr_to_md_file(file_path)
                if md_file_path:
                    # Read the generated .md file
                    with open(md_file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                    return content, None
                else:
                    return None, "Failed to process OCR file"
            else:
                # For non-HTML/non-OCR files, read normally
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                return content, None
        except Exception as e:
            return None, str(e)
    
    def _is_ocr_file(self, file_path):
        """Check if the file requires OCR processing"""
        return self.ocr_handler.is_ocr_file(file_path)
    
    def _process_ocr_to_md_file(self, file_path):
        """Process OCR file and create a permanent .md file"""
        return self.ocr_handler.process_ocr_to_md_file(file_path)
    
    def _is_html_file(self, file_path):
        """Check if the file is an HTML file"""
        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in ['.html', '.htm']
    
    def _process_html_to_md_file(self, file_path):
        """Process HTML file and create a permanent .md file"""
        try:
            # Create markdown file path
            file_name = os.path.basename(file_path)
            file_base, _ = os.path.splitext(file_name)
            md_file = f"{file_base}.md"
            md_file_path = os.path.join(os.path.dirname(file_path), md_file)
            
            # Extract HTML content to markdown
            success, error = self.html_parser.extract_all_visible_text(file_path, md_file_path)
            
            if success:
                print(f"✅ HTML file processed: {file_path}")
                print(f"📄 Generated markdown file: {md_file_path}")
                print(f"📄 Using generated markdown file for translation")
                return md_file_path
            else:
                print(f"❌ Error processing HTML: {error}")
                return None
                
        except Exception as e:
            print(f"❌ Error processing HTML file: {str(e)}")
            return None
    
    def _process_html_file(self, file_path, keep_temp=False):
        """Process HTML file and return extracted text content"""
        try:
            # Create temporary markdown file path
            file_name = os.path.basename(file_path)
            file_base, _ = os.path.splitext(file_name)
            temp_md_file = f"{file_base}_extracted.md"
            temp_md_path = os.path.join(os.path.dirname(file_path), temp_md_file)
            
            # Extract HTML content to markdown
            success, error = self.html_parser.extract_all_visible_text(file_path, temp_md_path)
            
            if success:
                # Read the extracted content
                with open(temp_md_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                print(f"✅ HTML file processed: {file_path}")
                print(f"📄 Extracted content saved to: {temp_md_path}")
                print(f"📄 Extracted content will be used for translation")
                
                # Clean up temporary file unless keep_temp is True
                if not keep_temp:
                    try:
                        os.remove(temp_md_path)
                        print(f"🧹 Cleaned up temporary file: {temp_md_file}")
                    except Exception as cleanup_error:
                        print(f"⚠️ Warning: Could not clean up temporary file: {str(cleanup_error)}")
                
                return content, None
            else:
                return None, error
                
        except Exception as e:
            return None, str(e)
    
    def file_exists(self, file_path):
        """Check if file exists"""
        return os.path.isfile(file_path)
    
    def get_file_size_kb(self, file_path):
        """Get file size in KB"""
        return os.path.getsize(file_path) / 1024
    
    def create_output_paths(self, file_path, target_lang):
        """Create output file paths - handle HTML and OCR files by using their .md counterparts"""
        # If it's an HTML file, use the corresponding .md file for output naming
        if self._is_html_file(file_path):
            file_name = os.path.basename(file_path)
            file_base, _ = os.path.splitext(file_name)
            # Use .md extension for HTML-derived files
            actual_file_base = file_base
            actual_file_ext = ".md"
        # If it's an OCR file, use the corresponding .md file for output naming
        elif self._is_ocr_file(file_path):
            file_name = os.path.basename(file_path)
            file_base, _ = os.path.splitext(file_name)
            # Use .md extension for OCR-derived files
            actual_file_base = f"{file_base}_ocr"
            actual_file_ext = ".md"
        else:
            file_name = os.path.basename(file_path)
            actual_file_base, actual_file_ext = os.path.splitext(file_name)
        
        output_file = f"{actual_file_base}_chunks_{target_lang.lower()}{actual_file_ext}"
        output_path = os.path.join(os.path.dirname(file_path), output_file)
        
        clean_output_file = f"{actual_file_base}_clean_translation{actual_file_ext}"
        clean_output_path = os.path.join(os.path.dirname(file_path), clean_output_file)
        
        timing_file = f"{actual_file_base}_chunk_translation_timing.txt"
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
        """Save clean translations to file with one line space between chunks"""
        try:
            with open(clean_output_path, 'w', encoding='utf-8') as file:
                clean_output = ""
                for i, item in enumerate(clean_translations):
                    item_str = str(item).strip()
                    clean_output += item_str
                    
                    # Add one line space between chunks (but not after the last chunk)
                    if i < len(clean_translations) - 1:
                        clean_output += "\n\n"
                
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
    
    def cleanup_temp_files(self, file_path):
        """Clean up temporary files created during HTML processing"""
        if self._is_html_file(file_path):
            try:
                file_name = os.path.basename(file_path)
                file_base, _ = os.path.splitext(file_name)
                temp_md_file = f"{file_base}_extracted.md"
                temp_md_path = os.path.join(os.path.dirname(file_path), temp_md_file)
                
                if os.path.exists(temp_md_path):
                    os.remove(temp_md_path)
                    print(f"🧹 Cleaned up temporary file: {temp_md_file}")
            except Exception as e:
                print(f"⚠️ Warning: Could not clean up temporary file: {str(e)}")
