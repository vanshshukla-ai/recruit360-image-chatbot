
import os, json
import streamlit as st

PROJECT="direct-tribute-502305-q5"; LOCATION="global"
MODEL="gemini-2.5-flash-image"

st.set_page_config(page_title="Recruit360 Image Chatbot", page_icon="🎨", layout="centered")

def _creds():
    try:
        if "gcp_service_account" in st.secrets:
            with open("/tmp/sa.json","w") as f: json.dump(dict(st.secrets["gcp_service_account"]),f)
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/tmp/sa.json"
    except Exception: pass
_creds()

@st.cache_resource(show_spinner=False)
def get_client():
    from google import genai
    return genai.Client(vertexai=True, project=PROJECT, location=LOCATION)

def generate_image(prompt):
    from google.genai import types
    client=get_client()
    resp=client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["IMAGE","TEXT"]))
    for part in resp.candidates[0].content.parts:
        if getattr(part,"inline_data",None) and part.inline_data.data:
            return part.inline_data.data
    return None

st.markdown("""<style>
.stApp{background:linear-gradient(180deg,#0e1117,#141b2e);}
.hero{padding:16px 22px;border-radius:14px;margin-bottom:10px;color:#fff;
 background:linear-gradient(100deg,#0b1b4d,#c0398a 55%,#f59e0b);}
.hero h1{margin:0;font-size:23px;font-weight:800;} .hero p{margin:3px 0 0;opacity:.92;font-size:13px;}
</style>""",unsafe_allow_html=True)
st.markdown("""<div class="hero"><h1>🎨 Recruit360 Image Chatbot</h1>
<p>Describe a product — Gemini generates the image, on Google Cloud (Vertex AI).</p></div>""",
unsafe_allow_html=True)

with st.sidebar:
    st.subheader("💡 Try these")
    for ex in ["A sleek modern water bottle, studio lighting, white background",
               "A pair of premium wireless earbuds, product photo",
               "A minimalist leather laptop bag on a desk",
               "A colorful eco-friendly reusable coffee cup"]:
        if st.button(ex, use_container_width=True): st.session_state.pending=ex
    st.markdown("---"); st.caption("Powered by Gemini image generation · Recruit360")

if "history" not in st.session_state: st.session_state.history=[]
for item in st.session_state.history:
    with st.chat_message("user"): st.markdown(item["prompt"])
    with st.chat_message("assistant"):
        if item.get("img"): st.image(item["img"], caption=item["prompt"], use_container_width=True)
        else: st.error(item.get("error","(no image)"))

prompt = st.chat_input("Describe the product to generate…")
if st.session_state.get("pending"): prompt=st.session_state.pending; st.session_state.pending=None

if prompt:
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Generating image with Gemini…"):
            try:
                img=generate_image(prompt)
                if img:
                    st.image(img, caption=prompt, use_container_width=True)
                    st.session_state.history.append({"prompt":prompt,"img":img})
                    st.download_button("⬇️ Download image", img, file_name="product.png", mime="image/png")
                else:
                    st.error("No image returned."); st.session_state.history.append({"prompt":prompt,"error":"No image returned"})
            except Exception as e:
                st.error(f"Image generation failed: {e}")
                st.session_state.history.append({"prompt":prompt,"error":str(e)})
