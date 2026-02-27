import streamlit as st
import os
import tempfile
from extractor import extract_biomarkers
from comparator import load_benchmarks, compare, group_by_category
from rag import generate_summary

# --- PAGE CONFIG ---
st.set_page_config(page_title="Lab Report AI", page_icon="🧬", layout="wide")

# --- CSS HACKS FOR BETTER UI ---
st.markdown("""
    <style>
    .stMetricDelta > div { font-size: 14px !important; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: PATIENT DETAILS & SETTINGS ---
with st.sidebar:
    st.header("⚙️ Patient & Settings")
    patient_name = st.text_input("Patient Name", value="Shashank")
    gender = st.selectbox("Gender", ["male", "female"])

# --- MAIN UI ---
st.title("🧬 Lab Report Intelligence Agent")
st.markdown("Upload a raw diagnostic PDF to instantly extract biomarkers, compare against medical benchmarks, and generate a patient-friendly summary.")

# DYNAMIC UPLOAD WIDGET
uploaded_file = st.file_uploader("Upload Blood Report (PDF)", type=["pdf"])

if uploaded_file is not None:
    if st.button("🧠 Analyze Report", type="primary", use_container_width=True):
        
        # This stays static as requested
        benchmark_path = "medical_benchmark.json" 
        
        # --- 1. EXTRACTION PHASE (DYNAMIC PDF HANDLING) ---
        with st.spinner("🔍 Extracting tabular data from uploaded PDF..."):
            
            # Securely create a dynamic temporary file path for whatever PDF is uploaded
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                dynamic_pdf_path = tmp_file.name
            
            # Run your actual extractor on the dynamic path
            extracted_data = extract_biomarkers(dynamic_pdf_path, benchmark_path)
            
            # Clean up: delete the temporary PDF from your Mac so it doesn't take up space
            os.remove(dynamic_pdf_path) 
            
        # Safety catch in case the PDF is unreadable
        if not extracted_data:
            st.error("❌ No biomarkers found. Please check the PDF format or extraction logic.")
            st.stop()

        # --- 2. COMPARISON PHASE ---
        with st.spinner("📊 Comparing against medical benchmarks..."):
            benchmarks = load_benchmarks(benchmark_path)
            compared_data = compare(extracted_data, benchmarks, gender=gender)
            grouped_data = group_by_category(compared_data)
        
        # --- DISPLAY TABULAR RESULTS ---
        st.subheader("🔬 Extracted Biomarkers")
        
        # Create tabs for different categories to make it look clean
        tabs = st.tabs(list(grouped_data.keys()))
        
        for idx, (category, markers) in enumerate(grouped_data.items()):
            with tabs[idx]:
                # Create a 3-column grid for the metrics
                cols = st.columns(3)
                col_idx = 0
                for name, data in markers.items():
                    val_str = f"{data['value']} {data['unit']}"
                    
                    # Determine color and delta
                    if data["status"] == "low":
                        delta = "LOW"
                        delta_color = "inverse" # Red
                    elif data["status"] == "high":
                        delta = "HIGH"
                        delta_color = "inverse" # Red
                    else:
                        delta = "NORMAL"
                        delta_color = "normal"  # Green
                    
                    cols[col_idx % 3].metric(label=name, value=val_str, delta=delta, delta_color=delta_color)
                    col_idx += 1

        # --- 3. GENERATION PHASE ---
        st.markdown("---")
        st.subheader("🤖 AI Patient Summary")
        
        with st.spinner("Connecting to Gemini API to generate empathetic summary..."):
            try:
                summary = generate_summary(compared_data, benchmarks, patient_name=patient_name, gender=gender)
                st.info("Agent generation complete. Sourced purely from verified clinical context.")
                st.markdown(summary)
            except Exception as e:
                st.error(f"API Error: {e}")
                st.warning("Make sure your .env file has GEMINI_API_KEY set correctly!")