"""
Simple example: Process a single PDF with image analysis
"""

from pdf_ingestion import PDFIngestionPipeline

# Initialize pipeline with image analysis enabled
pipeline = PDFIngestionPipeline(
    ocr_confidence_threshold=0.80,  # Re-OCR pages below 80% confidence
    dpi=300,                         # Image quality for OCR
    analyze_images=True,             # Enable image analysis
    vision_model="moondream"         # Use lightweight model (CPU-friendly)
)

# Process your PDF
pdf_file = "mano_pdfs/Info_Verrechnung_VERN.pdf"  # Change this path
output_file = pipeline.process_pdf(pdf_file)

print(f"\n✅ Done! Check the output: {output_file}")
print("\nThe markdown file includes:")
print("  - Structured text from the PDF")
print("  - Enhanced OCR for scanned pages")
print("  - Detailed descriptions of all diagrams/images")
