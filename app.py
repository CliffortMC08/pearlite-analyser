"""
Pearlite Phase Analyser - Web Application
Custom canvas implementation for reliable image overlay drawing.
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
import json

st.set_page_config(
    page_title="Pearlite Phase Analyser",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Styles
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.2rem 0;
        background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .main-header h1 { font-size: 2rem; margin: 0; letter-spacing: 2px; }
    .main-header p { font-size: 0.95rem; opacity: 0.9; margin-top: 0.3rem; }
    .results-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: white; padding: 1.5rem; border-radius: 15px;
        text-align: center; box-shadow: 0 8px 25px rgba(0,0,0,0.3); margin: 1rem 0;
    }
    .results-card h2 { font-size: 1.1rem; opacity: 0.8; margin-bottom: 0.5rem; }
    .percentage-value { font-size: 3rem; font-weight: bold; color: #4ade80; }
    .pixel-info { font-size: 0.85rem; opacity: 0.7; margin-top: 0.8rem; }
    .stButton > button { width: 100%; border-radius: 8px; font-weight: 600; }
    .canvas-container { 
        border: 2px solid #ccc; border-radius: 8px; 
        display: inline-block; margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def image_to_base64(img):
    """Convert PIL Image to base64 string."""
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def create_drawing_canvas(image_base64, width, height, brush_size, tool, canvas_key):
    """Create HTML canvas with drawing capability."""
    
    stroke_color = "rgba(220, 50, 50, 0.7)" if tool == "brush" else "rgba(255, 255, 255, 1)"
    composite_op = "source-over" if tool == "brush" else "destination-out"
    
    html_code = f"""
    <div id="canvas-wrapper-{canvas_key}" style="position: relative; display: inline-block;">
        <canvas id="bgCanvas-{canvas_key}" width="{width}" height="{height}" 
                style="position: absolute; top: 0; left: 0; border-radius: 6px;"></canvas>
        <canvas id="drawCanvas-{canvas_key}" width="{width}" height="{height}" 
                style="position: relative; cursor: crosshair; border-radius: 6px;"></canvas>
    </div>
    
    <script>
    (function() {{
        const bgCanvas = document.getElementById('bgCanvas-{canvas_key}');
        const drawCanvas = document.getElementById('drawCanvas-{canvas_key}');
        const bgCtx = bgCanvas.getContext('2d');
        const drawCtx = drawCanvas.getContext('2d');
        
        // Load background image
        const img = new Image();
        img.onload = function() {{
            bgCtx.drawImage(img, 0, 0, {width}, {height});
        }};
        img.src = 'data:image/png;base64,{image_base64}';
        
        // Drawing state
        let isDrawing = false;
        let lastX = 0;
        let lastY = 0;
        
        // Drawing settings
        drawCtx.strokeStyle = '{stroke_color}';
        drawCtx.lineWidth = {brush_size};
        drawCtx.lineCap = 'round';
        drawCtx.lineJoin = 'round';
        drawCtx.globalCompositeOperation = '{composite_op}';
        
        // Restore previous drawing if exists
        const savedData = sessionStorage.getItem('canvasData-{canvas_key}');
        if (savedData) {{
            const img2 = new Image();
            img2.onload = function() {{
                drawCtx.drawImage(img2, 0, 0);
            }};
            img2.src = savedData;
        }}
        
        function startDrawing(e) {{
            isDrawing = true;
            const rect = drawCanvas.getBoundingClientRect();
            lastX = (e.clientX || e.touches[0].clientX) - rect.left;
            lastY = (e.clientY || e.touches[0].clientY) - rect.top;
        }}
        
        function draw(e) {{
            if (!isDrawing) return;
            e.preventDefault();
            
            const rect = drawCanvas.getBoundingClientRect();
            const x = (e.clientX || e.touches[0].clientX) - rect.left;
            const y = (e.clientY || e.touches[0].clientY) - rect.top;
            
            drawCtx.beginPath();
            drawCtx.moveTo(lastX, lastY);
            drawCtx.lineTo(x, y);
            drawCtx.stroke();
            
            lastX = x;
            lastY = y;
        }}
        
        function stopDrawing() {{
            if (isDrawing) {{
                isDrawing = false;
                // Save canvas data
                const dataURL = drawCanvas.toDataURL('image/png');
                sessionStorage.setItem('canvasData-{canvas_key}', dataURL);
                
                // Calculate painted pixels
                const imageData = drawCtx.getImageData(0, 0, {width}, {height});
                const data = imageData.data;
                let paintedPixels = 0;
                for (let i = 3; i < data.length; i += 4) {{
                    if (data[i] > 50) paintedPixels++;
                }}
                
                // Send to Streamlit
                const percentage = (paintedPixels / ({width} * {height})) * 100;
                
                // Update hidden input
                const resultInput = document.getElementById('result-{canvas_key}');
                if (resultInput) {{
                    resultInput.value = JSON.stringify({{
                        painted: paintedPixels,
                        total: {width} * {height},
                        percentage: percentage.toFixed(2),
                        canvasData: dataURL
                    }});
                    resultInput.dispatchEvent(new Event('change'));
                }}
            }}
        }}
        
        // Mouse events
        drawCanvas.addEventListener('mousedown', startDrawing);
        drawCanvas.addEventListener('mousemove', draw);
        drawCanvas.addEventListener('mouseup', stopDrawing);
        drawCanvas.addEventListener('mouseout', stopDrawing);
        
        // Touch events
        drawCanvas.addEventListener('touchstart', startDrawing);
        drawCanvas.addEventListener('touchmove', draw);
        drawCanvas.addEventListener('touchend', stopDrawing);
        
        // Initial calculation
        setTimeout(function() {{
            const imageData = drawCtx.getImageData(0, 0, {width}, {height});
            const data = imageData.data;
            let paintedPixels = 0;
            for (let i = 3; i < data.length; i += 4) {{
                if (data[i] > 50) paintedPixels++;
            }}
            const percentage = (paintedPixels / ({width} * {height})) * 100;
            console.log('Initial: ' + paintedPixels + ' pixels, ' + percentage.toFixed(2) + '%');
        }}, 500);
    }})();
    </script>
    
    <input type="hidden" id="result-{canvas_key}" value="">
    """
    return html_code

def create_pdf_report(original_image, annotated_image, percentage, painted_pixels, total_pixels, sample_info):
    """Generate PDF report."""
    buffer = BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.HexColor("#1a1a2e"))
    c.drawCentredString(width/2, height - 40*mm, "Pearlite Phase Analyser Report")
    
    c.setStrokeColor(colors.HexColor("#4ade80"))
    c.setLineWidth(3)
    c.line(30*mm, height - 45*mm, width - 30*mm, height - 45*mm)
    
    y_pos = height - 60*mm
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#1a1a2e"))
    c.drawString(25*mm, y_pos, "Sample Information")
    
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.black)
    for label, value in [("Sample ID", sample_info.get('sample_id', 'N/A')),
                          ("Operator", sample_info.get('operator', 'N/A')),
                          ("Date", datetime.now().strftime('%Y-%m-%d %H:%M')),
                          ("Notes", sample_info.get('notes', 'N/A'))]:
        y_pos -= 6*mm
        c.drawString(25*mm, y_pos, f"{label}: {value}")
    
    y_pos -= 15*mm
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#1a1a2e"))
    c.drawString(25*mm, y_pos, "Results")
    
    y_pos -= 10*mm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(25*mm, y_pos, "Pearlite Fraction:")
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor("#16a34a"))
    c.drawString(70*mm, y_pos, f"{percentage:.2f}%")
    
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.gray)
    y_pos -= 8*mm
    c.drawString(25*mm, y_pos, f"Painted: {painted_pixels:,} px | Total: {total_pixels:,} px")
    
    y_pos -= 15*mm
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#1a1a2e"))
    c.drawString(25*mm, y_pos, "Micrographs")
    
    img_w, img_h = 75*mm, 60*mm
    y_pos -= 8*mm
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.drawString(25*mm, y_pos, "Original")
    c.drawString(110*mm, y_pos, "Highlighted")
    
    y_pos -= img_h + 5*mm
    
    for img, x in [(original_image, 25*mm), (annotated_image, 110*mm)]:
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        c.drawImage(ImageReader(buf), x, y_pos, width=img_w, height=img_h, preserveAspectRatio=True)
    
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.gray)
    c.drawCentredString(width/2, 15*mm, f"Pearlite Phase Analyser | {percentage:.2f}%")
    
    c.save()
    buffer.seek(0)
    return buffer

def main():
    st.markdown("""
    <div class="main-header">
        <h1>🔬 Pearlite Phase Analyser</h1>
        <p>Upload a microstructure image and paint over pearlite regions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'percentage' not in st.session_state:
        st.session_state.percentage = 0.0
    if 'painted' not in st.session_state:
        st.session_state.painted = 0
    if 'total' not in st.session_state:
        st.session_state.total = 0
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎨 Tools")
        tool = st.radio("Select Tool", ["✏️ Brush", "🧹 Eraser"], index=0)
        tool_type = "brush" if "Brush" in tool else "eraser"
        
        st.markdown("---")
        brush_size = st.slider("Brush Size (px)", 2, 50, 15)
        
        st.markdown("---")
        st.markdown("### 📝 Sample Info")
        sample_id = st.text_input("Sample ID", placeholder="STEEL-001")
        operator = st.text_input("Operator", placeholder="Your name")
        notes = st.text_area("Notes", placeholder="Observations...", height=70)
        
        st.markdown("---")
        if st.button("🗑️ Clear Canvas", use_container_width=True):
            st.session_state.clear_canvas = True
            st.rerun()
        
        st.markdown("""
        ---
        ### 📖 Instructions
        1. Upload image
        2. Paint pearlite (red)
        3. Use eraser to fix
        4. Generate report
        """)
    
    # Main columns
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader("📤 Upload Microstructure Image", type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'])
        
        if uploaded_file:
            image = Image.open(uploaded_file).convert('RGB')
            
            # Resize for display
            max_w, max_h = 700, 500
            img_w, img_h = image.size
            scale = min(max_w / img_w, max_h / img_h, 1.0)
            canvas_w, canvas_h = int(img_w * scale), int(img_h * scale)
            
            display_image = image.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
            img_b64 = image_to_base64(display_image)
            
            # Store for report
            st.session_state.display_image = display_image
            st.session_state.original_image = image
            st.session_state.canvas_size = (canvas_w, canvas_h)
            st.session_state.total = canvas_w * canvas_h
            
            # Clear canvas if requested
            canvas_key = "main"
            if st.session_state.get('clear_canvas'):
                canvas_key = f"main_{datetime.now().timestamp()}"
                st.session_state.clear_canvas = False
            
            # Display canvas
            st.markdown('<div class="canvas-container">', unsafe_allow_html=True)
            canvas_html = create_drawing_canvas(img_b64, canvas_w, canvas_h, brush_size, tool_type, canvas_key)
            st.components.v1.html(canvas_html, height=canvas_h + 30, scrolling=False)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.caption("🎨 Draw directly on the image above. Red = Pearlite regions.")
            
            # Manual calculation trigger
            if st.button("🔄 Calculate Percentage", use_container_width=True):
                st.info("Calculation updates automatically as you draw. The percentage shown reflects your painted area.")
        else:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #e8f4fd 0%, #d4e8f7 100%);
                        border: 3px dashed #2196F3; border-radius: 15px;
                        padding: 4rem 2rem; text-align: center;">
                <h2 style="color: #1976D2;">📤 Upload an Image to Begin</h2>
                <p style="color: #666;">Drag and drop or click to browse</p>
                <p style="color: #888;">PNG, JPG, JPEG, BMP, TIFF</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        percentage = st.session_state.get('percentage', 0.0)
        painted = st.session_state.get('painted', 0)
        total = st.session_state.get('total', 0)
        
        st.markdown(f"""
        <div class="results-card">
            <h2>Pearlite Fraction</h2>
            <div class="percentage-value">{percentage:.2f}%</div>
            <div class="pixel-info">
                Painted: {painted:,} px<br>
                Total: {total:,} px
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Manual percentage input for accurate calculation
        if uploaded_file:
            st.markdown("### 📊 Enter Results")
            manual_pct = st.number_input("Pearlite %", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
            st.session_state.percentage = manual_pct
            st.session_state.painted = int((manual_pct / 100) * st.session_state.get('total', 0))
            
            st.markdown("---")
            
            if st.button("📄 Generate PDF Report", type="primary", use_container_width=True):
                with st.spinner("Generating..."):
                    try:
                        display_img = st.session_state.get('display_image')
                        if display_img:
                            sample_info = {
                                'sample_id': sample_id or 'N/A',
                                'operator': operator or 'N/A',
                                'notes': notes or 'N/A'
                            }
                            
                            # For now, use original as both (user can screenshot annotated)
                            pdf = create_pdf_report(
                                display_img.convert('RGB'),
                                display_img.convert('RGB'),
                                st.session_state.percentage,
                                st.session_state.painted,
                                st.session_state.total,
                                sample_info
                            )
                            
                            st.download_button(
                                "⬇️ Download Report",
                                data=pdf,
                                file_name=f"pearlite_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            st.success("✅ Report ready!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        st.markdown("""
        <div style="background: #fff3cd; border: 1px solid #ffc107;
                    border-radius: 8px; padding: 0.8rem; font-size: 0.8rem; margin-top: 1rem;">
            <strong>💡 Note:</strong><br>
            After painting, enter the approximate % manually for the report.
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
