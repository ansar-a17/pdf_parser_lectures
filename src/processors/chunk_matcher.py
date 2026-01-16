"""
Chunk Matcher - Intelligently match transcript sentences to slides
using cosine similarity and build coherent chunks.
"""

from typing import Dict, List, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class TranscriptSlideChunker:
    """Match transcript sentences to slides and build coherent chunks."""
    
    def __init__(self, model):
        """
        Initialize the chunker with an embedding model.
        
        Args:
            model: SentenceTransformer model for generating embeddings
        """
        self.model = model
        self.similarity_threshold = 0.75
    
    def build_chunks(
        self, 
        transcript_sentences: Dict[str, np.ndarray],  # {sentence: embedding}
        slide_pages: Dict[int, str],  # {page_num: content}
        similarity_threshold: float = 0.75
    ) -> List[Dict]:
        """
        Match transcript sentences to slides and build chunks.
        
        Args:
            transcript_sentences: Dictionary of transcript sentences with embeddings
            slide_pages: Dictionary of slide page numbers with content
            similarity_threshold: Minimum cosine similarity to match (default 0.75)
        
        Returns:
            List of chunks with matched content
        """
        self.similarity_threshold = similarity_threshold
        
        print(f"Building chunks with threshold: {similarity_threshold}")
        print(f"Total transcript sentences: {len(transcript_sentences)}")
        print(f"Total slide pages: {len(slide_pages)}")
        
        # Step 1: Generate embeddings for slide content
        slide_embeddings = self._generate_slide_embeddings(slide_pages)
        
        # Step 2: Match each transcript sentence to the best slide
        chunks = self._match_and_chunk(
            transcript_sentences, 
            slide_pages,
            slide_embeddings
        )
        
        print(f"Created {len(chunks)} chunks")
        return chunks
    
    def build_chunks_with_windows(
        self,
        transcript_sentences: Dict[str, np.ndarray],
        slide_pages: Dict[int, str],
        window_size: int = 5,
        similarity_threshold: float = 0.60
    ) -> List[Dict]:
        """
        Match windows of transcript sentences to slides for better context.
        
        Args:
            transcript_sentences: Dictionary of transcript sentences with embeddings
            slide_pages: Dictionary of slide page numbers with content
            window_size: Number of consecutive sentences per window
            similarity_threshold: Minimum cosine similarity to match
        
        Returns:
            List of chunks with matched content
        """
        self.similarity_threshold = similarity_threshold
        
        print(f"\nBuilding chunks with WINDOWED approach")
        print(f"  Window size: {window_size} sentences")
        print(f"  Similarity threshold: {similarity_threshold}")
        print(f"  Total transcript sentences: {len(transcript_sentences)}")
        print(f"  Total slide pages: {len(slide_pages)}")
        
        # Generate slide embeddings
        slide_embeddings = self._generate_slide_embeddings(slide_pages)
        
        # Create windows from sentences
        sentence_list = list(transcript_sentences.keys())
        chunks = []
        current_chunk = None
        
        # Process sentences in sliding windows
        for i in range(0, len(sentence_list), window_size // 2):  # 50% overlap
            window_sentences = sentence_list[i:i + window_size]
            if not window_sentences:
                continue
            
            # Combine window sentences into one text
            window_text = " ".join(window_sentences)
            
            # Generate embedding for the window
            window_embedding = self.model.encode(window_text)
            
            # Find best matching slide
            best_match = self._find_best_slide_match(window_embedding, slide_embeddings)
            
            if best_match:
                page_num, similarity = best_match
                
                if i < 20:  # Show first few matches
                    print(f"  Window {i//window_size + 1}: matched to page {page_num} (sim: {similarity:.3f})")
                
                if similarity >= similarity_threshold:
                    # Check if we should start a new chunk or extend current
                    if current_chunk is None or current_chunk['page_num'] != page_num:
                        # Save previous chunk
                        if current_chunk:
                            chunks.append(current_chunk)
                        
                        # Start new chunk
                        current_chunk = {
                            'page_num': page_num,
                            'slide_content': slide_pages[page_num],
                            'transcript_sentences': window_sentences.copy(),
                            'similarities': [similarity] * len(window_sentences),
                            'window_similarity': similarity
                        }
                    else:
                        # Extend current chunk (avoiding duplicates from overlap)
                        for sent in window_sentences:
                            if sent not in current_chunk['transcript_sentences']:
                                current_chunk['transcript_sentences'].append(sent)
                                current_chunk['similarities'].append(similarity)
                else:
                    # Low similarity - save current chunk and mark as unmatched
                    if current_chunk:
                        chunks.append(current_chunk)
                        current_chunk = None
        
        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        print(f"\nCreated {len(chunks)} chunks using windowed approach")
        return chunks
    
    def _generate_slide_embeddings(
        self, 
        slide_pages: Dict[int, str]
    ) -> Dict[int, np.ndarray]:
        """Generate embeddings for each slide's content."""
        slide_embeddings = {}
        
        print("\nGenerating slide embeddings...")
        for page_num, content in slide_pages.items():
            # Clean and prepare slide content
            cleaned_content = content.strip()
            if cleaned_content:
                embedding = self.model.encode(cleaned_content)
                slide_embeddings[page_num] = embedding
            else:
                # Empty slide - create zero embedding
                slide_embeddings[page_num] = np.zeros(self.model.get_sentence_embedding_dimension())
        
        print(f"Generated embeddings for {len(slide_embeddings)} slides")
        return slide_embeddings
    
    def _match_and_chunk(
        self,
        transcript_sentences: Dict[str, np.ndarray],
        slide_pages: Dict[int, str],
        slide_embeddings: Dict[int, np.ndarray]
    ) -> List[Dict]:
        """Match sentences to slides and build chunks."""
        chunks = []
        current_chunk = None
        
        print("\nMatching sentences to slides...")
        for i, (sentence, sentence_embedding) in enumerate(transcript_sentences.items(), 1):
            # Find best matching slide
            best_match = self._find_best_slide_match(
                sentence_embedding, 
                slide_embeddings
            )
            
            if best_match:
                page_num, similarity = best_match
                
                if i <= 5:  # Show first few matches
                    print(f"  Sentence {i}: matched to page {page_num} (sim: {similarity:.3f})")
                
                # Check if similarity meets threshold
                if similarity >= self.similarity_threshold:
                    # Start new chunk or continue current one
                    if current_chunk is None or current_chunk['page_num'] != page_num:
                        # Save previous chunk if exists
                        if current_chunk:
                            chunks.append(current_chunk)
                        
                        # Start new chunk
                        current_chunk = {
                            'page_num': page_num,
                            'slide_content': slide_pages[page_num],
                            'transcript_sentences': [sentence],
                            'similarities': [similarity]
                        }
                    else:
                        # Add to current chunk (same slide)
                        current_chunk['transcript_sentences'].append(sentence)
                        current_chunk['similarities'].append(similarity)
                else:
                    # Similarity too low - unmatched sentence
                    if current_chunk:
                        chunks.append(current_chunk)
                        current_chunk = None
                    
                    # Add as unmatched chunk
                    chunks.append({
                        'page_num': None,
                        'slide_content': None,
                        'transcript_sentences': [sentence],
                        'similarities': [similarity],
                        'note': f'Low similarity ({similarity:.3f}) - no slide match'
                    })
        
        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _find_best_slide_match(
        self,
        sentence_embedding: np.ndarray,
        slide_embeddings: Dict[int, np.ndarray]
    ) -> Tuple[int, float]:
        """Find the slide with highest cosine similarity to the sentence."""
        best_page = None
        best_similarity = -1.0
        
        sentence_embedding = sentence_embedding.reshape(1, -1)
        
        for page_num, slide_embedding in slide_embeddings.items():
            slide_embedding = slide_embedding.reshape(1, -1)
            similarity = cosine_similarity(sentence_embedding, slide_embedding)[0][0]
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_page = page_num
        
        return (best_page, best_similarity) if best_page else None
    
    def get_chunk_summary(self, chunks: List[Dict]) -> str:
        """Get a readable summary of chunks."""
        summary = []
        summary.append(f"\n{'='*80}")
        summary.append(f"CHUNK SUMMARY")
        summary.append(f"{'='*80}")
        summary.append(f"Total Chunks: {len(chunks)}\n")
        
        matched_chunks = [c for c in chunks if c['page_num'] is not None]
        unmatched_chunks = [c for c in chunks if c['page_num'] is None]
        
        summary.append(f"Matched Chunks: {len(matched_chunks)}")
        summary.append(f"Unmatched Chunks: {len(unmatched_chunks)}\n")
        
        for i, chunk in enumerate(chunks, 1):
            summary.append(f"--- Chunk {i} ---")
            summary.append(f"Slide Page: {chunk['page_num'] if chunk['page_num'] else 'No Match'}")
            summary.append(f"Sentences: {len(chunk['transcript_sentences'])}")
            
            if chunk['similarities']:
                avg_sim = np.mean(chunk['similarities'])
                min_sim = np.min(chunk['similarities'])
                max_sim = np.max(chunk['similarities'])
                summary.append(f"Similarity - Avg: {avg_sim:.3f}, Min: {min_sim:.3f}, Max: {max_sim:.3f}")
            
            # Show first sentence preview
            first_sentence = chunk['transcript_sentences'][0]
            preview = first_sentence[:80] + "..." if len(first_sentence) > 80 else first_sentence
            summary.append(f"First Sentence: {preview}")
            
            if 'note' in chunk:
                summary.append(f"Note: {chunk['note']}")
            
            summary.append("")
        
        return "\n".join(summary)
    
    def export_chunks_to_text(self, chunks: List[Dict], output_file: str):
        """Export chunks to a readable text file."""
        print(f"\nExporting chunks to {output_file}...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"{'='*80}\n")
            f.write(f"TRANSCRIPT-SLIDE MATCHING RESULTS\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"Total Chunks: {len(chunks)}\n")
            f.write(f"Similarity Threshold: {self.similarity_threshold}\n\n")
            
            for i, chunk in enumerate(chunks, 1):
                f.write(f"\n{'='*80}\n")
                f.write(f"CHUNK {i}\n")
                f.write(f"{'='*80}\n\n")
                
                f.write(f"SLIDE PAGE: {chunk['page_num'] if chunk['page_num'] else 'NO MATCH'}\n")
                
                if chunk['similarities']:
                    avg_sim = np.mean(chunk['similarities'])
                    f.write(f"Average Similarity: {avg_sim:.3f}\n")
                
                if 'note' in chunk:
                    f.write(f"Note: {chunk['note']}\n")
                
                f.write("\n")
                
                if chunk['slide_content']:
                    f.write("--- SLIDE CONTENT ---\n")
                    f.write(f"{chunk['slide_content']}\n\n")
                
                f.write("--- TRANSCRIPT ---\n")
                for j, (sentence, sim) in enumerate(zip(
                    chunk['transcript_sentences'], 
                    chunk['similarities']
                ), 1):
                    f.write(f"{j}. [Similarity: {sim:.3f}] {sentence}\n")
                
                f.write("\n")
        
        print(f"Chunks exported successfully!")
    
    def get_statistics(self, chunks: List[Dict]) -> Dict:
        """Get detailed statistics about the chunks."""
        stats = {
            'total_chunks': len(chunks),
            'matched_chunks': len([c for c in chunks if c['page_num'] is not None]),
            'unmatched_chunks': len([c for c in chunks if c['page_num'] is None]),
            'total_sentences': sum(len(c['transcript_sentences']) for c in chunks),
            'avg_sentences_per_chunk': 0,
            'avg_similarity': 0,
            'slides_with_matches': set()
        }
        
        if chunks:
            stats['avg_sentences_per_chunk'] = stats['total_sentences'] / len(chunks)
            
            all_similarities = []
            for chunk in chunks:
                all_similarities.extend(chunk['similarities'])
                if chunk['page_num'] is not None:
                    stats['slides_with_matches'].add(chunk['page_num'])
            
            if all_similarities:
                stats['avg_similarity'] = np.mean(all_similarities)
            
            stats['unique_slides_matched'] = len(stats['slides_with_matches'])
        
        return stats
    
    def build_simple_dict(self, chunks: List[Dict], slide_pages: Dict[int, str] = None) -> Dict[int, List]:
        """
        Build a simple dictionary structure: {slide_number: [slide_content, [transcripts]]}.
        Initializes ALL slides with empty transcript lists to ensure consistency.
        
        Args:
            chunks: List of chunks from build_chunks_with_windows()
            slide_pages: Dictionary of all slide pages {page_num: content}. 
                         If provided, initializes all slides with empty lists.
        
        Returns:
            Dictionary with structure: {slide_num: [slide_content, [transcript_sentences]]}
        """
        slide_data = {}
        
        # Initialize ALL slides if slide_pages is provided
        if slide_pages:
            for page_num, content in slide_pages.items():
                slide_data[page_num] = [content, []]
        
        # Fill in matched transcripts
        for chunk in chunks:
            slide_num = chunk.get('page_num')
            
            # Only process matched chunks
            if slide_num is not None:
                if slide_num not in slide_data:
                    # Initialize if not already done (fallback for when slide_pages not provided)
                    slide_data[slide_num] = [
                        chunk['slide_content'],
                        []
                    ]
                
                # Add transcript sentences (avoid duplicates from overlapping windows)
                for sentence in chunk['transcript_sentences']:
                    if sentence not in slide_data[slide_num][1]:
                        slide_data[slide_num][1].append(sentence)
        
        return slide_data


def create_chunks_from_data(
    transcript_dict: Dict[str, np.ndarray],
    pages_dict: Dict[int, str],
    model,
    threshold: float = 0.75
) -> List[Dict]:
    """
    Convenience function to create chunks.
    
    Args:
        transcript_dict: {sentence: embedding}
        pages_dict: {page_num: content}
        model: SentenceTransformer model
        threshold: Similarity threshold (default 0.75)
    
    Returns:
        List of matched chunks
    """
    chunker = TranscriptSlideChunker(model)
    chunks = chunker.build_chunks(transcript_dict, pages_dict, threshold)
    return chunks
