"""
Page-by-Page Content Extractor for Docling Documents

This module provides functionality to extract content from PDF files
organized by page number using Docling's document parsing capabilities.
"""

from typing import Dict
from docling.document_converter import DocumentConverter


class PageContentExtractor:
    """Extract and organize PDF content by page number."""
    
    def __init__(self):
        """Initialize the document converter."""
        self.converter = DocumentConverter()
    
    def extract_pages(self, pdf_path: str) -> Dict[int, str]:
        """
        Extract content from a PDF file organized by page number.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary mapping page numbers to page content as markdown strings
            Example: {1: "Page 1 content...", 2: "Page 2 content...", ...}
        """
        # Convert the PDF document
        result = self.converter.convert(pdf_path)
        doc = result.document
        
        # Initialize page content dictionary
        page_contents = {}
        
        # Iterate through all pages in the document
        # doc.pages is a Dict[int, PageItem] where keys are page numbers
        for page_no in sorted(doc.pages.keys()):
            # Export content for this specific page using page_no parameter
            page_markdown = doc.export_to_markdown(page_no=page_no)
            page_contents[page_no] = page_markdown
        
        return page_contents
    
    def extract_pages_detailed(self, pdf_path: str) -> Dict[int, Dict]:
        """
        Extract detailed content from a PDF file organized by page number.
        
        This version provides more detailed information including page metadata,
        text items, tables, and pictures for each page.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary mapping page numbers to detailed page information
            Example: {
                1: {
                    'markdown': "Page content...",
                    'size': {'width': 612.0, 'height': 792.0},
                    'has_image': True,
                    'items': ['text1', 'text2', ...]
                },
                ...
            }
        """
        # Convert the PDF document
        result = self.converter.convert(pdf_path)
        doc = result.document
        
        # Initialize page content dictionary
        page_contents = {}
        
        # Iterate through all pages
        for page_no, page_item in doc.pages.items():
            page_info = {
                'page_number': page_no,
                'markdown': doc.export_to_markdown(page_no=page_no),
                'size': {
                    'width': page_item.size.width,
                    'height': page_item.size.height
                },
                'has_image': page_item.image is not None,
            }
            
            # Collect text items for this page
            page_texts = []
            for text_item in doc.texts:
                # Check if text item belongs to this page
                if text_item.prov:
                    for prov in text_item.prov:
                        if prov.page_no == page_no:
                            page_texts.append(text_item.text)
                            break
            
            page_info['text_items'] = page_texts
            page_info['text_count'] = len(page_texts)
            
            # Count tables on this page
            page_tables = []
            for table in doc.tables:
                if table.prov:
                    for prov in table.prov:
                        if prov.page_no == page_no:
                            page_tables.append({
                                'rows': table.data.num_rows,
                                'cols': table.data.num_cols
                            })
                            break
            
            page_info['tables'] = page_tables
            page_info['table_count'] = len(page_tables)
            
            # Count pictures on this page
            page_pictures = []
            for picture in doc.pictures:
                if picture.prov:
                    for prov in picture.prov:
                        if prov.page_no == page_no:
                            page_pictures.append({
                                'label': picture.label.value if hasattr(picture.label, 'value') else str(picture.label)
                            })
                            break
            
            page_info['pictures'] = page_pictures
            page_info['picture_count'] = len(page_pictures)
            
            page_contents[page_no] = page_info
        
        return page_contents
    
    def get_page_count(self, pdf_path: str) -> int:
        """
        Get the total number of pages in a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Number of pages in the document
        """
        result = self.converter.convert(pdf_path)
        doc = result.document
        return len(doc.pages)