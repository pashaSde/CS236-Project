#!/bin/bash
# Create better PDFs using Chrome/pandoc

MD_FILE="$1"
OUTPUT_PDF="$2"
INCLUDE_IMAGES="${3:-no}"

if [ -z "$MD_FILE" ] || [ -z "$OUTPUT_PDF" ]; then
    echo "Usage: $0 <markdown_file> <output_pdf> [with-images]"
    exit 1
fi

# Get absolute paths
MD_PATH=$(cd "$(dirname "$MD_FILE")" && pwd)/$(basename "$MD_FILE")
OUT_DIR=$(dirname "$OUTPUT_PDF")
PDF_NAME=$(basename "$OUTPUT_PDF")

cd "$OUT_DIR" || exit 1

# Create styled HTML
HTML_FILE="${PDF_NAME%.pdf}.html"

pandoc "$MD_PATH" -o "$HTML_FILE" \
    --standalone \
    --self-contained \
    --metadata title="$(head -n 1 "$MD_PATH" | sed 's/^# //')" \
    --css=<(cat <<'EOF'
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    max-width: 900px;
    margin: 0 auto;
    padding: 40px 60px;
    color: #24292e;
    background: white;
}
h1 {
    color: #1a1a1a;
    border-bottom: 3px solid #0366d6;
    padding-bottom: 0.3em;
    margin-top: 24px;
    margin-bottom: 16px;
    font-size: 2em;
    font-weight: 600;
}
h2 {
    color: #1a1a1a;
    border-bottom: 2px solid #e1e4e8;
    padding-bottom: 0.3em;
    margin-top: 24px;
    margin-bottom: 16px;
    font-size: 1.5em;
    font-weight: 600;
}
h3 {
    color: #1a1a1a;
    margin-top: 24px;
    margin-bottom: 16px;
    font-size: 1.25em;
    font-weight: 600;
}
h4 {
    color: #1a1a1a;
    margin-top: 20px;
    margin-bottom: 12px;
    font-size: 1em;
    font-weight: 600;
}
code {
    background-color: rgba(27,31,35,.05);
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    font-size: 85%;
}
pre {
    background-color: #f6f8fa;
    border-radius: 6px;
    padding: 16px;
    overflow-x: auto;
    line-height: 1.45;
    border: 1px solid #d0d7de;
}
pre code {
    background-color: transparent;
    padding: 0;
    border-radius: 0;
    font-size: 85%;
    line-height: 1.45;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
    border: 1px solid #d0d7de;
}
th, td {
    border: 1px solid #d0d7de;
    padding: 8px 13px;
    text-align: left;
}
th {
    background-color: #f6f8fa;
    font-weight: 600;
}
tr:nth-child(2n) {
    background-color: #f6f8fa;
}
ul, ol {
    margin: 16px 0;
    padding-left: 2em;
}
li {
    margin: 0.25em 0;
}
li > p {
    margin: 0;
}
blockquote {
    border-left: 4px solid #d0d7de;
    padding: 0 16px;
    margin: 16px 0;
    color: #57606a;
}
hr {
    height: 0.25em;
    padding: 0;
    margin: 24px 0;
    background-color: #d0d7de;
    border: 0;
}
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 20px auto;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
    border-radius: 4px;
}
@media print {
    body {
        margin: 0;
        padding: 20mm;
    }
    h1, h2, h3, h4, h5, h6 {
        page-break-after: avoid;
    }
    table, pre {
        page-break-inside: avoid;
    }
}
EOF
)

# Convert HTML to PDF using Chrome
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    --headless \
    --disable-gpu \
    --print-to-pdf="$PDF_NAME" \
    --no-margins \
    --print-to-pdf-no-header \
    "$HTML_FILE" \
    2>/dev/null

# Clean up HTML
rm "$HTML_FILE"

if [ -f "$PDF_NAME" ]; then
    SIZE=$(du -h "$PDF_NAME" | awk '{print $1}')
    echo "Created: $PDF_NAME ($SIZE)"
else
    echo "Failed to create PDF"
    exit 1
fi

