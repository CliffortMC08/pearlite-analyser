"""
Pearlite Phase Analyser - Web Application
"""

import streamlit as st
from PIL import Image
import numpy as np
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import base64

from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Pearlite Phase Analyser", page_icon="", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f5f5f5; }
    .main-header {
        text-align: center;
        padding: 20px;
        background-color: #2c3e50;
        color: white;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .main-header h1 { color: white !important; font-size: 2rem; margin: 0; }
    .main-header p { color: #ecf0f1 !important; margin-top: 5px; }
    .results-box {
        background-color: #2c3e50;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    .results-box h3 { color: #ecf0f1 !important; margin-bottom: 10px; }
    .big-percent { font-size: 3rem; font-weight: bold; color: #2ecc71 !important; }
    .pixel-text { color: #bdc3c7 !important; font-size: 0.9rem; margin-top: 10px; }
    .section-title { color: #2c3e50 !important; font-size: 1.1rem; font-weight: bold; margin: 10px 0; }
    div[data-testid="stSidebar"] { background-color: #ecf0f1; }
    div[data-testid="stSidebar"] h2, div[data-testid="stSidebar"] h3, 
    div[data-testid="stSidebar"] label { color: #2c3e50 !important; }
    
    .canvas-wrapper {
        position: relative;
        display: inline-block;
        margin: 0 auto;
    }
    .canvas-wrapper img {
        position: absolute;
        top: 0;
        left: 0;
        z-index: 1;
        pointer-events: none;
    }
    .canvas-wrapper canvas {
        position: relative;
        z-index: 2;
    }
</style>
""", unsafe_allow_html=True)

def image_to_data_url(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}"

def create_pdf(orig_img, ann_img, pct, painted, total, info):
    buf = BytesIO()
    c = pdf_canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.HexColor("#2c3e50"))
    c.drawCentredString(w/2, h-40*mm, "Pearlite Phase Analyser Report")
    c.setStrokeColor(colors.HexColor("#2ecc71"))
    c.setLineWidth(3)
    c.line(30*mm, h-45*mm, w-30*mm, h-45*mm)
    
    y = h - 60*mm
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#2c3e50"))
    c.drawString(25*mm, y, "Sample Information")
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.black)
    for lbl, val in [("Sample ID", info['sample_id']), ("Operator", info['operator']), 
                      ("Date", datetime.now().strftime('%Y-%m-%d %H:%M')), ("Notes", info['notes'])]:
        y -= 6*mm
        c.drawString(25*mm, y, f"{lbl}: {val}")
    
    y -= 15*mm
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#2c3e50"))
    c.drawString(25*mm, y, "Results")
    y -= 10*mm
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.black)
    c.drawString(25*mm, y, "Pearlite Fraction:")
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor("#2ecc71"))
    c.drawString(70*mm, y, f"{pct:.2f}%")
    
    y -= 15*mm
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#2c3e50"))
    c.drawString(25*mm, y, "Micrographs")
    y -= 8*mm
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.drawString(25*mm, y, "Original")
    c.drawString(110*mm, y, "Highlighted")
    y -= 65*mm
    
    for img, x in [(orig_img, 25*mm), (ann_img, 110*mm)]:
        b = BytesIO()
        img.save(b, format='PNG')
        b.seek(0)
        c.drawImage(ImageReader(b), x, y, width=75*mm, height=60*mm, preserveAspectRatio=True)
    
    c.save()
    buf.seek(0)
    return buf

def calc_pct(canvas_result, size):
    if canvas_result is None or canvas_result.image_data is None:
        return 0.0, 0, size[0]*size[1]
    alpha = canvas_result.image_data[:,:,3]
    painted = int(np.sum(alpha > 50))
    total = size[0] * size[1]
    return (painted/total)*100 if total > 0 else 0.0, painted, total

# Header
st.markdown('''
<div class="main-header">
    <h1>Pearlite Phase Analyser</h1>
    <p>Upload a microstructure image and paint over pearlite regions</p>
</div>
''', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## Drawing Tools")
    tool = st.radio("Select Tool", ["Brush (Red)", "Eraser"])
    stroke_color = "rgba(220,50,50,0.7)" if "Brush" in tool else "rgba(0,0,0,0)"
    brush_size = st.slider("Brush Size (px)", 2, 50, 15)
    
    st.markdown("---")
    st.markdown("## Report Information")
    sample_id = st.text_input("Sample ID", placeholder="e.g. STEEL-001")
    operator = st.text_input("Operator", placeholder="Your name")
    notes = st.text_area("Notes", placeholder="Observations...", height=80)
    
    st.markdown("---")
    st.markdown("## Instructions")
    st.markdown("""
    1. Upload microstructure image
    2. Paint pearlite regions in red
    3. Use eraser to fix mistakes
    4. Generate PDF report
    """)

# Main content
col1, col2 = st.columns([3, 1])

with col1:
    uploaded = st.file_uploader("Upload Microstructure Image", type=['png','jpg','jpeg','bmp','tiff'])
    
    if uploaded:
        img = Image.open(uploaded).convert('RGB')
        max_w, max_h = 650, 450
        scale = min(max_w/img.width, max_h/img.height, 1.0)
        cw, ch = int(img.width*scale), int(img.height*scale)
        display_img = img.resize((cw, ch), Image.Resampling.LANCZOS)
        
        # Convert image to base64 for CSS background
        img_data_url = image_to_data_url(display_img)
        
        st.markdown('<p class="section-title">Paint on the image below (red = pearlite)</p>', unsafe_allow_html=True)
        
        # Custom CSS to show image as canvas background
        st.markdown(f"""
        <style>
            canvas[class*="drawable"] {{
                background-image: url('{img_data_url}') !important;
                background-size: cover !important;
                background-repeat: no-repeat !important;
            }}
        </style>
        """, unsafe_allow_html=True)
        
        # Center the canvas
        _, col_center, _ = st.columns([1, 6, 1])
        with col_center:
            canvas_result = st_canvas(
                fill_color="rgba(0,0,0,0)",
                stroke_width=brush_size,
                stroke_color=stroke_color,
                background_color="rgba(255,255,255,0)",
                height=ch,
                width=cw,
                drawing_mode="freedraw",
                key="canvas",
            )
        
        pct, painted, total = calc_pct(canvas_result, (cw, ch))
        st.session_state['display_img'] = display_img
        st.session_state['canvas_result'] = canvas_result
    else:
        st.info("Upload a microstructure image to begin analysis")
        pct, painted, total = 0.0, 0, 0
        canvas_result = None
        display_img = None

with col2:
    st.markdown(f'''
    <div class="results-box">
        <h3>Pearlite Fraction</h3>
        <div class="big-percent">{pct:.2f}%</div>
        <div class="pixel-text">
            Painted: {painted:,} px<br>
            Total: {total:,} px
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if uploaded:
        if st.button("Generate PDF Report", type="primary", use_container_width=True):
            display_img = st.session_state.get('display_img')
            canvas_result = st.session_state.get('canvas_result')
            
            if display_img:
                if canvas_result and canvas_result.image_data is not None:
                    arr = canvas_result.image_data.astype(np.uint8)
                    overlay = Image.fromarray(arr, 'RGBA')
                    annotated = display_img.copy().convert('RGBA')
                    annotated = Image.alpha_composite(annotated, overlay).convert('RGB')
                else:
                    annotated = display_img
                
                info = {'sample_id': sample_id or 'N/A', 'operator': operator or 'N/A', 'notes': notes or 'N/A'}
                pdf = create_pdf(display_img, annotated, pct, painted, total, info)
                
                st.download_button(
                    "Download PDF Report", 
                    pdf, 
                    f"pearlite_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf", 
                    "application/pdf", 
                    use_container_width=True
                )
                st.success("Report generated!")
