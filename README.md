# 🧪 privacy-aware-face-recognition

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)
[![CI](https://github.com/felixcwj/privacy-aware-face-recognition/actions/workflows/ci.yml/badge.svg)](https://github.com/felixcwj/privacy-aware-face-recognition/actions/workflows/ci.yml)

---

## 📄 License
This project is licensed under the **MIT License**. See **[LICENSE](LICENSE)** for details.

---

## 🔍 What is this?
A **reproducible benchmark** for privacy‑aware face recognition:
- Compare an original face vs. **style/filtered variants**
- Compute **similarity scores** with multiple engines
- Assign **de‑identification risk buckets**

**Engines**: FaceNet, DeepFace, AWS Rekognition, Face++  
**Outputs**: cleaned CSVs, ranked lists, short text summary (no images)  
**Focus**: reproducibility (scriptable CLI, pinned dependencies)

---

## 🧱 Project Structure
```text
privacy-aware-face-recognition/
|-- src/
|   |-- compare/
|   |   |-- run_facenet_compare.py
|   |   |-- run_deepface_compare.py
|   |   |-- run_aws_compare.py
|   |   `-- run_facepp_compare.py
|   |-- utils/
|   |   |-- io_helpers.py
|   |   |-- filename_cleaner.py
|   |   `-- bucketer.py          # Safe / Buffer / Warning / High-Risk
|   `-- analysis/
|       |-- merge_4models.py
|       `-- make_report.py
|-- data/           # small demo images (non-sensitive) + .gitkeep
|-- results/
|   |-- csv/
|   |-- figures/
|   `-- .gitkeep
|-- .env.example
|-- requirements.txt
`-- README.md
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

- **Windows (PowerShell)**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```
> If blocked by policy: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

- **Windows (CMD)**
```bat
python -m venv venv
venv\Scripts\activate.bat
```

- **Windows (Git Bash)**
```bash
python -m venv venv
source venv\Scripts\activate
```

- **macOS / Linux**
```bash
python3 -m venv venv
source venv\bin\activate
```

### 3) Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4) Set API Keys (Optional)
**Step 1. Copy template → `.env`**
```bash
cp .env.example .env
```
**Step 2. Fill your keys in `.env`**
```dotenv
AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
FACEPP_API_KEY=YOUR_FACEPP_API_KEY
FACEPP_API_SECRET=YOUR_FACEPP_API_SECRET
```
**Step 3. Keep secrets out of Git**
```gitignore
# keep secrets local
.env
```

---

## 🖼️ Use with Your Own Images

### Folder layout (example)
```text
myfolder/
|-- myface.jpg          # source
|-- v1.jpg              # variant
`-- v2.png              # variant
```

## ✅ Run Commands (Copy/Paste Safe)

### Windows (PowerShell)
```powershell
python src/cli.py --folder "C:\path\to\myfolder" --source "myface.jpg" --engines facenet,deepface
python src/cli.py --folder "C:\path\to\myfolder" --source "myface.jpg" --engines facenet,deepface,aws,facepp
```

### Windows (CMD)
```bat
python src\cli.py --folder "C:\path\to\myfolder" --source "myface.jpg" --engines facenet,deepface
python src\cli.py --folder "C:\path\to\myfolder" --source "myface.jpg" --engines facenet,deepface,aws,facepp
```

### Windows (Git Bash, POSIX-style path)
```bash
python src/cli.py --folder "C:\path\to\myfolder" --source "myface.jpg" --engines facenet,deepface
python src/cli.py --folder "C:\path\to\myfolder" --source "myface.jpg" --engines facenet,deepface,aws,facepp
```

### macOS / Linux
```bash
python src/cli.py --folder "\Users\you\myfolder" --source "myface.jpg" --engines facenet,deepface
python src/cli.py --folder "\Users\you\myfolder" --source "myface.jpg" --engines facenet,deepface,aws,facepp
```
