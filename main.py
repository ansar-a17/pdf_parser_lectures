from src.extractors.page_extractor import PageContentExtractor
from src.processors.transcriptions import process_transcripts
from src.processors.build_data import build_transcripts
from src.processors.chunk_matcher import TranscriptSlideChunker
from src.core.embedding import model

# Step 1: Extract slides from PDF
print("="*80)
print("STEP 1: Extracting slides from PDF")
print("="*80)
extractor = PageContentExtractor()
pages = extractor.extract_pages("lecture\\CV8.pdf")
print(f"Extracted {len(pages)} pages")

# Step 2: Process transcripts and generate embeddings
print("\n" + "="*80)
print("STEP 2: Processing transcripts")
print("="*80)
lines = process_transcripts("lecture\\transcripts.txt")
transcripts = build_transcripts(lines)  # Returns {sentence: embedding}
print(f"Processed {len(transcripts)} transcript sentences")

# Step 3: Match transcripts to slides and create chunks
print("\n" + "="*80)
print("STEP 3: Matching transcripts to slides (WINDOWED)")
print("="*80)
chunker = TranscriptSlideChunker(model)
chunks = chunker.build_chunks_with_windows(
    transcript_sentences=transcripts,
    slide_pages=pages,
    window_size=5,
    similarity_threshold=0.60  # Lower threshold for better matching
)

# Step 4: Display results
print("\n" + chunker.get_chunk_summary(chunks))

# Step 5: Build simple dictionary structure
print("\n" + "="*80)
print("STEP 5: Building data structure")
print("="*80)
slide_data = chunker.build_simple_dict(chunks, pages)
print(f"Built data structure with {len(slide_data)} slides")

# Display empty slides information
empty_slides = [num for num, (_, trans) in slide_data.items() if len(trans) == 0]
print(f"\n  Slides with transcripts: {len(slide_data) - len(empty_slides)}")
print(f"  Slides without transcripts: {len(empty_slides)}")
if empty_slides:
    print(f"  Empty slide numbers: {sorted(empty_slides)}")
    print("\n  Preview of empty slides (first 3):")
    for slide_num in sorted(empty_slides)[:3]:
        content = slide_data[slide_num][0]
        print(f"    Slide {slide_num}: {content[:120]}...")

# Step 6: Show statistics
print("\n" + "="*80)
print("STATISTICS")
print("="*80)
stats = chunker.get_statistics(chunks)
print(f"Total Chunks: {stats['total_chunks']}")
print(f"Matched Chunks: {stats['matched_chunks']}")
print(f"Unmatched Chunks: {stats['unmatched_chunks']}")
print(f"Total Sentences: {stats['total_sentences']}")
print(f"Avg Sentences per Chunk: {stats['avg_sentences_per_chunk']:.2f}")
print(f"Avg Similarity: {stats['avg_similarity']:.3f}")
print(f"Unique Slides Matched: {stats['unique_slides_matched']}")

# Step 7: Display sample data
print("\n" + "="*80)
print("SAMPLE DATA STRUCTURE")
print("="*80)
for slide_num in sorted(list(slide_data.keys()))[:3]:  # Show first 3 slides
    slide_content, transcripts = slide_data[slide_num]
    print(f"\n📄 Slide {slide_num}:")
    print(f"   Content preview: {slide_content[:80]}...")
    print(f"   Transcript count: {len(transcripts)} sentences")
    if transcripts:
        print(f"   First transcript: {transcripts[0][:100]}...")
    else:
        print(f"   (No transcripts matched to this slide)")

print("\n✅ Done! Data structure ready in 'slide_data' variable.")
print(f"\nAccess examples:")
print(f"  - slide_data[6]  # Get slide 6 content and transcripts")
print(f"  - slide_data[6][0]  # Get slide 6 content only")
print(f"  - slide_data[6][1]  # Get slide 6 transcript sentences")

# Optional: Export to files
from src.utils.data_utils import export_to_json
export_to_json(slide_data, "slide_data.json")
