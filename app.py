"""
app.py
Streamlit UI for the DDR Report Generation System.
Run with: streamlit run app.py
"""

import streamlit as st
import os
import tempfile
import shutil
from dotenv import load_dotenv

from extractor import extract_from_pdf
from ddr_generator import generate_ddr
from report_builder import build_docx_report

load_dotenv()

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DDR Report Generator",
    page_icon="🏗️",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1A568C;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .step-box {
        background: #f0f6ff;
        border-left: 4px solid #1A568C;
        padding: 1rem 1.2rem;
        border-radius: 6px;
        margin-bottom: 1rem;
    }
    .success-box {
        background: #f0fff4;
        border-left: 4px solid #4CAF50;
        padding: 1rem 1.2rem;
        border-radius: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🏗️ DDR Report Generator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">AI-powered Detailed Diagnostic Report generation from inspection + thermal PDFs</div>',
    unsafe_allow_html=True,
)
st.divider()

# ── Sidebar: API Key ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key_input = st.text_input(
        "Gemini API Key",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        type="password",
        help="Get your key from console.anthropic.com",
    )
    property_name = st.text_input(
        "Property / Project Name",
        value="Property Inspection Report",
        help="This will appear on the cover page",
    )
    st.divider()
    st.markdown("**How it works:**")
    st.markdown("""
    1. Upload both PDFs  
    2. Click **Generate DDR**  
    3. Claude extracts + merges data  
    4. Download your .docx report  
    """)
    st.info("Powered by Google Gemini 1.5 Flash (Free)")

# ── Upload Section ────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="step-box"><b>📄 Step 1: Upload Inspection Report</b></div>', unsafe_allow_html=True)
    inspection_file = st.file_uploader(
        "Inspection Report PDF",
        type=["pdf"],
        key="inspection",
        label_visibility="collapsed",
    )
    if inspection_file:
        st.success(f"✅ {inspection_file.name} uploaded")

with col2:
    st.markdown('<div class="step-box"><b>🌡️ Step 2: Upload Thermal Report</b></div>', unsafe_allow_html=True)
    thermal_file = st.file_uploader(
        "Thermal Report PDF",
        type=["pdf"],
        key="thermal",
        label_visibility="collapsed",
    )
    if thermal_file:
        st.success(f"✅ {thermal_file.name} uploaded")

st.divider()

# ── Generate Button ───────────────────────────────────────────────────────────
st.markdown('<div class="step-box"><b>🚀 Step 3: Generate the DDR Report</b></div>', unsafe_allow_html=True)

generate_btn = st.button(
    "⚡ Generate DDR Report",
    type="primary",
    disabled=not (inspection_file and thermal_file and api_key_input),
    use_container_width=True,
)

if not inspection_file or not thermal_file:
    st.caption("⬆️ Please upload both PDFs to enable generation.")
if not api_key_input:
    st.caption("🔑 Please enter your Anthropic API key in the sidebar.")

# ── Processing ────────────────────────────────────────────────────────────────
if generate_btn:
    work_dir = tempfile.mkdtemp(prefix="ddr_")
    insp_img_dir = os.path.join(work_dir, "inspection_images")
    therm_img_dir = os.path.join(work_dir, "thermal_images")
    output_docx = os.path.join(work_dir, "DDR_Report.docx")

    try:
        progress_bar = st.progress(0, text="Starting...")
        status_area = st.empty()

        # Save uploaded files temporarily
        insp_path = os.path.join(work_dir, "inspection.pdf")
        therm_path = os.path.join(work_dir, "thermal.pdf")
        with open(insp_path, "wb") as f:
            f.write(inspection_file.read())
        with open(therm_path, "wb") as f:
            f.write(thermal_file.read())

        # Step 1: Extract inspection PDF
        status_area.info("📄 Extracting Inspection Report (text + images)...")
        progress_bar.progress(15, text="Extracting inspection report...")
        inspection_data = extract_from_pdf(insp_path, insp_img_dir)
        st.write(
            f"✅ Inspection: {len(inspection_data['pages'])} pages, "
            f"{len(inspection_data['images'])} images extracted"
        )

        # Step 2: Extract thermal PDF
        status_area.info("🌡️ Extracting Thermal Report (text + images)...")
        progress_bar.progress(30, text="Extracting thermal report...")
        thermal_data = extract_from_pdf(therm_path, therm_img_dir)
        st.write(
            f"✅ Thermal: {len(thermal_data['pages'])} pages, "
            f"{len(thermal_data['images'])} images extracted"
        )

        # Step 3: Generate DDR via Claude
        status_area.info("🤖 Sending to Claude API for DDR generation (may take 30-60 sec)...")
        progress_bar.progress(50, text="Claude is analyzing and writing the DDR...")

        def update_status(msg):
            status_area.info(f"🤖 {msg}")

        ddr_text = generate_ddr(
            inspection_data=inspection_data,
            thermal_data=thermal_data,
            api_key=api_key_input,
            progress_callback=update_status,
        )
        progress_bar.progress(80, text="DDR generated, building Word document...")

        # Step 4: Build Word document
        status_area.info("📝 Building Word document with images...")
        build_docx_report(
            ddr_text=ddr_text,
            inspection_images=inspection_data["images"],
            thermal_images=thermal_data["images"],
            output_path=output_docx,
            property_name=property_name,
        )
        progress_bar.progress(100, text="Done!")
        status_area.empty()

        # ── Success UI ────────────────────────────────────────────────
        st.success("🎉 DDR Report Generated Successfully!")

        col_a, col_b = st.columns(2)
        with col_a:
            with open(output_docx, "rb") as f:
                st.download_button(
                    label="📥 Download DDR Report (.docx)",
                    data=f,
                    file_name=f"DDR_{property_name.replace(' ', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    type="primary",
                )

        # Show DDR text preview
        with st.expander("👁️ Preview DDR Text (Markdown)", expanded=True):
            st.markdown(ddr_text)

        # Show image counts
        with st.expander(f"🖼️ Extracted Images Summary"):
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Inspection Images", len(inspection_data["images"]))
                for img in inspection_data["images"]:
                    st.caption(f"📷 {img['filename']} (pg {img['page_num']}, {img['size'][0]}×{img['size'][1]})")
            with c2:
                st.metric("Thermal Images", len(thermal_data["images"]))
                for img in thermal_data["images"]:
                    st.caption(f"🌡️ {img['filename']} (pg {img['page_num']}, {img['size'][0]}×{img['size'][1]})")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.exception(e)
    finally:
        # Clean up temp files (keep docx for download)
        pass

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("DDR Report Generator | Built with Gemini 1.5 Flash + PyMuPDF + python-docx")
