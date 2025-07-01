from bs4 import BeautifulSoup, NavigableString
import os

def extract_all_visible_text(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"❌ File not found: {input_path}")
        return
    
    with open(input_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    output_lines = []
    
    def preserve_structure_extract(element, preserve_inline=False):
        """Extract text while preserving HTML structure"""
        
        if isinstance(element, NavigableString):
            text = str(element).strip()
            if text:
                if preserve_inline:
                    return text + " "
                else:
                    return text
            return ""
        
        if not hasattr(element, 'name') or element.name is None:
            return ""
        
        # Block-level elements that should create new lines
        block_elements = ['div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                         'li', 'tr', 'td', 'th', 'section', 'article', 
                         'header', 'footer', 'main', 'aside', 'nav']
        
        # Inline elements that should preserve spacing
        inline_elements = ['span', 'a', 'strong', 'em', 'b', 'i', 'u', 
                          'small', 'mark', 'del', 'ins', 'sub', 'sup']
        
        result = ""
        
        # Handle different element types
        if element.name in block_elements:
            # For block elements, extract all text and add appropriate formatting
            if element.name.startswith('h') and element.name[1:].isdigit():
                # Headers get special formatting
                header_text = element.get_text(separator=" ", strip=True)
                if header_text:
                    level = element.name[1:]
                    result = f"\n{'#' * int(level)} {header_text}\n"
            elif element.name == 'li':
                # List items
                li_text = ""
                for child in element.children:
                    li_text += preserve_structure_extract(child, preserve_inline=True)
                if li_text.strip():
                    result = f"• {li_text.strip()}\n"
            elif element.name in ['td', 'th']:
                # Table cells - keep on same line with separator
                cell_text = ""
                for child in element.children:
                    cell_text += preserve_structure_extract(child, preserve_inline=True)
                if cell_text.strip():
                    result = f"{cell_text.strip()} | "
            elif element.name == 'tr':
                # Table rows
                row_text = ""
                for child in element.children:
                    if child.name in ['td', 'th']:
                        row_text += preserve_structure_extract(child)
                if row_text.strip():
                    result = f"{row_text.rstrip(' | ')}\n"
            else:
                # Other block elements
                block_text = ""
                for child in element.children:
                    block_text += preserve_structure_extract(child, preserve_inline=True)
                if block_text.strip():
                    result = f"{block_text.strip()}\n"
        
        elif element.name in inline_elements:
            # Inline elements preserve their content with spacing
            inline_text = ""
            for child in element.children:
                inline_text += preserve_structure_extract(child, preserve_inline=True)
            result = inline_text
        
        elif element.name in ['ul', 'ol']:
            # Lists
            list_text = ""
            for child in element.children:
                if child.name == 'li':
                    list_text += preserve_structure_extract(child)
            result = list_text
        
        elif element.name == 'table':
            # Tables
            table_text = "\n--- TABLE ---\n"
            for child in element.children:
                table_text += preserve_structure_extract(child)
            table_text += "--- END TABLE ---\n"
            result = table_text
        
        elif element.name == 'br':
            # Line breaks
            result = "\n"
        
        else:
            # For other elements, recursively process children
            for child in element.children:
                result += preserve_structure_extract(child, preserve_inline)
        
        return result
    
    # Start extraction from body or entire document
    main_content = preserve_structure_extract(soup.body if soup.body else soup)
    
    # Clean up extra whitespace while preserving intentional line breaks
    lines = main_content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        cleaned_line = line.strip()
        if cleaned_line:  # Only add non-empty lines
            cleaned_lines.append(cleaned_line)
        elif cleaned_lines and cleaned_lines[-1]:  # Preserve single empty lines
            cleaned_lines.append("")
    
    # Write to output file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(cleaned_lines))
    
    print(f"✅ Content extracted with preserved structure and saved to: {output_path}")

# Alternative function for exact HTML structure preservation
def extract_with_exact_structure(input_path, output_path):
    """Alternative approach that more closely mirrors HTML structure"""
    
    if not os.path.exists(input_path):
        print(f"❌ File not found: {input_path}")
        return
    
    with open(input_path, "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get text with separators that preserve structure
    text = soup.get_text(separator="|NEWLINE|", strip=True)
    
    # Replace separators with actual newlines
    formatted_text = text.replace("|NEWLINE|", "\n")
    
    # Clean up excessive newlines while preserving structure
    lines = formatted_text.split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(cleaned_lines))
    
    print(f"✅ Content extracted with exact structure and saved to: {output_path}")

# Example usage
input_html = "/home/anish/html/2024_Volume_Volume 11_Part_Part II_1732888536-converted.html"
output_txt = "/home/anish/html/2024_Volume_Volume 11_Part_Part II_1732888536-converted.md"

# Use the main function
extract_all_visible_text(input_html, output_txt)

# Or try the alternative approach for even closer structure preservation
# extract_with_exact_structure(input_html, "exact_structure_output.md")