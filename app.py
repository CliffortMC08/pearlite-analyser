"""
Pearlite Phase Analyser - Web Application
A Streamlit-based tool for quantifying pearlite phases in steel microstructure images.
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

# Fix for streamlit-drawable-canvas compatibility with newer Streamlit versions
import streamlit.elements.image as st_image
if not hasattr(st_image, 'image_to_url'):
    def _image_to_url(image, width, clamp, channels, output_format, image_id):
        """Compatibility shim for older streamlit-drawable-canvas."""
        from PIL import Image as PILImage
        if isinstance(image, PILImage.Image):
            buffered = BytesIO()
            # Ensure RGB mode for compatibility
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"
        elif isinstance(image, np.ndarray):
            img = PILImage.fromarray(image.astype('uint8'))
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"
        return ""
    st_image.image_to_url = _image_to_url

# Now import canvas after the patch
from streamlit_drawable_canvas import st_canvas

# Page configuration
st.set_page_config(
    page_title="Pearlite Phase Analyser",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
    }
    
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .main-header h1 {
        font-size: 2.2rem;
        margin: 0;
        letter-spacing: 2px;
    }
    
    .main-header p {
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    .results-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        margin: 1rem 0;
    }
    
    .results-card h2 {
        font-size: 1.1rem;
        opacity: 0.8;
        margin-bottom: 0.5rem;
    }
    
    .percentage-value {
        font-size: 3rem;
        font-weight: bold;
        color: #4ade80;
        text-shadow: 0 0 20px rgba(74, 222, 128, 0.5);
    }
    
    .pixel-info {
        font-size: 0.85rem;
        opacity: 0.7;
        margin-top: 0.8rem;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def create_pdf_report(original_image, annotated_image, percentage, painted_pixels, total_pixels, sample_info):
    """Generate a professional PDF report."""
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
    y_pos -= 8*mm
    c.drawString(25*mm, y_pos, f"Sample ID: {sample_info.get('sample_id', 'N/A')}")
    y_pos -= 6*mm
    c.drawString(25*mm, y_pos, f"Operator: {sample_info.get('operator', 'N/A')}")
    y_pos -= 6*mm
    c.drawString(25*mm, y_pos, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y_pos -= 6*mm
    c.drawString(25*mm, y_pos, f"Notes: {sample_info.get('notes', 'N/A')}")
    
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
    c.drawString(25*mm, y_pos, f"Painted Pixels: {painted_pixels:,}  |  Total Pixels: {total_pixels:,}")
    
    y_pos -= 15*mm
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#1a1a2e"))
    c.drawString(25*mm, y_pos, "Micrographs")
    
    img_width = 75*mm
    img_height = 60*mm
    
    y_pos -= 8*mm
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.drawString(25*mm, y_pos, "Original Image")
    c.drawString(110*mm, y_pos, "Highlighted Pearlite")
    
    y_pos -= img_height + 5*mm
    
    orig_buffer = BytesIO()
    original_image.save(orig_buffer, format='PNG')
    orig_buffer.seek(0)
    c.drawImage(ImageReader(orig_buffer), 25*mm, y_pos, width=img_width, height=img_height, preserveAspectRatio=True)
    
    ann_buffer = BytesIO()
    annotated_image.save(ann_buffer, format='PNG')
    ann_buffer.seek(0)
    c.drawImage(ImageReader(ann_buffer), 110*mm, y_pos, width=img_width, height=img_height, preserveAspectRatio=True)
    
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.gray)
    c.drawCentredString(width/2, 15*mm, "Pearlite Phase Analyser")
    c.drawCentredString(width/2, 10*mm, f"Pearlite Fraction: {percentage:.2f}%")
    
    c.save()
    buffer.seek(0)
    return buffer

def calculate_percentage(canvas_result, image_size):
    """Calculate pearlite percentage from canvas."""
    if canvas_result is None or canvas_result.image_data is None:
        return 0.0, 0, 0
    
    alpha_channel = canvas_result.image_data[:, :, 3]
    painted_pixels = int(np.sum(alpha_channel > 50))
    total_pixels = image_size[0] * image_size[1]
    
    if total_pixels == 0:
        return 0.0, 0, 0
    
    percentage = (painted_pixels / total_pixels) * 100
    return percentage, painted_pixels, total_pixels

def main():
    st.markdown("""
    <div class="main-header">
        <h1>🔬 Pearlite Phase Analyser</h1>
        <p>Upload a microstructure image and highlight pearlite regions to calculate phase fraction</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎨 Painting Tools")
        
        tool_mode = st.radio(
            "Select Tool",
            ["✏️ Brush (Highlight)", "🧹 Eraser"],
            index=0
        )
        
        stroke_color = "rgba(220, 50, 50, 0.7)" if "Brush" in tool_mode else "rgba(0, 0, 0, 0)"
        
        st.markdown("---")
        st.markdown("### 🔘 Brush Size")
        brush_size = st.slider("Size (px)", 2, 50, 15)
        
        st.markdown("---")
        st.markdown("### 👁️ Visibility")
        show_overlay = st.checkbox("Show Paint Layer", value=True)
        
        st.markdown("---")
        st.markdown("### 📝 Sample Info (for report)")
        sample_id = st.text_input("Sample ID", placeholder="e.g., STEEL-001")
        operator = st.text_input("Operator", placeholder="Your name")
        notes = st.text_area("Notes", placeholder="Observations...", height=80)
        
        st.markdown("---")
        st.markdown("""
        ### 📖 How to Use
        1. Upload a microstructure image
        2. Select Brush tool
        3. Paint over pearlite (dark regions)
        4. Use Eraser to fix mistakes
        5. Generate PDF Report
        """)
    
    # Main area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "📤 Upload Microstructure Image",
            type=['png', 'jpg', 'jpeg', 'bmp', 'tiff']
        )
        
        if uploaded_file is not None:
            # Load image
            image = Image.open(uploaded_file).convert('RGB')
            
            # Canvas sizing
            max_width = 700
            max_height = 500
            img_w, img_h = image.size
            scale = min(max_width / img_w, max_height / img_h, 1.0)
            canvas_w = int(img_w * scale)
            canvas_h = int(img_h * scale)
            
            # Resize for display
            display_image = image.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
            
            # Convert to numpy array for canvas background
            bg_array = np.array(display_image)
            
            # Drawing canvas with numpy array background
            canvas_result = st_canvas(
                fill_color="rgba(0, 0, 0, 0)",
                stroke_width=brush_size,
                stroke_color=stroke_color if show_overlay else "rgba(0, 0, 0, 0)",
                background_image=Image.fromarray(bg_array),
                update_streamlit=True,
                height=canvas_h,
                width=canvas_w,
                drawing_mode="freedraw",
                key="canvas",
            )
            
            percentage, painted, total = calculate_percentage(canvas_result, (canvas_w, canvas_h))
        else:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #e8f4fd 0%, #d4e8f7 100%);
                border: 3px dashed #2196F3;
                border-radius: 15px;
                padding: 4rem 2rem;
                text-align: center;
            ">
                <h2 style="color: #1976D2;">📤 Upload an Image to Begin</h2>
                <p style="color: #666;">Drag and drop or click to browse</p>
                <p style="color: #888; font-size: 0.9rem;">PNG, JPG, JPEG, BMP, TIFF</p>
            </div>
            """, unsafe_allow_html=True)
            percentage, painted, total = 0.0, 0, 0
            canvas_result = None
            image = None
            canvas_w, canvas_h = 0, 0
    
    with col2:
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
        
        # Generate Report
        if uploaded_file is not None:
            if st.button("📄 Generate PDF Report", type="primary", use_container_width=True):
                with st.spinner("Generating..."):
                    try:
                        display_image = image.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
                        
                        if canvas_result is not None and canvas_result.image_data is not None:
                            canvas_array = canvas_result.image_data.astype(np.uint8)
                            canvas_img = Image.fromarray(canvas_array, 'RGBA')
                            annotated = display_image.copy().convert('RGBA')
                            annotated = Image.alpha_composite(annotated, canvas_img).convert('RGB')
                        else:
                            annotated = display_image
                        
                        sample_info = {
                            'sample_id': sample_id or 'N/A',
                            'operator': operator or 'N/A',
                            'notes': notes or 'N/A'
                        }
                        
                        pdf = create_pdf_report(display_image, annotated, percentage, painted, total, sample_info)
                        
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
        else:
            st.button("📄 Generate PDF Report", disabled=True, use_container_width=True)
        
        st.markdown("""
        <div style="
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 8px;
            padding: 0.8rem;
            font-size: 0.8rem;
            margin-top: 1rem;
        ">
            <strong>💡 Tips:</strong><br>
            • Brush highlights pearlite (dark regions)<br>
            • Adjust brush size for precision<br>
            • Toggle overlay to verify coverage
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
