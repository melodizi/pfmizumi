import streamlit as st
import pandas as pd
import json
import io
from datetime import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import numpy as np


# ตั้งค่า Page
st.set_page_config(
    page_title="Chatbot Performance Metrics Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS ที่กำหนดเอง
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .metric-label {
        font-size: 0.9em;
        opacity: 0.9;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 2em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def parse_json_safe(json_string):
    """แยก JSON อย่างปลอดภัย"""
    try:
        return json.loads(json_string)
    except:
        return None

# ========== KPI EVALUATION SYSTEM ==========
KPI_STANDARD = {
    "accuracy": 0.85,
    "avg_prompt_tokens": 400,
    "avg_response_tokens": 200,
    "response_length": 500,
}

def evaluate_metric(name, value, standard):
    """ประเมินผลเทียบกับ KPI Standard
    
    Parameters:
    - name: ชื่อ metric
    - value: ค่าที่วัดได้
    - standard: ค่า standard
    
    Returns:
    - (status, advice) tuple
    """
    if standard is None or standard == 0:
        return "N/A", "ไม่สามารถประเมิน"
    
    # ถ้าเป็น accuracy (0-1 scale) เทียบกับ percentage
    if "accuracy" in name.lower():
        ratio = value / standard
    else:
        # สำหรับ token counts และอื่นๆ
        if value >= standard * 1.15:
            return "🔴 สูงเกินไป", "ควรลดค่าอย่างด่วน"
        elif value >= standard:
            return "🟢 ดี", "เหมาะสม"
        elif value >= standard * 0.8:
            return "🟡 พอใช้", "ควรปรับปรุงในไม่ช้า"
        else:
            return "🔴 ต่ำ", "ต้องแก้ไขด่วน"
    
    if ratio >= 1.15:
        return "🟢 ดี", "เหมาะสม"
    elif ratio >= 1.0:
        return "🟢 ดี", "เหมาะสม"
    elif ratio >= 0.8:
        return "🟡 พอใช้", "ควรปรับปรุง"
    else:
        return "🔴 ต่ำ", "ต้องแก้ไขด่วน"

def recommendation(metric_name, value):
    """ให้คำแนะนำโดยอิงตาม metric
    
    Returns: string ของคำแนะนำภาษาไทย
    """
    advice = {
        "accuracy": "✓ เพิ่ม training data หรือปรับปรุง intent classification\n✓ ตรวจสอบ manual labels ว่าถูกต้องหรือไม่",
        "avg_prompt_tokens": "✓ ลด system prompt ให้กระชับขึ้น\n✓ ตัด chat history ที่ไม่จำเป็น\n✓ บีบอัดข้อมูลในคำถาม",
        "avg_response_tokens": "✓ บังคับ AI ให้ตอบสั้นลง\n✓ เพิ่ม max_tokens limit\n✓ ให้คำตอบเฉพาะจุด ไม่ละเอียดเกินไป",
        "response_length": "✓ ตั้งความยาว response ให้เหมาะสม\n✓ ใช้ bullet points แทน paragraph\n✓ ปรับ prompt ให้ AI รู้ว่าควรตอบสั้น",
        "avg_latency_sec": "✓ ปรับ model complexity\n✓ เพิ่มจำนวน inference resources",
    }
    
    return advice.get(metric_name, "✓ ตรวจสอบระบบ\n✓ ติดต่อ support team")

# ========== OpenAI Integration for Business Insights ==========
@st.cache_data
def calculate_business_impact(acc, precision, recall, f1):
    """คำนวณ Business Impact Score จาก metrics (ไม่ต้อง API)"""
    
    # แปลง metrics เป็น scores (0-100)
    acc_score = acc * 100
    precision_score = precision * 100
    recall_score = recall * 100
    f1_score = f1 * 100
    
    # Business impact analysis
    insights = []
    
    # Revenue Impact
    if acc_score >= 85:
        insights.append(f"💰 **ยอดขาย:** Accuracy {acc_score:.1f}% → ความเสี่ยงต่ำ ลูกค้าเชื่อถือ Chatbot")
    elif acc_score >= 70:
        insights.append(f"💰 **ยอดขาย:** Accuracy {acc_score:.1f}% → ปกติ ต้องปรับปรุง")
    else:
        insights.append(f"💰 **ยอดขาย:** Accuracy {acc_score:.1f}% → ⚠️ เสี่ยง ลูกค้าอาจไม่ซื้อ")
    
    # Product Recommendation
    if precision_score >= 75:
        insights.append(f"🛍️ **สินค้า:** Precision {precision_score:.1f}% → แนะนำได้ถูกต้อง ลูกค้าพอใจ")
    elif precision_score >= 60:
        insights.append(f"🛍️ **สินค้า:** Precision {precision_score:.1f}% → พอใช้ เพิ่มการ training")
    else:
        insights.append(f"🛍️ **สินค้า:** Precision {precision_score:.1f}% → ⚠️ แนะนำผิด เสี่ยงแบรนด์")
    
    # Sales Opportunities
    if recall_score >= 75:
        insights.append(f"📈 **โอกาสขาย:** Recall {recall_score:.1f}% → จับได้ครบ ไม่พลาดการขาย")
    elif recall_score >= 60:
        insights.append(f"📈 **โอกาสขาย:** Recall {recall_score:.1f}% → พลาดไป 40% ของการขาย")
    else:
        insights.append(f"📈 **โอกาสขาย:** Recall {recall_score:.1f}% → ⚠️ พลาดมากเกินไป")
    
    # Scaling Risk
    if f1_score >= 75:
        insights.append(f"✅ **ปลอดภัย:** F1 Score {f1_score:.1f}% → สามารถ Scale-up ได้")
    elif f1_score >= 70:
        insights.append(f"⚠️ **เสี่ยง:** F1 Score {f1_score:.1f}% → ต้องแก้ไขก่อน Scale-up")
    else:
        insights.append(f"🔴 **Critical:** F1 Score {f1_score:.1f}% → ต้องแก้ไขด่วน ห้าม Scale-up")
    
    # Overall recommendation
    overall_score = (acc_score + precision_score + recall_score + f1_score) / 4
    if overall_score >= 80:
        recommendation = "🟢 **Recommendation:** ระบบพร้อมใช้ - Maintain quality"
    elif overall_score >= 70:
        recommendation = "🟡 **Recommendation:** ปรับปรุงอย่างค่อยเป็นค่อยไป - Focus on accuracy & recall"
    else:
        recommendation = "🔴 **Recommendation:** ต้องแก้ไขด่วน - Retrain model & label data"
    
    insights.append(recommendation)
    
    return "\n\n".join(insights)

def assess_system_health(acc, precision, recall, f1):
    """ประเมิน Health ของระบบตาม health rules (ไม่ต้อง API)"""
    
    acc_pct = acc * 100
    precision_pct = precision * 100
    recall_pct = recall * 100
    f1_pct = f1 * 100
    
    # Health rules
    issues = []
    
    if acc_pct < 70:
        issues.append(("🔴 Critical", "Accuracy < 70% - Model needs retraining"))
    elif acc_pct < 80:
        issues.append(("🟡 Warning", "Accuracy < 80% - Performance is degrading"))
    
    if precision_pct < 75:
        issues.append(("🔴 Brand Risk", "Precision < 75% - Recommending wrong products"))
    
    if recall_pct < 60:
        issues.append(("🔴 Missing Sales", "Recall < 60% - Losing 40%+ of opportunities"))
    elif recall_pct < 75:
        issues.append(("🟡 Warning", "Recall < 75% - Losing sales to competitors"))
    
    if f1_pct < 70:
        issues.append(("🔴 Unsafe to Scale", "F1 < 70% - Cannot scale production"))
    
    # Determine overall status
    if any("🔴" in issue[0] for issue in issues):
        status = "🔴 Critical"
        primary_risk = issues[0][1]
        action = "Start immediate investigation & fix"
    elif any("🟡" in issue[0] for issue in issues):
        status = "🟡 Warning"
        primary_risk = issues[0][1] if issues else "Minor issues detected"
        action = "Monitor and plan improvements"
    else:
        status = "🟢 Healthy"
        primary_risk = "No issues detected - System performing well"
        action = "Maintain current quality level"
    
    return {
        "status": status,
        "risk": primary_risk,
        "priority_action": action,
        "all_issues": issues
    }

def extract_token_usage(reply_json):
    """ดึง Token Usage จาก raw_reply"""
    if isinstance(reply_json, str):
        reply_json = parse_json_safe(reply_json)
    
    if not reply_json or not isinstance(reply_json, dict):
        return None
    
    token_usage = reply_json.get('token_usage', {})
    
    return {
        'prompt_token_count': token_usage.get('prompt_token_count', 0),
        'candidates_token_count': token_usage.get('candidates_token_count', 0),
        'total_token_count': token_usage.get('total_token_count', 0),
        'thoughts_token_count': token_usage.get('thoughts_token_count', 0),
    }

def extract_message_content(raw_request, raw_reply):
    """แยกข้อความจาก raw_request และ raw_reply"""
    try:
        request_json = parse_json_safe(raw_request)
        reply_json = parse_json_safe(raw_reply)
        
        user_message = ""
        ai_message = ""
        
        # ดึง user message จาก request
        if isinstance(request_json, dict):
            if 'data' in request_json and 'content' in request_json['data']:
                content = request_json['data']['content']
                if 'content' in content and 'text' in content['content']:
                    user_message = content['content']['text']
            elif 'content' in request_json and 'text' in request_json['content']:
                user_message = request_json['content']['text']
        
        # ดึง AI message จาก reply
        if isinstance(reply_json, dict) and 'text' in reply_json:
            ai_message = reply_json['text']
        
        return user_message, ai_message
    except:
        return "", ""

def detect_intent(text):
    """จำแนก Intent จากข้อความอย่างละเอียด"""
    if not isinstance(text, str):
        return "other"
    
    text = text.lower()
    
    # ความปลอดภัย
    if "คนท้อง" in text or "pregnant" in text:
        return "safety_pregnancy"
    
    if any(k in text for k in ["แพ้", "แสบ", "แดง", "สิวขึ้น", "ระคายเคือง"]):
        return "adverse_reaction"
    
    if any(k in text for k in ["ใช้ร่วม", "คู่กับ", "ด้วยกัน", "ทาทับ"]):
        return "ingredient_conflict"
    
    # สินค้า
    if any(k in text for k in ["แนะนำ", "เหมาะ", "สีไหน", "ผิว", "เลือก"]):
        return "product_recommendation"
    
    if any(k in text for k in ["วิธีใช้", "ใช้ยังไง", "ทายังไง", "ลำดับ"]):
        return "usage_method"
    
    # การขาย
    if any(k in text for k in ["โปร", "ราคา", "ลด", "ของแถม", "รีวิว"]):
        return "promotion"
    
    # ออเดอร์
    if any(k in text for k in ["สั่ง", "ออเดอร์", "เลขพัสดุ"]):
        return "order_status"
    
    if any(k in text for k in ["ส่งช้า", "ยังไม่ส่ง", "ขนส่ง", "ยังไม่ได้รับ"]):
        return "shipping_problem"
    
    # ทักทาย
    if any(k in text for k in ["สวัสดี", "hello", "hi"]):
        return "greeting"
    
    return "other"

def classify_intent(text):
    """Alias ของ detect_intent เพื่อความเข้ากันได้"""
    return detect_intent(text)

def suggest_intent(text):
    """Alias ของ detect_intent เพื่อแนะนำ"""
    return detect_intent(text)

def risk_level(intent):
    """กำหนดระดับความเสี่ยง"""
    risk_map = {
        "safety_pregnancy": "🔴 High",
        "adverse_reaction": "🔴 High",
        "ingredient_conflict": "🟡 Medium",
        "product_recommendation": "🟡 Medium",
        "usage_method": "🟢 Low",
        "promotion": "🟢 Low",
        "order_status": "🟢 Low",
        "shipping_problem": "🟡 Medium",
        "greeting": "🟢 Low",
        "new_product": "🟡 Medium",
        "usage_instruction": "🟢 Low",
        "ingredient_info": "🟢 Low",
        "general": "🟢 Low",
        "other": "🟢 Low",
    }
    
    return risk_map.get(intent, "🟢 Low")

def analyze(df):
    """วิเคราะห์และเพิ่ม Intent และ Risk Level"""
    df["intent_ai"] = df["user_message"].apply(classify_intent)
    df["risk_level"] = df["intent_ai"].apply(risk_level)
    
    return df

def clean_data(messages_df):
    """Clean data และ extract ข้อมูลที่ต้องการ"""
    cleaned_data = []
    for idx, row in messages_df.iterrows():
        try:
            user_msg, ai_msg = extract_message_content(row['raw_request'], row['raw_reply'])
            # ข้ามข้อมูลที่ว่าง
            if not user_msg or not ai_msg:
                continue
            # Auto-detect intent
            detected_intent = classify_intent(user_msg)
            suggest_int = suggest_intent(user_msg)  # Suggestion for manual labeling
            risk = risk_level(detected_intent)
            # เพิ่มเงื่อนไข FAIL ถ้า ai_message มีคำต้องห้าม
            fail_keywords = ["รอแอดมิน", "ไม่พบข้อมูล", "ไม่ทราบข้อมูล"]
            ai_fail = any(kw in ai_msg for kw in fail_keywords)
            if ai_fail:
                detected_intent = "FAIL"
                risk = "🔴 High"
            cleaned_data.append({
                'user_message': user_msg,
                'ai_message': ai_msg,
                'intent_suggest': suggest_int,     # แนะนำให้ label
                'intent_true': '',                  # ว่างไว้สำหรับ manual input
                'intent_ai': detected_intent,       # Auto-detected
                'risk_level': risk,                 # Auto-detected
            })
        except Exception as e:
            st.warning(f"⚠️ Error processing row {idx}: {str(e)}")
            continue
    return pd.DataFrame(cleaned_data)

def analyze_accuracy(cleaned_df):
    """คำนวณ Accuracy, Precision, Recall, F1 ด้วย sklearn
    
    Returns dict with sklearn metrics
    """
    if cleaned_df is None or len(cleaned_df) == 0:
        return None
    
    # Filter only rows with intent_true labeled
    labeled_df = cleaned_df[cleaned_df['intent_true'].notna() & (cleaned_df['intent_true'] != '')]
    
    if len(labeled_df) == 0:
        return None
    
    y_true = labeled_df["intent_true"].str.lower().values
    y_pred = labeled_df["intent_ai"].str.lower().values
    
    # Calculate metrics using sklearn
    acc = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average="weighted", zero_division=0)
    recall = recall_score(y_true, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    
    # Calculate confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    # Get all classes
    classes = sorted(np.unique(np.concatenate([y_true, y_pred])))
    
    # Classification report
    class_report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    
    return {
        'total': len(cleaned_df),
        'labeled': len(labeled_df),
        'unlabeled': len(cleaned_df) - len(labeled_df),
        'accuracy_percent': round(acc * 100, 2),
        'accuracy': round(acc, 4),
        'precision': round(precision, 4),
        'recall': round(recall, 4),
        'f1': round(f1, 4),
        'confusion_matrix': cm,
        'classes': classes,
        'classification_report': class_report,
        'y_true': y_true,
        'y_pred': y_pred,
    }

def translate_business(metrics):
    """แปลง ML metrics เป็น business language
    
    Returns dict with business-friendly interpretations
    """
    if metrics is None:
        return None
    
    acc = metrics['accuracy']
    recall = metrics['recall']
    precision = metrics['precision']
    
    # Calculate business impact %
    sales_loss = round((1 - acc) * 100, 1)
    missed_customer = round((1 - recall) * 100, 1)
    brand_risk = round((1 - precision) * 100, 1)
    
    return {
        "accuracy": f"{acc*100:.1f}%",
        "sales_impact": f"อาจเสียยอดขาย ~{sales_loss}%",
        "missed_opportunity": f"พลาดลูกค้า ~{missed_customer}%",
        "brand_risk": f"เสี่ยงแนะนำผิด ~{brand_risk}%",
        "precision": f"{precision*100:.1f}%",
        "recall": f"{recall*100:.1f}%",
        "f1": f"{metrics['f1']*100:.1f}%"
    }


def plot_confusion_matrix(accuracy_result):
    """วาด Confusion Matrix เป็น Heatmap ด้วย Plotly"""
    if accuracy_result is None or 'confusion_matrix' not in accuracy_result:
        return None
    
    cm = accuracy_result['confusion_matrix']
    classes = accuracy_result['classes']
    
    # Create confusion matrix DataFrame
    cm_df = pd.DataFrame(
        cm,
        index=classes,
        columns=classes
    )
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=classes,
        y=classes,
        text=cm,
        texttemplate='%{text}',
        textfont={"size": 12},
        colorscale="Blues",
        colorbar=dict(title="จำนวน")
    ))
    
    fig.update_layout(
        title="Confusion Matrix - ความสับสนของเจตนา",
        xaxis_title="ที่ AI ทำนายแล้ว",
        yaxis_title="ที่ถูกต้องแล้ว (ป้ายกำกับ)",
        height=600,
        width=800
    )
    
    return fig, cm_df


