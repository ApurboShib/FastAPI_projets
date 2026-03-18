import streamlit as st
import requests

# Configure page settings
st.set_page_config(
    page_title="Health Insurance  Premium Predictor",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a beautiful modern design
st.markdown("""
    <style>
    /* Styling for the main title */
    .main-title {
        font-size: 42px;
        font-weight: 700;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0px;
    }
    /* Subtitle styling */
    .sub-title {
        font-size: 18px;
        color: #64748B;
        text-align: center;
        margin-bottom: 40px;
    }
    /* Style for the predict button */
    .stButton>button {
        width: 100%;
        background-color: #2563EB;
        color: white;
        font-weight: 600;
        padding: 10px 0;
        border-radius: 8px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    /* Card-like container styling */
    .css-1r6slb0, .css-18e3th9 {
        background-color: #F8FAFC;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Main UI
st.markdown("<h1 class='main-title'>🏥 Health Insurance Premium Predictor</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Enter your details below to instantly predict your health premium category using our advanced ML model.</p>", unsafe_allow_html=True)

# Create a nice layout grouping fields
with st.container():
    st.markdown("### 👤 Personal Information")
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input("Age", min_value=1, max_value=119, value=30, step=1, help="Age in years")
        weight = st.number_input("Weight (kg)", min_value=1.0, max_value=120.0, value=75.0, step=0.1, help="Weight in kilograms")
        height = st.number_input("Height (m)", min_value=0.5, max_value=2.5, value=1.70, step=0.01, help="Height in meters")
        
    with col2:
        city = st.text_input("City of Residence", value="Dhaka", placeholder="e.g. Dhaka, Chittagong")
        occupations = st.selectbox("Occupation", ['Self-Employed', 'Retired', 'Student', 'Employed', 'Unemployed'])
        income_lpa = st.selectbox("Annual Income (LPA)", ['Below 3 LPA', '3-6 LPA', '6-10 LPA', '10-15 LPA', 'Above 15 LPA'])

    st.markdown("<br>", unsafe_allow_html=True)
    smoking = st.toggle("Do you smoke?", value=False)
    
st.markdown("---")

# Prediction action
api_url = "http://127.0.0.1:8000/predict"

if st.button("Predict Premium Category &nbsp; "):
    payload = {
        "age": int(age),
        "weight": float(weight),
        "height": float(height),
        "income_lpa": income_lpa,
        "smoking": bool(smoking),
        "city": city,
        "occupations": occupations
    }
    
    with st.spinner("Analyzing your profile..."):
        try:
            response = requests.post(api_url, json=payload)
            
            if response.status_code == 200:
                prediction = response.json().get("prediction-catagory", "Unknown")
                
                # Show dynamic success styles based on result
                if "High" in prediction:
                    st.markdown(f"""
                        <div style="padding: 1rem; border-radius: 0.5rem; background-color: #d1fae5; color: #065f46; border: 1px solid #10b981; font-weight: 500;">
                            <strong>Predicted Category:</strong> {prediction}
                        </div>
                    """, unsafe_allow_html=True)
                elif "Medium" in prediction:
                    st.markdown(f"""
                        <div style="padding: 1rem; border-radius: 0.5rem; background-color: #fef3c7; color: #92400e; border: 1px solid #f59e0b; font-weight: 500;">
                            <strong>Predicted Category:</strong> {prediction}
                        </div>
                    """, unsafe_allow_html=True)
                else:    
                    st.markdown(f"""
                        <div style="padding: 1rem; border-radius: 0.5rem; background-color: #fee2e2; color: #991b1b; border: 1px solid #ef4444; font-weight: 500;">
                            <strong>Predicted Category:</strong> {prediction}
                        </div>
                    """, unsafe_allow_html=True)
            else:
                error_detail = response.json().get("detail", response.text)
                st.error(f"Prediction missing or failed: {error_detail}")
                
        except requests.exceptions.ConnectionError:
            st.error(" Could not connect to the Backend API. Make sure your FastAPI server is running on `127.0.0.1:8000`")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
