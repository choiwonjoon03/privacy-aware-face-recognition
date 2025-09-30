# privacy-aware-face-recognition

_Reproducible benchmark of privacy-aware face recognition: multi-model similarity scoring & de-identification evaluation (FaceNet, DeepFace, AWS Rekognition, Face++)._

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)]()
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

[![CI](https://github.com/choiwonjoon03/privacy-aware-face-recognition/actions/workflows/ci.yml/badge.svg)](../../actions/workflows/ci.yml)


## ✨ What is this?
An end-to-end benchmark to evaluate **privacy-aware face recognition**.  
It compares an original face image against many **style/filtered variants**, computes **similarity scores** across multiple engines, and assesses **de-identification safety** with bucketed risk labels.

- Engines: **FaceNet**, **DeepFace**, **AWS Rekognition**, **Face++**
- Outputs: cleaned CSVs, ranked top/bottom lists, text summary (no images)
- Goals: reproducible pipeline → clear **privacy risk** interpretation

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
├─ data/
│  ├─ samples/      # small demo images (non-sensitive)
│  └─ .gitkeep
├─ results/
│  ├─ csv/
│  ├─ figures/
│  └─ .gitkeep
├─ .env.example     # API keys template (no secrets)
├─ requirements.txt
└─ README.md
```
---

## 🔧 Setup

1) Clon
```bash
git clone https://github.com/<YOUR-ACCOUNT>/privacy-aware-face-recognition.git
cd privacy-aware-face-recognition
```

3) Python Virtual Environment
Create and activate a Python virtual environment.

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

3) Install Dependencie
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

5) Set API Keys (Optional)
```bash
cp .env.example .env

Edit the .env file with your API keys (do not commit .env)
```
```
### 🖼️ Use with your own images
```bash
# Put your images in a folder. Example:
#  - source: myface.jpg
#  - variants: v1.jpg, v2.png, ...

# Facenet + DeepFace only (no API keys needed)
python src/cli.py --folder "C:/path/to/myfolder" --source "myface.jpg" --engines facenet,deepface

# All engines (AWS/Face++ keys required in .env)
python src/cli.py --folder "C:/path/to/myfolder" --source "myface.jpg" --engines facenet,deepface,aws,facepp
```