def plot_per_class_metrics(accuracy_result):
    """วาดแผนภูมิ Precision, Recall, F1 ต่อคลาส"""
    if accuracy_result is None or 'classification_report' not in accuracy_result:
        return None
    
    report = accuracy_result['classification_report']
    classes = accuracy_result['classes']
    
    # Extract per-class metrics
    precisions = []
    recalls = []
    f1_scores = []
    
    for cls in classes:
        if str(cls) in report:
            precisions.append(report[str(cls)]['precision'])
            recalls.append(report[str(cls)]['recall'])
            f1_scores.append(report[str(cls)]['f1-score'])
    
    # Create subplots
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=("Precision", "Recall", "F1-Score"),
        specs=[[{}, {}, {}]]
    )
    
    # Add bars
    fig.add_trace(
        go.Bar(x=classes, y=precisions, name="Precision", marker_color="lightblue"),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=classes, y=recalls, name="Recall", marker_color="lightgreen"),
        row=1, col=2
    )
    fig.add_trace(
        go.Bar(x=classes, y=f1_scores, name="F1-Score", marker_color="lightyellow"),
        row=1, col=3
    )
    
    fig.update_layout(
        title_text="เมตริกต่อเจตนา (Per-Class Metrics)",
        showlegend=False,
        height=400,
        width=1200
    )
    
    return fig


