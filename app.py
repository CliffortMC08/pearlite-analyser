"""
Pearlite Phase Analyser - Web Application
Image with canvas overlay, auto-syncing results.
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

# Read percentage from URL params if available
params = st.query_params
url_pct = float(params.get("pct", 0))
url_painted = int(params.get("painted", 0))

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
        total_px = cw * ch
        
        canvas_html = f"""
        <style>
            #canvas-container {{
                position: relative;
                width: {cw}px;
                height: {ch}px;
                margin: 0 auto;
                border: 2px solid #27ae60;
                border-radius: 5px;
                overflow: hidden;
            }}
            #bgImage {{ position: absolute; top: 0; left: 0; width: {cw}px; height: {ch}px; z-index: 1; }}
            #drawCanvas {{ position: absolute; top: 0; left: 0; z-index: 2; cursor: crosshair; }}
            #resultsBar {{
                background: linear-gradient(135deg, #2c3e50, #34495e);
                color: white;
                padding: 15px 20px;
                border-radius: 5px;
                margin-top: 10px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-family: Arial, sans-serif;
            }}
            .label {{ font-size: 14px; color: #bdc3c7; }}
            .value {{ font-size: 28px; font-weight: bold; color: #2ecc71; }}
            .pixels {{ font-size: 12px; color: #95a5a6; }}
            #syncBtn {{
                background: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
                margin-top: 10px;
            }}
            #syncBtn:hover {{ background: #2ecc71; }}
        </style>
        
        <div id="canvas-container">
            <img id="bgImage" src="data:image/png;base64,{img_b64}">
            <canvas id="drawCanvas" width="{cw}" height="{ch}"></canvas>
        </div>
        
        <div id="resultsBar">
            <div>
                <div class="label">Pearlite Fraction</div>
                <div class="value" id="percentDisplay">0.00%</div>
            </div>
            <div style="text-align:right;">
                <div class="pixels" id="paintedDisplay">Painted: 0 px</div>
                <div class="pixels">Total: {total_px:,} px</div>
            </div>
        </div>
        
        <div style="text-align:center;">
            <button id="syncBtn" onclick="syncResults()">Sync Results for Report</button>
        </div>
        
        <script>
        const canvas = document.getElementById('drawCanvas');
        const ctx = canvas.getContext('2d');
        let isDrawing = false;
        let lastX = 0, lastY = 0;
        let currentPct = 0;
        let currentPainted = 0;
        
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.lineWidth = {brush_size};
        ctx.strokeStyle = '{stroke_color}';
        ctx.globalCompositeOperation = {eraser_mode} ? 'destination-out' : 'source-over';
        
        const saved = sessionStorage.getItem('pearliteCanvas_{cw}_{ch}');
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
        
        function startDraw(e) {{ isDrawing = true; [lastX, lastY] = getPos(e); }}
        
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
                sessionStorage.setItem('pearliteCanvas_{cw}_{ch}', canvas.toDataURL());
                updateCount();
            }}
        }}
        
        function updateCount() {{
            const imageData = ctx.getImageData(0, 0, {cw}, {ch});
            let count = 0;
            for (let i = 3; i < imageData.data.length; i += 4) {{
                if (imageData.data[i] > 50) count++;
            }}
            currentPainted = count;
            currentPct = ((count / {total_px}) * 100).toFixed(2);
            document.getElementById('percentDisplay').textContent = currentPct + '%';
            document.getElementById('paintedDisplay').textContent = 'Painted: ' + count.toLocaleString() + ' px';
        }}
        
        function syncResults() {{
            const url = new URL(window.parent.location.href);
            url.searchParams.set('pct', currentPct);
            url.searchParams.set('painted', currentPainted);
            window.parent.location.href = url.toString();
        }}
        
        canvas.addEventListener('mousedown', startDraw);
        canvas.addEventListener('mousemove', draw);
        canvas.addEventListener('mouseup', stopDraw);
        canvas.addEventListener('mouseout', stopDraw);
        canvas.addEventListener('touchstart', startDraw);
        canvas.addEventListener('touchmove', draw);
        canvas.addEventListener('touchend', stopDraw);
        
        updateCount();
        </script>
        """
        
        components.html(canvas_html, height=ch+130)
        
        st.session_state['display_img'] = display_img
        st.session_state['total'] = total_px
        
    else:
        st.info("Upload a microstructure image to begin")

with col2:
    st.markdown("### Results")
    
    total = st.session_state.get('total', 0)
    pct = url_pct if url_pct > 0 else 0.0
    painted = url_painted if url_painted > 0 else 0
    
    st.markdown(f"**Pearlite Fraction**")
    st.markdown(f"<span style='font-size:2.5rem;color:#27ae60;font-weight:bold;'>{pct:.2f}%</span>", unsafe_allow_html=True)
    st.caption(f"Painted: {painted:,} px")
    st.caption(f"Total: {total:,} px")
    
    st.markdown("---")
    
    if uploaded:
        if st.button("Generate PDF Report", type="primary", use_container_width=True):
            display_img = st.session_state.get('display_img')
            if display_img and pct > 0:
                pdf = create_pdf_report(
                    display_img, display_img, pct, painted, total,
                    sample_id or "N/A", operator or "N/A", notes or "N/A"
                )
                st.download_button("Download PDF", pdf, 
                    f"pearlite_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    "application/pdf", use_container_width=True)
                st.success("Report ready!")
            elif pct == 0:
                st.warning("Click 'Sync Results' below the image first")
    else:
        st.info("Upload an image to begin")
