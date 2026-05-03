import streamlit as st
import random
import pandas as pd 
import google.generativeai as genai
from reportlab.pdfgen import canvas
from io import BytesIO
st.set_page_config(page_title="VoltGuard AI", layout="wide") 
API_KEY = st.secrets["API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("models/gemini-2.0-flash-lite")
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to right, #f7f8fc, #eef2f7);
        color: #1a1a1a;
    }

    /* Metric cards styling */
    div[data-testid="metric-container"] {
        background-color: white;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
    }

    /* Buttons styling */
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
    }

    .stButton>button:hover {
        background-color: #45a049;
    }

    /* Subheader style */
    h1, h2, h3 {
        color: #1f3b57;
    }
    </style>
    """,
    unsafe_allow_html=True
)


if "data" not in st.session_state:
    st.session_state.data = {
        "time": [],
        "voltage": [],
        "current": [],
        "temp": []
    }

st.title("⚡ VoltGuard AI - Smart Electrical Safety System")
st.markdown("Real-Time Monitoring Dashboard for  Voltage, Current & Temperature")
st.markdown("---")
# SAFE RANGES DISPLAY
st.subheader("📊 Safe Operating Ranges")

colA, colB, colC = st.columns(3)

colA.info("🔌 Voltage: 198V – 242V")
colB.info("⚡ Current: 0A – 20A")
colC.info("🌡️ Temperature: 0°C – 70°C")

st.markdown("---")

# SIMULATED SENSOR VALUES
voltage = random.randint(210, 260)
current = random.randint(5, 25)
temp = random.randint(30, 90)

st.session_state.data["time"].append(len(st.session_state.data["time"]))
st.session_state.data["voltage"].append(voltage)
st.session_state.data["current"].append(current)
st.session_state.data["temp"].append(temp)

st.subheader("📡 Live Electrical Data")

c1, c2, c3 = st.columns(3)

c1.metric("Voltage", f"{voltage} V")
c2.metric("Current", f"{current} A")
c3.metric("Temperature", f"{temp} °C")

st.markdown("---")
st.subheader("📈 Live System Trends")

df = pd.DataFrame(st.session_state.data)

st.line_chart(df.set_index("time")[["voltage", "current", "temp"]])
st.markdown("---")

st.subheader("📄 System Report")
if st.button("Generate Report"):

    pdf_buffer = BytesIO()

    pdf = canvas.Canvas(pdf_buffer)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(180, 800, "VoltGuard AI Report")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 750, f"Total Samples: {len(df)}")
    pdf.drawString(50, 720, f"Average Voltage: {df['voltage'].mean():.2f} V")
    pdf.drawString(50, 690, f"Average Current: {df['current'].mean():.2f} A")
    pdf.drawString(50, 660, f"Average Temperature: {df['temp'].mean():.2f} °C")

    pdf.drawString(50, 620, "System Report Generated Successfully")

    pdf.save()

    pdf_buffer.seek(0)

    st.download_button(
        "📄 Download PDF Report",
        pdf_buffer,
        "voltguard_report.pdf",
        "application/pdf"
    )


# ANALYSIS BUTTON
if st.button("Analyze System"):

    st.subheader("⚡ System Analysis Report")

    if voltage < 198 or voltage > 242:
        st.error("⚠️ Voltage Out of Safe Range!")
        st.write("Reason: Voltage instability detected due to supply fluctuation.")
        st.write("Action: Check stabilizer or power source immediately.")
    else:
        st.success("✔️ Voltage is Normal")

    if current > 20:
        st.error("⚠️ Overcurrent Detected!")
        st.write("Reason: Electrical load exceeds safe threshold.")
        st.write("Action: Reduce connected devices or load.")
    else:
        st.success("✔️ Current is Normal")

    if temp <= 70:
        st.success("🌡️ Temperature Normal")
    elif temp <= 85:
        st.warning("🌡️ Temperature High (Warning Zone)")
        st.write("Reason: Heat accumulation in system components.")
        st.write("Action: Improve cooling or reduce load.")
    else:
        st.error("🌡️ Critical Overheating!")
        st.write("Reason: System overheating beyond safe limit.")
        st.write("Action: Immediate shutdown required.")

    # ✅ ALWAYS DEFINE PROMPT
    prompt = f"""
Voltage = {voltage}V
Current = {current}A
Temperature = {temp}°C
Provide professional electrical safety feedback and recommendations.
"""

    try:
      if "ai_feedback" not in st.session_state:

           response = model.generate_content(prompt)

           st.session_state.ai_feedback = response.text

            st.subheader("🤖 AI-Based Feedback")

            st.write(st.session_state.ai_feedback)
             except Exception as e:
              st.error(f"AI Error: {e}")