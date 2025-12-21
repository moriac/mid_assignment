# Quick Guide: Installing Tesseract with Hebrew

## 📥 Step-by-Step Installation

### 1. Download
Visit: https://github.com/UB-Mannheim/tesseract/wiki
Download: `tesseract-ocr-w64-setup-v5.3.3.20231005.exe` (or latest version)

### 2. Install with Hebrew Language Support

**During installation:**
```
┌─────────────────────────────────────────┐
│  Choose Components                      │
├─────────────────────────────────────────┤
│  ☑ Tesseract OCR                        │
│  ☑ English language data                │
│  ▼ Additional language data (download)  │  ← Click to expand
│     ☐ Arabic                            │
│     ☐ Chinese - Simplified              │
│     ☐ French                            │
│     ☑ Hebrew                            │  ← CHECK THIS BOX!
│     ☐ Spanish                           │
│     ...                                 │
└─────────────────────────────────────────┘
```

**IMPORTANT**: Scroll through the language list and check **Hebrew** (עברית)

### 3. Add to PATH

After installation, add to your system PATH:

**Quick Method:**
1. Press `Win + R`
2. Type: `sysdm.cpl` and press Enter
3. Click "Advanced" tab
4. Click "Environment Variables"
5. Edit "Path" under System variables
6. Add: `C:\Program Files\Tesseract-OCR`
7. Click OK everywhere

### 4. Restart Terminal

**CRITICAL**: Close and reopen your PowerShell/VS Code terminal!

### 5. Verify

In a NEW terminal window:
```powershell
# Check version
tesseract --version

# Check languages - should show both eng and heb
tesseract --list-langs
```

Expected output:
```
List of available languages (2):
eng
heb
```

### 6. Run the OCR Script

```powershell
python pdf_to_supabase_ocr.py
```

---

## 🔧 Troubleshooting

**Problem**: `tesseract: command not found`
- **Solution**: Restart your terminal, or add `C:\Program Files\Tesseract-OCR` to PATH manually

**Problem**: Hebrew not in language list
- **Solution**: 
  1. Download: https://github.com/tesseract-ocr/tessdata/raw/main/heb.traineddata
  2. Save to: `C:\Program Files\Tesseract-OCR\tessdata\heb.traineddata`
  3. Restart terminal

**Problem**: Still no Hebrew
- **Solution**: Reinstall Tesseract and carefully select Hebrew during installation
