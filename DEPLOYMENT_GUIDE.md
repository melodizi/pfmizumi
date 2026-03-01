# 📚 คู่มือการ Deploy - Chatbot Performance Metrics Analyzer

## 📦 ไฟล์ที่ต้องใช้สำหรับ Deploy

สำหรับการนำโปรแกรมไปลงใช้งานที่เครื่องอื่น คุณจำเป็นต้องมี:

```
/pfmizumi
├── app.py                 ← โปรแกรมหลัก (จำเป็น)
├── requirements.txt       ← packages ที่ต้องติดตั้ง (จำเป็น)
├── .gitignore            ← บอก Git ไฟล์ไหนไม่ต้องเก็บ
├── README.md             ← เอกสารแนะนำการใช้งาน
├── DEPLOYMENT_GUIDE.md   ← ไฟล์นี้ (เอกสารติดตั้ง)
└── .env (ถ้ามี)          ← ตั้งค่า Environment (ไม่ต้อง upload)
```

## 🚀 วิธีการ Deploy ที่แนะนำ

### ✅ **วิธีที่ 1: Streamlit Community Cloud (ง่ายที่สุด ⭐ แนะนำ)**

**ข้อดี:** 
- ฟรีเต็มหน้า ✓
- ไม่ต้องจัดการ Server ✓
- Auto-deploy จาก GitHub ✓
- HTTPS ได้อัตโนมัติ ✓

**ข้อเสีย:**
- ต้องมี GitHub Account
- มีข้อจำกัด CPU/Memory
- ต้องรอคิว

**ขั้นตอน:**

#### 1. เตรียม GitHub Repository

```bash
# เข้าไปในโฟลเดอร์โปรเจค
cd d:\Documents\pfmizumi

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Chatbot Performance Analyzer"

# Rename branch to main (ถ้ายังเป็น master)
git branch -M main

# Add remote (แทนที่ YOUR_USERNAME และ YOUR_REPO)
git remote add origin https://github.com/YOUR_USERNAME/chatbot-analyzer.git

# Push to GitHub
git push -u origin main
```

#### 2. Deploy ไปที่ Streamlit Cloud

1. ไปที่ https://share.streamlit.io
2. Log in ด้วย GitHub Account
3. Click **"New app"**
4. ใส่ข้อมูล:
   - Repository: `YOUR_USERNAME/chatbot-analyzer`
   - Branch: `main`
   - File path: `app.py`
5. Click **"Deploy"**
6. รอให้ deploy เสร็จ (ประมาณ 2-5 นาที)
7. ได้ URL แบบนี้: `https://your-app-name.streamlit.app`

**ใช้งาน:** แค่แชร์ URL นั้นให้คนอื่น!

---

### ✅ **วิธีที่ 2: VPS/Server ของตัวเอง (ควบคุมได้มากขึ้น)**

**ข้อดี:**
- ควบคุมเต็มที่ ✓
- ไม่มีข้อจำกัด ✓
- เหมาะสำหรับ Production ✓

**ข้อเสีย:**
- ต้องจ่ายค่า Server
- ต้องรู้ Linux
- ต้องจัดการ Security

**ขั้นตอน:**

#### 1. เตรียมเครื่อง Server

```bash
# SSH เข้าเครื่อง
ssh user@server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# ติดตั้ง Python
sudo apt install python3.9 python3-pip python3-venv git -y
```

#### 2. Clone โปรเจค

```bash
# Clone from GitHub
git clone https://github.com/YOUR_USERNAME/chatbot-analyzer.git
cd chatbot-analyzer

# หรือ upload ไฟล์โดยตรง SCP:
# scp -r /path/to/pfmizumi user@server-ip:/home/user/
```

#### 3. ตั้งค่า Environment

```bash
# สร้าง virtual environment
python3 -m venv venv

# Activate venv
source venv/bin/activate

# ติดตั้ง packages
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. รันแอป (Choice A: ใช้ Supervisor)

```bash
# ติดตั้ง supervisor
sudo apt install supervisor

