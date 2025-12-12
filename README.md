# High-Accuracy PDF Ingestion System

A hybrid Docling + Tesseract OCR pipeline for extracting clean, structured text from PDFs with maximum accuracy, plus **local vision model support** for analyzing diagrams and images.

## Features

✅ **High Structural Accuracy** - Preserves headings, reading order, lists, multi-column layouts, and tables  
✅ **Integrated OCR** - Handles both digital and scanned PDFs automatically  
✅ **Quality Boost** - Re-runs OCR with Tesseract on low-confidence pages  
✅ **🆕 Image Analysis** - Analyzes diagrams, charts, and images using local vision models (NO API costs!)  
✅ **LLM-Ready Output** - Exports clean Markdown perfect for AI processing  
✅ **Batch Processing** - Process entire directories of PDFs  
✅ **Fully Local** - No API keys or cloud services required

## System Requirements

### Windows

1. **Python 3.8+**
2. **Tesseract OCR**
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to default location (or add to PATH)
   - Verify installation: `tesseract --version`

3. **Poppler** (for PDF to image conversion)
   - Download from: https://github.com/oschwartz10612/poppler-windows/releases
   - Extract to `C:\Program Files\poppler` or similar
   - Add `C:\Program Files\poppler\Library\bin` to your PATH

### Linux

```bash
sudo apt-get install tesseract-ocr poppler-utils
```

### macOS

```bash
brew install tesseract poppler
```

## Installation

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended)
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```

3. **Install Python dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Verify Tesseract is accessible**
   ```powershell
   tesseract --version
   ```

   If Tesseract is not found, you may need to specify its path in your code:
   ```python
   import pytesseract
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

## Usage

### Quick Start: Process with Image Analysis

```powershell
python pdf_ingestion.py path/to/document.pdf
```

Output will be saved as `document_clean.md` with image descriptions included! 🎉

### Process Entire mano_pdfs Folder

```powershell
python process_mano_pdfs.py
```

This will:
- Find all PDFs in `mano_pdfs` (including subdirectories)
- Process each one with OCR enhancement
- Analyze all diagrams and images
- Save outputs to `clean_output/` with image descriptions

### Advanced Options

```powershell
# Without image analysis (faster)
python pdf_ingestion.py input.pdf --no-images

# Choose vision model (moondream/ollama/transformers)
python pdf_ingestion.py input.pdf --vision-model moondream

# Adjust OCR confidence threshold (0-1, default: 0.80)
python pdf_ingestion.py input.pdf --threshold 0.75

# Increase DPI for better OCR quality (default: 300)
python pdf_ingestion.py input.pdf --dpi 400

# Don't search subdirectories
python pdf_ingestion.py mano_pdfs --no-recursive
```

### Vision Model Options

See **[VISION_SETUP.md](VISION_SETUP.md)** for detailed vision model setup instructions.

- **moondream** (default) - Fast, CPU-friendly, ~2GB
- **ollama** - Easy setup, good quality, ~4GB
- **transformers** - Most accurate, requires GPU, ~13GB

## Using as a Library

```python
from pdf_ingestion import PDFIngestionPipeline, process_directory

# Process a single file with image analysis
pipeline = PDFIngestionPipeline(
    ocr_confidence_threshold=0.80, 
    dpi=300,
    analyze_images=True,
    vision_model="moondream"
)
output = pipeline.process_pdf("lecture_notes.pdf")
print(f"Output saved to: {output}")

# Process all PDFs in a folder
outputs = process_directory(
    input_dir="mano_pdfs",
    output_dir="clean_markdown",
    recursive=True,
    analyze_images=True,
    vision_model="moondream"
)
```

## Quick Start: Process Your PDFs

Process all PDFs in the `mano_pdfs` folder:

```powershell
python pdf_ingestion.py mano_pdfs -o clean_output
```

Or use the convenience script:

```powershell
python process_mano_pdfs.py
```

## How It Works

1. **Parse with Docling** - Extracts structure (headings, layout, tables)
2. **Check OCR Quality** - Identifies low-confidence pages
3. **Enhance OCR** - Re-runs Tesseract on problematic pages at high DPI
4. **🆕 Analyze Images** - Extracts and describes diagrams using local vision model
5. **Export Markdown** - Combines structure + enhanced text + image descriptions

## Output Format

The system generates clean Markdown with:
- Proper heading hierarchy
- Lists and bullet points
- Table structure
- Preserved reading order
- Clean paragraphs
- **🆕 Detailed image/diagram descriptions** appended in "Image Analysis" section

Perfect for:
- AI/LLM processing
- Note-taking apps
- Documentation systems
- Text analysis

## Troubleshooting

### "Tesseract not found"

**Windows:** Add Tesseract to PATH or set explicitly:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### "Poppler not found"

**Windows:** Download Poppler and add `poppler/Library/bin` to PATH

### Low accuracy results

Try increasing DPI:
```powershell
python pdf_ingestion.py input.pdf --dpi 400
```

### Out of memory errors

Reduce DPI or process files individually:
```powershell
python pdf_ingestion.py input.pdf --dpi 200
```

## Project Structure

```
docling/
├── pdf_ingestion.py         # Main pipeline implementation
├── process_mano_pdfs.py     # Convenience script for mano_pdfs
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── instructions.md         # Original design document
├── mano_pdfs/             # Input PDFs
│   └── hormonsystem/
└── clean_output/          # Generated Markdown files
```

## License

Open source - use freely for any purpose.

## Credits

Built with:
- [Docling](https://github.com/DS4SD/docling) - IBM's document understanding engine
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - Google's OCR engine
- [pdf2image](https://github.com/Belval/pdf2image) - PDF to image conversion
