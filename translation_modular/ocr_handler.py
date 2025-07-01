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

# Configure logging for OCR handler
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OCRHandler:
    """Handles OCR processing for PDF and image files"""
    
    def __init__(self):
        self.supported_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
    
    def is_ocr_file(self, file_path):
        """Check if the file requires OCR processing"""
        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in self.supported_extensions
    
    def get_input_format(self, file_path):
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
    
    def process_ocr_to_md_file(self, file_path):
        """Process OCR file and create a permanent .md file"""
        try:
            # Create markdown file path
            file_name = os.path.basename(file_path)
            file_base, _ = os.path.splitext(file_name)
            md_file = f"{file_base}_ocr.md"
            md_file_path = os.path.join(os.path.dirname(file_path), md_file)
            
            # Process OCR and generate markdown
            success, error = self.ocr_and_markdown(file_path, md_file_path)
            
            if success:
                print(f"✅ OCR file processed: {file_path}")
                print(f"📄 Generated markdown file: {md_file_path}")
                print(f"📄 Using generated markdown file for translation")
                return md_file_path
            else:
                print(f"❌ Error processing OCR: {error}")
                return None
                
        except Exception as e:
            print(f"❌ Error processing OCR file: {str(e)}")
            return None
    
    def ocr_and_markdown(self, input_doc_path, output_md_path):
        """Perform OCR and save to markdown file"""
        try:
            input_doc_path = Path(input_doc_path)
            output_md_path = Path(output_md_path)
            
            # Create output directory if it doesn't exist
            output_md_path.parent.mkdir(parents=True, exist_ok=True)

            # Determine input format
            input_format = self.get_input_format(input_doc_path)
            
            # Set accelerator options
            accelerator_options = AcceleratorOptions(device=AcceleratorDevice.CPU)

            # Configure pipeline for Hindi OCR
            pipeline_options = PdfPipelineOptions()
            
            # Hindi language codes for EasyOCR (try both variations)
            HINDI_LANG_CODES = ["hi", "en"]  # Try both language codes
            
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
            elif input_format == InputFormat.IMAGE:
                # For images, we also use default options as they don't use PdfFormatOption
                format_options = {}

            # Create document converter
            doc_converter = DocumentConverter(format_options=format_options)

            logger.info(f"Starting OCR conversion for: {input_doc_path.name} (Format: {input_format.name})")
            conv_res = doc_converter.convert(input_doc_path)
            conv_doc = conv_res.document
            
            # Export to markdown
            md_text = conv_doc.export_to_markdown()

            # Save markdown file
            with open(output_md_path, "w", encoding='utf-8') as f:
                f.write(md_text)
                
            logger.info(f"OCR markdown text has been written to {output_md_path}")
            print(f"Successfully processed OCR: {input_doc_path.name}")
            
            return True, None

        except Exception as e:
            error_msg = f"Failed to process OCR {input_doc_path}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
