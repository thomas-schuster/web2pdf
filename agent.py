#!/usr/bin/env python3

import os
import sys
import subprocess
from datetime import date
from urllib.parse import urlparse
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import yaml

def fetch_html(url, output_file):
    print("🌐 Downloading HTML...")
    r = requests.get(url)
    r.raise_for_status()
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(r.text)

def extract_metadata(html_file):
    print("🔍 Extracting metadata...")
    with open(html_file, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    title = soup.title.string.strip() if soup.title else "Unknown Title"

    # Try to get author from meta tags
    author = "Unknown Author"
    author_meta = soup.find("meta", attrs={"name": "author"}) or soup.find("meta", attrs={"property": "author"})
    if author_meta and author_meta.get("content"):
        author = author_meta["content"].strip()

    import re
    # Clean up metadata values
    title = re.sub(r'[^\x20-\x7E]', '', title).strip()
    author = re.sub(r'[^\x20-\x7E]', '', author).strip()

    return title, author

def convert_to_markdown(html_file, md_file):
    print("📝 Converting HTML to Markdown...")
    subprocess.run(["pandoc", html_file, "-f", "html", "-t", "markdown", "-o", md_file], check=True)

def insert_metadata(md_file, metadata):
    import re
    import yaml

    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 🧹 Cleanup: PDF image references to normal links
    content = re.sub(r'!\[[^\]]*\]\([^\s)]+\.pdf[^\)]*\)', lambda m: '[PDF link](' + m.group(0).split('](')[-1].rstrip(')') + ')', content)
    
    # 🧹 Cleanup: Remove problematic inline SVG and base64 images that break LaTeX
    content = re.sub(r'!\[[^\]]*\]\(data:image/[^)]*\)', '[Image]', content)
    
    # 🧹 Cleanup: Remove problematic characters that break LaTeX
    # Fix URLs with problematic characters for LaTeX
    content = re.sub(r'(\{rel="[^"]*"\})', '', content)  # Remove {rel="noopener"} attributes
    content = re.sub(r'_hsenc=[^&\)\s]*', '', content)  # Remove _hsenc parameters
    content = re.sub(r'\?utm_[^&\)\s]*', '', content)  # Remove utm parameters
    content = re.sub(r'&utm_[^&\)\s]*', '', content)  # Remove additional utm parameters
    
    # Clean up any double ampersands or trailing symbols
    content = re.sub(r'&&+', '&', content)
    content = re.sub(r'&\)', ')', content)
    content = re.sub(r'\?\)', ')', content)
    
    # 🧹 Remove complex CSS classes and attributes that can break LaTeX
    content = re.sub(r'\{[^}]*\}', '', content)  # Remove CSS classes like {.flex .items-center}
    content = re.sub(r'target="_blank"[^)]*', '', content)  # Remove target attributes
    
    # 🧹 Remove pandoc div blocks that can cause issues
    content = re.sub(r':::+[^:]*:::+', '', content, flags=re.DOTALL)
    content = re.sub(r'::+[^:]*::+', '', content, flags=re.DOTALL)

    yaml_header = "---\n" + yaml.dump(metadata) + "---\n"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(yaml_header + "\n" + content)

def generate_pdf(md_file, tex_template, pdf_file):
    print("📄 Generating LaTeX and PDF...")
    
    # Generate LaTeX file first
    tex_file = pdf_file.replace('.pdf', '.tex')
    print(f"📝 Creating LaTeX file: {tex_file}")
    subprocess.run([
        "pandoc", md_file,
        "--template", tex_template,
        "-o", tex_file,
        "--highlight-style=pygments"
    ], check=True)
    
    # Generate PDF from LaTeX
    print(f"📄 Creating PDF from LaTeX: {pdf_file}")
    subprocess.run([
        "pandoc", md_file,
        "--template", tex_template,
        "-o", pdf_file,
        "--pdf-engine=xelatex",
        "--highlight-style=pygments"
    ], check=True)

def main():
    if len(sys.argv) != 2:
        print("❌ Usage: python agent.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    slug = Path(urlparse(url).path).stem or "article"
    today = date.today().isoformat()

    html_file = f"{slug}.html"
    md_file = f"{slug}.md"
    pdf_file = f"{slug}.pdf"
    tex_file = f"{slug}.tex"
    tex_template = "webarticle.latex"

    for file in (html_file, md_file, pdf_file, tex_file):
        if Path(file).exists():
            Path(file).unlink()

    fetch_html(url, html_file)
    title, author = extract_metadata(html_file)
    convert_to_markdown(html_file, md_file)

    editor = os.getenv("USER") or os.getenv("USERNAME") or "Editor"

    print("\n✅ Please confirm or edit the following metadata:")
    print("(Press Enter to keep the current value, or type a new value)")
    
    # Interactive metadata editing
    new_title = input(f"Title  [{title}]: ").strip()
    if new_title:
        title = new_title
    
    new_author = input(f"Author [{author}]: ").strip()
    if new_author:
        author = new_author
    
    new_editor = input(f"Editor [{editor}]: ").strip()
    if new_editor:
        editor = new_editor
    
    new_date = input(f"Date   [{today}]: ").strip()
    if new_date:
        today = new_date
    
    # URL is usually not changed, but allow it just in case
    new_url = input(f"URL    [{url}]: ").strip()
    if new_url:
        url = new_url

    metadata = {
        "title": title,
        "author": author,
        "url": url,
        "editor": editor,
        "date": today
    }
    insert_metadata(md_file, metadata)
    generate_pdf(md_file, tex_template, pdf_file)
    print(f"✅ Done! Generated files:")
    print(f"   📄 PDF: {pdf_file}")
    print(f"   📝 LaTeX: {tex_file}")
    print(f"   📰 Markdown: {md_file}")
    print(f"   🌐 HTML: {html_file}")

if __name__ == "__main__":
    main()
