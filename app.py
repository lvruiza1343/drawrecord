import os
import streamlit as st
import base64
from openai import OpenAI
import openai
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# Estilos base
st.set_page_config(page_title='🎨 Tablero Inteligente', layout="centered", page_icon="🧠")

# --- Sidebar ---
with st.sidebar:
    st.markdown("## 🤖 Acerca de la App")
    st.info("Esta aplicación permite a una IA interpretar un dibujo hecho a mano. Solo dibuja en el panel y presiona **'Analizar Imagen'**.")
    st.markdown("---")
    stroke_width = st.slider('✏️ Ancho de la línea', 1, 30, 5)
    st.markdown("Puedes usar el panel principal para dibujar 👇")

# --- Encabezado con animación y estilo ---
st.markdown("""
    <h1 style='text-align: center; color: #4A90E2;'>🧠 Tablero Inteligente</h1>
    <p style='text-align: center; color: #555;'>Dibuja tu idea y deja que la IA lo interprete</p>
""", unsafe_allow_html=True)

# --- Canvas para dibujo ---
canvas_result = st_canvas(
    fill_color="rgba(255,165,0,0.3)",
    stroke_width=stroke_width,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=350,
    width=450,
    drawing_mode="freedraw",
    key="canvas",
)

# --- Entrada de clave API ---
st.markdown("### 🔐 Ingresa tu clave de OpenAI")
api_input = st.text_input('Clave API', type='password')
os.environ['OPENAI_API_KEY'] = api_input
api_key = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)

# --- Botón con estilo moderno ---
analyze_button = st.button("🧪 Analizar Imagen", use_container_width=True)

# --- Función de codificación ---
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded
    except FileNotFoundError:
        return None

# --- Lógica de análisis ---
if canvas_result.image_data is not None and api_key and analyze_button:
    with st.spinner("🔍 Analizando imagen..."):
        input_array = np.array(canvas_result.image_data)
        img = Image.fromarray(input_array.astype('uint8'), 'RGBA')
        img.save("img.png")

        base64_image = encode_image_to_base64("img.png")
        if base64_image is None:
            st.error("❌ Error al procesar la imagen.")
        else:
            prompt_text = "Describe en español brevemente la imagen"
            messages = [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                        },
                    },
                ],
            }]

            try:
                message_placeholder = st.empty()
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=500,
                )

                content = response.choices[0].message.content
                message_placeholder.markdown(f"### 📌 Resultado:\n{content}")

            except Exception as e:
                st.error(f"⚠️ Ocurrió un error al procesar la imagen: {e}")

elif analyze_button and (canvas_result.image_data is None or not api_key):
    if not api_key:
        st.warning("🔑 Debes ingresar tu clave de API antes de continuar.")
    if canvas_result.image_data is None:
        st.warning("🖼️ No has dibujado nada en el panel.")

# Pie de página
st.markdown("<hr>", unsafe_allow_html=True)
st.caption("Desarrollado con 💙 usando Streamlit, OpenAI y mucho cariño.")

