"""
Pearlite Phase Analyser - Web Application
Streamlit app with drawable canvas for pearlite phase quantification.
"""

import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

st.set_page_config(
    page_title="Pearlite Phase Analyser",
    page_icon="🔬",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {text-align:center;padding:1.5rem;background:linear-gradient(90deg,#1a1a2e,#16213e);color:white;border-radius:10px;margin-bottom:1rem;}
    .main-header h1 {font-size:2.2rem;margin:0;}
    .main-header p {opacity:0.9;margin-top:0.5rem;}
    .results-card {background:linear-gradient(135deg,#1a1a2e,#16213e);color:white;padding:1.5rem;border-radius:15px;text-align:center;margin:1rem 0;}
    .percentage-value {font-size:3rem;font-weight:bold;color:#4ade80;}
    .pixel-info {font-size:0.85rem;opacity:0.7;margin-top:0.5rem;}
</style>
""", unsafe_allow_html=True)

def create_pdf(orig_img, ann_img, pct, painted, total, info):
    buf = BytesIO()
    c = pdf_canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(w/2, h-40*mm, "Pearlite Phase Analyser Report")
    c.setStrokeColor(colors.HexColor("#4ade80"))
    c.setLineWidth(3)
    c.line(30*mm, h-45*mm, w-30*mm, h-45*mm)
    
    y = h - 60*mm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(25*mm, y, "Sample Information")
    c.setFont("Helvetica", 11)
    for lbl, val in [("Sample ID", info['sample_id']), ("Operator", info['operator']), 
                      ("Date", datetime.now().strftime('%Y-%m-%d %H:%M')), ("Notes", info['notes'])]:
        y -= 6*mm
        c.drawString(25*mm, y, f"{lbl}: {val}")
    
    y -= 15*mm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(25*mm, y, "Results")
    y -= 10*mm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(25*mm, y, "Pearlite Fraction:")
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor("#16a34a"))
    c.drawString(70*mm, y, f"{pct:.2f}%")
    c.setFillColor(colors.black)
    
    y -= 15*mm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(25*mm, y, "Micrographs")
    y -= 8*mm
    c.setFont("Helvetica", 10)
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
st.markdown('<div class="main-header"><h1>🔬 Pearlite Phase Analyser</h1><p>Upload image and paint pearlite regions</p></div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🎨 Tools")
    tool = st.radio("Tool", ["✏️ Brush", "🧹 Eraser"])
    stroke_color = "rgba(220,50,50,0.7)" if "Brush" in tool else "rgba(0,0,0,0)"
    brush_size = st.slider("Brush Size", 2, 50, 15)
    
    st.markdown("---")
    st.markdown("### 📝 Report Info")
    sample_id = st.text_input("Sample ID", "")
    operator = st.text_input("Operator", "")
    notes = st.text_area("Notes", "", height=70)

# Main
col1, col2 = st.columns([3, 1])

with col1:
    uploaded = st.file_uploader("📤 Upload Image", type=['png','jpg','jpeg','bmp','tiff'])
    
    if uploaded:
        img = Image.open(uploaded).convert('RGB')
        max_w, max_h = 700, 500
        scale = min(max_w/img.width, max_h/img.height, 1.0)
        cw, ch = int(img.width*scale), int(img.height*scale)
        display_img = img.resize((cw, ch), Image.Resampling.LANCZOS)
        
        canvas_result = st_canvas(
            fill_color="rgba(0,0,0,0)",
            stroke_width=brush_size,
            stroke_color=stroke_color,
            background_image=display_img,
            height=ch,
            width=cw,
            drawing_mode="freedraw",
            key="canvas",
        )
        
        pct, painted, total = calc_pct(canvas_result, (cw, ch))
    else:
        st.info("👆 Upload a microstructure image to begin")
        pct, painted, total = 0.0, 0, 0
        canvas_result = None
        display_img = None
        cw, ch = 0, 0

with col2:
    st.markdown(f'<div class="results-card"><h3>Pearlite Fraction</h3><div class="percentage-value">{pct:.2f}%</div><div class="pixel-info">Painted: {painted:,} px<br>Total: {total:,} px</div></div>', unsafe_allow_html=True)
    
    if uploaded and st.button("📄 Generate Report", type="primary", use_container_width=True):
        if canvas_result and canvas_result.image_data is not None:
            arr = canvas_result.image_data.astype(np.uint8)
            overlay = Image.fromarray(arr, 'RGBA')
            annotated = display_img.copy().convert('RGBA')
            annotated = Image.alpha_composite(annotated, overlay).convert('RGB')
        else:
            annotated = display_img
        
        info = {'sample_id': sample_id or 'N/A', 'operator': operator or 'N/A', 'notes': notes or 'N/A'}
        pdf = create_pdf(display_img, annotated, pct, painted, total, info)
        
        st.download_button("⬇️ Download PDF", pdf, f"pearlite_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf", "application/pdf", use_container_width=True)
