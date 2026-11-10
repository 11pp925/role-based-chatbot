import streamlit as st
import requests

st.set_page_config(page_title="Role-based Creative Chatbot", page_icon="🎭", layout="wide")

ROLES = {
    "🎥 Video Director": {
        "system": (
            "You are an experienced video director. Answer with concrete advice on "
            "shot composition, camera movement, lighting, editing rhythm, and "
            "storytelling. Suggest specific shots or scene ideas."
        ),
        "hint": "Think like a director: plan the shots, framing, and mood of a film scene.",
        "placeholder": "e.g., How can I express sadness in movement?",
    },
    "💃 Dance Instructor": {
        "system": (
            "You are a professional dance instructor and choreographer. Answer with "
            "practical guidance on movement, rhythm, body expression, and "
            "choreography. Describe movements step by step."
        ),
        "hint": "Think like a choreographer: express emotion through the body.",
        "placeholder": "e.g., How can I express sadness in movement?",
    },
    "👗 Fashion Stylist": {
        "system": (
            "You are a creative fashion stylist. Answer with ideas about outfits, "
            "color palettes, textures, silhouettes, and styling that fit the "
            "mood or concept described."
        ),
        "hint": "Think like a stylist: let clothing and color tell the story.",
        "placeholder": "e.g., What outfit conveys quiet confidence?",
    },
    "🎭 Acting Coach": {
        "system": (
            "You are an acting coach. Answer with practical techniques for emotion, "
            "voice, gesture, character building, and scene work. Offer short "
            "exercises the actor can try."
        ),
        "hint": "Think like a coach: build a believable character and emotion.",
        "placeholder": "e.g., How do I play a character hiding grief?",
    },
    "🎨 Art Curator": {
        "system": (
            "You are an art curator. Answer with insights on themes, visual "
            "language, art history, and exhibition concepts. Connect ideas to "
            "relevant artists or movements."
        ),
        "hint": "Think like a curator: connect ideas to art and context.",
        "placeholder": "e.g., How would you curate an exhibition about memory?",
    },
}

with st.sidebar:
    st.subheader("🔑 API & Role Settings")
    api_key = st.text_input("Enter your Gemini API Key:", type="password", placeholder="Paste Gemini API key")
    role_name = st.selectbox("Choose a role:", list(ROLES.keys()))
    st.info(ROLES[role_name]["hint"])
    model = "gemini-2.5-flash"
    st.caption("Model: Gemini 2.5 Flash (free tier where available)")

st.title("🎭 Role-based Creative Chatbot")
st.write("Select a creative role and ask your question!")

question = st.text_area(
    "💬 Enter your question or idea:",
    placeholder=ROLES[role_name]["placeholder"],
)

if st.button("Generate Response"):
    if not api_key:
        st.warning("Please enter your Gemini API key in the sidebar.")
    elif not question.strip():
        st.warning("Please enter a question or idea.")
    else:
        try:
            with st.spinner("Thinking..."):
                response = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                    headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
                    json={
                        "system_instruction": {"parts": [{"text": ROLES[role_name]["system"]}]},
                        "contents": [{"role": "user", "parts": [{"text": question.strip()}]}],
                        "generationConfig": {"temperature": 0.8},
                    },
                    timeout=60,
                )
                if not response.ok:
                    try:
                        error_message = response.json().get("error", {}).get("message", "Request failed")
                    except ValueError:
                        error_message = f"HTTP {response.status_code}"
                    raise RuntimeError(f"Gemini API error ({response.status_code}): {error_message}")
                data = response.json()
                answer = "\n".join(
                    part.get("text", "")
                    for candidate in data.get("candidates", [])
                    for part in candidate.get("content", {}).get("parts", [])
                ).strip()
                if not answer:
                    answer = "No text was returned. Try another question."
            st.markdown(f"### {role_name}")
            st.write(answer)
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()
st.caption("Built for 'Art & Advanced Big Data' • Prof. Jahwan Koo (SKKU)")
