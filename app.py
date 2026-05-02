import streamlit as st

st.set_page_config(page_title="Calculadora de Precios", layout="wide")

st.title("💰 Calculadora de Precios para Negocio")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.header("Ingrese los datos")
    
    costo_producto = st.number_input(
        "Costo del producto ($)",
        min_value=0.0,
        step=0.01,
        format="%.2f"
    )
    
    margen_ganancia = st.slider(
        "Margen de ganancia (%)",
        min_value=0,
        max_value=500,
        value=30,
        step=5
    )
    
    impuesto = st.number_input(
        "Impuesto aplicable (%)",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=0.1,
        format="%.2f"
    )
    
    cantidad = st.number_input(
        "Cantidad de unidades",
        min_value=1,
        step=1,
        value=1
    )

with col2:
    st.header("Resultados")
    
    if costo_producto > 0:
        ganancia_unitaria = costo_producto * (margen_ganancia / 100)
        precio_base = costo_producto + ganancia_unitaria
        impuesto_unitario = precio_base * (impuesto / 100)
        precio_final = precio_base + impuesto_unitario
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.metric("Costo unitario", f"${costo_producto:.2f}")
            st.metric("Ganancia unitaria", f"${ganancia_unitaria:.2f}")
            st.metric("Precio base", f"${precio_base:.2f}")
        
        with col_b:
            st.metric("Impuesto unitario", f"${impuesto_unitario:.2f}")
            st.metric("Precio final unitario", f"${precio_final:.2f}")
            st.metric("Total por cantidad", f"${precio_final * cantidad:.2f}")
        
        st.markdown("---")
        st.subheader("Resumen de ventas")
        
        col_x, col_y, col_z = st.columns(3)
        
        with col_x:
            st.info(f"**Costo total:** ${costo_producto * cantidad:.2f}")
        
        with col_y:
            st.success(f"**Ganancia total:** ${ganancia_unitaria * cantidad:.2f}")
        
        with col_z:
            st.warning(f"**Ingreso total:** ${precio_final * cantidad:.2f}")
    else:
        st.warning("Ingresa un costo mayor a $0 para ver los resultados")

st.markdown("---")
st.caption("Calculadora de precios - Optimiza tus márgenes de ganancia 📊")
