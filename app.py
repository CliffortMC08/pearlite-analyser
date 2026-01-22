"""
Pearlite Phase Analyser - Web Application
Canvas overlays on image like glass.
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
import base64

st.set_page_config(page_title="Pearlite Phase Analyser", layout="wide")

def image_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

def create_pdf_report(original_img, annotated_img, percentage, painted_px, total_px, sample_id, operator, notes):
    buffer = BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(colors.HexColor("#2c3e50"))
    c.drawCentredString(width/2, height - 35*mm, "Pearlite Phase Analyser Report")
    
    c.setStrokeColor(colors.HexColor("#27ae60"))
    c.setLineWidth(2)
    c.line(25*mm, height - 40*mm, width - 25*mm, height - 40*mm)
    
    y = height - 55*mm
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#2c3e50"))
    c.drawString(25*mm, y, "Sample Information")
    
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    for label, value in [("Sample ID", sample_id), ("Operator", operator), 
                          ("Date", datetime.now().strftime('%Y-%m-%d %H:%M')), ("Notes", notes)]:
        y -= 6*mm
        c.drawString(25*mm, y, f"{label}: {value}")
    
    y -= 12*mm
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#2c3e50"))
    c.drawString(25*mm, y, "Results")
    y -= 8*mm
    c.setFont("Helvetica", 10)
    c.drawString(25*mm, y, "Pearlite Fraction:")
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.HexColor("#27ae60"))
    c.drawString(60*mm, y, f"{percentage:.2f}%")
    
    y -= 6*mm
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.gray)
    c.drawString(25*mm, y, f"Painted: {painted_px:,} px  |  Total: {total_px:,} px")
    
    y -= 12*mm
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#2c3e50"))
    c.drawString(25*mm, y, "Micrographs")
    y -= 6*mm
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.black)
    c.drawString(25*mm, y, "Original")
    c.drawString(110*mm, y, "Highlighted")
    
    y -= 58*mm
    for img, x in [(original_img, 25*mm), (annotated_img, 110*mm)]:
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        c.drawImage(ImageReader(buf), x, y, width=70*mm, height=55*mm, preserveAspectRatio=True)
    
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.gray)
    c.drawCentredString(width/2, 15*mm, "Pearlite Phase Analyser")
    
    c.save()
    buffer.seek(0)
    return buffer

def calculate_percentage(canvas_data, total_pixels):
    if canvas_data is None or canvas_data.image_data is None:
        return 0.0, 0
    alpha = canvas_data.image_data[:, :, 3]
    painted = int(np.sum(alpha > 50))
    pct = (painted / total_pixels) * 100 if total_pixels > 0 else 0.0
    return pct, painted

# Title
st.markdown("""
<h1 style="text-align:center; color:#2c3e50; border-bottom:3px solid #27ae60; padding-bottom:10px;">
Pearlite Phase Analyser
</h1>
<p style="text-align:center; color:#7f8c8d;">Draw on the image to highlight pearlite regions</p>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Tools")
    tool = st.radio("Tool", ["Brush", "Eraser"])
    stroke_color = "rgba(220, 50, 50, 0.7)" if tool == "Brush" else "rgba(0,0,0,0)"
    brush_size = st.slider("Brush Size", 2, 50, 15)
    
    st.markdown("---")
    st.header("Report Info")
    sample_id = st.text_input("Sample ID")
    operator = st.text_input("Operator")
    notes = st.text_area("Notes", height=80)

# Main
col1, col2 = st.columns([3, 1])

with col1:
    uploaded = st.file_uploader("Upload Microstructure Image", type=["png", "jpg", "jpeg", "bmp", "tiff"])
    
    if uploaded:
        img = Image.open(uploaded).convert("RGB")
        
        # Resize
        max_w, max_h = 700, 500
        scale = min(max_w/img.width, max_h/img.height, 1.0)
        cw, ch = int(img.width * scale), int(img.height * scale)
        display_img = img.resize((cw, ch), Image.Resampling.LANCZOS)
        
        # Convert to base64
        img_b64 = image_to_base64(display_img)
        
        # Create overlay effect with CSS
        st.markdown(f"""
        <style>
            div[data-testid="stVerticalBlock"] div[data-testid="element-container"]:has(canvas) {{
                background-image: url('data:image/png;base64,{img_b64}');
                background-size: {cw}px {ch}px;
                background-repeat: no-repeat;
                background-position: top left;
            }}
        </style>
        """, unsafe_allow_html=True)
        
        # Canvas with transparent background
        canvas_result = st_canvas(
            fill_color="rgba(0,0,0,0)",
            stroke_width=brush_size,
            stroke_color=stroke_color,
            background_color="rgba(0,0,0,0)",
            height=ch,
            width=cw,
            drawing_mode="freedraw",
            key="canvas",
        )
        
        total_px = cw * ch
        percentage, painted_px = calculate_percentage(canvas_result, total_px)
        
        st.session_state['display_img'] = display_img
        st.session_state['canvas_result'] = canvas_result
        st.session_state['pct'] = percentage
        st.session_state['painted'] = painted_px
        st.session_state['total'] = total_px
    else:
        st.info("Upload a microstructure image to begin")
        percentage, painted_px, total_px = 0.0, 0, 0

with col2:
    st.markdown("### Results")
    st.markdown(f"**Pearlite Fraction**")
    st.markdown(f"<span style='font-size:2.5rem;color:#27ae60;font-weight:bold;'>{percentage:.2f}%</span>", unsafe_allow_html=True)
    st.caption(f"Painted: {painted_px:,} px")
    st.caption(f"Total: {total_px:,} px")
    
    st.markdown("---")
    
    if uploaded:
        if st.button("Generate PDF Report", type="primary", use_container_width=True):
            display_img = st.session_state.get('display_img')
            canvas_result = st.session_state.get('canvas_result')
            pct = st.session_state.get('pct', 0)
            painted = st.session_state.get('painted', 0)
            total = st.session_state.get('total', 0)
            
            if display_img:
                if canvas_result and canvas_result.image_data is not None:
                    arr = canvas_result.image_data.astype(np.uint8)
                    overlay = Image.fromarray(arr, 'RGBA')
                    annotated = display_img.copy().convert('RGBA')
                    annotated = Image.alpha_composite(annotated, overlay).convert('RGB')
                else:
                    annotated = display_img
                
                pdf = create_pdf_report(display_img, annotated, pct, painted, total,
                                        sample_id or "N/A", operator or "N/A", notes or "N/A")
                
                st.download_button("Download PDF", pdf, 
                                   f"pearlite_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                   "application/pdf", use_container_width=True)
                st.success("Report ready!")
