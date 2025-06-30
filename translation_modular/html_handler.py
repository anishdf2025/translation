import os
import re
from bs4 import BeautifulSoup
from text_splitter import TextSplitter
from language_detector import LanguageDetector
from translation_service import TranslationService

class OptimizedHTMLHandler:
    """Optimized HTML handler that translates only text content, not HTML structure"""
    
    def __init__(self):
        self.text_splitter = TextSplitter()
        self.language_detector = LanguageDetector()
        self.translation_service = TranslationService()
        
    def extract_text_only(self, html_content):
        """Extract only translatable text content, no HTML tags or structure"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements completely
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Tags that contain translatable content
        translatable_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'div', 
                           'li', 'td', 'th', 'blockquote', 'em', 'strong', 'b', 'i',
                           'label', 'button', 'a']
        
        text_elements = []
        element_id = 0
        
        # Extract text from elements
        for tag_name in translatable_tags:
            elements = soup.find_all(tag_name)
            for element in elements:
                # Get only the direct text content (not from children)
                direct_text = ""
                for content in element.contents:
                    if hasattr(content, 'strip') and content.strip():  # Text node
                        direct_text += content.strip() + " "
                
                direct_text = direct_text.strip()
                if direct_text and len(direct_text) > 2:  # Only meaningful text
                    text_elements.append({
                        'id': element_id,
                        'element': element,
                        'text': direct_text,
                        'tag': tag_name,
                        'type': 'content'
                    })
                    element_id += 1
        
        # Extract alt attributes from images
        img_tags = soup.find_all('img', alt=True)
        for img in img_tags:
            alt_text = img.get('alt', '').strip()
            if alt_text and len(alt_text) > 2:
                text_elements.append({
                    'id': element_id,
                    'element': img,
                    'text': alt_text,
                    'tag': 'img',
                    'type': 'alt',
                    'attribute': 'alt'
                })
                element_id += 1
        
        # Extract title attributes
        title_elements = soup.find_all(attrs={'title': True})
        for elem in title_elements:
            title_text = elem.get('title', '').strip()
            if title_text and len(title_text) > 2:
                text_elements.append({
                    'id': element_id,
                    'element': elem,
                    'text': title_text,
                    'tag': elem.name,
                    'type': 'title',
                    'attribute': 'title'
                })
                element_id += 1
        
        return soup, text_elements
    
    def prepare_text_for_translation(self, text_elements):
        """Prepare only the text content for translation with minimal markers"""
        pure_texts = []
        text_mapping = {}
        
        for elem in text_elements:
            text_id = elem['id']
            clean_text = elem['text'].strip()
            
            # Store mapping
            text_mapping[text_id] = {
                'original': clean_text,
                'element_info': elem
            }
            
            # Add only the clean text to translation list
            pure_texts.append(clean_text)
        
        return pure_texts, text_mapping
    
    def create_translation_batches(self, pure_texts, source_lang):
        """Create efficient batches of pure text for translation"""
        target_tokens = 2048 if source_lang == 'hi' else 1024
        
        batches = []
        current_batch = []
        current_length = 0
        
        for text in pure_texts:
            text_length = len(text.split())
            
            # If adding this text would exceed limit, start new batch
            if current_length + text_length > target_tokens and current_batch:
                batches.append(current_batch)
                current_batch = [text]
                current_length = text_length
            else:
                current_batch.append(text)
                current_length += text_length
        
        # Add the last batch
        if current_batch:
            batches.append(current_batch)
        
        return batches
    
    def translate_batches(self, batches, source_lang, target_lang):
        """Translate batches of pure text"""
        all_translated_texts = []
        
        print(f"Translating {len(batches)} batches from {source_lang} to {target_lang}...")
        
        for i, batch in enumerate(batches, 1):
            print(f"Translating batch {i}/{len(batches)} ({len(batch)} texts)...")
            
            try:
                # Join texts with a clear separator for translation
                batch_text = " ||| ".join(batch)
                
                # Translate the batch
                translated_batch = self.translation_service.translate_text(
                    batch_text, source_lang, target_lang
                )
                
                # Split back into individual translations
                translated_parts = translated_batch.split(" ||| ")
                
                # Ensure we have the same number of parts
                if len(translated_parts) == len(batch):
                    all_translated_texts.extend(translated_parts)
                else:
                    # Fallback: translate individually if splitting failed
                    print(f"Batch splitting failed for batch {i}, translating individually...")
                    for text in batch:
                        try:
                            individual_translation = self.translation_service.translate_text(
                                text, source_lang, target_lang
                            )
                            all_translated_texts.append(individual_translation)
                        except Exception as e:
                            print(f"Error translating individual text: {e}")
                            all_translated_texts.append(text)  # Keep original
                            
            except Exception as e:
                print(f"Error translating batch {i}: {e}")
                # Keep original texts if translation fails
                all_translated_texts.extend(batch)
        
        return all_translated_texts
    
    def apply_translations(self, soup, text_mapping, translated_texts):
        """Apply translated texts back to their original positions"""
        text_index = 0
        
        for text_id in sorted(text_mapping.keys()):
            if text_index < len(translated_texts):
                element_info = text_mapping[text_id]['element_info']
                element = element_info['element']
                translated_text = translated_texts[text_index].strip()
                
                if element_info['type'] == 'content':
                    # Replace text content
                    # Clear existing text content but keep child elements
                    for content in list(element.contents):
                        if hasattr(content, 'strip'):  # Text node
                            content.replace_with(translated_text)
                            break
                    else:
                        # If no text node found, add the translated text
                        if element.string:
                            element.string.replace_with(translated_text)
                        else:
                            element.insert(0, translated_text)
                
                elif element_info['type'] in ['alt', 'title']:
                    # Replace attribute value
                    attribute = element_info['attribute']
                    element[attribute] = translated_text
                
                text_index += 1
        
        return soup
    
    def process_html_file(self, input_file_path, source_lang=None, target_lang=None):
        """Process HTML file with optimized text-only translation"""
        # Read HTML file
        with open(input_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"Processing HTML file: {input_file_path}")
        
        # Extract only text content
        soup, text_elements = self.extract_text_only(html_content)
        
        if not text_elements:
            print("No translatable content found in HTML file.")
            return None
        
        print(f"Found {len(text_elements)} translatable text elements")
        
        # Prepare pure text for translation
        pure_texts, text_mapping = self.prepare_text_for_translation(text_elements)
        
        # Auto-detect language if not provided
        if source_lang is None:
            sample_text = " ".join(pure_texts[:5])
            source_lang = self.language_detector.detect_language(sample_text)
            print(f"Detected source language: {source_lang}")
        
        # Set target language
        if target_lang is None:
            target_lang = 'hi' if source_lang == 'en' else 'en'
            print(f"Target language: {target_lang}")
        
        # Create efficient translation batches
        batches = self.create_translation_batches(pure_texts, source_lang)
        print(f"Text organized into {len(batches)} efficient batches for translation")
        
        # Calculate total text length for optimization info
        total_chars = sum(len(text) for text in pure_texts)
        print(f"Total text to translate: {total_chars} characters (HTML structure excluded)")
        
        # Translate batches
        translated_texts = self.translate_batches(batches, source_lang, target_lang)
        
        # Apply translations back to HTML
        translated_soup = self.apply_translations(soup, text_mapping, translated_texts)
        
        # Generate output file path
        base_name = os.path.splitext(os.path.basename(input_file_path))[0]
        output_dir = os.path.dirname(input_file_path)
        output_file_path = os.path.join(output_dir, f"{base_name}_translated_{source_lang}_to_{target_lang}.html")
        
        # Save translated HTML
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(str(translated_soup.prettify()))
        
        print(f"Translated HTML saved to: {output_file_path}")
        
        # Save optimized translation log
        log_file_path = os.path.join(output_dir, f"{base_name}_translation_log.txt")
        with open(log_file_path, 'w', encoding='utf-8') as f:
            f.write(f"Optimized HTML Translation Log\n")
            f.write(f"==============================\n\n")
            f.write(f"Source file: {input_file_path}\n")
            f.write(f"Output file: {output_file_path}\n")
            f.write(f"Source language: {source_lang}\n")
            f.write(f"Target language: {target_lang}\n")
            f.write(f"Text elements: {len(text_elements)}\n")
            f.write(f"Translation batches: {len(batches)}\n")
            f.write(f"Total characters translated: {total_chars}\n")
            f.write(f"Optimization: HTML structure excluded from translation\n\n")
            
            f.write("Translation Details:\n")
            f.write("===================\n\n")
            
            text_index = 0
            for text_id in sorted(text_mapping.keys()):
                if text_index < len(translated_texts):
                    original = text_mapping[text_id]['original']
                    translated = translated_texts[text_index]
                    element_info = text_mapping[text_id]['element_info']
                    
                    f.write(f"ID {text_id} ({element_info['tag']} - {element_info['type']}):\n")
                    f.write(f"Original: {original}\n")
                    f.write(f"Translated: {translated}\n")
                    f.write("-" * 50 + "\n")
                    
                    text_index += 1
        
        print(f"Translation log saved to: {log_file_path}")
        
        return output_file_path

def main():
    """Main function for optimized HTML file processing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python optimized_html_handler.py <html_file_path> [source_lang] [target_lang]")
        print("Example: python optimized_html_handler.py myfile.html en hi")
        return
    
    html_file_path = sys.argv[1]
    source_lang = sys.argv[2] if len(sys.argv) > 2 else None
    target_lang = sys.argv[3] if len(sys.argv) > 3 else None
    
    if not os.path.exists(html_file_path):
        print(f"File not found: {html_file_path}")
        return
    
    handler = OptimizedHTMLHandler()
    try:
        output_file = handler.process_html_file(html_file_path, source_lang, target_lang)
        if output_file:
            print(f"\n✓ Optimized HTML translation completed successfully!")
            print(f"✓ Translated file: {output_file}")
            print(f"✓ Only text content was translated (HTML structure preserved)")
    except Exception as e:
        print(f"Error processing HTML file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()