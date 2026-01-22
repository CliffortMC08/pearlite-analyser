"""
Pearlite Phase Analyser - Web Application
Built with Gradio for reliable canvas drawing with automatic calculation.
"""

import gradio as gr
from PIL import Image
import numpy as np
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import tempfile
import os

def create_pdf_report(original_image, annotated_image, percentage, painted_pixels, total_pixels, sample_id, operator, notes):
    """Generate PDF report."""
    buffer = BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Title
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.HexColor("#1a1a2e"))
    c.drawCentredString(width/2, height - 40*mm, "Pearlite Phase Analyser Report")
    
    c.setStrokeColor(colors.HexColor("#4ade80"))
    c.setLineWidth(3)
    c.line(30*mm, height - 45*mm, width - 30*mm, height - 45*mm)
    
    # Sample Info
    y_pos = height - 60*mm
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#1a1a2e"))
    c.drawString(25*mm, y_pos, "Sample Information")
    
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.black)
    y_pos -= 8*mm
    c.drawString(25*mm, y_pos, f"Sample ID: {sample_id or 'N/A'}")
    y_pos -= 6*mm
    c.drawString(25*mm, y_pos, f"Operator: {operator or 'N/A'}")
    y_pos -= 6*mm
    c.drawString(25*mm, y_pos, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    y_pos -= 6*mm
    c.drawString(25*mm, y_pos, f"Notes: {notes or 'N/A'}")
    
    # Results
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
    
    # Images
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
    
    # Draw images
    if original_image is not None:
        orig_buf = BytesIO()
        original_image.save(orig_buf, format='PNG')
        orig_buf.seek(0)
        c.drawImage(ImageReader(orig_buf), 25*mm, y_pos, width=img_w, height=img_h, preserveAspectRatio=True)
    
    if annotated_image is not None:
        ann_buf = BytesIO()
        annotated_image.save(ann_buf, format='PNG')
        ann_buf.seek(0)
        c.drawImage(ImageReader(ann_buf), 110*mm, y_pos, width=img_w, height=img_h, preserveAspectRatio=True)
    
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.gray)
    c.drawCentredString(width/2, 15*mm, f"Pearlite Phase Analyser | {percentage:.2f}%")
    
    c.save()
    buffer.seek(0)
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_file.write(buffer.getvalue())
    temp_file.close()
    return temp_file.name

def calculate_pearlite(image_with_mask):
    """Calculate pearlite percentage from the drawn mask."""
    if image_with_mask is None:
        return "0.00%", "0", "0", None, None
    
    # image_with_mask is a dict with 'background', 'layers', 'composite'
    if isinstance(image_with_mask, dict):
        composite = image_with_mask.get('composite')
        background = image_with_mask.get('background')
        layers = image_with_mask.get('layers', [])
        
        if composite is not None:
            img_array = np.array(composite)
        elif len(layers) > 0 and layers[0] is not None:
            img_array = np.array(layers[0])
        else:
            return "0.00%", "0", "0", background, background
        
        # Count red-ish pixels (painted areas)
        if len(img_array.shape) == 3 and img_array.shape[2] >= 3:
            # Check for red color (R > 150, G < 100, B < 100) or alpha > 0 in RGBA
            if img_array.shape[2] == 4:
                # RGBA - check alpha channel for any drawing
                alpha = img_array[:, :, 3]
                red = img_array[:, :, 0]
                painted_mask = (alpha > 50) & (red > 100)
            else:
                # RGB - check for red color
                red = img_array[:, :, 0]
                green = img_array[:, :, 1]
                blue = img_array[:, :, 2]
                painted_mask = (red > 150) & (green < 150) & (blue < 150)
            
            painted_pixels = int(np.sum(painted_mask))
            total_pixels = img_array.shape[0] * img_array.shape[1]
            
            if total_pixels > 0:
                percentage = (painted_pixels / total_pixels) * 100
            else:
                percentage = 0.0
            
            return f"{percentage:.2f}%", f"{painted_pixels:,}", f"{total_pixels:,}", background, composite
    
    return "0.00%", "0", "0", None, None

