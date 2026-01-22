"""
Pearlite Phase Analyser - Web Application
Quantify pearlite phases in steel microstructure images.
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

# Page config
st.set_page_config(
    page_title="Pearlite Phase Analyser",
    layout="wide"
)

# Simple clean CSS
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #2c3e50;
        font-size: 2rem;
        font-weight: bold;
        padding: 10px 0;
        border-bottom: 3px solid #27ae60;
        margin-bottom: 20px;
    }
    .subtitle {
        text-align: center;
        color: #7f8c8d;
        margin-bottom: 20px;
    }
    .result-label {
        color: #2c3e50;
        font-weight: bold;
        font-size: 1.1rem;
    }
    .result-value {
        color: #27ae60;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .info-text {
        color: #7f8c8d;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

def create_pdf_report(original_img, annotated_img, percentage, painted_px, total_px, sample_id, operator, notes):
    """Generate PDF report."""
    buffer = BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Title
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(colors.HexColor("#2c3e50"))
    c.drawCentredString(width/2, height - 35*mm, "Pearlite Phase Analyser Report")
    
    # Green line
    c.setStrokeColor(colors.HexColor("#27ae60"))
    c.setLineWidth(2)
    c.line(25*mm, height - 40*mm, width - 25*mm, height - 40*mm)
    
    # Sample Information
    y = height - 55*mm
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#2c3e50"))
    c.drawString(25*mm, y, "Sample Information")
    
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    y -= 7*mm
    c.drawString(25*mm, y, f"Sample ID: {sample_id}")
    y -= 5*mm
    c.drawString(25*mm, y, f"Operator: {operator}")
    y -= 5*mm
    c.drawString(25*mm, y, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y -= 5*mm
    c.drawString(25*mm, y, f"Notes: {notes}")
    
    # Results
    y -= 12*mm
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#2c3e50"))
    c.drawString(25*mm, y, "Results")
    
    y -= 8*mm
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.drawString(25*mm, y, "Pearlite Fraction:")
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.HexColor("#27ae60"))
    c.drawString(60*mm, y, f"{percentage:.2f}%")
    
    y -= 6*mm
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.gray)
    c.drawString(25*mm, y, f"Painted: {painted_px:,} px  |  Total: {total_px:,} px")
    
    # Images
    y -= 12*mm
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#2c3e50"))
    c.drawString(25*mm, y, "Micrographs")
    
    y -= 6*mm
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.black)
    c.drawString(25*mm, y, "Original")
    c.drawString(110*mm, y, "Highlighted")
    
    img_w, img_h = 70*mm, 55*mm
    y -= img_h + 3*mm
    
    # Original image
    buf1 = BytesIO()
    original_img.save(buf1, format='PNG')
    buf1.seek(0)
    c.drawImage(ImageReader(buf1), 25*mm, y, width=img_w, height=img_h, preserveAspectRatio=True)
    
    # Annotated image
    buf2 = BytesIO()
    annotated_img.save(buf2, format='PNG')
    buf2.seek(0)
    c.drawImage(ImageReader(buf2), 110*mm, y, width=img_w, height=img_h, preserveAspectRatio=True)
    
    # Footer
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.gray)
    c.drawCentredString(width/2, 15*mm, "Pearlite Phase Analyser")
    
    c.save()
    buffer.seek(0)
    return buffer

def calculate_percentage(canvas_data, total_pixels):
    """Calculate percentage of painted area."""
    if canvas_data is None or canvas_data.image_data is None:
        return 0.0, 0
    
    # Count pixels with alpha > threshold (painted pixels)
    alpha_channel = canvas_data.image_data[:, :, 3]
    painted_pixels = int(np.sum(alpha_channel > 50))
    
    if total_pixels > 0:
        percentage = (painted_pixels / total_pixels) * 100
    else:
        percentage = 0.0
    
    return percentage, painted_pixels

# ============ MAIN APP ============

# Title
st.markdown('<div class="main-title">Pearlite Phase Analyser</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload a microstructure image, paint pearlite regions, and calculate phase fraction</div>', unsafe_allow_html=True)

# Sidebar - Tools
with st.sidebar:
    st.header("Tools")
    
    tool_mode = st.radio("Drawing Tool", ["Brush (Highlight)", "Eraser"])
    
    if "Brush" in tool_mode:
        stroke_color = "rgba(220, 50, 50, 0.7)"  # Semi-transparent red
    else:
        stroke_color = "rgba(0, 0, 0, 0)"  # Transparent for eraser
    
    brush_size = st.slider("Brush Size", min_value=2, max_value=50, value=15)
    
    st.markdown("---")
    st.header("Report Info")
    sample_id = st.text_input("Sample ID", value="", placeholder="Enter sample ID")
    operator = st.text_input("Operator", value="", placeholder="Enter operator name")
    notes = st.text_area("Notes", value="", placeholder="Enter notes", height=100)

# Main content
col_main, col_results = st.columns([3, 1])

with col_main:
    # File uploader
    uploaded_file = st.file_uploader("Upload Microstructure Image", type=["png", "jpg", "jpeg", "bmp", "tiff"])
    
    if uploaded_file is not None:
        # Load image
        original_image = Image.open(uploaded_file).convert("RGB")
        
        # Resize for display
        max_width, max_height = 700, 500
        img_width, img_height = original_image.size
        scale = min(max_width / img_width, max_height / img_height, 1.0)
        canvas_width = int(img_width * scale)
        canvas_height = int(img_height * scale)
        
        display_image = original_image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
        
        # Show original image as reference
        st.write("**Reference Image** (view while drawing below)")
        st.image(display_image, width=canvas_width)
        
        st.write("**Draw Here** (paint pearlite regions in red)")
        
        # Drawing canvas
        canvas_result = st_canvas(
            fill_color="rgba(0, 0, 0, 0)",
            stroke_width=brush_size,
            stroke_color=stroke_color,
            background_color="#f0f0f0",
            height=canvas_height,
            width=canvas_width,
            drawing_mode="freedraw",
            key="drawing_canvas",
        )
        
        # Calculate percentage
        total_pixels = canvas_width * canvas_height
        percentage, painted_pixels = calculate_percentage(canvas_result, total_pixels)
        
        # Store in session state for report
        st.session_state['display_image'] = display_image
        st.session_state['canvas_result'] = canvas_result
        st.session_state['percentage'] = percentage
        st.session_state['painted_pixels'] = painted_pixels
        st.session_state['total_pixels'] = total_pixels
        
    else:
        st.info("Please upload a microstructure image to begin.")
        percentage = 0.0
        painted_pixels = 0
        total_pixels = 0

with col_results:
    st.markdown("### Results")
    
    st.markdown(f'<p class="result-label">Pearlite Fraction</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="result-value">{percentage:.2f}%</p>', unsafe_allow_html=True)
    
    st.markdown(f'<p class="info-text">Painted: {painted_pixels:,} px</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="info-text">Total: {total_pixels:,} px</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Generate Report Button
    if uploaded_file is not None:
        if st.button("Generate PDF Report", type="primary", use_container_width=True):
            display_image = st.session_state.get('display_image')
            canvas_result = st.session_state.get('canvas_result')
            pct = st.session_state.get('percentage', 0.0)
            painted = st.session_state.get('painted_pixels', 0)
            total = st.session_state.get('total_pixels', 0)
            
            if display_image is not None:
                # Create annotated image
                if canvas_result is not None and canvas_result.image_data is not None:
                    canvas_array = canvas_result.image_data.astype(np.uint8)
                    canvas_img = Image.fromarray(canvas_array, 'RGBA')
                    annotated = display_image.copy().convert('RGBA')
                    annotated = Image.alpha_composite(annotated, canvas_img)
                    annotated = annotated.convert('RGB')
                else:
                    annotated = display_image
                
                # Generate PDF
                pdf_buffer = create_pdf_report(
                    display_image,
                    annotated,
                    pct,
                    painted,
                    total,
                    sample_id or "N/A",
                    operator or "N/A",
                    notes or "N/A"
                )
                
                # Download button
                st.download_button(
                    label="Download PDF",
                    data=pdf_buffer,
                    file_name=f"pearlite_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                st.success("Report generated!")
    
    st.markdown("---")
    st.markdown("**Instructions:**")
    st.markdown("""
    1. Upload image
    2. Look at reference
    3. Draw on canvas below
    4. Match pearlite regions
    5. Generate report
    """)
