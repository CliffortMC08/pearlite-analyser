"""
Pearlite Phase Analyser - Professional Web Application
"""

import streamlit as st
from PIL import Image
from io import BytesIO
import base64
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Pearlite Phase Analyser",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

def image_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

# Professional CSS styling - Grey/White theme
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main background */
    .stApp {
        background: #f8f9fa;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
        padding-top: 1rem;
    }
    [data-testid="stSidebar"] * {
        color: #374151 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        background: #f3f4f6;
        padding: 10px 15px;
        border-radius: 8px;
        margin: 3px 0;
        transition: all 0.2s;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: #e5e7eb;
    }
    
    /* Header styling */
    .main-header {
        background: #ffffff;
        padding: 25px 40px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e5e7eb;
    }
    .main-header h1 {
        color: #1f2937;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #6b7280;
        font-size: 1rem;
        margin: 8px 0 0 0;
    }
    .header-badge {
        display: inline-block;
        background: #374151;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 12px;
        vertical-align: middle;
    }
    
    /* Hide default file uploader styling */
    [data-testid="stFileUploader"] {
        background: transparent !important;
    }
    [data-testid="stFileUploader"] > div {
        padding: 0 !important;
    }
    [data-testid="stFileUploader"] section {
        background: #ffffff;
        border: 2px dashed #d1d5db;
        border-radius: 12px;
        padding: 25px;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: #9ca3af;
        background: #f9fafb;
    }
    
    /* Card styling */
    .info-card {
        background: #f9fafb;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #e5e7eb;
        margin-bottom: 15px;
    }
    .info-card h4 {
        color: #1f2937;
        margin: 0 0 10px 0;
        font-size: 1rem;
    }
    .info-card p {
        color: #6b7280;
        margin: 0;
        font-size: 0.85rem;
        line-height: 1.5;
    }
    
    /* Button styling */
    .stButton > button {
        background: #374151 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background: #4b5563 !important;
        box-shadow: 0 4px 12px rgba(55, 65, 81, 0.25) !important;
    }
    
    /* Slider styling */
    .stSlider > div > div {
        background: #6b7280 !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🔬 Pearlite Phase Analyser <span class="header-badge">v2.0</span></h1>
    <p>Professional metallographic phase fraction analysis tool</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎨 Drawing Tools")
    tool = st.radio("Select Tool", ["🖌️ Brush", "🧹 Eraser"], label_visibility="collapsed")
    tool = "Brush" if "Brush" in tool else "Eraser"
    
    st.markdown("### 📏 Brush Size")
    brush_size = st.slider("Size", 2, 50, 15, label_visibility="collapsed")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        clear_canvas = st.button("🗑️ Clear", use_container_width=True)
    with col2:
        undo_action = st.button("↩️ Undo", use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("### 📖 Quick Guide")
    st.markdown("""
    <div class="info-card">
        <p>
        <strong>1.</strong> Upload your micrograph<br>
        <strong>2.</strong> Paint over pearlite regions<br>
        <strong>3.</strong> View real-time calculations<br>
        <strong>4.</strong> Use eraser to correct mistakes
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ⌨️ Shortcuts")
    st.markdown("""
    <div class="info-card">
        <p>
        <strong>B</strong> - Brush tool<br>
        <strong>E</strong> - Eraser tool<br>
        <strong>[ ]</strong> - Brush size<br>
        <strong>C</strong> - Clear canvas
        </p>
    </div>
    """, unsafe_allow_html=True)

# Main content
uploaded = st.file_uploader(
    "Drop your microstructure image here or click to browse",
    type=["png", "jpg", "jpeg", "bmp", "tiff"],
    label_visibility="collapsed"
)

if uploaded:
    # Track image to detect new uploads
    current_image_key = f"{uploaded.name}_{uploaded.size}"
    
    if 'last_image_key' not in st.session_state or st.session_state.last_image_key != current_image_key:
        st.session_state.last_image_key = current_image_key
        st.session_state.clear_canvas = True
    
    if clear_canvas:
        st.session_state.clear_canvas = True
    
    should_clear = st.session_state.get('clear_canvas', False)
    if should_clear:
        st.session_state.clear_canvas = False
    
    do_undo = undo_action
    
    img = Image.open(uploaded).convert("RGB")
    max_w, max_h = 900, 600
    scale = min(max_w/img.width, max_h/img.height, 1.0)
    cw, ch = int(img.width * scale), int(img.height * scale)
    display_img = img.resize((cw, ch), Image.Resampling.LANCZOS)
    img_b64 = image_to_base64(display_img)
    
    stroke_color = "rgba(220,50,50,0.7)" if tool == "Brush" else "rgba(0,0,0,0)"
    eraser_mode = "true" if tool == "Eraser" else "false"
    total_px = cw * ch
    clear_js = "localStorage.removeItem('pearliteCanvas'); localStorage.removeItem('pearliteHistory');" if should_clear else ""
    undo_js = "undoLast();" if do_undo else ""
    
    canvas_html = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            box-sizing: border-box;
        }}
        
        .canvas-wrapper {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 15px;
        }}
        
        #canvas-container {{
            position: relative;
            width: {cw}px;
            height: {ch}px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            border: 1px solid #e5e7eb;
        }}
        
        #bgImage {{
            position: absolute;
            top: 0;
            left: 0;
            width: {cw}px;
            height: {ch}px;
            z-index: 1;
        }}
        
        #drawCanvas {{
            position: absolute;
            top: 0;
            left: 0;
            z-index: 2;
            cursor: crosshair;
        }}
        
        .results-panel {{
            width: {cw}px;
            background: #ffffff;
            border-radius: 10px;
            padding: 20px 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border: 1px solid #e5e7eb;
        }}
        
        .result-main {{
            text-align: left;
            flex-shrink: 0;
        }}
        
        .result-label {{
            color: #6b7280;
            font-size: 12px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        
        .result-value {{
            color: #1f2937;
            font-size: 32px;
            font-weight: 700;
            line-height: 1;
        }}
        
        .result-details {{
            text-align: right;
            flex-shrink: 0;
        }}
        
        .detail-row {{
            color: #6b7280;
            font-size: 13px;
            margin: 3px 0;
        }}
        
        .detail-value {{
            color: #374151;
            font-weight: 600;
        }}
        
        .progress-bar {{
            width: {cw}px;
            height: 6px;
            background: #e5e7eb;
            border-radius: 3px;
            overflow: hidden;
        }}
        
        .progress-fill {{
            height: 100%;
            background: #6b7280;
            border-radius: 3px;
            transition: width 0.3s ease;
            width: 0%;
        }}
        
        .toolbar {{
            width: {cw}px;
            background: #ffffff;
            border-radius: 8px;
            padding: 10px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border: 1px solid #e5e7eb;
        }}
        
        .tool-indicator {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .tool-badge {{
            background: {"#fef2f2" if tool == "Brush" else "#f3f4f6"};
            color: {"#dc2626" if tool == "Brush" else "#374151"};
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .size-indicator {{
            color: #6b7280;
            font-size: 12px;
        }}
        
        .image-name {{
            color: #9ca3af;
            font-size: 12px;
            max-width: 180px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
    </style>
    
    <div class="canvas-wrapper">
        <div class="toolbar">
            <div class="tool-indicator">
                <span class="tool-badge">{"🖌️ Brush" if tool == "Brush" else "🧹 Eraser"}</span>
                <span class="size-indicator">Size: {brush_size}px</span>
            </div>
            <span class="image-name">📁 {uploaded.name}</span>
        </div>
        
        <div id="canvas-container">
            <img id="bgImage" src="data:image/png;base64,{img_b64}">
            <canvas id="drawCanvas" width="{cw}" height="{ch}"></canvas>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" id="progressFill"></div>
        </div>
        
        <div class="results-panel">
            <div class="result-main">
                <div class="result-label">Pearlite Fraction</div>
                <div class="result-value" id="percentDisplay">0.00%</div>
            </div>
            <div class="result-details">
                <div class="detail-row">Painted: <span class="detail-value" id="paintedDisplay">0</span> px</div>
                <div class="detail-row">Total: <span class="detail-value">{total_px:,}</span> px</div>
            </div>
        </div>
    </div>
    
    <script>
    {clear_js}
    
    const canvas = document.getElementById('drawCanvas');
    const ctx = canvas.getContext('2d');
    let isDrawing = false;
    let lastX = 0, lastY = 0;
    let history = [];
    const maxHistory = 20;
    
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.lineWidth = {brush_size};
    ctx.strokeStyle = '{stroke_color}';
    ctx.globalCompositeOperation = {eraser_mode} ? 'destination-out' : 'source-over';
    
    // Load saved canvas
    const saved = localStorage.getItem('pearliteCanvas');
    if (saved) {{
        const img = new Image();
        img.onload = function() {{ 
            ctx.drawImage(img, 0, 0); 
            updateCount(); 
            saveToHistory();
        }};
        img.src = saved;
    }}
    
    function saveToHistory() {{
        history.push(canvas.toDataURL());
        if (history.length > maxHistory) history.shift();
        localStorage.setItem('pearliteHistory', JSON.stringify(history));
    }}
    
    function undoLast() {{
        if (history.length > 1) {{
            history.pop();
            const lastState = history[history.length - 1];
            const img = new Image();
            img.onload = function() {{
                ctx.clearRect(0, 0, {cw}, {ch});
                ctx.drawImage(img, 0, 0);
                localStorage.setItem('pearliteCanvas', canvas.toDataURL());
                updateCount();
            }};
            img.src = lastState;
        }} else {{
            ctx.clearRect(0, 0, {cw}, {ch});
            history = [];
            localStorage.removeItem('pearliteCanvas');
            updateCount();
        }}
    }}
    
    {undo_js}
    
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
            localStorage.setItem('pearliteCanvas', canvas.toDataURL());
            saveToHistory();
            updateCount();
        }}
    }}
    
    function updateCount() {{
        const imageData = ctx.getImageData(0, 0, {cw}, {ch});
        let count = 0;
        for (let i = 3; i < imageData.data.length; i += 4) {{
            if (imageData.data[i] > 50) count++;
        }}
        const pct = ((count / {total_px}) * 100);
        document.getElementById('percentDisplay').textContent = pct.toFixed(2) + '%';
        document.getElementById('paintedDisplay').textContent = count.toLocaleString();
        document.getElementById('progressFill').style.width = pct + '%';
    }}
    
    canvas.addEventListener('mousedown', startDraw);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDraw);
    canvas.addEventListener('mouseout', stopDraw);
    canvas.addEventListener('touchstart', startDraw);
    canvas.addEventListener('touchmove', draw);
    canvas.addEventListener('touchend', stopDraw);
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {{
        if (e.key === 'c' || e.key === 'C') {{
            ctx.clearRect(0, 0, {cw}, {ch});
            localStorage.removeItem('pearliteCanvas');
            history = [];
            updateCount();
        }}
    }});
    
    updateCount();
    </script>
    """
    
    components.html(canvas_html, height=ch + 220)

else:
    # Clean upload prompt
    st.markdown("""
    <div style="
        background: #ffffff;
        border: 2px dashed #d1d5db;
        border-radius: 12px;
        padding: 50px 40px;
        text-align: center;
        margin: 20px auto;
        max-width: 500px;
    ">
        <div style="font-size: 3rem; margin-bottom: 15px;">📤</div>
        <h3 style="color: #1f2937; margin-bottom: 8px; font-size: 1.3rem; font-weight: 600;">Upload Your Micrograph</h3>
        <p style="color: #6b7280; margin-bottom: 20px; font-size: 0.95rem;">
            Drag and drop or click above to browse
        </p>
        <p style="color: #9ca3af; font-size: 0.85rem;">
            PNG, JPG, JPEG, BMP, TIFF
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: #ffffff; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #e5e7eb;">
            <div style="font-size: 2rem; margin-bottom: 12px;">🎯</div>
            <h4 style="color: #1f2937; margin-bottom: 6px; font-size: 0.95rem; font-weight: 600;">Precise Analysis</h4>
            <p style="color: #6b7280; font-size: 0.85rem; line-height: 1.4;">Pixel-level accuracy for reliable measurements</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #ffffff; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #e5e7eb;">
            <div style="font-size: 2rem; margin-bottom: 12px;">⚡</div>
            <h4 style="color: #1f2937; margin-bottom: 6px; font-size: 0.95rem; font-weight: 600;">Real-Time Results</h4>
            <p style="color: #6b7280; font-size: 0.85rem; line-height: 1.4;">See calculations update instantly</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: #ffffff; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #e5e7eb;">
            <div style="font-size: 2rem; margin-bottom: 12px;">🖌️</div>
            <h4 style="color: #1f2937; margin-bottom: 6px; font-size: 0.95rem; font-weight: 600;">Easy to Use</h4>
            <p style="color: #6b7280; font-size: 0.85rem; line-height: 1.4;">Intuitive brush and eraser tools</p>
        </div>
        """, unsafe_allow_html=True)
