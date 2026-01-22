# 🔬 Pearlite Phase Analyser

A web-based tool for quantifying pearlite phases in steel microstructure images.

## Features

- **Image Upload**: Support for PNG, JPG, JPEG, BMP, TIFF formats
- **Digital Painting**: Highlight pearlite regions with a red brush
- **Eraser Tool**: Fix mistakes easily
- **Adjustable Brush Size**: 2px to 50px
- **Real-time Calculation**: Instant pearlite percentage calculation
- **PDF Reports**: Generate professional lab reports

## Live Demo

🌐 [https://pearlite-analyser.streamlit.app](https://pearlite-analyser.streamlit.app)

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
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Deployment on Streamlit Cloud

1. Push this repository to GitHub
2. Go to [Streamlit Cloud](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app" and select this repository
5. Set main file path to `app.py`
6. Click "Deploy"

## How to Use

1. **Upload** a microstructure image
2. **Select Brush** tool from the sidebar
3. **Paint** over pearlite regions (dark areas)
4. **Use Eraser** to fix any mistakes
5. **View Results** - percentage updates in real-time
6. **Generate Report** - creates a PDF with your analysis

## Tech Stack

- **Streamlit** - Web framework
- **streamlit-drawable-canvas** - Drawing functionality
- **Pillow** - Image processing
- **ReportLab** - PDF generation
- **NumPy** - Pixel calculations

## License

MIT License
