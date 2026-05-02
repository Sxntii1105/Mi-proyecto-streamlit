import streamlit as st
import random
import time

st.set_page_config(page_title="Tarjeta Interactiva", layout="wide")

st.title("🎉 Tarjeta Interactiva de Celebración")

col1, col2 = st.columns([1, 1])

with col1:
    titulo = st.text_input("Título de la tarjeta", "¡Feliz Cumpleaños!")
    motivo = st.text_area("Motivo o mensaje", "Que disfrutes este día especial")

with col2:
    st.info("Presiona el botón para activar la celebración")

if st.button("🎈 ¡CELEBRA! 🎊", key="celebrate", use_container_width=True):
    st.balloons()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;'>
            <h1 style='font-size: 48px; margin: 0;'>{titulo}</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 15px; color: white;'>
            <h3 style='margin: 0;'>{motivo}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 15px; color: white;'>
            <h2 style='margin: 0;'>🎂 🎁 🎉</h2>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<style>
.emoji-rain {
    font-size: 40px;
    animation: fall 3s infinite;
}
@keyframes fall {
    to {
        transform: translateY(100vh) rotate(360deg);
        opacity: 0;
    }
}
</style>
""", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)
emojis = ["🎈", "🎊", "🎉", "🎁", "🌟", "💫", "✨"]

with col1:
    if st.button("🎈 Globos", use_container_width=True):
        st.snow()

with col2:
    if st.button("⭐ Estrellas", use_container_width=True):
        st.balloons()

with col3:
    if st.button("🎊 Confeti", use_container_width=True):
        st.balloons()

with col4:
    if st.button("✨ Magia", use_container_width=True):
        st.snow()

with col5:
    if st.button("🌟 Todo", use_container_width=True):
        st.balloons()
        st.snow()

st.markdown("""
<div style='text-align: center; margin-top: 40px;'>
    <h2>🎂 Que lo disfrutes 🎂</h2>
</div>
""", unsafe_allow_html=True)