def generate_report(image_with_mask, sample_id, operator, notes):
    """Generate PDF report."""
    if image_with_mask is None:
        return None
    
    pct_str, painted_str, total_str, original, annotated = calculate_pearlite(image_with_mask)
    
    percentage = float(pct_str.replace('%', ''))
    painted = int(painted_str.replace(',', ''))
    total = int(total_str.replace(',', ''))
    
    if original is None:
        if isinstance(image_with_mask, dict):
            original = image_with_mask.get('background')
    
    if original is not None:
        original_pil = Image.fromarray(np.array(original)) if not isinstance(original, Image.Image) else original
    else:
        original_pil = Image.new('RGB', (100, 100), 'white')
    
    if annotated is not None:
        annotated_pil = Image.fromarray(np.array(annotated)) if not isinstance(annotated, Image.Image) else annotated
    else:
        annotated_pil = original_pil
    
    pdf_path = create_pdf_report(
        original_pil.convert('RGB'),
        annotated_pil.convert('RGB'),
        percentage, painted, total,
        sample_id, operator, notes
    )
    
    return pdf_path

def update_calculation(image_with_mask):
    """Update calculation when drawing changes."""
    return calculate_pearlite(image_with_mask)[:3]

# Custom CSS
custom_css = """
.gradio-container {
    font-family: 'Segoe UI', sans-serif;
}
.main-header {
    text-align: center;
    padding: 20px;
    background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
    color: white;
    border-radius: 10px;
    margin-bottom: 20px;
}
.results-box {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: white;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
}
.percentage-display {
    font-size: 48px;
    font-weight: bold;
    color: #4ade80;
}
"""

# Build the interface
with gr.Blocks(css=custom_css, title="Pearlite Phase Analyser") as app:
    
    gr.HTML("""
    <div class="main-header">
        <h1>🔬 Pearlite Phase Analyser</h1>
        <p>Upload a microstructure image and paint over pearlite regions to calculate phase fraction</p>
    </div>
    """)
    
    with gr.Row():
        # Left column - Canvas
        with gr.Column(scale=3):
            image_editor = gr.ImageEditor(
                label="📤 Upload image and paint pearlite regions (use red brush)",
                type="numpy",
                brush=gr.Brush(colors=["#DC3232"], default_color="#DC3232", color_mode="fixed"),
                eraser=gr.Eraser(default_size=15),
                height=500,
                layers=False,
                transforms=[],
            )
            
            calc_btn = gr.Button("🔄 Calculate Percentage", variant="secondary", size="lg")
        
        # Right column - Results & Controls
        with gr.Column(scale=1):
            gr.Markdown("### 📊 Results")
            
            percentage_display = gr.Textbox(
                label="Pearlite Fraction",
                value="0.00%",
                interactive=False,
                elem_classes=["percentage-display"]
            )
            
            with gr.Row():
                painted_display = gr.Textbox(label="Painted (px)", value="0", interactive=False)
                total_display = gr.Textbox(label="Total (px)", value="0", interactive=False)
            
            gr.Markdown("---")
            gr.Markdown("### 📝 Sample Information")
            
            sample_id = gr.Textbox(label="Sample ID", placeholder="e.g., STEEL-001")
            operator = gr.Textbox(label="Operator", placeholder="Your name")
            notes = gr.Textbox(label="Notes", placeholder="Observations...", lines=2)
            
            gr.Markdown("---")
            
            report_btn = gr.Button("📄 Generate PDF Report", variant="primary", size="lg")
            report_file = gr.File(label="Download Report")
            
            gr.Markdown("""
            ---
            ### 💡 Instructions
            1. Upload microstructure image
            2. Use red brush to paint pearlite
            3. Use eraser to fix mistakes  
            4. Click Calculate to update %
            5. Generate PDF report
            """)
    
    # Event handlers
    calc_btn.click(
        fn=update_calculation,
        inputs=[image_editor],
        outputs=[percentage_display, painted_display, total_display]
    )
    
    image_editor.change(
        fn=update_calculation,
        inputs=[image_editor],
        outputs=[percentage_display, painted_display, total_display]
    )
    
    report_btn.click(
        fn=generate_report,
        inputs=[image_editor, sample_id, operator, notes],
        outputs=[report_file]
    )

# Launch
if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
