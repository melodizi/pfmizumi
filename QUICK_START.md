# ⚡ Quick Start - ติดตั้งและใช้งานอย่างรวดเร็ว

## 🔥 ทำในเครื่องใหม่ (บน Windows/Mac/Linux)

### 1️⃣ ดาวน์โหลดและเตรียมเครื่อง

```bash
# ลงเครื่องโปรเจค (Copy folder ใหม่)
cd /path/to/where/you/want/it
git clone https://github.com/YOUR_USERNAME/chatbot-analyzer.git
cd chatbot-analyzer
```

**หรือ ดาวน์โหลด ZIP:**
- ไปที่ GitHub → Click "Code" → "Download ZIP"
- แตกไฟล์

### 2️⃣ ติดตั้ง Python (ถ้ายังไม่มี)

**Windows:**
- ไปที่ https://www.python.org/downloads/
- Download Python 3.9 หรือ 3.10 หรือ 3.13
- ติดตั้ง + **เก้ว "Add Python to PATH"**

**macOS:**
```bash
brew install python3
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install python3 python3-pip python3-venv
```

ตรวจสอบ:
```bash
python --version  # ต้องเป็น Python 3.8+
pip --version
```

### 3️⃣ สร้าง Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4️⃣ ติดตั้ง Packages

```bash
pip install -r requirements.txt
```

ตรวจสอบ:
```bash
pip list  # ต้องมี streamlit, pandas, plotly, scikit-learn
```

### 5️⃣ รันแอป!

```bash
streamlit run app.py
```

**คำสั่งนี้จะ:**
- ✓ เปิด Terminal ขึ้นมา
- ✓ หลังจาก 3-5 วินาที เบราว์เซอร์จะเปิด http://localhost:8501
- ✓ ถ้าเบราว์เซอร์ไม่เปิด ให้ copy URL จาก Terminal

### 6️⃣ ใช้งาน

1. **Menu 1 - นำเข้าข้อมูล**
   - Upload CSV/Excel หรือ Paste JSON
   - ดู Preview ข้อมูล

2. **Menu 2 - ทำความสะอาด**
   - ดู Data Stats
   - แก้ไข intent_true
   - Click "🧮 Recalculate All Metrics"

3. **Menu 3 - ดูสถิติ**
   - ดู Accuracy, Precision, Recall, F1
   - ดู Confusion Matrix
   - ดู Per-Class Metrics

4. **Menu 4 - ส่งออก**
   - ส่งออก CSV/JSON/HTML

---

## 📦 ไฟล์ที่ต้องการสำหรับการ Deploy

```
chatbot-analyzer/
├── app.py                    ← หลัก
├── requirements.txt          ← packages
├── .gitignore               ← บอก git ไฟล์ไหนไม่เก็บ
├── README.md                ← เอกสาร
├── DEPLOYMENT_GUIDE.md      ← คู่มือ Deploy
└── QUICK_START.md           ← ไฟล์นี้
```

**ไม่ต้องส่ง:**
- ❌ `/venv` - virtual environment
- ❌ `*.csv, *.xlsx` - data files
- ❌ `.env` - API keys
- ❌ `__pycache__` - Python cache

---

## 🌐 Deploy ให้เพื่อนใช้

### **ง่ายที่สุด (Streamlit Cloud):**

```bash
# 1. Push ขึ้น GitHub
git add .
git commit -m "Deploy app"
git push

# 2. ไปที่ https://share.streamlit.io
# 3. Click "Deploy an app"
# 4. ใส่ repository, branch, file path
# 5. Click Deploy!

# 6. ส่งให้เพื่อน URL แบบนี้:
# https://your-app-name.streamlit.app
```

### **ที่บ้านใช้เอง (Simple):**

```bash
# เครื่องที่รัน app:
streamlit run app.py

# เพื่อนจะเข้าโดย:
# http://<your-ip>:8501
# หรือ http://localhost:8501 (ถ้าเครื่องเดียวกัน)
```

### **VPS/Server (Advanced):**
ดู [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

---

## 🛠️ คำสั่งที่ใช้บ่อย

```bash
# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Deactivate virtual environment
deactivate

# ติดตั้ง package ใหม่
pip install <package-name>

# บันทึก packages
pip freeze > requirements.txt

# ดู logs
streamlit run app.py --logger.level=debug

# รัน app ที่ port อื่น
streamlit run app.py --server.port 8502

# หยุด app
Ctrl+C (ใน Terminal)
```

---

## ❌ ปัญหาที่พบบ่อย

| ปัญหา | แก้ไข |
|------|-------|
| `Module not found` | `pip install -r requirements.txt` |
| Port 8501 ใช้ไป | `streamlit run app.py --server.port 8502` |
| ข้อมูล import ผิด | ตรวจสอบ CSV มี column `raw_request`, `raw_reply` หรือไม่ |
| Streamlit ไม่เปิด | ลอง http://localhost:8501 ใน browser |
| Permission denied | `chmod +x app.py` (Mac/Linux) |

---

## 📚 สำหรับการเรียนรู้เพิ่มเติม

- 📖 Streamlit Docs: https://docs.streamlit.io
- 🐍 Python Docs: https://docs.python.org/3/
- 🔬 Scikit-learn: https://scikit-learn.org
- 📊 Pandas: https://pandas.pydata.org

---

**วิดีโอคำสั่งแบบรวดเร็ว:**

```bash
# Windows - Step by Step:
python --version
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py

# Mac/Linux - Step by Step:
python3 --version
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

**ถ้าสำเร็จ ให้เห็น:**
```
  Local URL: http://localhost:8501
  Network URL: http://<your-ip>:8501
```

**All set! Good to go! 🎉**
