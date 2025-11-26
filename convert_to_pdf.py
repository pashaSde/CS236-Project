#!/usr/bin/env python3
"""
Better PDF converter for markdown files with proper styling
"""
import subprocess
import sys
from pathlib import Path

def convert_with_pandoc(md_file, output_pdf, include_images=False):
    """Convert markdown to PDF using pandoc with better options"""
    
    md_path = Path(md_file)
    pdf_path = Path(output_pdf)
    
    # Create a custom CSS for better styling
    css_content = """
    <style>
    body {
        font-family: 'Helvetica', 'Arial', sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        max-width: 800px;
        margin: 40px auto;
        padding: 20px;
        color: #333;
    }
    h1 {
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
        margin-top: 30px;
        font-size: 28pt;
    }
    h2 {
        color: #34495e;
        border-bottom: 2px solid #bdc3c7;
        padding-bottom: 8px;
        margin-top: 25px;
        font-size: 20pt;
    }
    h3 {
        color: #34495e;
        margin-top: 20px;
        font-size: 16pt;
    }
    h4 {
        color: #555;
        margin-top: 15px;
        font-size: 14pt;
    }
    code {
        background-color: #f4f4f4;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 10pt;
    }
    pre {
        background-color: #f8f8f8;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 15px;
        overflow-x: auto;
        font-size: 10pt;
        line-height: 1.4;
    }
    pre code {
        background: none;
        padding: 0;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 12px;
        text-align: left;
    }
    th {
        background-color: #3498db;
        color: white;
        font-weight: bold;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    ul, ol {
        margin: 15px 0;
        padding-left: 30px;
    }
    li {
        margin: 8px 0;
    }
    blockquote {
        border-left: 4px solid #3498db;
        padding-left: 15px;
        margin: 20px 0;
        color: #555;
        font-style: italic;
    }
    img {
        max-width: 100%;
        height: auto;
        display: block;
        margin: 20px auto;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 5px;
    }
    hr {
        border: none;
        border-top: 2px solid #bdc3c7;
        margin: 30px 0;
    }
    .page-break {
        page-break-after: always;
    }
    @media print {
        body {
            margin: 0;
            padding: 20px;
        }
    }
    </style>
    """
    
    # Write CSS to temp file
    css_file = md_path.parent / "temp_style.css"
    with open(css_file, 'w') as f:
        f.write(css_content.replace('<style>', '').replace('</style>', ''))
    
    try:
        # Pandoc command with better options
        cmd = [
            'pandoc',
            str(md_path),
            '-o', str(pdf_path),
            '--pdf-engine=wkhtmltopdf',
            '--css', str(css_file),
            '--standalone',
            '--self-contained',
            '-V', 'margin-top=20mm',
            '-V', 'margin-bottom=20mm',
            '-V', 'margin-left=20mm',
            '-V', 'margin-right=20mm',
        ]
        
        # Add resource path for images if needed
        if include_images:
            cmd.extend(['--resource-path', str(md_path.parent)])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Created: {pdf_path}")
            print(f"  Size: {pdf_path.stat().st_size // 1024} KB")
            return True
        else:
            print(f"Error: {result.stderr}")
            return False
            
    finally:
        # Clean up temp CSS
        if css_file.exists():
            css_file.unlink()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python convert_to_pdf.py <markdown_file> <output_pdf> [--with-images]")
        sys.exit(1)
    
    md_file = sys.argv[1]
    output_pdf = sys.argv[2]
    include_images = '--with-images' in sys.argv
    
    success = convert_with_pandoc(md_file, output_pdf, include_images)
    sys.exit(0 if success else 1)

