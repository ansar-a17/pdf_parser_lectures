# Vision Model Setup Guide

This guide explains how to set up local vision models for analyzing diagrams and images in your PDFs.

## Overview

The system supports three vision model options:

1. **Moondream** (Recommended) - Lightweight, CPU-friendly, fast
2. **Ollama** - Easy setup, good quality, moderate speed
3. **Transformers (LLaVA)** - Most accurate, requires GPU, slower

All options are **completely free** and run **locally** on your machine.

---

## Option 1: Moondream (Recommended)

### Pros
✅ Works well on CPU (no GPU needed)  
✅ Small model size (~2GB)  
✅ Fast inference  
✅ Good for diagrams and charts

### Setup

1. **Install dependencies** (if you haven't already):
   ```powershell
   pip install transformers torch accelerate
   ```

2. **First run will download the model automatically**:
   ```powershell
   python pdf_ingestion.py your_file.pdf --vision-model moondream
   ```

   The model (~2GB) will download on first use and be cached locally.

### Usage

```powershell
# Single file
python pdf_ingestion.py document.pdf --vision-model moondream

# Directory
python process_mano_pdfs.py  # Moondream is the default
```

---

## Option 2: Ollama

### Pros
✅ Easy installation  
✅ Good quality results  
✅ Can use different models easily  
✅ Supports GPU if available

### Setup

1. **Install Ollama**:
   - Download from: https://ollama.ai
   - Run installer (very quick)

2. **Pull the vision model**:
   ```powershell
   ollama pull llava
   ```

3. **Verify it's working**:
   ```powershell
   ollama list
   ```
   You should see `llava` in the list.

### Usage

```powershell
python pdf_ingestion.py document.pdf --vision-model ollama
```

---

## Option 3: Transformers (LLaVA)

### Pros
✅ Most accurate descriptions  
✅ Best for complex diagrams  
✅ Good technical understanding

### Cons
⚠️ Requires GPU with ~8GB VRAM  
⚠️ Larger download (~13GB)  
⚠️ Slower inference

### Setup

1. **Install dependencies**:
   ```powershell
   pip install transformers torch accelerate
   ```

2. **Ensure you have a CUDA-capable GPU**:
   ```powershell
   python -c "import torch; print(torch.cuda.is_available())"
   ```
   Should print `True`

### Usage

```powershell
python pdf_ingestion.py document.pdf --vision-model transformers
```

---

## Quick Start

### For Most Users (CPU-only)

```powershell
# Install requirements
pip install -r requirements.txt

# Process your PDFs (Moondream will download automatically)
python process_mano_pdfs.py
```

### Disable Image Analysis

If you don't want image analysis:

```powershell
python pdf_ingestion.py document.pdf --no-images
```

Or edit [process_mano_pdfs.py](process_mano_pdfs.py):
```python
analyze_images = False  # Change from True to False
```

---

## What Gets Analyzed?

The system:
1. **Extracts all images** from PDFs using PyMuPDF
2. **Filters small images** (< 100x100px) - likely decorations/logos
3. **Analyzes each image** with the vision model
4. **Generates detailed descriptions** focusing on:
   - Structure and layout
   - Labels and text within the image
   - Relationships between elements
   - Key information and data
5. **Adds descriptions** to the markdown output

## Example Output

In the generated markdown file:

```markdown
## Image Analysis

*Automatically generated descriptions of diagrams and images found in the document.*

### Image 1 (Page 3)

**Size:** 800x600

**Description:**
This diagram shows a flowchart depicting the hormone regulation system. 
The chart contains three main components: the hypothalamus at the top, 
connected by arrows to the pituitary gland in the middle, which then 
connects to target organs at the bottom. Each connection is labeled with 
hormone names and includes feedback loops indicated by dotted lines...

### Image 2 (Page 5)

**Size:** 1024x768

**Description:**
A detailed bar chart comparing hormone levels across different time periods...
```

---

## Troubleshooting

### "Out of memory" error

**Solution:** Use Moondream (works on CPU) or reduce batch size:
```python
# In pdf_ingestion.py, add to vision model initialization:
torch_dtype=torch.float16
```

### Slow processing

**Solutions:**
1. Use Moondream (fastest)
2. Skip small images (already implemented)
3. Process files one at a time
4. Use GPU if available

### Model download fails

**Solutions:**
1. Check internet connection
2. Try Ollama instead (better download management)
3. Manually download models:
   ```powershell
   python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('vikhyatk/moondream2')"
   ```

### Poor quality descriptions

**Solutions:**
1. Try a different model (Ollama or Transformers)
2. Increase image DPI:
   ```powershell
   python pdf_ingestion.py document.pdf --dpi 400
   ```

---

## Performance Comparison

| Model | Speed | Quality | GPU Required | Size |
|-------|-------|---------|--------------|------|
| Moondream | ⚡⚡⚡ Fast | ⭐⭐⭐ Good | ❌ No | 2GB |
| Ollama | ⚡⚡ Medium | ⭐⭐⭐⭐ Very Good | ❌ No (faster with GPU) | 4GB |
| Transformers | ⚡ Slow | ⭐⭐⭐⭐⭐ Excellent | ✅ Yes | 13GB |

---

## Cost

All models are **100% free** and run **locally**. No API keys, no subscriptions, no usage limits.

---

## Advanced: Switching Models

You can easily switch between models:

```python
from pdf_ingestion import PDFIngestionPipeline

# Use Moondream
pipeline = PDFIngestionPipeline(analyze_images=True, vision_model="moondream")
pipeline.process_pdf("document.pdf")

# Use Ollama
pipeline = PDFIngestionPipeline(analyze_images=True, vision_model="ollama")
pipeline.process_pdf("document.pdf")
```

Or via command line:

```powershell
python pdf_ingestion.py doc.pdf --vision-model moondream
python pdf_ingestion.py doc.pdf --vision-model ollama
python pdf_ingestion.py doc.pdf --vision-model transformers
```
