import streamlit as st
from datetime import datetime
from openai import OpenAI
from pymongo import MongoClient

# ------------------ MongoDB Setup ------------------
client_mongo = MongoClient(st.secrets["mongo"]["uri"])
db = client_mongo["founder_coach"]
reflections_collection = db["reflections"]

# ------------------ AI Client Setup (Together/OpenAI) ------------------
client = OpenAI(
    api_key=st.secrets["openai"]["api_key"],
    base_url="https://api.together.xyz/v1"
)

# ------------------ Streamlit UI Setup ------------------
st.set_page_config(page_title='Founder Mental Coach', layout='centered')
st.title("🧠 Founder Mental Coach")

st.subheader("📝 Weekly Reflection")
reflection = st.text_area("Write your weekly reflection:")
confidence = st.slider("Confidence level", 1, 5)
emotion = st.selectbox('Emotion', ['Focused', 'Anxious', 'Motivated', 'Overwhelmed', 'Frustrated'])

# ------------------ Submit and Save ------------------
if st.button("Submit"):
    if reflection.strip() == "":
        st.warning("Please write something in your reflection before submitting.")
    else:
        entry = {
            "timestamp": datetime.now(),  # store as datetime object
            "reflection": reflection,
            "confidence": confidence,
            "emotion": emotion
        }
        reflections_collection.insert_one(entry)
        st.success("Reflection submitted and saved to database!")

        # ------------------ AI Agent Execution ------------------
        with st.spinner("Thinking..."):
            prompt = f"""
You are a calm and thoughtful founder coach. A founder wrote the following reflection:

"{reflection}"

Their emotion is: {emotion}, and their confidence level is: {confidence}/5.

Summarize the core issue in exactly 2 sentences.
Reframe it positively in 1 sentence.
Suggest 1 actionable step for the next week in 1 sentence.

Respond in this format:
Summary:
Reframe:
Next Step:
"""
            response = client.chat.completions.create(
                model="meta-llama/Llama-3-70b-chat-hf",  # or gpt-3.5-turbo if using OpenAI
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                top_p=0.9,
                max_tokens=250
            )

            result = response.choices[0].message.content
            st.subheader("🧠 Coach’s Response")
            st.markdown(result)

# # ------------------ Reflection History ------------------
# reflections = list(reflections_collection.find().sort("timestamp", -1))
# if reflections:
#     st.subheader("📚 Your Reflection History")
#     for ref in reflections:
#         try:
#             time_str = ref["timestamp"].strftime("%Y-%m-%d %H:%M")
#         except Exception:
#             time_str = ref.get("timestamp", "Unknown Date")
#         st.markdown(f"**{time_str}** - *{ref['emotion']}*, Confidence: {ref['confidence']}")
#         st.markdown(f"> {ref['reflection']}")
#         st.markdown("---")

# ------------------ Reflection History with See More / See Less ------------------
st.subheader("📚 Your Reflection History")

# Fetch all reflections, sorted by latest first
all_reflections = list(reflections_collection.find().sort("timestamp", -1))

# Initialize session state for how many to show
if "num_visible" not in st.session_state:
    st.session_state.num_visible = 5  # show 5 initially

# Slice the reflections list
visible_reflections = all_reflections[:st.session_state.num_visible]

# Display visible reflections
for ref in visible_reflections:
    try:
        time_str = ref["timestamp"].strftime("%Y-%m-%d %H:%M")
    except:
        time_str = str(ref.get("timestamp", "Unknown"))

    st.markdown(f"**{time_str}** - *{ref['emotion']}*, Confidence: {ref['confidence']}")
    st.markdown(f"> {ref['reflection']}")
    st.markdown("---")

# Buttons to control visibility
col1, col2 = st.columns(2)

with col1:
    if st.session_state.num_visible < len(all_reflections):
        if st.button("🔽 See More"):
            st.session_state.num_visible += 5

with col2:
    if st.session_state.num_visible > 5:
        if st.button("🔼 See Less"):
            st.session_state.num_visible = max(5, st.session_state.num_visible - 5)


