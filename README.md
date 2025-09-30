# privacy-aware-face-recognition

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)
[![CI](https://github.com/felixcwj/privacy-aware-face-recognition/actions/workflows/ci.yml/badge.svg)](https://github.com/felixcwj/privacy-aware-face-recognition/actions/workflows/ci.yml)

---

## 📄 License
This project is licensed under the **MIT License**. See **[LICENSE](LICENSE)** for details.

---

## ✨ What is this?
Reproducible benchmark for **privacy-aware face recognition**. It compares an original face image against **style/filtered variants**, computes **similarity scores** across multiple engines, and assigns **de‑identification risk buckets**.
- Engines: **FaceNet**, **DeepFace**, **AWS Rekognition**, **Face++**
- Outputs: cleaned CSVs, ranked lists, brief text summary (no images)
- Focus: **reproducibility** (scriptable CLI, pinned deps)

---

## 📦 Project Structure
```text
privacy-aware-face-recognition/
├─ src/
│  ├─ compare/
│  │  ├─ run_facenet_compare.py
│  │  ├─ run_deepface_compare.py
│  │  ├─ run_aws_compare.py
│  │  └─ run_facepp_compare.py
│  ├─ utils/
│  │  ├─ io_helpers.py
│  │  ├─ filename_cleaner.py
│  │  └─ bucketer.py          # Safe / Buffer / Warning / High-Risk
│  └─ analysis/
│     ├─ merge_4models.py
│     └─ make_report.py
├─ data/           # small demo images (non-sensitive) + .gitkeep
├─ results/
│  ├─ csv/
│  ├─ figures/
│  └─ .gitkeep
├─ .env.example
├─ requirements.txt
└─ README.md
```

---

## 🔧 Setup

### 1) Clone
```bash
git clone https://github.com/felixcwj/privacy-aware-face-recognition.git
cd privacy-aware-face-recognition
```

### 2) Python Virtual Environment
Create and activate a Python virtual environment.

- **Windows (PowerShell):**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

- **Windows (CMD):**
```bash
python -m venv venv
venv\Scripts\activate.bat
```

- **Windows (Git Bash):**
```bash
python -m venv venv
source venv/Scripts/activate
```

- **macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3) Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4) Set API Keys (Optional)
```bash
cp .env.example .env
# Edit .env with your keys (do NOT commit .env)
# AWS_ACCESS_KEY_ID=...
# AWS_SECRET_ACCESS_KEY=...
# FACEPP_API_KEY=...
# FACEPP_API_SECRET=...
```

---

## 🖼️ Use with Your Own Images

### Folder layout (example)
```text
myfolder/
├─ myface.jpg          # source
├─ v1.jpg              # variant
└─ v2.png              # variant
```

### Run (no cloud APIs: Facenet + DeepFace)
```bash
python src/cli.py --folder "C:/path/to/myfolder" --source "myface.jpg" --engines facenet,deepface
```

### Run (all engines: requires keys in .env)
```bash
python src/cli.py --folder "C:/path/to/myfolder" --source "myface.jpg" --engines facenet,deepface,aws,facepp
```

### Notes
- Put **myface.jpg** and its variants (**v1.jpg**, **v2.png**, …) under the same folder.
- For macOS/Linux, replace the Windows path with a POSIX path, for example:
```bash
python src/cli.py --folder "/Users/you/myfolder" --source "myface.jpg" --engines facenet,deepface
```
