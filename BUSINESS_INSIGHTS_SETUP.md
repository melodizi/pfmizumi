# Business Insights Setup Guide

## Overview
ระบบ "Business Impact Analysis" ใช้ OpenAI API เพื่อแปลง AI metrics เป็นความหมายทางธุรกิจของ MizuMi

## Required Metrics
ระบบจะคำนวณ 4 metrics อัตโนมัติ:
- **Accuracy**: ความถูกต้องการจำแนก Intent (0-100%)
- **Precision**: ความแม่นยำของการแนะนำสินค้า (0-100%)
- **Recall**: โอกาสในการจับการซื้อขาย (0-100%)
- **F1 Score**: สมดุลระหว่าง Precision และ Recall (0-100%)

## Setup Steps

### 1. Get OpenAI API Key
ไปที่ https://platform.openai.com/api-keys เพื่อหา/สร้าง API Key

### 2. Set Environment Variable
เปิด Terminal/PowerShell จากโฟลเดอร์ pfmizumi แล้วรัน:

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-xxxxxxxxxxxx"
python -m streamlit run app.py
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=sk-xxxxxxxxxxxx
python -m streamlit run app.py
```

**Mac/Linux:**
```bash
export OPENAI_API_KEY="sk-xxxxxxxxxxxx"
python -m streamlit run app.py
```

### 3. Permanent Setup (ไม่ต้องพิมพ์ทุกครั้ง)

**Windows:**
1. ค้นหา "Environment Variables"
2. Click "Edit the system environment variables"
3. Click "Environment Variables" button
4. Click "New..." (ในส่วน User variables)
5. Variable name: `OPENAI_API_KEY`
6. Variable value: `sk-xxxxxxxxxxxx`
7. Restart Terminal และ Streamlit

## How It Works

### Tab 1: Business Impact
- แสดง Accuracy, Precision, Recall, F1 stats
- AI (GPT-4o-mini) วิเคราะห์ผลกระทบต่อ:
  - ยอดขายรวม
  - การแนะนำสินค้าที่ถูก
  - โอกาสขายที่พลาดไป
  - ความสำคัญของแบรนด์

### Tab 2: System Health
- ประเมิน Health ของ Chatbot System
- ติดตามกฎ Health Rules:
  - Accuracy < 70% → 🔴 Critical
  - Precision < 75% → 🔴 Brand Risk
  - Recall < 60% → 🔴 Missing Opportunities
  - F1 < 70% → 🔴 Unsafe to Scale

## Using Business Insights

### Prerequisites
1. ✅ Upload data (CSV/Excel/JSON)
2. ✅ Clean data และ extract messages
3. ✅ Label some intents_true (อย่างน้อย 10-20)
4. ✅ ไปตัวและ "📊 ดูสถิติ"
5. ✅ เลื่อนลงไปหาแถบ "💼 Business Impact" / "🎯 System Health"

### เลือก Tab
- **💼 Business Impact**: อ่านอินไซต์ทางธุรกิจ
- **🎯 System Health**: ดู Health Status และ risk

## Model Info
- **Model**: gpt-4o-mini (cost-effective)
- **Language**: Thai (ไทย)
- **Response time**: 2-5 seconds
- **Max tokens**: 300 (Business Insight), 200 (Status)

## Troubleshooting

### ❌ "⚠️ ยังไม่ได้ตั้ง OPENAI_API_KEY"
→ ต้องตั้ง Environment Variable ตามขั้นตอนท่า 2 หรือ 3

### ❌ "❌ ต้องติดตั้ง: pip install openai"
→ รัน: `pip install openai`

### ❌ "⚠️ ต้องมี cleaned data กับ labeled intents ก่อน"
→ ต้องกำหนด intent_true ก่อน (ไม่ใช่ intent_suggest)

### ❌ API Rate Limit Error
→ ลองใหม่ในอีก 1 นาที

## Cost Estimation
- **gpt-4o-mini**: ~$0.00015 / 1K input tokens
- 1 Business Insight ≈ 0.5-2 cents
- 1 Status ≈ 0.2-1 cent

## Tips
- ✅ กำหนด intent_true อย่างน้อย 20-30 row ก่อนสามารถหา insights
- ✅ ยิ่ง labeled data มากเท่าไร metrics ยิ่งแม่นยำ
- ✅ ใช้ Quick Actions ในเมนู Clean Data เพื่อเติมคำแนะนำ intent อย่างรวดเร็ว
- ✅ ดูแรมท์ metrics ว่า ต้องปรับปรุง ก่อนใช้ AI insights

## Next Steps
1. ตั้ง OPENAI_API_KEY
2. Label 20-30 intent_true
3. ไปที่ "📊 ดูสถิติ" → "💼 Business Impact"
4. อ่านอินไซต์และประเมิน health
