# 🔬 Pearlite Phase Analyser

A web-based tool for quantifying pearlite phases in steel microstructure images.

## Features

- **Image Upload**: Support for PNG, JPG, JPEG, BMP, TIFF formats
- **Digital Painting**: Highlight pearlite regions with a red brush
- **Eraser Tool**: Fix mistakes easily
- **Adjustable Brush Size**: Flexible brush sizes
- **Real-time Calculation**: Automatic pearlite percentage calculation
- **PDF Reports**: Generate professional lab reports

## Live Demo

🌐 [Hugging Face Spaces](https://huggingface.co/spaces/CliffortMC08/pearlite-analyser)

## Local Development

### Prerequisites
- Python 3.9+

### Installation

```bash
# Clone the repository
git clone https://github.com/CliffortMC08/pearlite-analyser.git
cd pearlite-analyser

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

The app will open at `http://localhost:7860`

## Deployment

### Hugging Face Spaces (Recommended)
1. Create a new Space on [Hugging Face](https://huggingface.co/spaces)
2. Select "Gradio" as the SDK
3. Upload or connect your GitHub repo
4. The app will deploy automatically

## How to Use

1. **Upload** a microstructure image
2. **Paint** over pearlite regions with the red brush
3. **Use Eraser** to fix any mistakes
4. **Click Calculate** to update the percentage
5. **Generate Report** - creates a PDF with your analysis

## Tech Stack

- **Gradio** - Web framework with canvas support
- **Pillow** - Image processing
- **ReportLab** - PDF generation
- **NumPy** - Pixel calculations

## License

MIT License
