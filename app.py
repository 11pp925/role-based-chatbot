import time
import requests
import streamlit as st

st.set_page_config(page_title="Role-based Creative Chatbot", page_icon="🎭", layout="wide")

ROLES = {
    "🎥 Video Director": {"system": "You are an experienced video director. Answer with concrete advice on shot composition, camera movement, lighting, editing rhythm, and storytelling. Suggest specific shots or scene ideas.", "hint": "Think like a director: plan the shots, framing, and mood of a film scene.", "placeholder": "e.g., How can I express loneliness through lighting?"},
    "💃 Dance Instructor": {"system": "You are a professional dance instructor and choreographer. Answer with practical guidance on movement, rhythm, body expression, and choreography. Describe movements step by step.", "hint": "Think like a choreographer: express emotion through the body.", "placeholder": "e.g., How can I express sadness in movement?"},
    "👗 Fashion Stylist": {"system": "You are a creative fashion stylist. Answer with ideas about outfits, color palettes, textures, silhouettes, and styling that fit the mood or concept described.", "hint": "Think like a stylist: let clothing and color tell the story.", "placeholder": "e.g., What outfit conveys quiet confidence?"},
    "🎭 Acting Coach": {"system": "You are an acting coach. Answer with practical techniques for emotion, voice, gesture, character building, and scene work. Offer short exercises the actor can try.", "hint": "Think like a coach: build a believable character and emotion.", "placeholder": "e.g., How do I play a character hiding grief?"},
    "🎨 Art Curator": {"system": "You are an art curator. Answer with insights on themes, visual language, art history, and exhibition concepts. Connect ideas to relevant artists or movements.", "hint": "Think like a curator: connect ideas to art and context.", "placeholder": "e.g., How would you curate an exhibition about memory?"},
}

API_ROOT = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "gemini-2.5-flash-lite"


def get_available_models(api_key):
    response = requests.get(f"{API_ROOT}/models", headers={"x-goog-api-key": api_key}, timeout=(10, 20))
    response.raise_for_status()
    return [m["name"].removeprefix("models/") for m in response.json().get("models", []) if "generateContent" in m.get("supportedGenerationMethods", [])]


def generate_answer(api_key, model, system_prompt, question):
    url = f"{API_ROOT}/models/{model}:generateContent"
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": question}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 700},
    }
    for attempt in range(3):
        try:
            response = requests.post(url, headers={"x-goog-api-key": api_key, "Content-Type": "application/json"}, json=payload, timeout=(10, 35))
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
            if attempt < 2:
                time.sleep(2 ** attempt * 2)
                continue
            raise RuntimeError("Connection timed out or failed after 3 attempts. Please try again later or choose another model.") from exc
        if response.status_code in (429, 500, 502, 503, 504) and attempt < 2:
            time.sleep(2 ** attempt * 2)
            continue
        if not response.ok:
            try:
                detail = response.json().get("error", {}).get("message", response.text[:300])
            except ValueError:
                detail = response.text[:300]
            raise RuntimeError(f"Gemini API error ({response.status_code}): {detail}")
        data = response.json()
        answer = "\n".join(part.get("text", "") for candidate in data.get("candidates", []) for part in candidate.get("content", {}).get("parts", []) if isinstance(part, dict)).strip()
        if not answer:
            raise RuntimeError("The model returned no text. Please try a different question or model.")
        return answer
    raise RuntimeError("Unable to get a response after 3 attempts.")

with st.sidebar:
    st.subheader("🔑 API & Role Settings")
    api_key = st.text_input("Enter your Gemini API Key:", type="password", placeholder="Paste Gemini API key")
    role_name = st.selectbox("Choose a role:", list(ROLES.keys()))
    st.info(ROLES[role_name]["hint"])
    st.caption("Default model: Gemini 2.5 Flash-Lite (availability depends on your account)")
    model = st.text_input("Model name", value=DEFAULT_MODEL, help="Use a model listed by your Gemini API account. You can check supported models below.").strip()
    if st.button("Check available models"):
        if not api_key:
            st.warning("Enter your API key first.")
        else:
            try:
                names = get_available_models(api_key)
                if names:
                    st.success("Models supporting generateContent:")
                    st.code("\n".join(names[:40]))
                else:
                    st.warning("No compatible models returned.")
            except requests.exceptions.RequestException as exc:
                st.error(f"Could not list models: {exc}")

st.title("🎭 Role-based Creative Chatbot")
st.write("Select a creative role and ask your question!")
question = st.text_area("💬 Enter your question or idea:", placeholder=ROLES[role_name]["placeholder"])

if st.button("Generate Response"):
    if not api_key:
        st.warning("Please enter your Gemini API key in the sidebar.")
    elif not question.strip():
        st.warning("Please enter a question or idea.")
    elif not model:
        st.warning("Please enter a model name.")
    else:
        try:
            with st.spinner("Thinking... (up to 3 attempts)"):
                answer = generate_answer(api_key, model, ROLES[role_name]["system"], question.strip())
            st.markdown(f"### {role_name}")
            st.write(answer)
        except Exception as exc:
            st.error(str(exc))
            st.info("If you see 404, click 'Check available models' and use a supported model name. If you see 503 or timeout, try another available model or wait and retry later.")

st.divider()
st.caption("Built for 'Art & Advanced Big Data' • Prof. Jahwan Koo (SKKU)")