def analyze_response_length(cleaned_df):
    """วิเคราะห์ความยาวของตอบหรือสั้น/ยาวเกินไป"""
    if cleaned_df is None or len(cleaned_df) == 0:
        return None
    
    lengths = []
    for _, row in cleaned_df.iterrows():
        msg = str(row.get('ai_message', ''))
        lengths.append(len(msg))
    
    lengths_array = pd.Series(lengths)
    
    # กำหนดมาตรฐาน
    # สั้นเกินไป: < 50 characters
    # ปกติ: 50-500 characters
    # ยาวเกินไป: > 500 characters
    
    short = len([l for l in lengths if l < 50])
    normal = len([l for l in lengths if 50 <= l <= 500])
    long = len([l for l in lengths if l > 500])
    
    return {
        'average_length': round(lengths_array.mean(), 2),
        'min_length': int(lengths_array.min()),
        'max_length': int(lengths_array.max()),
        'short_responses': short,  # < 50 chars
        'normal_responses': normal,  # 50-500 chars
        'long_responses': long,  # > 500 chars
        'short_percent': round((short / len(lengths) * 100), 2) if lengths else 0,
        'normal_percent': round((normal / len(lengths) * 100), 2) if lengths else 0,
        'long_percent': round((long / len(lengths) * 100), 2) if lengths else 0,
    }

def find_top_intents(cleaned_df):
    """หา Top Intent ที่ลูกค้าถามเยอะสุด"""
    if cleaned_df is None or len(cleaned_df) == 0:
        return None
    
    intent_counts = {}
    
    for _, row in cleaned_df.iterrows():
        intent_true = str(row.get('intent_true', '')).strip()
        if intent_true and intent_true.lower() != 'nan':
            intent_counts[intent_true] = intent_counts.get(intent_true, 0) + 1
    
    if not intent_counts:
        return None
    
    sorted_intents = sorted(intent_counts.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'top_intents': sorted_intents[:10],
        'total_unique_intents': len(intent_counts),
        'total_messages': len(cleaned_df),
    }

def analyze_response_risk(cleaned_df):
    """วิเคราะห์ความเสี่ยง (โดยบวกจากความไม่ถูกต้องและการตอบสั้นเกินไป)"""
    if cleaned_df is None or len(cleaned_df) == 0:
        return None
    
    accuracy_data = analyze_accuracy(cleaned_df)
    length_data = analyze_response_length(cleaned_df)
    
    if accuracy_data is None or length_data is None:
        return None
    
    # คำนวน risk score
    # ถ้า accuracy ต่ำ = เสี่ยงสูง
    # ถ้า short responses เยอะ = เสี่ยงสูง
    
    incorrect_rate = (1 - accuracy_data['accuracy']) * 100  # percentage of incorrect
    short_rate = length_data['short_percent']
    
    # Risk score: 0-100
    risk_score = (incorrect_rate * 0.6) + (short_rate * 0.4)  # ให้น้ำหนักมากกว่าไปที่ accuracy
    
    risk_level = "🟢 ต่ำ"
    if risk_score > 50:
        risk_level = "🔴 สูง"
    elif risk_score > 25:
        risk_level = "🟡 ปานกลาง"
    
    return {
        'risk_score': round(risk_score, 2),
        'risk_level': risk_level,
        'incorrect_rate': round(incorrect_rate, 2),
        'short_response_rate': round(short_rate, 2),
    }

