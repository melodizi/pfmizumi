# Intent Classification & Suggestion Guide (v2.0)

## ระบบจำแนก Intent และการแนะนำ (อัปเดตใหม่)

โปรแกรมมี Advanced Intent Detection ด้วยคีย์เวิร์ดที่ละเอียดมากขึ้น

### 📋 Columns ใน Clean Data:

| Column | Description | Editable | Auto-filled |
|--------|-------------|----------|-----------|
| **user_message** | ข้อความจากผู้ใช้ | ❌ | ✅ |
| **ai_message** | คำตอบจาก AI | ❌ | ✅ |
| **💡 intent_suggest** | 📍 แนะนำให้ label (Advanced Detection) | ❌ Locked | ✅ |
| **✏️ intent_true** | Ground Truth - คุณกรอก | ✅ **Edit** | ❌ |
| **🤖 intent_ai** | AI Detection | ❌ Locked | ✅ |
| **⚠️ risk_level** | ระดับความเสี่ยง | ❌ Locked | ✅ |

---

## 📊 Intent Types ทั้งหมด (13 ประเภท):

### 🔴 **High Risk (ความปลอดภัย)**

| Intent | Keywords | Risk | ตัวอย่าง |
|--------|----------|------|--------|
| **safety_pregnancy** | คนท้อง, pregnant | 🔴 High | "ฉันท้องแล้ว ใช้ได้ไหม" |
| **adverse_reaction** | แพ้, แสบ, แดง, สิวขึ้น, ระคายเคือง | 🔴 High | "มันทำให้ผื่นได้ไหม" |

### 🟡 **Medium Risk (ต้องให้ความสำคัญ)**

| Intent | Keywords | Risk | ตัวอย่าง |
|--------|----------|------|--------|
| **ingredient_conflict** | ใช้ร่วม, คู่กับ, ด้วยกัน, ทาทับ | 🟡 Medium | "ใช้ร่วมกับ Vitamin ได้ไหม" |
| **product_recommendation** | แนะนำ, เหมาะ, สีไหน, ผิว, เลือก | 🟡 Medium | "มีสีไหนแนะนำสำหรับผิวมัน" |
| **shipping_problem** | ส่งช้า, ยังไม่ส่ง, ขนส่ง, ยังไม่ได้รับ | 🟡 Medium | "ทำไมเก่า ยังไม่ได้รับ" |

### 🟢 **Low Risk (ปกติ)**

| Intent | Keywords | Risk | ตัวอย่าง |
|--------|----------|------|--------|
| **usage_method** | วิธีใช้, ใช้ยังไง, ทายังไง, ลำดับ | 🟢 Low | "วิธีใช้ยังไง" |
| **promotion** | โปร, ราคา, ลด, ของแถม, รีวิว | 🟢 Low | "ราคาเท่าไหร่" |
| **order_status** | สั่ง, ออเดอร์, เลขพัสดุ | 🟢 Low | "สั่งได้ไหม" |
| **greeting** | สวัสดี, hello, hi | 🟢 Low | "สวัสดี" |
| **other** | คำถามทั่วไป | 🟢 Low | "อื่นๆ" |

---

## 🚀 Advanced Features:

### ✨ Improved Keyword Detection
- ✅ เพิ่มคีย์เวิร์ดหลากหลาย
- ✅ Support ภาษาไทย & English
- ✅ ตรวจจับ Multiple Keywords

### 💡 Smart Suggestions
- ✅ Auto-suggest intention สำหรับ Labeling
- ✅ Quick Action ปุ่ม
- ✅ Batch Operations

### 📊 Better Risk Assessment
- ✅ 13 Intent Types
- ✅ 3 Risk Levels (High/Medium/Low)
- ✅ Real-time Evaluation

---

## 🎯 ตัวอย่างการจำแนก:

| User Message | Detected Intent | Risk | สาเหตุ |
|--------------|-----------------|------|-------|
| "ฉันแพ้แล้ว ทำไง" | adverse_reaction | 🔴 High | "แพ้" = keyword |
| "ใช้ร่วมกันได้ไหม" | ingredient_conflict | 🟡 Medium | "ใช้ร่วม" = keyword |
| "วิธีใช้ยังไง" | usage_method | 🟢 Low | "วิธีใช้" = keyword |
| "สั่งที่ไหน" | order_status | 🟢 Low | "สั่ง" = keyword |
| "สวัสดีค่ะ" | greeting | 🟢 Low | "สวัสดี" = keyword |
| "มีสีไหนแนะนำ" | product_recommendation | 🟡 Medium | "แนะนำ" = keyword |
| "ยังไม่ได้รับพัสดุ" | shipping_problem | 🟡 Medium | "ยังไม่ได้รับ" = keyword |

---

## 📥 How to Use:

1. **Import Data** → Upload CSV
2. **Clean Data** → Auto-detect Intent
3. **Review Suggestions** → ดู `💡 intent_suggest`
4. **Edit intent_true** → แก้ไขเอง หรือ Copy Suggestion
5. **Export** → ดาวน์โหลดข้อมูล

---

## 🔧 Customization:

รหัสฟังก์ชัน `detect_intent()` ใน `app.py` สามารถ Customize Keywords ได้:

```python
def detect_intent(text):
    if any(k in text for k in ["your", "keywords"]):
        return "your_intent_type"
```

