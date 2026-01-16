"""
Utility functions for working with the slide_data dictionary structure.

Structure: {slide_number: [slide_content, [related_transcripts]]}
"""

import json
from typing import Dict, List, Tuple


def get_slide_content(slide_data: Dict[int, List], slide_num: int) -> str:
    """
    Get the content of a specific slide.
    
    Args:
        slide_data: The slide data dictionary
        slide_num: Slide number to retrieve
        
    Returns:
        Slide content as string
    """
    if slide_num in slide_data:
        return slide_data[slide_num][0]
    return ""


def get_slide_transcripts(slide_data: Dict[int, List], slide_num: int) -> List[str]:
    """
    Get the transcript sentences for a specific slide.
    
    Args:
        slide_data: The slide data dictionary
        slide_num: Slide number to retrieve
        
    Returns:
        List of transcript sentences
    """
    if slide_num in slide_data:
        return slide_data[slide_num][1]
    return []


def get_full_transcript(slide_data: Dict[int, List], slide_num: int) -> str:
    """
    Get the full concatenated transcript for a specific slide.
    
    Args:
        slide_data: The slide data dictionary
        slide_num: Slide number to retrieve
        
    Returns:
        Full transcript as single string
    """
    transcripts = get_slide_transcripts(slide_data, slide_num)
    return " ".join(transcripts)


def get_all_slides(slide_data: Dict[int, List]) -> List[int]:
    """
    Get list of all slide numbers.
    
    Args:
        slide_data: The slide data dictionary
        
    Returns:
        Sorted list of slide numbers
    """
    return sorted(slide_data.keys())


def get_slide_pairs(slide_data: Dict[int, List]) -> List[Tuple[str, str]]:
    """
    Get list of (slide_content, full_transcript) pairs.
    
    Args:
        slide_data: The slide data dictionary
        
    Returns:
        List of tuples (slide_content, transcript)
    """
    pairs = []
    for slide_num in sorted(slide_data.keys()):
        content = slide_data[slide_num][0]
        transcript = " ".join(slide_data[slide_num][1])
        pairs.append((content, transcript))
    return pairs


def export_to_json(slide_data: Dict[int, List], filepath: str):
    """
    Export slide data to JSON file.
    
    Args:
        slide_data: The slide data dictionary
        filepath: Path to output JSON file
    """
    # Convert to JSON-friendly format
    json_data = {}
    for slide_num, (content, transcripts) in slide_data.items():
        json_data[str(slide_num)] = {
            "slide_content": content,
            "transcripts": transcripts,
            "transcript_count": len(transcripts)
        }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    print(f"Exported to {filepath}")


def load_from_json(filepath: str) -> Dict[int, List]:
    """
    Load slide data from JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Slide data dictionary
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # Convert back to original format
    slide_data = {}
    for slide_num_str, data in json_data.items():
        slide_num = int(slide_num_str)
        slide_data[slide_num] = [
            data["slide_content"],
            data["transcripts"]
        ]
    
    return slide_data


def export_to_text(slide_data: Dict[int, List], filepath: str):
    """
    Export slide data to readable text file.
    
    Args:
        slide_data: The slide data dictionary
        filepath: Path to output text file
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("SLIDE-TRANSCRIPT DATA\n")
        f.write("="*80 + "\n\n")
        f.write(f"Total Slides: {len(slide_data)}\n\n")
        
        for slide_num in sorted(slide_data.keys()):
            content, transcripts = slide_data[slide_num]
            
            f.write("\n" + "="*80 + "\n")
            f.write(f"SLIDE {slide_num}\n")
            f.write("="*80 + "\n\n")
            
            f.write("--- SLIDE CONTENT ---\n")
            f.write(content + "\n\n")
            
            f.write(f"--- TRANSCRIPT ({len(transcripts)} sentences) ---\n")
            if transcripts:
                for i, sentence in enumerate(transcripts, 1):
                    f.write(f"{i}. {sentence}\n")
            else:
                f.write("(No transcripts matched to this slide)\n")
            
            f.write("\n")
    
    print(f"Exported to {filepath}")


def search_transcripts(slide_data: Dict[int, List], keyword: str) -> List[int]:
    """
    Search for slides containing a keyword in their transcripts.
    
    Args:
        slide_data: The slide data dictionary
        keyword: Keyword to search for (case-insensitive)
        
    Returns:
        List of slide numbers containing the keyword
    """
    matching_slides = []
    keyword_lower = keyword.lower()
    
    for slide_num, (content, transcripts) in slide_data.items():
        full_transcript = " ".join(transcripts).lower()
        if keyword_lower in full_transcript:
            matching_slides.append(slide_num)
    
    return sorted(matching_slides)


def get_statistics(slide_data: Dict[int, List]) -> Dict:
    """
    Get statistics about the slide data.
    
    Args:
        slide_data: The slide data dictionary
        
    Returns:
        Dictionary with statistics
    """
    total_slides = len(slide_data)
    total_sentences = sum(len(transcripts) for _, transcripts in slide_data.values())
    empty_slides = sum(1 for _, transcripts in slide_data.values() if len(transcripts) == 0)
    
    if total_slides > 0:
        avg_sentences = total_sentences / total_slides
    else:
        avg_sentences = 0
    
    return {
        'total_slides': total_slides,
        'total_sentences': total_sentences,
        'avg_sentences_per_slide': avg_sentences,
        'slides_with_transcripts': total_slides - empty_slides,
        'empty_slides': empty_slides
    }


# Example usage
if __name__ == "__main__":
    # Example data structure
    example_data = {
        6: [
            "## Scale\n\nWhat is scale?",
            ["we're going to talk about scale", "scale means different sizes", "this is important"]
        ],
        8: [
            "## High / Low Scale",
            ["high scale refers to...", "low scale means..."]
        ]
    }
    
    # Usage examples
    print("Slide 6 content:", get_slide_content(example_data, 6))
    print("Slide 6 transcripts:", get_slide_transcripts(example_data, 6))
    print("Slide 6 full transcript:", get_full_transcript(example_data, 6))
    print("All slides:", get_all_slides(example_data))
    print("Statistics:", get_statistics(example_data))
