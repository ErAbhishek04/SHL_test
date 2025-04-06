import streamlit as st
import requests

# Title
st.title("🧠 SHL Assessment Recommender")

# User input
query = st.text_area("Enter job description or natural language query", height=200)

# Button
if st.button("🔍 Get Recommendations"):
    if query.strip():
        with st.spinner("Fetching recommendations..."):
            try:
                # 🔗 Update to your deployed FastAPI URL if remote
                backend_url = "https://shl-test-8mez.onrender.com"
                response = requests.post(backend_url, json={"query": query})
                
                if response.status_code == 200:
                    data = response.json()
                    st.markdown("---")
                    st.markdown("### ✨ Recommended Assessments")
                    st.markdown(data.get("groq_suggestion", "No suggestion found."))
                else:
                    st.error("❌ Error: Could not fetch recommendations.")
            except Exception as e:
                st.error(f"⚠️ Exception: {str(e)}")
    else:
        st.warning("Please enter a query.")
