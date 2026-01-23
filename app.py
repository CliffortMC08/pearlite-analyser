"""
Pearlite Phase Analyser - Web Application
Image with canvas overlay.
"""

import streamlit as st
from PIL import Image
from io import BytesIO
import base64
import streamlit.components.v1 as components

st.set_page_config(page_title="Pearlite Phase Analyser", layout="wide")

def image_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

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
    clear_canvas = st.button("🗑️ Clear All", use_container_width=True)

# Custom CSS to change file uploader button text
st.markdown("""
<style>
    [data-testid="stFileUploader"] button {
        display: none;
    }
    [data-testid="stFileUploader"] section {
        padding: 0;
    }
    [data-testid="stFileUploader"] section > input + div {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Main
uploaded = st.file_uploader("Upload Microstructure Image", type=["png", "jpg", "jpeg", "bmp", "tiff"])

if uploaded:
    # Track image to detect new uploads
    current_image_key = f"{uploaded.name}_{uploaded.size}"
    
    # Check if new image uploaded
    if 'last_image_key' not in st.session_state or st.session_state.last_image_key != current_image_key:
        st.session_state.last_image_key = current_image_key
        st.session_state.clear_canvas = True
    
    # Check if Clear All button pressed
    if clear_canvas:
        st.session_state.clear_canvas = True
    
    should_clear = st.session_state.get('clear_canvas', False)
    if should_clear:
        st.session_state.clear_canvas = False
    
    img = Image.open(uploaded).convert("RGB")
    max_w, max_h = 800, 550
    scale = min(max_w/img.width, max_h/img.height, 1.0)
    cw, ch = int(img.width * scale), int(img.height * scale)
    display_img = img.resize((cw, ch), Image.Resampling.LANCZOS)
    img_b64 = image_to_base64(display_img)
    
    stroke_color = "rgba(220,50,50,0.7)" if tool == "Brush" else "rgba(0,0,0,0)"
    eraser_mode = "true" if tool == "Eraser" else "false"
    total_px = cw * ch
    clear_js = "localStorage.removeItem('pearliteCanvas');" if should_clear else ""
    
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
    
    <script>
    {clear_js}
    
    const canvas = document.getElementById('drawCanvas');
    const ctx = canvas.getContext('2d');
    let isDrawing = false;
    let lastX = 0, lastY = 0;
    
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.lineWidth = {brush_size};
    ctx.strokeStyle = '{stroke_color}';
    ctx.globalCompositeOperation = {eraser_mode} ? 'destination-out' : 'source-over';
    
    const saved = localStorage.getItem('pearliteCanvas');
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
            localStorage.setItem('pearliteCanvas', canvas.toDataURL());
            updateCount();
        }}
    }}
    
    function updateCount() {{
        const imageData = ctx.getImageData(0, 0, {cw}, {ch});
        let count = 0;
        for (let i = 3; i < imageData.data.length; i += 4) {{
            if (imageData.data[i] > 50) count++;
        }}
        const pct = ((count / {total_px}) * 100).toFixed(2);
        document.getElementById('percentDisplay').textContent = pct + '%';
        document.getElementById('paintedDisplay').textContent = 'Painted: ' + count.toLocaleString() + ' px';
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
    
    components.html(canvas_html, height=ch+80)
else:
    st.info("Upload a microstructure image to begin")
