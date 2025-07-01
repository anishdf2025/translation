from bs4 import BeautifulSoup
import os

def extract_all_visible_text(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"❌ File not found: {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    output_lines = []

    def recursive_extract(element, depth=0):
        indent = "    " * depth  # indentation for nested structure
        for child in element.children:
            if child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                text = child.get_text(strip=True)
                if text:
                    output_lines.append(f"\n# {child.name.upper()}: {text}")
                    output_lines.append("-" * 60)
            elif child.name in ['p', 'li', 'span', 'div', 'strong', 'em', 'a', 'td', 'th']:
                text = child.get_text(strip=True)
                if text:
                    output_lines.append(indent + text)
            elif child.name in ['ul', 'ol', 'table', 'thead', 'tbody', 'tr']:
                recursive_extract(child, depth + 1)
            elif child.string and not child.name:
                text = child.string.strip()
                if text:
                    output_lines.append(indent + text)
            elif child.name:
                recursive_extract(child, depth)

    recursive_extract(soup.body if soup.body else soup)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"✅ All content extracted and saved to: {output_path}")

# Example usage
input_html = "/home/anish/html/[2023] 4 S.C.R. 1144 1.html" 
output_txt = "all_extracted_output.txt"
extract_all_visible_text(input_html, output_txt)
