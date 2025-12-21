# OCR Setup for PDF Processing

Your PDFs contain **scanned images** without extractable text, so we need OCR (Optical Character Recognition).

## 🔧 Install Tesseract OCR with Hebrew Support (Required)

### Windows Installation Steps:

1. **Download Tesseract installer**:
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Click on the latest version link (e.g., `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)
   - Download the installer

2. **Run the installer with Hebrew language**:
   
   a. Double-click the downloaded `.exe` file
   
   b. Click "Next" through the initial screens
   
   c. **CRITICAL STEP - Select Languages**:
      - When you see the "Choose Components" screen
      - Expand "Additional language data (download)" 
      - Scroll down and **check the box for "Hebrew"** (עברית)
      - Also keep "English" checked
      - Click "Next"
   
   d. Choose installation location (default: `C:\Program Files\Tesseract-OCR\`)
   
   e. Click "Install"

3. **Add Tesseract to System PATH**:
   
   a. Press `Windows Key + R`, type `sysdm.cpl`, press Enter
   
   b. Go to "Advanced" tab → Click "Environment Variables"
   
   c. Under "System variables", find "Path" → Click "Edit"
   
   d. Click "New" and add: `C:\Program Files\Tesseract-OCR`
   
   e. Click "OK" on all windows
   
   f. **IMPORTANT**: Close and reopen PowerShell/VS Code terminal for changes to take effect

4. **Verify installation** (in a NEW terminal window):
   ```powershell
   tesseract --version
   ```
   You should see version information.

5. **Verify Hebrew is installed**:
   ```powershell
   tesseract --list-langs
   ```
   You should see:
   ```
   List of available languages (2):
   eng
   heb
   ```

### 📥 Alternative: Manual Hebrew Data Download

If you already installed Tesseract without Hebrew:

1. Download Hebrew data file from: https://github.com/tesseract-ocr/tessdata/raw/main/heb.traineddata
2. Copy `heb.traineddata` to: `C:\Program Files\Tesseract-OCR\tessdata\`
3. Restart your terminal

## 🚀 Run the OCR-enabled script

After installing Tesseract:

```powershell
python pdf_to_supabase_ocr.py
```

## 🔍 What's Different?

- **Old script** (`pdf_to_supabase.py`): Only extracts existing text from PDFs
- **New OCR script** (`pdf_to_supabase_ocr.py`): Uses OCR to read text from scanned images

## ⚠️ Notes

- OCR processing is slower than direct text extraction
- OCR accuracy depends on image quality
- Hebrew OCR requires the Hebrew language data to be installed
- The script will process ~22 pages with OCR, which may take a few minutes