def calculate_metrics(messages_df):
    """คำนวน Performance Metrics"""
    if len(messages_df) == 0:
        return None
    
    total_prompt_tokens = 0
    total_candidate_tokens = 0
    total_tokens = 0
    total_response_length = 0
    min_tokens = float('inf')
    max_tokens = 0
    valid_messages = 0
    
    for _, row in messages_df.iterrows():
        try:
            token_usage = extract_token_usage(row['raw_reply'])
            
            if token_usage:
                prompt_count = token_usage.get('prompt_token_count', 0) or 0
                candidate_count = token_usage.get('candidates_token_count', 0) or 0
                total_count = token_usage.get('total_token_count', 0) or 0
                
                if total_count > 0:
                    total_prompt_tokens += prompt_count
                    total_candidate_tokens += candidate_count
                    total_tokens += total_count
                    
                    min_tokens = min(min_tokens, total_count)
                    max_tokens = max(max_tokens, total_count)
                    valid_messages += 1
            
            # ดึง Response Length
            reply_json = parse_json_safe(row['raw_reply'])
            if reply_json and isinstance(reply_json, dict) and 'text' in reply_json:
                text_len = len(str(reply_json['text']))
                if text_len > 0:
                    total_response_length += text_len
        except Exception as e:
            st.warning(f"⚠️ Error processing message: {str(e)}")
            continue
    
    count = len(messages_df)
    valid_messages = max(valid_messages, 1)
    
    return {
        'total_messages': count,
        'total_prompt_tokens': int(total_prompt_tokens),
        'total_candidate_tokens': int(total_candidate_tokens),
        'total_tokens': int(total_tokens),
        'average_prompt_tokens': int(round(total_prompt_tokens / valid_messages)) if valid_messages > 0 else 0,
        'average_candidate_tokens': int(round(total_candidate_tokens / valid_messages)) if valid_messages > 0 else 0,
        'average_total_tokens': int(round(total_tokens / valid_messages)) if valid_messages > 0 else 0,
        'average_response_length': int(round(total_response_length / count)) if count > 0 else 0,
        'min_total_tokens': int(min_tokens) if min_tokens != float('inf') else 0,
        'max_total_tokens': int(max_tokens),
        'timestamp': datetime.now().isoformat(),
    }

# Main App
st.title("🤖 Chatbot Performance Metrics Analyzer")
st.markdown("วิเคราะห์และ Export รายงาน Performance Metrics")

# Sidebar Navigation
st.sidebar.title("📌 เมนู")
menu = st.sidebar.radio("เลือก:", ["📤 นำเข้าข้อมูล", "🧹 Clean Data", "� วิเคราะห์ผลลัพธ์", "�📊 ดูสถิติ"])

# Initialize Session State
# Initialize Session State
if 'messages_df' not in st.session_state:
    st.session_state.messages_df = None
if 'metrics' not in st.session_state:
    st.session_state.metrics = None
if 'cleaned_df' not in st.session_state:
    st.session_state.cleaned_df = None

# ========== Sidebar Navigation ==========
st.sidebar.markdown("---")
st.sidebar.info("✅ Local Analytics - No API Key Required\n\n🎯 All calculations done locally!")
st.sidebar.markdown("---")

if menu == "📤 นำเข้าข้อมูล":
    st.header("📤 นำเข้าข้อมูล Chatbot")
    
    # เลือกวิธีการนำเข้า
    upload_method = st.radio("เลือกวิธีการนำเข้า:", ["📁 Upload ไฟล์", "📝 Paste JSON"])
    
    if upload_method == "📁 Upload ไฟล์":
        uploaded_file = st.file_uploader("เลือกไฟล์ CSV หรือ Excel", type=['csv', 'xlsx', 'xls'])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # ตรวจสอบ Column
                if 'raw_request' not in df.columns or 'raw_reply' not in df.columns:
                    st.error("❌ ไฟล์ต้องมี Column: raw_request และ raw_reply")
                else:
                    st.session_state.messages_df = df
                    st.session_state.metrics = calculate_metrics(df)
                    
                    st.success(f"✅ อ่านไฟล์สำเร็จ! ({len(df)} message)")
                    st.info("ไปที่ 📊 ดูสถิติ เพื่อดูผลการวิเคราะห์")
                    
                    with st.expander("ดูตัวอย่างข้อมูล"):
                        st.dataframe(df.head())
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    else:  # JSON Upload
        json_text = st.text_area("Paste JSON data:", height=300,
            placeholder='[{"raw_request": "...", "raw_reply": "..."}]')
        
        if st.button("💾 Save & Analyze"):
            if json_text.strip():
                try:
                    data = json.loads(json_text)
                    
                    if isinstance(data, dict):
                        data = [data]
                    
                    df = pd.DataFrame(data)
                    
                    if 'raw_request' not in df.columns or 'raw_reply' not in df.columns:
                        st.error("❌ JSON ต้องมี field: raw_request และ raw_reply")
                    else:
                        st.session_state.messages_df = df
                        st.session_state.metrics = calculate_metrics(df)
                        
                        st.success(f"✅ Parsed สำเร็จ! ({len(df)} message)")
                        st.info("ไปที่ 📊 ดูสถิติ เพื่อดูผลการวิเคราะห์")
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON format")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ กรุณา paste JSON data")
    
    # ข้อมูลความช่วยเหลือ
    st.markdown("---")
    st.subheader("📋 Data Format Requirements")
    with st.expander("ดูรายละเอียด"):
        st.markdown("""
        **Required Columns/Fields:**
        - `raw_request`: JSON string ของข้อความจากผู้ใช้
        - `raw_reply`: JSON string ของการตอบกลับพร้อม token_usage
        
        **Token Usage Fields:**
        - `prompt_token_count`: Token ของข้อความถาม
        - `candidates_token_count`: Token ของการตอบ
        - `total_token_count`: รวม Token ทั้งหมด
        
        **ตัวอย่าง:**
        ```json
        {
            "raw_request": "...",
            "raw_reply": "{\\"text\\": \\"..\\", \\"token_usage\\": {\\"prompt_token_count\\": 2534, \\"candidates_token_count\\": 35, \\"total_token_count\\": 2680}}"
        }
        ```
        """)

