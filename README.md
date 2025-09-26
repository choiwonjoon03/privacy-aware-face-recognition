# privacy-aware-face-recognition

_Reproducible benchmark of privacy-aware face recognition: multi-model similarity scoring & de-identification evaluation (FaceNet, DeepFace, AWS Rekognition, Face++)._

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)]()
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

## ✨ What is this?
An end-to-end benchmark to evaluate **privacy-aware face recognition**.  
It compares an original face image against many **style/filtered variants**, computes **similarity scores** across multiple engines, and assesses **de-identification safety** with bucketed risk labels.

- Engines: **FaceNet**, **DeepFace**, **AWS Rekognition**, **Face++**
- Outputs: cleaned CSVs, ranked top/bottom lists, summary tables, optional charts
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

---

## 🔧 Setup
```bash
# 1) clone
git clone https://github.com/<YOUR-ACCOUNT>/privacy-aware-face-recognition.git
cd privacy-aware-face-recognition

# 2) python venv
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

# 3) deps
pip install --upgrade pip
pip install -r requirements.txt

# 4) secrets (copy and edit)
cp .env.example .env
# then open .env to put your keys (never commit .env)
