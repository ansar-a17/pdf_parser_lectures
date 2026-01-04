from pdf_ingestion import PDFIngestionPipeline

pipeline = PDFIngestionPipeline(
    ocr_confidence_threshold=0.80,
    dpi=300,                  
    analyze_images=True,      
    vision_model="moondream"
)

# Process your PDF
pdf_file = r"mano_pdfs\08_Verdauungssäfte_Lösung.pdf"
output_file = pipeline.process_pdf(pdf_file)

print(f"\n✅ Done! Check the output: {output_file}")
print("\nThe markdown file includes:")
print("  - Structured text from the PDF")
print("  - Enhanced OCR for scanned pages")
print("  - Detailed descriptions of all diagrams/images")
