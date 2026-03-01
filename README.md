# Chatbot Performance Metrics Analyzer

ระบบวิเคราะห์ประสิทธิภาพ Chatbot ด้วย Python + Streamlit สำหรับนำเข้าข้อมูลการสนทนา วิเคราะห์เมตริกความแม่นยำ ตรวจสอบ Intent Detection และส่งออกรายงาน

**Language:** Thai (ไทย) | English

## 🌟 ฟีเจอร์หลัก

- **📤 นำเข้าข้อมูล**: รองรับ CSV, Excel (.xlsx, .xls), และ JSON
- **📝 แก้ไขและตรวจสอบ**: ตารางแบบ inline editor สำหรับแก้ไข intent_true
- **📊 วิเคราะห์ประสิทธิภาพ**: 
  - Accuracy, Precision, Recall, F1-Score (sklearn)
  - Token Usage Analysis
  - Response Length Analysis
  - Intent Classification
  - Risk Assessment
- **🔍 Confusion Matrix**: แสดงเมตริกต่อเจตนา (Per-Class Performance)
- **💼 Business Impact Analysis**: แปลงเมตริก ML เป็นภาษาธุรกิจ
- **📥 ส่งออกรายงาน**: CSV, JSON, HTML formats
- **🌍 รองรับภาษาไทย**: Full support for Thai language
- **⚡ Real-time Calculation**: คำนวณอัตโนมัติตามการเปลี่ยนแปลง

## 📋 รูปแบบข้อมูล

### คอลัมน์ที่จำเป็น

- **raw_request**: JSON string ของข้อความผู้ใช้
- **raw_reply**: JSON string ของตอบกลับ + token_usage
- **intent_true**: ป้ายกำกับที่ถูก (สำหรับทำให้ถูกต้อง)

### ตัวอย่างข้อมูล

```json
{
  "raw_request": "{\"msg_id\": \"...\", \"text\": \"...สวัสดี...\"}",
  "raw_reply": "{\"text\": \"...สวัสดีค่ะ...\", \"token_usage\": {\"prompt_token_count\": 150, \"candidates_token_count\": 50, \"total_token_count\": 200}}"
}
```

## 🚀 การติดตั้งและใช้งาน

### ข้อกำหนดเบื้องต้น

**สำหรับเหมืองหลัก (Development/Single Machine):**
- Python 3.8 หรือ 3.9 หรือ 3.10 หรือ 3.13+
- pip (Package Manager Python)

### ขั้นตอนการติดตั้งบนเครื่องเดียว (Local Development)

1. **โคลน/ดาวน์โหลดโปรเจค:**
```bash
# ถ้าใช้ git
git clone <repository-url>
cd pfmizumi

# หรือดาวน์โหลด zip แล้วแตกไฟล์
```

2. **สร้าง virtual environment (ขอแนะนำ):**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **ติดตั้ง dependencies:**
```bash
pip install -r requirements.txt
```

4. **รันแอปพลิเคชัน:**
```bash
streamlit run app.py
```

แอปจะเปิดที่ `http://localhost:8501` โดยอัตโนมัติ

### 🌐 การ Deploy ไปยังเครื่องอื่น

#### **วิธี 1: ใช้ Streamlit Community Cloud (แนะนำ - ง่ายที่สุด)**

1. สร้าง GitHub Repository ของคุณ
2. Push โค้ดของคุณขึ้น GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

3. ไปที่ https://share.streamlit.io
4. เข้าด้วย GitHub Account
5. Click "Deploy an app"
6. ใส่ Repository, Branch, File path (app.py)
7. Click Deploy!

**ข้อดี:** ฟรี, ไม่ต้องจัดการ Server, Auto-deploy จาก GitHub
**ข้อเสีย:** ต้องคิวรอ, มีข้อจำกัด CPU/Memory

---

#### **วิธี 2: Deploy บน Private Server / VPS**

1. **เตรียมเครื่อง Server:**
```bash
# SSH เข้าเครื่อง Server
ssh user@server-ip

# ติดตั้ง Python
sudo apt update
sudo apt install python3.9 python3-pip

# Clone repository
git clone <your-repo-url>
cd pfmizumi

# สร้าง virtual env
python3 -m venv venv
source venv/bin/activate

# ติดตั้ง dependencies
pip install -r requirements.txt
```

2. **รันด้วย Supervisor/SystemD (ให้ restart อัตโนมัติ):**

**ตัวเลือก A: ใช้ Supervisord**
```bash
# ติดตั้ง supervisor
sudo apt install supervisor

# สร้างไฟล์ config
sudo nano /etc/supervisor/conf.d/streamlit.conf
```

เพิ่มเนื้อหา:
```ini
[program:streamlit]
directory=/home/user/pfmizumi
command=/home/user/pfmizumi/venv/bin/streamlit run app.py --server.port=8501 --server.headless=true
autostart=true
autorestart=true
stderr_logfile=/var/log/streamlit.err.log
stdout_logfile=/var/log/streamlit.out.log
user=user
```

รัน:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start streamlit
```

**ตัวเลือก B: ใช้ SystemD**
```bash
sudo nano /etc/systemd/system/streamlit.service
```

เพิ่มเนื้อหา:
```ini
[Unit]
Description=Streamlit Chatbot Analyzer
After=network.target

[Service]
Type=simple
User=user
WorkingDirectory=/home/user/pfmizumi
ExecStart=/home/user/pfmizumi/venv/bin/streamlit run app.py --server.port=8501 --server.headless=true
Restart=always