# สร้างไฟล์ config
sudo nano /etc/supervisor/conf.d/streamlit.conf
```

เพิ่มเนื้อหาต่อไปนี้ (แก้ path ให้ตรงกับเครื่องของคุณ):

```ini
[program:streamlit]
directory=/home/user/chatbot-analyzer
command=/home/user/chatbot-analyzer/venv/bin/streamlit run app.py \
    --server.port=8501 \
    --server.headless=true \
    --server.address=0.0.0.0

autostart=true
autorestart=true
stderr_logfile=/var/log/streamlit.err.log
stdout_logfile=/var/log/streamlit.out.log
user=user
```

เรียก supervisor:

```bash
# Reload config
sudo supervisorctl reread
sudo supervisorctl update

# Start app
sudo supervisorctl start streamlit

# Check status
sudo supervisorctl status streamlit
```

#### 5. ตั้ง Nginx Reverse Proxy

```bash
# ติดตั้ง nginx
sudo apt install nginx -y

# สร้างไฟล์ config
sudo tee /etc/nginx/sites-available/chatbot > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Restart
sudo systemctl restart nginx
```

#### 6. เพิ่ม HTTPS (SSL Certificate - ฟรีด้วย Let's Encrypt)

```bash
# ติดตั้ง Certbot
sudo apt install certbot python3-certbot-nginx -y

# ขอ certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

**ผลลัพธ์:** แอปจะเปิดที่ `https://your-domain.com` ✓

---

### ✅ **วิธีที่ 3: Docker + Docker Compose (สำหรับเครื่องที่มี Docker)**

**ไฟล์ Dockerfile:**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Expose port
EXPOSE 8501

# Run
CMD ["streamlit", "run", "app.py", \
     "--server.headless=true", \
     "--server.port=8501", \
     "--server.address=0.0.0.0"]
```

**ไฟล์ docker-compose.yml:**

```yaml
version: '3.8'

services:
  chatbot-analyzer:
    build: .
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_CONFIG_SERVER_PORT=8501
      - STREAMLIT_CONFIG_SERVER_ADDRESS=0.0.0.0
      - STREAMLIT_CONFIG_SERVER_HEADLESS=true
    volumes:
      - ./data:/app/data
    restart: always
```

**รัน:**

```bash
# Build and run
docker-compose up -d

# ตรวจสอบ logs
docker-compose logs -f

# Stop
docker-compose down
```

---

### ✅ **วิธีที่ 4: PythonAnywhere (ง่าย ไม่ต้อง Terminal)**

1. ไปที่ https://www.pythonanywhere.com
2. สร้าง Free Account
3. Upload ไฟล์ ของคุณ
4. ติดตั้ง dependencies
5. สร้าง Web App
6. บอก PythonAnywhere รัน `app.py`

---

## 📋 Checklist ก่อน Deploy

- [ ] ทดสอบรันบนเครื่องตัวเองแล้ว (`streamlit run app.py`)
- [ ] `requirements.txt` มี packages ทั้งหมด
- [ ] ไม่มี `.env` ไปใน Git
- [ ] `.gitignore` ได้ตั้งค่าแล้ว
- [ ] ไม่มี hardcoded paths
- [ ] ทดสอบนำเข้าข้อมูล CSV/Excel/JSON
- [ ] สามารถคำนวณเมตริกได้ดี
- [ ] ปุ่ม Export ทำงานปกติ

---

## 🐛 Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'streamlit'"

**แก้:**
```bash
pip install -r requirements.txt
```

### ❌ "Port 8501 already in use"

**แก้:**
```bash
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8501
kill -9 <PID>
```

### ❌ "Permission denied" เมื่อรัน app

**แก้:**
```bash
chmod +x app.py
```

### ❌ Data ไม่ load ถูกต้อง

**แก้:**
- ตรวจสอบรูปแบบ CSV/Excel
- ดู column คือ `raw_request`, `raw_reply`, `intent_true` หรือไม่
- ลอง JSON format แทน

---

## 📞 ติดต่อและสนับสนุน

หากมีปัญหา:
1. ตรวจสอบ terminal logs
2. ดู GitHub Issues
3. ทดสอบบนเครื่องอื่น

---

**Happy Deploying! 🚀**
