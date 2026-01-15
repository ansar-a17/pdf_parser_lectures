import os
import io
from pathlib import Path
from typing import Optional, Dict
from docling.document_converter import DocumentConverter
from PIL import Image
import fitz


class PDFIngestionPipeline:
    def __init__(self, dpi: int = 300, 
                 analyze_images: bool = True, vision_model: str = "moondream"):
        self.dpi = dpi
        self.converter = DocumentConverter()
        self.analyze_images = analyze_images
        self.vision_model_type = vision_model
        self.vision_model = None
        self.vision_processor = None
        self.device = None
        
        if self.analyze_images:
            self._initialize_vision_model()
        
    def process_pdf(self, pdf_path: str, output_path: Optional[str] = None) -> str:
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        print(f"Processing: {pdf_path.name}")
        
        print("  [1/3] Parsing with Docling...")
        result = self.converter.convert(str(pdf_path))
        doc = result.document
        
        image_descriptions = {}
        if self.analyze_images:
            print("  [2/3] Analyzing images with vision model...")
            image_descriptions = self._analyze_images(pdf_path)
            if image_descriptions:
                print(f"    Analyzed {len(image_descriptions)} image(s)")
        
        print("  [3/3] Exporting to Markdown...")
        markdown_content = doc.export_to_markdown()
        
        if image_descriptions:
            markdown_content = self._inject_image_descriptions(markdown_content, image_descriptions)
        
        if output_path is None:
            output_path = pdf_path.parent / f"{pdf_path.stem}_clean.md"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        print(f"✓ Complete: {output_path}")
        return str(output_path)
    
    def _initialize_vision_model(self):
        print("  [Init] Loading vision model...")
        
        try:
            if self.vision_model_type == "moondream":
                import torch
                from transformers import AutoModelForCausalLM, AutoTokenizer
                
                model_id = "vikhyatk/moondream2"
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self.device = device
                print(f"    Loading {model_id} on {device.upper()}...")
                
                self.vision_processor = AutoTokenizer.from_pretrained(model_id)
                self.vision_model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    trust_remote_code=True,
                    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                    device_map="auto" if device == "cuda" else None
                ).to(device)
                
                print(f"    ✓ Moondream model loaded on {device.upper()}")
            
            elif self.vision_model_type == "ollama":
                import subprocess
                try:
                    result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
                    if "llava" not in result.stdout:
                        print("    Installing llava model via Ollama...")
                        subprocess.run(["ollama", "pull", "llava"], check=True)
                    print("    ✓ Ollama llava ready")
                except FileNotFoundError:
                    print("    ⚠ Ollama not found. Install from https://ollama.ai")
                    print("    Falling back to transformers...")
                    self.vision_model_type = "moondream"
                    self._initialize_vision_model()
                    return
            
            elif self.vision_model_type == "transformers":
                from transformers import AutoProcessor, LlavaForConditionalGeneration
                model_id = "llava-hf/llava-1.5-7b-hf"
                print(f"    Loading {model_id} (this may take a while)...")
                self.vision_processor = AutoProcessor.from_pretrained(model_id)
                self.vision_model = LlavaForConditionalGeneration.from_pretrained(
                    model_id,
                    device_map="auto"
                )
                print("    ✓ LLaVA model loaded")
        
        except Exception as e:
            print(f"    ⚠ Could not load vision model: {e}")
            print("    Image analysis will be skipped")
            self.analyze_images = False
    
    def _analyze_images(self, pdf_path: Path) -> Dict[int, str]:
        if not self.analyze_images or self.vision_model is None:
            return {}
        
        descriptions = {}
        
        try:
            pdf_document = fitz.open(str(pdf_path))
            
            img_index = 0
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                images = page.get_images()
                
                for img in images:
                    img_index += 1
                    try:
                        xref = img[0]
                        base_image = pdf_document.extract_image(xref)
                        image_bytes = base_image["image"]
                        
                        image = Image.open(io.BytesIO(image_bytes))
                        
                        if image.width < 100 or image.height < 100:
                            continue
                        
                        description = self._describe_image(image, img_index)
                        if description:
                            descriptions[img_index] = {
                                'description': description,
                                'page': page_num + 1,
                                'size': f"{image.width}x{image.height}"
                            }
                            print(f"      Image {img_index} (page {page_num + 1}): Analyzed")
                    
                    except Exception as e:
                        print(f"      ⚠ Error analyzing image {img_index}: {e}")
                        continue
            
            pdf_document.close()
        
        except Exception as e:
            print(f"    ⚠ Error extracting images: {e}")
        
        return descriptions
    
    def _describe_image(self, image: Image.Image, img_index: int) -> Optional[str]:
        try:
            if self.vision_model_type == "moondream":
                enc_image = self.vision_model.encode_image(image)
                prompt = "Describe this diagram or image in detail. Focus on the structure, labels, relationships, and key information presented."
                description = self.vision_model.answer_question(enc_image, prompt, self.vision_processor)
                return description
            
            elif self.vision_model_type == "ollama":
                import subprocess
                import json
                import tempfile
                
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    image.save(tmp.name)
                    tmp_path = tmp.name
                
                try:
                    result = subprocess.run(
                        ["ollama", "run", "llava", 
                         "Describe this diagram or image in detail. Focus on the structure, labels, relationships, and key information presented.",
                         tmp_path],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    return result.stdout.strip()
                finally:
                    os.unlink(tmp_path)
            
            elif self.vision_model_type == "transformers":
                prompt = "USER: <image>\nDescribe this diagram or image in detail. Focus on the structure, labels, relationships, and key information presented.\nASSISTANT:"
                inputs = self.vision_processor(text=prompt, images=image, return_tensors="pt")
                
                import torch
                with torch.no_grad():
                    output = self.vision_model.generate(**inputs, max_new_tokens=200)
                description = self.vision_processor.decode(output[0], skip_special_tokens=True)
                
                if "ASSISTANT:" in description:
                    description = description.split("ASSISTANT:")[-1].strip()
                
                return description
        
        except Exception as e:
            print(f"      ⚠ Error describing image: {e}")
            return None
    
    def _inject_image_descriptions(self, markdown: str, descriptions: Dict[int, str]) -> str:
        if descriptions:
            markdown += "\n\n---\n\n## Image Analysis\n\n"
            markdown += "*Automatically generated descriptions of diagrams and images found in the document.*\n\n"
            
            for img_idx, info in sorted(descriptions.items()):
                markdown += f"### Image {img_idx} (Page {info['page']})\n\n"
                markdown += f"**Size:** {info['size']}\n\n"
                markdown += f"**Description:**\n{info['description']}\n\n"
        
        return markdown


def process_single_pdf(pdf_path: str, output_dir: Optional[str] = None, 
                      dpi: int = 300,
                      analyze_images: bool = True, vision_model: str = "moondream"):
    pipeline = PDFIngestionPipeline(
        dpi=dpi,
        analyze_images=analyze_images,
        vision_model=vision_model
    )
    
    if output_dir:
        pdf_name = Path(pdf_path).stem
        output_path = Path(output_dir) / f"{pdf_name}_clean.md"
    else:
        output_path = None
    
    return pipeline.process_pdf(pdf_path, output_path)


def process_directory(input_dir: str, output_dir: str, 
                     dpi: int = 300,
                     recursive: bool = True, analyze_images: bool = True,
                     vision_model: str = "moondream"):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if recursive:
        pdf_files = list(input_path.rglob("*.pdf"))
    else:
        pdf_files = list(input_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return []
    
    print(f"Found {len(pdf_files)} PDF file(s)")
    print("=" * 60)
    
    pipeline = PDFIngestionPipeline(
        dpi=dpi,
        analyze_images=analyze_images,
        vision_model=vision_model
    )
    
    output_files = []
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] {pdf_file.name}")
        
        try:
            relative_path = pdf_file.relative_to(input_path)
            output_file = output_path / relative_path.parent / f"{pdf_file.stem}_clean.md"
            
            result = pipeline.process_pdf(str(pdf_file), str(output_file))
            output_files.append(result)
            
        except Exception as e:
            print(f"✗ Error processing {pdf_file.name}: {e}")
    
    print("\n" + "=" * 60)
    print(f"✓ Processed {len(output_files)}/{len(pdf_files)} files successfully")
    
    return output_files
