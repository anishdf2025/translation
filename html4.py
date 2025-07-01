import os
from bs4 import BeautifulSoup

def extract_text_from_html(input_path, output_path):
    # Check if input file exists
    if not os.path.exists(input_path):
        print(f"❌ File not found: {input_path}")
        return

    # Read HTML content
    with open(input_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Parse HTML
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract visible text
    text = soup.get_text(separator="\n", strip=True)

    # Save to output file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"✅ Extracted text saved to: {output_path}")

# Example usage
input_html = "/home/anish/html/[2023] 4 S.C.R. 1144 1.html"      # 🔁 Change to your HTML file
output_txt = "extracted_text.txt"  # 🔁 Output .txt file
extract_text_from_html(input_html, output_txt)
