# HTML File Processing Integration

## Overview
The translation system now automatically handles HTML files! When you provide an HTML file as input, the system will:

1. **Automatically detect** that it's an HTML file (`.html` or `.htm` extension)
2. **Extract all visible text** while preserving structure (headers, lists, tables, etc.)
3. **Generate a `.md` file** with the extracted content
4. **Use the generated `.md` file** for translation processing
5. **Create appropriately named output files** based on the original HTML filename

## Features

### HTML Processing Capabilities
- ✅ Extracts all visible text content
- ✅ Preserves document structure (headers, paragraphs, lists)
- ✅ Handles tables with proper formatting
- ✅ Removes scripts and styles automatically
- ✅ Maintains semantic formatting with markdown syntax

### Automatic Workflow
- ✅ No manual steps required
- ✅ Seamless integration with existing translation logic
- ✅ No changes to existing functionality for other file types

## How It Works

### Before (Manual Process)
1. Run `html6.py` on HTML file → generates `.md` file
2. Manually copy path to `.md` file
3. Paste path when prompted: "Enter the path to the text file"
4. Translation proceeds

### After (Automatic Process)
1. Enter HTML file path when prompted: "Enter the path to the text file"
2. System automatically generates `.md` file
3. Translation proceeds using extracted content
4. All output files are properly named

## Example Usage

```bash
cd /home/anish/gemma3_ollama_tra_NER_QA/translation_modular
python3 main.py
```

When prompted for file path:
```
Enter the path to the text file (or 'quit' to exit)
> /path/to/your/document.html
```

The system will automatically:
- Generate: `/path/to/your/document.md`
- Create translation files: `document_chunks_hindi.md`, `document_clean_translation.md`, etc.

## Files Added/Modified

### New Files
- `html_parser.py` - HTML processing logic (based on html6.py)

### Modified Files
- `file_handler.py` - Added HTML detection and processing integration

### Key Methods Added
- `_is_html_file()` - Detects HTML files by extension
- `_process_html_to_md_file()` - Converts HTML to markdown file
- Updated `read_file()` - Handles HTML files automatically
- Updated `create_output_paths()` - Proper naming for HTML-derived files

## Output Files for HTML Input

For input file: `document.html`

Generated files:
- `document.md` (extracted content)
- `document_chunks_hindi.md` (detailed translations)
- `document_clean_translation.md` (clean translations)
- `document_chunk_translation_timing.txt` (timing information)

## Compatibility
- ✅ Fully backward compatible with existing text/markdown files
- ✅ No changes required to existing workflow for non-HTML files
- ✅ All existing features and functionality preserved

## Dependencies
- `beautifulsoup4` (already in requirements.txt)
- All existing dependencies remain the same
