import json
import ollama
from pathlib import Path


def extract_key_terms(slide_num, slide_data):
    """Extract key terms from slide content and transcripts using Mistral 7B."""
    
    # Prepare the content
    slide_content = slide_data['slide_content']
    transcripts = ' '.join(slide_data['transcripts'])
    
    prompt = f"""Analyze this lecture slide and extract the most important technical terms, concepts, and keywords.

Slide Content:
{slide_content}

Transcripts:
{transcripts}

Extract 2-5 key technical terms, concepts, or important phrases from this content.
Return ONLY a valid JSON array of strings, nothing else.
Example format: ["scale space", "Laplacian of Gaussian", "blob detection", "image derivatives", "Gaussian filter"]

Key terms:"""

    try:
        response = ollama.generate(
            model='mistral:7b',
            prompt=prompt,
            options={
                'temperature': 0.3,  # Lower for more consistent extraction
                'num_predict': 150    # Limit output length
            }
        )
        
        # Extract the response text
        result = response['response'].strip()
        
        # Try to parse as JSON
        try:
            key_terms = json.loads(result)
            return key_terms
        except json.JSONDecodeError:
            # If not valid JSON, try to extract terms from the text
            print(f"Warning: Could not parse JSON for slide {slide_num}. Raw response: {result}")
            return []
            
    except Exception as e:
        print(f"Error processing slide {slide_num}: {e}")
        return []


def process_all_slides(input_file='slide_data.json', output_file='slide_data_with_terms.json'):
    """Process all slides and extract key terms."""
    
    # Load the slide data
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Processing {len(data)} slides...")
    print("=" * 60)
    
    # Process each slide
    for slide_num, slide_info in data.items():
        if slide_info['transcript_count'] > 0:
            print(f"\nProcessing Slide {slide_num}...")
            
            key_terms = extract_key_terms(slide_num, slide_info)
            
            # Add key terms to the slide data
            slide_info['key_terms'] = key_terms
            
            print(f"Slide {slide_num} key terms: {key_terms}")
        else:
            print(f"\nSkipping Slide {slide_num} (no transcripts)")
            slide_info['key_terms'] = []
    
    # Save the updated data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print(f"Processing complete! Results saved to {output_file}")