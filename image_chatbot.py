"""
Recruit360 Image Chatbot — Gemini/Imagen product image generator (GCP).
Type a product description -> Vertex AI Imagen generates the image -> shown in chat.
Auth: service account in st.secrets["gcp_service_account"] (Streamlit Cloud) or ADC (Colab).
"""
import os, json, io, base64
import streamlit as st

PROJECT="direct-tribute-502305-q5"; LOCATION="us-central1"
IMAGE_MODEL="imagen-4.0-generate-001"   # Vertex AI Imagen 4

st.set_page_config(page_title="Recruit360 Image Chatbot", page_icon="🎨", layout="centered")

# ---- auth ----
def _creds():
    try:
        if "gcp_service_account" in st.secrets:
            with open("/tmp/sa.json","w") as f: json.dump(dict(st.secrets["gcp_service_account"]),f)
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/tmp/sa.json"
    except Exception: pass
_creds()

@st.cache_resource(show_spinner=False)
def get_model():
    import vertexai
    from vertexai.preview.vision_models import ImageGenerationModel
    vertexai.init(project=PROJECT, location=LOCATION)
    return ImageGenerationModel.from_pretrained(IMAGE_MODEL)

# ---- UI ----
st.markdown("""<style>
.stApp{background:linear-gradient(180deg,#0e1117,#141b2e);}
.hero{padding:16px 22px;border-radius:14px;margin-bottom:10px;color:#fff;
 background:linear-gradient(100deg,#0b1b4d,#c0398a 55%,#f59e0b);}
.hero h1{margin:0;font-size:23px;font-weight:800;} .hero p{margin:3px 0 0;opacity:.92;font-size:13px;}
</style>""",unsafe_allow_html=True)
st.markdown("""<div class="hero"><h1>🎨 Recruit360 Image Chatbot</h1>
<p>Describe a product — Gemini (Vertex AI Imagen) generates the image. On Google Cloud.</p></div>""",
unsafe_allow_html=True)

with st.sidebar:
    st.subheader("💡 Try these")
    for ex in ["A sleek modern water bottle, studio lighting, white background",
               "A pair of premium wireless earbuds, product photo",
               "A minimalist leather laptop bag on a desk",
               "A colorful eco-friendly reusable coffee cup"]:
        if st.button(ex, use_container_width=True): st.session_state.pending=ex
    st.markdown("---")
    st.caption("Powered by Vertex AI Imagen · Recruit360")

if "history" not in st.session_state: st.session_state.history=[]

# render past
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
        with st.spinner("Generating image with Vertex AI Imagen…"):
            try:
                model=get_model()
                res=model.generate_images(prompt=prompt, number_of_images=1,
                        aspect_ratio="1:1", safety_filter_level="block_some")
                img_bytes=res[0]._image_bytes
                st.image(img_bytes, caption=prompt, use_container_width=True)
                st.session_state.history.append({"prompt":prompt,"img":img_bytes})
                st.download_button("⬇️ Download image", img_bytes, file_name="product.png", mime="image/png")
            except Exception as e:
                st.error(f"Image generation failed: {e}")
                st.session_state.history.append({"prompt":prompt,"error":str(e)})