[Install]
WantedBy=multi-user.target
```

รัน:
```bash
sudo systemctl daemon-reload
sudo systemctl enable streamlit
sudo systemctl start streamlit
sudo systemctl status streamlit
```

3. **ตั้ง Reverse Proxy (nginx):**

```bash
# ติดตั้ง nginx
sudo apt install nginx

# สร้างไฟล์ config
sudo nano /etc/nginx/sites-available/streamlit
```

เพิ่มเนื้อหา:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

เปิดใช้งาน:
```bash
sudo ln -s /etc/nginx/sites-available/streamlit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

4. **เพิ่ม HTTPS (SSL) - ขอแนะนำ:**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

#### **วิธี 3: ใช้ Docker (สำหรับ Container Deployment)**

1. **สร้าง Dockerfile:**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.headless=true", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. **สร้าง .dockerignore:**

```
__pycache__
*.pyc
.git
.env
venv/
*.csv
*.xlsx
```

3. **Build และ Run:**

```bash
# Build image
docker build -t chatbot-analyzer .

# Run container
docker run -p 8501:8501 chatbot-analyzer
```

---

#### **วิธี 4: ใช้ PythonAnywhere (Simple Web Hosting)**

1. ไปที่ https://www.pythonanywhere.com
2. ลงทะเบียนเพื่อสร้าง Free Account
3. Upload ไฟล์ของคุณ
4. สร้าง Web App ด้วย Streamlit
5. ติดตั้ง dependencies
6. Reload app

---

### 📋 Checklist สำหรับการ Deploy

- [ ] `requirements.txt` มี package ที่ถูกต้อง ทั้งหมด
- [ ] `app.py` ไม่มี hardcoded paths (ใช้ relative paths)
- [ ] ไม่มี `.env` file ที่มี API keys ใน Git repository
- [ ] `.gitignore` ได้ตั้งค่าแล้ว (ข้อมูล, venv, .env)
- [ ] รัน `streamlit run app.py` ได้สำเร็จในเครื่อง
- [ ] ถ้าใช้ Database ให้ตั้ง Connection String จาก Environment Variables
- [ ] ถ้าใช้ API key ให้ตั้งเป็น Secrets แทน

### 📝 ตัวอย่าง .gitignore:

## 📖 Usage Guide

### Menu 1: Import Data

1. **Choose Import Mode**:
   - **Upload File**: Upload a CSV or Excel file
   - **Paste JSON**: Directly paste JSON data

2. **File Upload**:
   - Select a CSV or Excel file with `raw_request` and `raw_reply` columns
   - Click the upload area or drag and drop
   - Wait for the file to be processed

3. **JSON Paste**:
   - Copy and paste your JSON data into the text area
   - Click "Save & Analyze" to process

4. **Success**: After import, you'll see a success message and be taken to the metrics view

### Menu 2: View & Export Metrics

1. **Review Metrics**:
   - View all calculated performance metrics
   - See maximum and minimum values
   - Check average statistics

2. **Export Reports**:
   - **CSV**: Export metrics as a spreadsheet-compatible format
   - **JSON**: Export raw metrics and metadata
   - **HTML**: Generate a formatted HTML report

## 🏗️ Project Structure

```
src/
├── components/
│   ├── ImportMenu.tsx      # Data import interface
│   ├── ImportMenu.css      # Import styling
│   ├── MetricsMenu.tsx     # Metrics display interface
│   └── MetricsMenu.css     # Metrics styling
├── App.tsx                 # Main application component
├── App.css                 # Main styling
├── types.ts                # TypeScript type definitions
├── utils.ts                # Utility functions for data processing
├── main.tsx                # Entry point
└── index.css               # Global styling
```

## 🛠️ Technologies Used

- **React 18**: User interface framework
- **TypeScript**: Type-safe JavaScript
- **Vite**: Lightning-fast build tool
- **PapaParse**: CSV parsing library
- **XLSX**: Excel file support
- **CSS3**: Responsive styling with gradients and animations

## 📝 Export Formats

### CSV Export
Exports metrics as comma-separated values, compatible with Excel and Google Sheets.

### JSON Export
Exports complete metrics data with metadata and summary information.

### HTML Export
Generates a formatted HTML report with styled cards and sections, ready for printing or sharing.

## 🔧 Configuration

### Vite Configuration
- Development server port: 3000
- Auto-open browser on start
- HMR (Hot Module Replacement) enabled

### TypeScript Configuration
- Target ES2020
- Strict mode enabled
- JSX support with React 18

## 📦 Dependencies

### Production
- `react@^18.2.0`: React framework
- `react-dom@^18.2.0`: React DOM rendering
- `react-icons@^4.12.0`: Icon library
- `papaparse@^5.4.1`: CSV parser
- `xlsx@^0.18.5`: Excel support

### Development
- `@vitejs/plugin-react@^4.2.0`: React support for Vite
- `typescript@^5.2.2`: TypeScript compiler
- `vite@^5.0.8`: Build tool

## 🐛 Troubleshooting

### File Upload Not Working
- Ensure your file is in CSV or Excel format
- Verify that it has `raw_request` and `raw_reply` columns
- Check file size (very large files may need to be split)

### JSON Paste Error
- Validate your JSON using a JSON validator
- Ensure it contains the required `raw_request` and `raw_reply` fields
- Check for special character encoding issues

### Metrics Not Calculating
- Verify token_usage data exists in raw_reply JSON
- Check that token counts are numeric values
- Ensure at least one valid message pair is provided

## 📄 License

This project is open source and available for personal and commercial use.

## 🤝 Support

For issues or feature requests, please feel free to report them.

## 📧 Contact

For questions or feedback about this application, please contact the development team.

---

**Version**: 1.0.0  
**Last Updated**: February 2026

#   p f m i z u m i  
 #   p f m i z u m i  
 