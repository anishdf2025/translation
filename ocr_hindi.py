import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    EasyOcrOptions, 
    PdfPipelineOptions, 
    AcceleratorDevice, 
    AcceleratorOptions
)
from pathlib import Path
import logging
import mimetypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_input_format(file_path):
    """Determine the input format based on file extension"""
    file_path = Path(file_path)
    extension = file_path.suffix.lower()
    
    format_mapping = {
        '.pdf': InputFormat.PDF,
        '.png': InputFormat.IMAGE,
        '.jpg': InputFormat.IMAGE,
        '.jpeg': InputFormat.IMAGE,
    }
    
    return format_mapping.get(extension, InputFormat.PDF)  # Default to PDF

def ocr_and_markdown(input_doc_path, output_dir=None):
    try:
        input_doc_path = Path(input_doc_path)
        if output_dir is None:
            output_dir = input_doc_path.parent
        else:
            output_dir = Path(output_dir)

        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        file_stem = input_doc_path.stem
        output_md = output_dir / f"{file_stem}_hindi_ocr.md"

        # Determine input format
        input_format = get_input_format(input_doc_path)
        
        # Set accelerator options
        accelerator_options = AcceleratorOptions(device=AcceleratorDevice.CPU)

        # Configure pipeline for Hindi OCR
        pipeline_options = PdfPipelineOptions()
        
        # Hindi language codes for EasyOCR (try both variations)
        HINDI_LANG_CODES = ["hi","en"]  # Try both language codes
        
        # Basic pipeline settings
        pipeline_options.do_code_enrichment = False  # Disable for better OCR focus
        pipeline_options.do_formula_enrichment = False  # Disable for better OCR focus
        pipeline_options.images_scale = 2.0  # Reduce scale for better performance
        pipeline_options.generate_page_images = True
        pipeline_options.generate_picture_images = True
        pipeline_options.accelerator_options = accelerator_options
        
        # Configure EasyOCR with Hindi settings
        pipeline_options.ocr_options = EasyOcrOptions(
            force_full_page_ocr=True,
            confidence_threshold=0.3,  # Lower threshold for better detection
            lang=HINDI_LANG_CODES
        )

        # Create format options for multiple formats
        format_options = {}
        
        # Configure format options based on input type
        if input_format == InputFormat.PDF:
            format_options[InputFormat.PDF] = PdfFormatOption(pipeline_options=pipeline_options)
        elif input_format == InputFormat.HTML:
            # For HTML, we need to configure it properly - HTML doesn't use PdfFormatOption
            format_options = {}  # Use default options for HTML
        elif input_format == InputFormat.IMAGE:
            # For images, we also use default options as they don't use PdfFormatOption
            format_options = {}

        # Create document converter
        doc_converter = DocumentConverter(format_options=format_options)

        logger.info(f"Starting conversion for: {input_doc_path.name} (Format: {input_format.name})")
        conv_res = doc_converter.convert(input_doc_path)
        conv_doc = conv_res.document
        
        # Export to markdown
        md_text = conv_doc.export_to_markdown()

        # Save markdown file
        with open(output_md, "w", encoding='utf-8') as f:  # Specify UTF-8 encoding
            f.write(md_text)
            
        logger.info(f"Markdown text has been written to {output_md}")
        print(f"Successfully processed: {input_doc_path.name}")
        
        return md_text

    except Exception as e:
        logger.error(f"Failed to process {input_doc_path}: {str(e)}")
        print(f"Error processing {input_doc_path.name}: {str(e)}")
        return None

def process_directory(input_dir, output_dir=None):
    """Process all supported files in the input directory and save results to the output directory"""
    input_dir = Path(input_dir)
    if output_dir is None:
        output_dir = input_dir / "output"
    else:
        output_dir = Path(output_dir)
        
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all supported files in the input directory
    supported_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
    
    all_files = []
    for ext in supported_extensions:
        all_files.extend(list(input_dir.glob(f"*{ext}")))
        all_files.extend(list(input_dir.glob(f"*{ext.upper()}")))  # Also check uppercase extensions
    
    # Remove duplicates and sort
    all_files = sorted(list(set(all_files)))
    
    if not all_files:
        logger.warning(f"No supported files found in {input_dir}")
        logger.info(f"Supported formats: {', '.join(supported_extensions)}")
        return {}
    
    # Group files by type for better logging
    file_types = {}
    for file_path in all_files:
        ext = file_path.suffix.lower()
        if ext not in file_types:
            file_types[ext] = []
        file_types[ext].append(file_path.name)
    
    logger.info(f"Found {len(all_files)} supported files to process:")
    for ext, files in file_types.items():
        logger.info(f"  {ext.upper()}: {len(files)} files")
    
    # Process each file
    results = {}
    for file_path in all_files:
        logger.info(f"Processing {file_path.name}...")
        md_text = ocr_and_markdown(file_path, output_dir)
        results[file_path.name] = md_text is not None
    
    # Summary
    successful = sum(1 for success in results.values() if success)
    logger.info(f"Processing complete: {successful}/{len(all_files)} files successfully processed")
    
    if successful < len(all_files):
        failed_files = [name for name, success in results.items() if not success]
        logger.warning(f"Failed to process: {', '.join(failed_files)}")
    
    return results

# Example usage
if __name__ == "__main__":
    # Define input and output directories
    input_directory = "/home/anish/OCR_gemma_facebook/png/"
    output_directory = "/home/anish/OCR_gemma_facebook/png1/"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    # Process all supported files in the directory
    print(f"Processing all supported files in: {input_directory}")
    print(f"Supported formats: PDF, PNG, JPG, JPEG")
    print(f"Saving results to: {output_directory}")
    
    # Get all supported files in the input directory
    input_path = Path(input_directory)
    supported_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
    
    all_files = []
    for ext in supported_extensions:
        all_files.extend(list(input_path.glob(f"*{ext}")))
        all_files.extend(list(input_path.glob(f"*{ext.upper()}")))
    
    all_files = sorted(list(set(all_files)))
    
    if all_files:
        print(f"Found {len(all_files)} supported files to process")
        
        # Show file breakdown by type
        file_types = {}
        for file_path in all_files:
            ext = file_path.suffix.lower()
            if ext not in file_types:
                file_types[ext] = 0
            file_types[ext] += 1
        
        for ext, count in file_types.items():
            print(f"  {ext.upper()}: {count} files")
        
        # Process all files
        results = process_directory(input_directory, output_directory)
        
        # Show summary
        successful = sum(1 for success in results.values() if success)
        print(f"✅ Successfully processed: {successful}/{len(all_files)} files")
        
        if successful < len(all_files):
            failed_files = [name for name, success in results.items() if not success]
            print(f"❌ Failed to process: {', '.join(failed_files)}")
        
        print(f"All processed files are saved in: {output_directory}")
    else:
        print(f"No supported files found in {input_directory}")
        print("Supported formats: PDF, HTML, PNG, JPG, JPEG, GIF, BMP, TIFF")
        print("Please check the input directory path and ensure it contains supported files.")