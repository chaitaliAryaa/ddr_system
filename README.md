# 🏗️ DDR Report Generator

AI-powered system that reads inspection + thermal PDFs and generates a structured **Detailed Diagnostic Report (DDR)** using Claude claude-opus-4-5.

---

## 📁 Project Structure

```
ddr_system/
├── app.py              → Streamlit web UI (main app)
├── run_cli.py          → Command-line version
├── extractor.py        → PDF text + image extraction (PyMuPDF)
├── ddr_generator.py    → Claude API integration
├── report_builder.py   → Word document builder (python-docx)
├── requirements.txt    → Python dependencies
├── .env.example        → API key template
└── README.md
```

---

## ⚡ Quick Setup (5 Minutes)

### Step 1: Install Python
Make sure Python 3.10+ is installed.
```bash
python --version
```
If not installed, download from https://www.python.org/downloads/

---

### Step 2: Create project folder & copy files
```bash
mkdir ddr_system
cd ddr_system
# Copy all the project files here
```

---

### Step 3: Create virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

---

### Step 4: Install dependencies
```bash
pip install -r requirements.txt
```

---

### Step 5: Set your API key
```bash
# Copy the example file
cp .env.example .env

# Edit .env and paste your Anthropic API key:
# ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxx
```
Get your API key from: https://console.anthropic.com/

---

## 🚀 Run the App

### Option A: Web UI (Recommended for demo)
```bash
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

**Steps in the UI:**
1. Enter your API key in the sidebar (or set it in .env)
2. Upload the Inspection Report PDF
3. Upload the Thermal Report PDF
4. Click **Generate DDR Report**
5. Download the .docx file

---

### Option B: Command Line
```bash
python run_cli.py \
  --inspection "path/to/inspection_report.pdf" \
  --thermal "path/to/thermal_report.pdf" \
  --output "DDR_Final.docx" \
  --property "123 Main Street Property"
```

---

## 📊 What It Does

```
[Inspection PDF] ──┐
                    ├──► [Extract Text + Images] ──► [Claude claude-opus-4-5 API] ──► [Word Document]
[Thermal PDF]    ──┘         (PyMuPDF)                  (DDR Generation)             (python-docx)
```

1. **Extract** – Pulls all text and images from both PDFs page by page
2. **Analyze** – Sends everything to Claude claude-opus-4-5 with vision capabilities
3. **Generate** – Claude writes a structured DDR with all 7 required sections
4. **Build** – Creates a professional .docx report with embedded images

---

## 📋 DDR Output Sections

1. Property Issue Summary
2. Area-wise Observations (with images)
3. Probable Root Cause
4. Severity Assessment (color-coded table)
5. Recommended Actions
6. Additional Notes
7. Missing or Unclear Information

---

## ⚙️ How It Handles Edge Cases

| Scenario | Behavior |
|----------|----------|
| Missing information | Writes "Not Available" |
| Conflicting data | Explicitly mentions the conflict |
| No images in PDF | Writes "Image Not Available" |
| Tiny/icon images (<50px) | Automatically skipped |
| Very large images | Auto-resized to fit page |

---

## 🔧 Limitations & Future Improvements

**Current Limitations:**
- Requires Anthropic API (paid usage for large documents)
- Processing time: 30-60 seconds per report
- Works best with text-based PDFs (not scanned image PDFs without OCR)

**Future Improvements:**
- OCR support for scanned PDFs (pytesseract)
- Batch processing multiple reports
- PDF output in addition to .docx
- Comparison view (before/after reports)
- Local LLM support (Ollama) for privacy

---

## 🎥 Loom Video Script

**[0:00-0:30] What I built:**
"I built an AI system that takes two PDF documents — an inspection report and a thermal report — and automatically generates a structured Detailed Diagnostic Report."

**[0:30-1:30] How it works:**
1. Show the upload UI
2. Demonstrate uploading both PDFs
3. Click generate and show the progress
4. Show the downloaded .docx with images

**[1:30-2:30] Architecture walkthrough:**
Show the 4 files and explain each module briefly.

**[2:30-3:30] Limitations + improvements:**
Mention the edge cases table above.
