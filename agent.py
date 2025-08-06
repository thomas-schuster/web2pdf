#!/usr/bin/env python3

import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import requests
import yaml
from bs4 import BeautifulSoup
from PIL import Image


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
    title = re.sub(r"[^\x20-\x7E]", "", title).strip()
    author = re.sub(r"[^\x20-\x7E]", "", author).strip()

    return title, author


def convert_to_markdown(html_file, md_file):
    print("📝 Converting HTML to Markdown...")
    subprocess.run(["pandoc", html_file, "-f", "html", "-t", "markdown", "-o", md_file], check=True)


def download_images(md_file, slug):
    print("🖼️  Downloading and processing images...")

    # Create img directory
    img_dir = Path("img")
    img_dir.mkdir(exist_ok=True)

    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Find all image URLs
    image_pattern = r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*>'
    images = re.findall(image_pattern, content)

    downloaded_images = {}

    for i, (img_url, alt_text) in enumerate(images):
        if not img_url.startswith("http"):
            continue

        try:
            # Get file extension
            parsed_url = urlparse(img_url)
            ext = Path(parsed_url.path).suffix or ".jpg"
            
            # Convert GIF to JPG for LaTeX compatibility
            if ext.lower() == '.gif':
                ext = '.jpg'
                print(f"  🔄 Converting GIF to JPG for LaTeX compatibility")

            # Create filename
            filename = f"{slug}_image_{i+1}{ext}"
            img_path = img_dir / filename

            # Download image
            print(f"  📥 Downloading: {filename}")
            response = requests.get(img_url, stream=True)
            response.raise_for_status()

            # For GIF files, download as temporary file first, then convert
            if img_url.lower().endswith('.gif'):
                temp_path = img_dir / f"temp_{filename}"
                with open(temp_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Convert GIF to JPEG
                try:
                    print(f"  🔄 Converting GIF to JPG...")
                    with Image.open(temp_path) as img:
                        # Convert to RGB mode (required for JPEG)
                        if img.mode in ('RGBA', 'P'):
                            img = img.convert('RGB')
                        # Save first frame as JPEG
                        img.save(img_path, 'JPEG', quality=90)
                    # Remove temporary file
                    temp_path.unlink()
                except Exception as e:
                    print(f"  ⚠️  GIF conversion failed: {e}")
                    # Fall back to original file
                    temp_path.rename(img_path)
            else:
                with open(img_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

            downloaded_images[img_url] = {
                "path": f"img/{filename}",  # Include img/ prefix for correct path
                "alt": alt_text,
                "filename": filename,
            }

        except Exception as e:
            print(f"  ⚠️  Failed to download {img_url}: {e}")
            # Use placeholder for failed downloads
            downloaded_images[img_url] = {"path": "example-image-a", "alt": alt_text, "filename": "example-image-a"}

    return downloaded_images


def insert_metadata(md_file, metadata, downloaded_images=None):
    import re

    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 🧹 Cleanup: PDF image references to normal links
    content = re.sub(
        r"!\[[^\]]*\]\([^\s)]+\.pdf[^\)]*\)", lambda m: "[PDF link](" + m.group(0).split("](")[-1].rstrip(")") + ")", content
    )

    # 🧹 Cleanup: Remove problematic inline SVG and base64 images that break LaTeX
    content = re.sub(r"!\[[^\]]*\]\(data:image/[^)]*\)", "[Image]", content)
    
    # 🧹 Cleanup: Remove problematic Next.js image URLs that break LaTeX
    content = re.sub(r"!\[[^\]]*\]\(/_next/image/[^)]*\)", "[Image]", content)

    # 🖼️ Process downloaded images
    if downloaded_images:
        # Replace figure blocks with simple image placeholders
        def replace_figure(match):
            img_url = match.group(1)
            alt_text = match.group(2)

            if img_url in downloaded_images:
                img_info = downloaded_images[img_url]
                if img_info["filename"] == "example-image-a":
                    return f"![{alt_text}](example-image-a)"
                else:
                    return f"![{alt_text}]({img_info['path']})"
            return f"[Image: {alt_text}]"

        # Replace HTML img tags
        content = re.sub(r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*>', replace_figure, content)

        # Replace figure blocks
        content = re.sub(
            r'<figure[^>]*>.*?<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*>.*?</figure>',
            replace_figure,
            content,
            flags=re.DOTALL,
        )

    # 🧹 Cleanup: Remove problematic characters that break LaTeX
    # Fix URLs with problematic characters for LaTeX
    content = re.sub(r'(\{rel="[^"]*"\})', "", content)  # Remove {rel="noopener"} attributes
    content = re.sub(r"_hsenc=[^&\)\s]*", "", content)  # Remove _hsenc parameters
    content = re.sub(r"\?utm_[^&\)\s]*", "", content)  # Remove utm parameters
    content = re.sub(r"&utm_[^&\)\s]*", "", content)  # Remove additional utm parameters

    # Clean up any double ampersands or trailing symbols
    content = re.sub(r"&&+", "&", content)
    content = re.sub(r"&\)", ")", content)
    content = re.sub(r"\?\)", ")", content)

    # 🧹 Remove complex CSS classes and attributes that can break LaTeX
    content = re.sub(r"\{[^}]*\}", "", content)  # Remove CSS classes like {.flex .items-center}
    content = re.sub(r'target="_blank"[^)]*', "", content)  # Remove target attributes

    # 🧹 Remove pandoc div blocks that can cause issues
    content = re.sub(r":::+[^:]*:::+", "", content, flags=re.DOTALL)
    content = re.sub(r"::+[^:]*::+", "", content, flags=re.DOTALL)

    yaml_header = "---\n" + yaml.dump(metadata) + "---\n"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(yaml_header + "\n" + content)


def generate_pdf(md_file, tex_template, pdf_file):
    print("📄 Generating LaTeX and PDF...")

    # Generate LaTeX file first
    tex_file = pdf_file.replace(".pdf", ".tex")
    print(f"📝 Creating LaTeX file: {tex_file}")
    subprocess.run(["pandoc", md_file, "--template", tex_template, "-o", tex_file, "--highlight-style=pygments"], check=True)

    # Post-process LaTeX file to fix image handling
    with open(tex_file, "r", encoding="utf-8") as f:
        latex_content = f.read()

    # Simply remove pandocbounded wrapper but keep includegraphics
    import re

    latex_content = re.sub(r"\\pandocbounded\{(\\includegraphics\[[^\]]*\]\{[^}]+\})\}", r"\1", latex_content)

    # Write back the corrected LaTeX
    with open(tex_file, "w", encoding="utf-8") as f:
        f.write(latex_content)

    # Generate PDF from LaTeX
    print(f"📄 Creating PDF from LaTeX: {pdf_file}")
    subprocess.run(
        ["pandoc", md_file, "--template", tex_template, "-o", pdf_file, "--pdf-engine=xelatex", "--highlight-style=pygments"],
        check=True,
    )


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

    # Download images
    downloaded_images = download_images(md_file, slug)

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

    metadata = {"title": title, "author": author, "url": url, "editor": editor, "date": today}
    insert_metadata(md_file, metadata, downloaded_images)
    generate_pdf(md_file, tex_template, pdf_file)

    # Optional LaTeX compilation with our custom module
    print("\n🔧 Optional: Advanced LaTeX compilation")
    print("Would you like to compile the LaTeX file with our enhanced compiler?")
    print("(This provides better error handling and detailed output)")
    try:
        compile_choice = input("Compile LaTeX? (y/N): ").strip().lower()
    except EOFError:
        compile_choice = "n"  # Default to 'no' if no input available

    if compile_choice == "y":
        try:
            # Try importing from the current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)

            from latex_compiler import LaTeXCompiler

            compiler = LaTeXCompiler()
            print(f"\n🔄 Compiling {tex_file} with enhanced LaTeX compiler...")
            success = compiler.compile_document(tex_file)
            if success:
                print("✅ Enhanced LaTeX compilation completed successfully!")
            else:
                print("❌ Enhanced LaTeX compilation failed. Check the output above for details.")
        except ImportError as e:
            print(f"❌ LaTeX compiler module not found: {e}")
            print("   Make sure latex_compiler.py is in the same directory as agent.py")
        except Exception as e:
            print(f"❌ Error during enhanced compilation: {e}")

    print("\n✅ Done! Generated files:")
    print(f"   📄 PDF: {pdf_file}")
    print(f"   📝 LaTeX: {tex_file}")
    print(f"   📰 Markdown: {md_file}")
    print(f"   🌐 HTML: {html_file}")


if __name__ == "__main__":
    main()
