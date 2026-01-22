"""
Pearlite Phase Analyser - Web Application
Image with canvas overlay using HTML positioning.
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
import streamlit.components.v1 as components

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
    c.drawString(25*mm, y, f"Painted: {painted_px:,} px | Total: {total_px:,} px")
    
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

# Title
st.markdown("""
<h1 style="text-align:center; color:#2c3e50; border-bottom:3px solid #27ae60; padding-bottom:10px;">
Pearlite Phase Analyser
</h1>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Tools")
    tool = st.radio("Tool", ["Brush", "Eraser"])
    brush_size = st.slider("Brush Size", 2, 50, 15)
    st.markdown("---")
    st.header("Report Info")
    sample_id = st.text_input("Sample ID")
    operator = st.text_input("Operator")
    notes = st.text_area("Notes", height=80)

# Main
col1, col2 = st.columns([4, 1])

with col1:
    uploaded = st.file_uploader("Upload Microstructure Image", type=["png", "jpg", "jpeg", "bmp", "tiff"])
    
    if uploaded:
        img = Image.open(uploaded).convert("RGB")
        max_w, max_h = 800, 550
        scale = min(max_w/img.width, max_h/img.height, 1.0)
        cw, ch = int(img.width * scale), int(img.height * scale)
        display_img = img.resize((cw, ch), Image.Resampling.LANCZOS)
        img_b64 = image_to_base64(display_img)
        
        stroke_color = "rgba(220,50,50,0.7)" if tool == "Brush" else "rgba(0,0,0,0)"
        eraser_mode = "true" if tool == "Eraser" else "false"
        
        # Custom HTML canvas component with image background
        canvas_html = f"""
        <div id="canvas-container" style="position:relative; width:{cw}px; height:{ch}px; margin:0 auto; border:1px solid #ccc;">
            <img src="data:image/png;base64,{img_b64}" style="position:absolute; top:0; left:0; width:{cw}px; height:{ch}px; z-index:1;">
            <canvas id="drawCanvas" width="{cw}" height="{ch}" style="position:absolute; top:0; left:0; z-index:2; cursor:crosshair;"></canvas>
        </div>
        <div style="text-align:center; margin-top:10px;">
            <span id="pixelCount" style="color:#27ae60; font-weight:bold;">Painted: 0 px</span>
        </div>
        <input type="hidden" id="canvasData" value="">
        
        <script>
        (function() {{
            const canvas = document.getElementById('drawCanvas');
            const ctx = canvas.getContext('2d');
            let isDrawing = false;
            let lastX = 0, lastY = 0;
            
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            ctx.lineWidth = {brush_size};
            ctx.strokeStyle = '{stroke_color}';
            ctx.globalCompositeOperation = {eraser_mode} ? 'destination-out' : 'source-over';
            
            // Load saved data
            const saved = sessionStorage.getItem('pearliteCanvas');
            if (saved) {{
                const img = new Image();
                img.onload = function() {{ ctx.drawImage(img, 0, 0); updateCount(); }};
                img.src = saved;
            }}
            
            function getPos(e) {{
                const rect = canvas.getBoundingClientRect();
                const x = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
                const y = (e.touches ? e.touches[0].clientY : e.clientY) - rect.top;
                return [x, y];
            }}
            
            function startDraw(e) {{
                isDrawing = true;
                [lastX, lastY] = getPos(e);
            }}
            
            function draw(e) {{
                if (!isDrawing) return;
                e.preventDefault();
                const [x, y] = getPos(e);
                ctx.beginPath();
                ctx.moveTo(lastX, lastY);
                ctx.lineTo(x, y);
                ctx.stroke();
                [lastX, lastY] = [x, y];
            }}
            
            function stopDraw() {{
                if (isDrawing) {{
                    isDrawing = false;
                    sessionStorage.setItem('pearliteCanvas', canvas.toDataURL());
                    updateCount();
                    document.getElementById('canvasData').value = canvas.toDataURL();
                }}
            }}
            
            function updateCount() {{
                const imageData = ctx.getImageData(0, 0, {cw}, {ch});
                let count = 0;
                for (let i = 3; i < imageData.data.length; i += 4) {{
                    if (imageData.data[i] > 50) count++;
                }}
                const pct = ((count / ({cw} * {ch})) * 100).toFixed(2);
                document.getElementById('pixelCount').innerHTML = 
                    'Painted: ' + count.toLocaleString() + ' px (' + pct + '%)';
                
                // Send to Streamlit
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: {{ painted: count, percentage: pct, dataUrl: canvas.toDataURL() }}
                }}, '*');
            }}
            
            canvas.addEventListener('mousedown', startDraw);
            canvas.addEventListener('mousemove', draw);
            canvas.addEventListener('mouseup', stopDraw);
            canvas.addEventListener('mouseout', stopDraw);
            canvas.addEventListener('touchstart', startDraw);
            canvas.addEventListener('touchmove', draw);
            canvas.addEventListener('touchend', stopDraw);
        }})();
        </script>
        """
        
        components.html(canvas_html, height=ch+50)
        
        # Get values from session
        total_px = cw * ch
        painted_px = st.session_state.get('painted_px', 0)
        percentage = st.session_state.get('percentage', 0.0)
        
        st.session_state['display_img'] = display_img
        st.session_state['cw'] = cw
        st.session_state['ch'] = ch
        st.session_state['total'] = total_px
        
        # Manual input for percentage (since HTML can't send back to Streamlit easily)
        st.markdown("---")
        st.markdown("**Enter the percentage shown above:**")
        manual_pct = st.number_input("Pearlite %", min_value=0.0, max_value=100.0, value=0.0, step=0.01)
        st.session_state['pct'] = manual_pct
        st.session_state['painted'] = int((manual_pct / 100) * total_px)
        
    else:
        st.info("Upload a microstructure image to begin")
        manual_pct = 0.0

with col2:
    st.markdown("### Results")
    pct = st.session_state.get('pct', 0.0)
    painted = st.session_state.get('painted', 0)
    total = st.session_state.get('total', 0)
    
    st.markdown(f"**Pearlite Fraction**")
    st.markdown(f"<span style='font-size:2.2rem;color:#27ae60;font-weight:bold;'>{pct:.2f}%</span>", unsafe_allow_html=True)
    st.caption(f"Painted: {painted:,} px")
    st.caption(f"Total: {total:,} px")
    
    st.markdown("---")
    
    if uploaded:
        if st.button("Generate PDF Report", type="primary", use_container_width=True):
            display_img = st.session_state.get('display_img')
            if display_img:
                # For the report, we use the original image since we can't get canvas data back
                pdf = create_pdf_report(
                    display_img, display_img, pct, painted, total,
                    sample_id or "N/A", operator or "N/A", notes or "N/A"
                )
                st.download_button("Download PDF", pdf, 
                    f"pearlite_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    "application/pdf", use_container_width=True)
                st.success("Report ready!")