elif menu == "🧹 Clean Data":
    st.header("🧹 Clean Data & Extract Messages")
    
    if st.session_state.messages_df is None:
        st.warning("⚠️ ยังไม่มีข้อมูล กรุณา Import ข้อมูลจากเมนู 📤 ก่อน")
    else:
        st.info("📋 โปรแกรมจะ Clean Data และแยก Message ให้คุณ")
        
        if st.button("🧹 Clean & Extract"):
            with st.spinner("กำลัง Clean Data..."):
                cleaned_df = clean_data(st.session_state.messages_df)
                st.session_state.cleaned_df = cleaned_df
        
        if st.session_state.cleaned_df is not None:
            cleaned_df = st.session_state.cleaned_df
            st.success(f"✅ Clean สำเร็จ! ({len(cleaned_df)} messages extracted)")
            
            st.markdown("---")
            st.subheader("📊 Extracted Data")
            
            # แสดงตาราง
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric("Total Messages", len(cleaned_df))
            with col2:
                st.metric("Valid Data", f"{len(cleaned_df)}/{len(st.session_state.messages_df)}")
            
            # Editable Table
            st.markdown("### ✏️ Edit & Review Data")
            st.info("💡 💡 ใช้ **intent_suggest** เป็นแนวทางในการกรอก **intent_true**")
            
            edited_df = st.data_editor(
                cleaned_df,
                use_container_width=True,
                height=400,
                column_config={
                    "user_message": st.column_config.TextColumn("User Message", width="medium"),
                    "ai_message": st.column_config.TextColumn("AI Message", width="medium"),
                    "intent_suggest": st.column_config.TextColumn("💡 Suggested", width="small", disabled=True),
                    "intent_true": st.column_config.TextColumn("✏️ True (Edit)", width="small"),
                    "intent_ai": st.column_config.TextColumn("🤖 AI", width="small", disabled=True),
                    "risk_level": st.column_config.TextColumn("⚠️ Risk", width="small", disabled=True),
                }
            )
            
            st.session_state.cleaned_df = edited_df
            
            st.markdown("---")
            st.subheader("⚡ Quick Actions")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📋 Copy All Suggestions → intent_true"):
                    """Auto-fill intent_true จาก intent_suggest"""
                    for i in range(len(edited_df)):
                        if edited_df.loc[i, 'intent_true'] == '' or pd.isna(edited_df.loc[i, 'intent_true']):
                            edited_df.loc[i, 'intent_true'] = edited_df.loc[i, 'intent_suggest']
                    st.session_state.cleaned_df = edited_df
                    st.success("✅ Copied all suggestions to intent_true")
                    st.rerun()
            
            with col2:
                if st.button("🧹 Auto-fill Empty intent_true"):
                    """Fill empty intent_true only"""
                    count = 0
                    for i in range(len(edited_df)):
                        if edited_df.loc[i, 'intent_true'] == '' or pd.isna(edited_df.loc[i, 'intent_true']):
                            edited_df.loc[i, 'intent_true'] = edited_df.loc[i, 'intent_suggest']
                            count += 1
                    st.session_state.cleaned_df = edited_df
                    st.success(f"✅ Auto-filled {count} empty fields")
                    st.rerun()
            
            with col3:
                if st.button("🔍 Show Data Stats"):
                    """แสดงสถิติข้อมูล"""
                    total = len(edited_df)
                    filled = len(edited_df[edited_df['intent_true'] != ''])
                    empty = total - filled
                    
                    st.info(f"📊 **Data Stats:**\n- Total: {total}\n- Filled: {filled}\n- Empty: {empty}")
            
            st.session_state.cleaned_df = edited_df
            
            st.markdown("---")
            st.subheader("🔄 Recalculate Metrics")
            
            if st.button("🧮 Recalculate All Metrics", key="recalc_metrics", type="primary"):
                """คำนวณเมตริกใหม่หลังจากแก้ไข intent_true"""
                # Reset metrics cache
                if 'metrics_result' in st.session_state:
                    del st.session_state.metrics_result
                if 'accuracy_result' in st.session_state:
                    del st.session_state.accuracy_result
                st.success("✅ Metrics cleared! Moving to 📊 ดูสถิติ to recalculate...")
                st.info("💡 กรุณาไปที่ Tab **📊 ดูสถิติ** เพื่อดูค่าเมตริกใหม่")
                st.rerun()
            
            st.markdown("---")
            st.subheader("📥 Export Cleaned Data")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Export CSV
                csv_content = edited_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📊 Download CSV",
                    data=csv_content,
                    file_name=f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Export Excel
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    edited_df.to_excel(writer, sheet_name='Cleaned Data', index=False)
                
                excel_buffer.seek(0)
                st.download_button(
                    label="📋 Download Excel",
                    data=excel_buffer.getvalue(),
                    file_name=f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            with col3:
                # Export JSON
                json_content = edited_df.to_json(orient='records', force_ascii=False, indent=2)
                st.download_button(
                    label="📄 Download JSON",
                    data=json_content,
                    file_name=f"cleaned_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            # Preview
            st.markdown("---")
            st.subheader("👀 Data Preview")
            
            sample_size = st.slider("Show first N rows:", 1, len(edited_df), 5)
            st.dataframe(edited_df.head(sample_size), use_container_width=True)

elif menu == "� วิเคราะห์ผลลัพธ์":
    st.header("📈 วิเคราะห์ผลลัพธ์ AI")
    
    if st.session_state.cleaned_df is None or len(st.session_state.cleaned_df) == 0:
        st.warning("⚠️ ยังไม่มีข้อมูล Clean กรุณา Clean Data จากเมนู 🧹 ก่อน")
    else:
        cleaned_df = st.session_state.cleaned_df
        
        # ตรวจสอบว่ามี intent_true หรือไม่
        if cleaned_df['intent_true'].isna().all() or (cleaned_df['intent_true'] == '').all():
            st.warning("⚠️ ยังไม่มี Intent (True) โปรดเพิ่มข้อมูล Intent ในเมนู 🧹 ก่อน")
        else:
            st.info("📊 กำลังวิเคราะห์ข้อมูล...")
            
            # 1. Accuracy Analysis
            st.markdown("---")
            st.subheader("🎯 Risk Level Distribution")
            
            # Count risk levels
            risk_counts = cleaned_df['risk_level'].value_counts()
            
            col1, col2, col3 = st.columns(3)
            
            high_count = len(cleaned_df[cleaned_df['risk_level'].str.contains('High', case=False, na=False)])
            medium_count = len(cleaned_df[cleaned_df['risk_level'].str.contains('Medium', case=False, na=False)])
            low_count = len(cleaned_df[cleaned_df['risk_level'].str.contains('Low', case=False, na=False)])
            
            with col1:
                st.metric("🔴 High Risk", high_count, f"{round(high_count/len(cleaned_df)*100, 1)}%")
            
            with col2:
                st.metric("🟡 Medium Risk", medium_count, f"{round(medium_count/len(cleaned_df)*100, 1)}%")
            
            with col3:
                st.metric("🟢 Low Risk", low_count, f"{round(low_count/len(cleaned_df)*100, 1)}%")
            
            # Risk Distribution Chart
            risk_data = pd.DataFrame({
                'Risk Level': ['High', 'Medium', 'Low'],
                'Count': [high_count, medium_count, low_count]
            })
            fig = px.pie(risk_data, values='Count', names='Risk Level',
                        title='ลักษณะการกระจายตัวของระดับความเสี่ยง',
                        color_discrete_map={
                            'High': '#e74c3c',      # สีแดง
                            'Medium': '#f39c12',    # สีส้ม
                            'Low': '#2ecc71'        # สีเขียว
                        })
            st.plotly_chart(fig, use_container_width=True)
            
            # Top High Risk Intents
            if high_count > 0:
                st.markdown("---")
                st.subheader("⚠️ High Risk Messages ที่ต้องติดตาม")
                
                high_risk_df = cleaned_df[cleaned_df['risk_level'].str.contains('High', case=False, na=False)][
                    ['user_message', 'intent_ai', 'risk_level']
                ]
                
                st.dataframe(high_risk_df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.subheader("1️⃣ ความแม่นยำของ AI (Accuracy)")
            
            accuracy_data = analyze_accuracy(cleaned_df)
            if accuracy_data:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📊 Total Messages", accuracy_data['total'])
                
                with col2:
                    st.metric("✅ Labeled", accuracy_data['labeled'])
                
                with col3:
                    st.metric("❌ Unlabeled", accuracy_data['unlabeled'])
                
                with col4:
                    st.metric("🎯 Accuracy", f"{accuracy_data['accuracy_percent']}%", 
                             delta=None if accuracy_data['accuracy_percent'] >= 80 else "needs improvement")
                
                # Metrics Chart
                st.markdown("---")
                st.markdown("#### 📈 ML Metrics (sklearn)")
                metrics_chart_data = pd.DataFrame({
                    'Metric': ['Accuracy', 'Precision', 'Recall', 'F1'],
                    'Score': [
                        accuracy_data['accuracy'] * 100,
                        accuracy_data['precision'] * 100,
                        accuracy_data['recall'] * 100,
                        accuracy_data['f1'] * 100
                    ]
                })
                fig = px.bar(metrics_chart_data, x='Metric', y='Score', 
                            title='ML Metrics Comparison',
                            color_discrete_sequence=['#667eea'],
                            text='Score',
                            labels={'Score': 'Score (%)'})
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_yaxes(range=[0, 100])
                st.plotly_chart(fig, use_container_width=True)
                
                # Confusion Matrix Section
                st.markdown("---")
                st.markdown("#### 🔍 Confusion Matrix - วิเคราะห์ความสับสน")
                st.info("📌 Confusion Matrix แสดงว่า AI ทำนายเจตนาได้ถูกต้องแล้วกี่ครั้ง และพลาดกี่ครั้ง ช่วยให้เห็นว่าเจตนาไหนที่ AI ยังสับสน")
                
                # Display confusion matrix chart and table
                cm_chart, cm_df = plot_confusion_matrix(accuracy_data)
                if cm_chart:
                    st.plotly_chart(cm_chart, use_container_width=True)
                    
                    # Show as table too
                    st.markdown("**Confusion Matrix ตารางค่า:**")
                    st.dataframe(cm_df, use_container_width=True)
                
                # Per-class metrics
                st.markdown("---")
                st.markdown("#### 📊 เมตริกต่อเจตนา (Per-Class Performance)")
                per_class_chart = plot_per_class_metrics(accuracy_data)
                if per_class_chart:
                    st.plotly_chart(per_class_chart, use_container_width=True)
                    
                    # Detailed classification report
                    st.markdown("**รายละเอียดเมตริกต่อเจตนา:**")
                    report_df = pd.DataFrame(accuracy_data['classification_report']).transpose()
                    st.dataframe(report_df, use_container_width=True)
            
            # 2. Response Length Analysis
            st.markdown("---")
            st.subheader("2️⃣ ความยาวของคำตอบ (Response Length)")
            
            length_data = analyze_response_length(cleaned_df)
            if length_data:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("📏 ความยาวเฉลี่ย", f"{length_data['average_length']} chars")
                
                with col2:
                    st.metric("📊 สั้นที่สุด", f"{length_data['min_length']} chars")
                
                with col3:
                    st.metric("📈 ยาวที่สุด", f"{length_data['max_length']} chars")
                
                # Length Distribution
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("🟩 สั้นเกินไป (< 50)", 
                             f"{length_data['short_responses']}\n({length_data['short_percent']}%)")
                
                with col2:
                    st.metric("🟪 ปกติ (50-500)", 
                             f"{length_data['normal_responses']}\n({length_data['normal_percent']}%)")
                
                with col3:
                    st.metric("🟥 ยาวเกินไป (> 500)", 
                             f"{length_data['long_responses']}\n({length_data['long_percent']}%)")
                
                # Chart
                length_chart_data = pd.DataFrame({
                    'ประเภท': ['สั้นเกินไป', 'ปกติ', 'ยาวเกินไป'],
                    'จำนวน': [length_data['short_responses'], length_data['normal_responses'], 
                             length_data['long_responses']]
                })
                fig = px.bar(length_chart_data, x='ประเภท', y='จำนวน',
                            title='การกระจายตัวของความยาวคำตอบ',
                            color='ประเภท',
                            color_discrete_sequence=['#3498db', '#2ecc71', '#e74c3c'])
                st.plotly_chart(fig, use_container_width=True)
            
            # 3. Top Intents
            st.markdown("---")
            st.subheader("3️⃣ หัวข้อที่ลูกค้าถามเยอะสุด (Top Intents)")
            
            intents_data = find_top_intents(cleaned_df)
            if intents_data and intents_data['top_intents']:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("🎯 Total Unique Intents", intents_data['total_unique_intents'])
                
                with col2:
                    st.metric("📝 Total Messages", intents_data['total_messages'])
                
                # Top Intents Table
                st.subheader("Top 10 Intent ที่ถูกถามบ่อยที่สุด:")
                
                top_intents_df = pd.DataFrame(
                    intents_data['top_intents'],
                    columns=['Intent', 'Count']
                )
                top_intents_df['Percentage'] = (top_intents_df['Count'] / intents_data['total_messages'] * 100).round(2)
                top_intents_df['Percentage'] = top_intents_df['Percentage'].apply(lambda x: f"{x}%")
                
                st.dataframe(top_intents_df, use_container_width=True, hide_index=True)
                
                # Chart
                fig = px.bar(top_intents_df, x='Intent', y='Count',
                            title='Top 10 Intent ที่ถูกถามบ่อยที่สุด',
                            labels={'Intent': 'Intent Type', 'Count': 'Frequency'},
                            color='Count',
                            color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ℹ️ ยังไม่มี Intent ที่ถูกใส่เพื่อวิเคราะห์")
            
            # 4. Response Risk Analysis
            st.markdown("---")
            st.subheader("4️⃣ การวิเคราะห์ความเสี่ยง (Response Risk)")
            
            risk_data = analyze_response_risk(cleaned_df)
            if risk_data:
                # Risk Score
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    risk_color = "🟢" if "ต่ำ" in risk_data['risk_level'] else "🟡" if "ปานกลาง" in risk_data['risk_level'] else "🔴"
                    st.metric(f"⚠️ Risk Score", f"{risk_data['risk_score']}/100",
                             delta=f"{risk_color} {risk_data['risk_level']}")
                
                with col2:
                    st.metric("❌ อัตราตอบผิด", f"{risk_data['incorrect_rate']}%")
                
                with col3:
                    st.metric("🟩 อัตราตอบสั้น", f"{risk_data['short_response_rate']}%")
                
                with col4:
                    if risk_data['risk_score'] < 25:
                        status = "✅ ปลอดภัย"
                        color = "#2ecc71"
                    elif risk_data['risk_score'] < 50:
                        status = "⚠️ ต้องติดตาม"
                        color = "#f39c12"
                    else:
                        status = "🚨 ต้องปรับปรุง"
                        color = "#e74c3c"
                    
                    st.markdown(f"<h3 style='color:{color}'>{status}</h3>", unsafe_allow_html=True)
                
                # Risk Factors
                st.subheader("📊 ปัจจัยความเสี่ยง:")
                
                risk_factors = []
                if risk_data['incorrect_rate'] > 20:
                    risk_factors.append(f"🔴 อัตราคำตอบผิดสูง ({risk_data['incorrect_rate']}%)")
                
                if risk_data['short_response_rate'] > 30:
                    risk_factors.append(f"🟡 คำตอบสั้นเกินไป ({risk_data['short_response_rate']}%)")
                
                if not risk_factors:
                    st.success("✅ ไม่พบปัจจัยความเสี่ยงที่มีนัยสำคัญ")
                else:
                    for factor in risk_factors:
                        st.warning(factor)
                # Risk Distribution Chart
                if 'risk_distribution' in risk_data:
                    st.markdown("#### 📊 การกระจายความเสี่ยง (Risk Distribution)")
                    risk_dist_df = pd.DataFrame(risk_data['risk_distribution'].items(), columns=['Risk Level', 'Count'])
                    risk_dist_df['Percentage'] = (risk_dist_df['Count'] / risk_dist_df['Count'].sum() * 100).round(2)
                    fig = px.pie(risk_dist_df, names='Risk Level', values='Count', title='Risk Distribution',
                                 color_discrete_sequence=['#2ecc71', '#f39c12', '#e74c3c'])
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(risk_dist_df, use_container_width=True)

                # Top Fail Cases Table
                if 'top_fail_cases' in risk_data and risk_data['top_fail_cases']:
                    st.markdown("#### 🚨 Top Fail Cases (AI ตอบผิด/FAIL)")
                    fail_df = pd.DataFrame(risk_data['top_fail_cases'])
                    st.dataframe(fail_df, use_container_width=True)
            
            st.markdown("---")
            st.subheader("💡 คำแนะนำ:")
            
            recommendations = []
            
            if accuracy_data and accuracy_data['accuracy_percent'] < 80:
                recommendations.append("📌 ปรับปรุงความแม่นยำของ AI เพิ่มเติม")
            
            if length_data and length_data['short_percent'] > 30:
                recommendations.append("📌 ให้ AI ตอบอย่างละเอียดมากขึ้น")
            
            if length_data and length_data['long_percent'] > 30:
                recommendations.append("📌 ปรับให้ AI ตอบสั้นและกระชับขึ้น")
            
            if not recommendations:
                st.info("✅ ระบบทำงานได้ดีแล้ว")
            else:
                for rec in recommendations:
                    st.info(rec)

elif menu == "�📊 ดูสถิติ":
    if st.session_state.metrics is None:
        st.warning("⚠️ ยังไม่มีข้อมูล กรุณา Import ข้อมูลก่อน")
    else:
        metrics = st.session_state.metrics
        
        st.header("📊 Performance Metrics Analysis")
        
        # แสดง Metrics Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📨 Total Messages", metrics['total_messages'])
        
        with col2:
            st.metric("🔢 Total Tokens", f"{metrics['total_tokens']:,}")
        
        with col3:
            st.metric("📝 Avg Response Tokens", metrics['average_total_tokens'])
        
        with col4:
            st.metric("📏 Avg Response Length", f"{metrics['average_response_length']} chars")
        
        st.markdown("---")
        
        # Detailed Summary
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Token Statistics")
            stats_data = {
                "Total Prompt Tokens": f"{metrics['total_prompt_tokens']:,}",
                "Total Candidate Tokens": f"{metrics['total_candidate_tokens']:,}",
                "Average Prompt Tokens": metrics['average_prompt_tokens'],
                "Average Candidate Tokens": metrics['average_candidate_tokens'],
            }
            for key, value in stats_data.items():
                st.write(f"**{key}:** {value}")
        
        with col2:
            st.subheader("🎯 Range Analysis")
            range_data = {
                "Minimum Total Tokens": metrics['min_total_tokens'],
                "Maximum Total Tokens": metrics['max_total_tokens'],
                "Token Range": f"{metrics['max_total_tokens'] - metrics['min_total_tokens']}",
                "Generated At": metrics['timestamp'][:10],
            }
            for key, value in range_data.items():
                st.write(f"**{key}:** {value}")
        
        st.markdown("---")
        
        # ========== KPI EVALUATION SECTION ==========
        st.subheader("📊 KPI Performance Evaluation")
        st.info("💡 ตรวจสอบว่า metrics ของคุณอยู่ในมาตรฐาน(KPI) หรือไม่")
        
        # Create KPI evaluation display
        kpi_tab1, kpi_tab2 = st.tabs(["📈 KPI Overview", "💡 Recommendations"])
        
        with kpi_tab1:
            # Token Metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📝 Prompt Token Analysis")
                avg_prompt = metrics['average_prompt_tokens']
                status, advice = evaluate_metric("avg_prompt_tokens", avg_prompt, KPI_STANDARD["avg_prompt_tokens"])
                
                st.metric("Avg Prompt Tokens", avg_prompt, delta=f"{avg_prompt - KPI_STANDARD['avg_prompt_tokens']} vs standard")
                st.write(f"**Status:** {status}")
                st.write(f"**Standard:** {KPI_STANDARD['avg_prompt_tokens']} tokens")
                
                if avg_prompt > KPI_STANDARD['avg_prompt_tokens']:
                    st.warning(f"⚠️ ปัจจุบัน: {avg_prompt} > มาตรฐาน: {KPI_STANDARD['avg_prompt_tokens']}")
                else:
                    st.success(f"✓ ปัจจุบัน: {avg_prompt} ≤ มาตรฐาน: {KPI_STANDARD['avg_prompt_tokens']}")
            
            with col2:
                st.markdown("### 💬 Response Token Analysis")
                avg_response = metrics['average_candidate_tokens']
                status, advice = evaluate_metric("avg_response_tokens", avg_response, KPI_STANDARD["avg_response_tokens"])
                
                st.metric("Avg Response Tokens", avg_response, delta=f"{avg_response - KPI_STANDARD['avg_response_tokens']} vs standard")
                st.write(f"**Status:** {status}")
                st.write(f"**Standard:** {KPI_STANDARD['avg_response_tokens']} tokens")
                
                if avg_response > KPI_STANDARD['avg_response_tokens']:
                    st.warning(f"⚠️ ปัจจุบัน: {avg_response} > มาตรฐาน: {KPI_STANDARD['avg_response_tokens']}")
                else:
                    st.success(f"✓ ปัจจุบัน: {avg_response} ≤ มาตรฐาน: {KPI_STANDARD['avg_response_tokens']}")
            
            # Response Length Analysis
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📏 Response Length Analysis")
                response_len = metrics['average_response_length']
                st.metric("Avg Response Length", f"{response_len} chars", delta=f"{response_len - KPI_STANDARD['response_length']} vs standard")
                st.write(f"**Standard:** {KPI_STANDARD['response_length']} characters")
                
                if response_len > KPI_STANDARD['response_length'] * 1.15:
                    st.error(f"🔴 ยาวเกินไป: {response_len} chars (standard: {KPI_STANDARD['response_length']})")
                elif response_len > KPI_STANDARD['response_length']:
                    st.warning(f"🟡 นิดนึ่งยาว: {response_len} chars (standard: {KPI_STANDARD['response_length']})")
                else:
                    st.success(f"🟢 ดี: {response_len} chars ≤ {KPI_STANDARD['response_length']}")
            
            with col1:
                # Accuracy from cleaned data if available
                if st.session_state.cleaned_df is not None:
                    accuracy_result = analyze_accuracy(st.session_state.cleaned_df)
                    if accuracy_result:
                        accuracy_pct = accuracy_result['accuracy_percent'] / 100
                        st.markdown("### 🎯 Intent Classification Accuracy")
                        st.metric("Accuracy", f"{accuracy_result['accuracy_percent']}%", 
                                delta=f"{(accuracy_pct - KPI_STANDARD['accuracy']) * 100:.1f}% vs standard")
                        st.write(f"**Standard:** {KPI_STANDARD['accuracy']*100}%")
                        st.write(f"**Labeled:** {accuracy_result['labeled']}/{accuracy_result['total']} messages")
                        
                        if accuracy_pct >= KPI_STANDARD['accuracy']:
                            st.success(f"🟢 ดี: {accuracy_result['accuracy_percent']}% ≥ {KPI_STANDARD['accuracy']*100}%")
                        else:
                            st.warning(f"🟡 ต่ำกว่ามาตรฐาน: {accuracy_result['accuracy_percent']}% < {KPI_STANDARD['accuracy']*100}%")
        
        with kpi_tab2:
            st.markdown("### 💡 Improvement Recommendations")
            
            recommendations_list = []
            
            # Check each metric and add recommendations
            avg_prompt = metrics['average_prompt_tokens']
            if avg_prompt > KPI_STANDARD['avg_prompt_tokens']:
                metric_name = "avg_prompt_tokens"
                recommendations_list.append((metric_name, avg_prompt, recommendation(metric_name, avg_prompt)))
            
            avg_response = metrics['average_candidate_tokens']
            if avg_response > KPI_STANDARD['avg_response_tokens']:
                metric_name = "avg_response_tokens"
                recommendations_list.append((metric_name, avg_response, recommendation(metric_name, avg_response)))
            
            response_len = metrics['average_response_length']
            if response_len > KPI_STANDARD['response_length']:
                metric_name = "response_length"
                recommendations_list.append((metric_name, response_len, recommendation(metric_name, response_len)))
            
            if st.session_state.cleaned_df is not None:
                accuracy_result = analyze_accuracy(st.session_state.cleaned_df)
                if accuracy_result and (accuracy_result['accuracy_percent'] / 100) < KPI_STANDARD['accuracy']:
                    metric_name = "accuracy"
                    recommendations_list.append((metric_name, accuracy_result['accuracy_percent'], recommendation(metric_name, accuracy_result['accuracy_percent'])))
            
            if not recommendations_list:
                st.success("🎉 ยินดีด้วย! ทุก metrics อยู่ในมาตรฐาน KPI")
            else:
                for idx, (metric_name, value, advice_text) in enumerate(recommendations_list, 1):
                    with st.expander(f"📌 {idx}. {metric_name.upper()} (ปัจจุบัน: {value})"):
                        st.markdown(advice_text)
            
            # Display all KPI standards
            st.markdown("---")
            st.markdown("### 📋 KPI Standards Reference")
            kpi_df = pd.DataFrame([
                {"Metric": "Average Prompt Tokens", "Standard": f"{KPI_STANDARD['avg_prompt_tokens']} tokens", "Description": "เฉลี่ยความยาว prompt"},
                {"Metric": "Average Response Tokens", "Standard": f"{KPI_STANDARD['avg_response_tokens']} tokens", "Description": "เฉลี่ยความยาว response"},
                {"Metric": "Average Response Length", "Standard": f"{KPI_STANDARD['response_length']} chars", "Description": "เฉลี่ยจำนวนตัวอักษร"},
                {"Metric": "Classification Accuracy", "Standard": f"{KPI_STANDARD['accuracy']*100}%", "Description": "ความถูกต้องของ intent"},
            ])
            st.dataframe(kpi_df, use_container_width=True)
        
        # ========== Business Insights Tab ==========
        insight_tab1, insight_tab2 = st.tabs(["💼 Business Impact", "🎯 System Health"])
        
        with insight_tab1:
            st.markdown("### 💼 Business Impact Analysis")
            st.info("📊 คำนวณผลกระทบทางธุรกิจจากการวิเคราะห์ AI metrics")
            
            if st.session_state.cleaned_df is not None:
                accuracy_result = analyze_accuracy(st.session_state.cleaned_df)
                if accuracy_result:
                    # Get business translation
                    business = translate_business(accuracy_result)
                    
                    st.markdown("#### 📊 Metrics (sklearn)")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Accuracy", f"{accuracy_result['accuracy']*100:.1f}%")
                    with col2:
                        st.metric("Precision", f"{accuracy_result['precision']*100:.1f}%")
                    with col3:
                        st.metric("Recall", f"{accuracy_result['recall']*100:.1f}%")
                    with col4:
                        st.metric("F1 Score", f"{accuracy_result['f1']*100:.1f}%")
                    
                    st.markdown("---")
                    st.markdown("#### 💡 Business Impact")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.error(f"💰 {business['sales_impact']}")
                    with col2:
                        st.warning(f"📈 {business['missed_opportunity']}")
                    with col3:
                        st.warning(f"🛍️ {business['brand_risk']}")
                    
                    st.markdown("---")
                    st.markdown("#### 📋 Summary")
                    st.info(f"""
**Labeled Data:** {accuracy_result['labeled']} / {accuracy_result['total']} ({accuracy_result['labeled']/accuracy_result['total']*100:.1f}%)

**ML Metrics (sklearn weighted average):**
- บอก Accuracy = {business['accuracy']}
- Precision = {business['precision']}
- Recall = {business['recall']}
- F1 Score = {business['f1']}

**Business Translation:**
- ยอดขาย: {business['sales_impact']}
- โอกาส: {business['missed_opportunity']}
- แบรนด์: {business['brand_risk']}
                    """)
                else:
                    st.warning("⚠️ ต้องมี intent_true labeled อย่างน้อย 1 row")
            else:
                st.warning("⚠️ ต้องมี cleaned data กับ labeled intents ก่อน")
        
        with insight_tab2:
            st.markdown("### 🎯 System Health Status")
            st.info("🔍 ประเมิน Health ของ Chatbot System (sklearn metrics)")
            
            if st.session_state.cleaned_df is not None:
                accuracy_result = analyze_accuracy(st.session_state.cleaned_df)
                if accuracy_result:
                    status_json = assess_system_health(
                        accuracy_result['accuracy'],
                        accuracy_result['precision'],
                        accuracy_result['recall'],
                        accuracy_result['f1']
                    )
                    
                    # Display status
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("#### 📊 System Status")
                        if "🔴" in status_json.get("status", ""):
                            st.error(status_json.get("status", "N/A"))
                        elif "🟡" in status_json.get("status", ""):
                            st.warning(status_json.get("status", "N/A"))
                        else:
                            st.success(status_json.get("status", "N/A"))
                    
                    with col2:
                        st.markdown("#### ⚠️ Risk Assessment")
                        risk_type = status_json.get("risk", "N/A")
                        st.warning(risk_type)
                    
                    with col3:
                        st.markdown("#### 🎯 Priority Action")
                        action = status_json.get("priority_action", "N/A")
                        st.info(action)
                    
                    # Rules reference
                    st.markdown("---")
                    st.markdown("#### 📋 Health Rules")
                    rules_df = pd.DataFrame([
                        {"Rule": "Accuracy < 70%", "Status": "🔴 Critical"},
                        {"Rule": "Precision < 75%", "Status": "🔴 Brand Risk"},
                        {"Rule": "Recall < 60%", "Status": "🔴 Missing Opportunities"},
                        {"Rule": "F1 < 70%", "Status": "🔴 Unsafe to Scale"},
                    ])
                    st.dataframe(rules_df, use_container_width=True, hide_index=True)
            else:
                st.warning("⚠️ ต้องมี cleaned data กับ labeled intents ก่อน")
        
        st.markdown("---")
        
        # Export Section
        st.subheader("📥 Export Report")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Export CSV
            csv_content = pd.DataFrame([metrics]).to_csv(index=False)
            st.download_button(
                label="📊 Download CSV",
                data=csv_content,
                file_name=f"metrics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Export JSON
            json_content = json.dumps(metrics, indent=2, ensure_ascii=False)
            st.download_button(
                label="📄 Download JSON",
                data=json_content,
                file_name=f"metrics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col3:
            # Export HTML
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot Performance Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }}
        h1 {{
            color: #667eea;
            text-align: center;
            margin-bottom: 30px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .metric-value {{
            font-size: 1.8em;
            font-weight: bold;
            margin-top: 10px;
        }}
        .summary {{
            background: #f5f7ff;
            border-left: 4px solid #667eea;
            padding: 20px;
            border-radius: 8px;
        }}
        .summary-row {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #e0e0e0;
        }}
        .footer {{
            text-align: center;
            color: #999;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Chatbot Performance Metrics Report</h1>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Messages</div>
                <div class="metric-value">{metrics['total_messages']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Tokens</div>
                <div class="metric-value">{metrics['total_tokens']:,}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Response Tokens</div>
                <div class="metric-value">{metrics['average_total_tokens']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Response Length</div>
                <div class="metric-value">{metrics['average_response_length']} chars</div>
            </div>
        </div>
        
        <div class="summary">
            <h2>📋 Detailed Summary</h2>
            <div class="summary-row">
                <span>Total Prompt Tokens:</span>
                <strong>{metrics['total_prompt_tokens']:,}</strong>
            </div>
            <div class="summary-row">
                <span>Total Candidate Tokens:</span>
                <strong>{metrics['total_candidate_tokens']:,}</strong>
            </div>
            <div class="summary-row">
                <span>Average Prompt Tokens:</span>
                <strong>{metrics['average_prompt_tokens']}</strong>
            </div>
            <div class="summary-row">
                <span>Average Candidate Tokens:</span>
                <strong>{metrics['average_candidate_tokens']}</strong>
            </div>
            <div class="summary-row">
                <span>Minimum Total Tokens:</span>
                <strong>{metrics['min_total_tokens']}</strong>
            </div>
            <div class="summary-row">
                <span>Maximum Total Tokens:</span>
                <strong>{metrics['max_total_tokens']}</strong>
            </div>
            <div class="summary-row">
                <span>Report Generated:</span>
                <strong>{metrics['timestamp']}</strong>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by Chatbot Performance Metrics Analyzer</p>
            <p>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
            """
            st.download_button(
                label="🌐 Download HTML",
                data=html_content,
                file_name=f"metrics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html"
            )
        
        # Clear Data Button
        st.markdown("---")
        if st.button("🔄 Clear Data"):
            st.session_state.messages_df = None
            st.session_state.metrics = None
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("**Version:** 1.0.0\n**Made with:** 🐍 Python + Streamlit")
