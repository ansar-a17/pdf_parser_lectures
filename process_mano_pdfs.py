from pdf_ingestion import process_directory
from pathlib import Path


def main():
    # Configuration
    input_dir = "mano_pdfs"
    output_dir = "clean_output"
    dpi = 300  # DPI for image conversion (higher = better quality, slower)
    analyze_images = True  # Analyze diagrams with vision model
    vision_model = "moondream"  # Options: "moondream", "ollama", "transformers"
    
    print("=" * 70)
    print("PDF Ingestion Pipeline - Processing mano_pdfs folder")
    print("=" * 70)
    print(f"Input:  {input_dir}")
    print(f"Output: {output_dir}")
    print(f"DPI: {dpi}")
    print(f"Image analysis: {analyze_images}")
    if analyze_images:
        print(f"Vision model: {vision_model}")
    print("=" * 70)
    
    # Check if input directory exists
    if not Path(input_dir).exists():
        print(f"\n❌ Error: Directory '{input_dir}' not found!")
        print("Please make sure the mano_pdfs folder exists.")
        return
    
    # Process all PDFs
    try:
        output_files = process_directory(
            input_dir=input_dir,
            output_dir=output_dir,
            dpi=dpi,
            recursive=True,
            analyze_images=analyze_images,
            vision_model=vision_model
        )
        
        print("\n" + "=" * 70)
        print("✅ Processing complete!")
        print(f"Generated {len(output_files)} markdown file(s) in: {output_dir}")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
