# OCR Integration Documentation

## Overview
The translation system now automatically handles OCR files (PDF, PNG, JPG, JPEG) in addition to HTML and Markdown files! When you provide an OCR file as input, the system will:

1. **Automatically detect** that it's an OCR file (`.pdf`, `.png`, `.jpg`, `.jpeg` extension)
2. **Process the file using Docling OCR** with Hindi language support
3. **Generate a `.md` file** with the extracted OCR content
4. **Use the generated `.md` file** for translation processing
5. **Create appropriately named output files** based on the original OCR filename

## Files Added/Modified

### New Files Created:
- `ocr_handler.py` - Handles OCR processing for PDF and image files

### Modified Files:
- `file_handler.py` - Updated to integrate OCR functionality
  - Added OCR file detection
  - Added OCR processing workflow
  - Updated output path creation for OCR files

## OCR Processing Capabilities
- ✅ Supports PDF files with text and images
- ✅ Supports PNG, JPG, JPEG image files
- ✅ Hindi and English language OCR recognition
- ✅ Automatic text extraction and markdown generation
- ✅ Seamless integration with existing translation workflow

## How It Works

### Complete Workflow
```
Input File → File Type Detection → Processing → Translation

PDF/Image File → OCR Processing → Generate .md → Split & Translate
HTML File → HTML Processing → Generate .md → Split & Translate  
Markdown File → Direct Processing → Split & Translate
```

### OCR Processing Steps
1. **File Detection**: System detects PDF/image files by extension
2. **OCR Configuration**: 
   - Hindi + English language support
   - CPU-based processing (CUDA disabled)
   - Optimized confidence threshold (0.3)
   - Full page OCR enabled
3. **Text Extraction**: Uses Docling with EasyOCR backend
4. **Markdown Generation**: Creates `filename_ocr.md` file
5. **Translation Processing**: Uses extracted content for translation

## Usage Examples

### Before (Manual Process)
1. Run `ocr_hindi.py` on PDF/image → generates `_hindi_ocr.md` file
2. Manually copy path to `.md` file
3. Paste path when prompted: "Enter the path to the text file"
4. Translation proceeds

### After (Automatic Process)
1. Enter OCR file path when prompted: "Enter the path to the text file"
2. System automatically processes OCR → generates `_ocr.md` file
3. Translation proceeds using extracted content
4. All output files are properly named

## File Processing Examples

### Input: `document.pdf`
- Auto-generates: `document_ocr.md`
- Translation outputs:
  - `document_ocr_chunks_english.md`
  - `document_ocr_clean_translation.md`
  - `document_ocr_chunk_translation_timing.txt`

### Input: `image.png`
- Auto-generates: `image_ocr.md`
- Translation outputs:
  - `image_ocr_chunks_english.md`
  - `image_ocr_clean_translation.md`
  - `image_ocr_chunk_translation_timing.txt`

## Supported File Types

| File Type | Extension | Processing Method | Output |
|-----------|-----------|-------------------|---------|
| PDF | `.pdf` | OCR Processing | `filename_ocr.md` |
| Images | `.png`, `.jpg`, `.jpeg` | OCR Processing | `filename_ocr.md` |
| HTML | `.html`, `.htm` | HTML Parsing | `filename.md` |
| Markdown | `.md` | Direct Processing | No conversion |
| Text | `.txt` | Direct Processing | No conversion |

## Technical Implementation

### OCR Handler Class
```python
class OCRHandler:
    def __init__(self):
        self.supported_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
    
    def is_ocr_file(self, file_path):
        # Check if file requires OCR processing
    
    def process_ocr_to_md_file(self, file_path):
        # Process OCR and create permanent .md file
    
    def ocr_and_markdown(self, input_doc_path, output_md_path):
        # Perform actual OCR using Docling
```

### Integration in FileHandler
```python
class FileHandler:
    def __init__(self):
        self.html_parser = HTMLParser()
        self.ocr_handler = OCRHandler()  # New OCR handler
    
    def read_file(self, file_path):
        if self._is_html_file(file_path):
            # HTML processing
        elif self._is_ocr_file(file_path):  # New OCR check
            # OCR processing
        else:
            # Direct file reading
```

## Configuration Details

### OCR Settings
- **Languages**: Hindi (`hi`) + English (`en`)
- **Device**: CPU (CUDA disabled for stability)
- **Confidence Threshold**: 0.3 (optimized for better detection)
- **Image Scale**: 2.0 (balanced performance)
- **Full Page OCR**: Enabled for complete text extraction

### Dependencies
- `docling` - Document processing and OCR
- `pathlib` - Path handling
- `logging` - Process logging

## Error Handling
- ✅ File existence validation
- ✅ OCR processing error catching
- ✅ Markdown generation validation
- ✅ Detailed error logging and user feedback

## Benefits
1. **Seamless Integration**: No manual steps required
2. **Multi-format Support**: PDF, images, HTML, markdown all supported
3. **Preserved Workflow**: Existing functionality unchanged
4. **Smart File Naming**: Proper output file organization
5. **Hindi Language Support**: Optimized for Hindi OCR recognition

## Testing the Integration

Run the system:
```bash
cd /home/anish/gemma3_ollama_tra_NER_QA/translation_modular
python3 main.py
```

Test with different file types:
- PDF: `> /path/to/document.pdf`
- Image: `> /path/to/image.png`  
- HTML: `> /path/to/document.html`
- Markdown: `> /path/to/document.md`

The system will automatically detect the file type and process accordingly!
