import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io

st.set_page_config(page_title="Generador de Facturas", layout="wide")

st.title("📋 Generador de Facturas")

# Información de la empresa
st.sidebar.header("Información de la Empresa")
empresa_nombre = st.sidebar.text_input("Nombre de la Empresa", "Mi Empresa")
empresa_direccion = st.sidebar.text_input("Dirección", "Calle Principal 123")
empresa_telefono = st.sidebar.text_input("Teléfono", "+34 123 456 789")
empresa_email = st.sidebar.text_input("Email", "info@miempresa.com")
empresa_rfc = st.sidebar.text_input("RFC/NIT", "ABC123456XYZ")

# Datos del cliente
st.header("Datos del Cliente")
col1, col2 = st.columns(2)

with col1:
    cliente_nombre = st.text_input("Nombre del Cliente")
    cliente_direccion = st.text_input("Dirección del Cliente")
    cliente_telefono = st.text_input("Teléfono del Cliente")

with col2:
    cliente_email = st.text_input("Email del Cliente")
    cliente_rfc = st.text_input("RFC/NIT del Cliente")
    fecha_factura = st.date_input("Fecha de Factura", datetime.now())

# Datos de la factura
st.header("Detalles de la Factura")
numero_factura = st.text_input("Número de Factura", "001")

# Tabla de productos/servicios
st.subheader("Productos/Servicios")
col1, col2, col3, col4 = st.columns(4)

productos = []
with col1:
    st.write("**Descripción**")
with col2:
    st.write("**Cantidad**")
with col3:
    st.write("**Precio Unitario**")
with col4:
    st.write("**Total**")

# Agregar filas de productos
num_filas = st.number_input("Número de líneas", min_value=1, max_value=20, value=3)

for i in range(int(num_filas)):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        descripcion = st.text_input(f"Descripción {i+1}", key=f"desc_{i}")
    with col2:
        cantidad = st.number_input(f"Cantidad {i+1}", min_value=0.0, value=1.0, key=f"cant_{i}")
    with col3:
        precio = st.number_input(f"Precio {i+1}", min_value=0.0, value=0.0, key=f"precio_{i}")
    with col4:
        total = cantidad * precio
        st.metric("Total", f"${total:.2f}")
    
    if descripcion:
        productos.append({
            "descripcion": descripcion,
            "cantidad": cantidad,
            "precio": precio,
            "total": total
        })

# Cálculos
subtotal = sum([p["total"] for p in productos])
iva_porcentaje = st.number_input("IVA (%)", min_value=0.0, max_value=100.0, value=21.0) / 100
iva = subtotal * iva_porcentaje
total_factura = subtotal + iva

# Resumen
st.header("Resumen de la Factura")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Subtotal", f"${subtotal:.2f}")
with col2:
    st.metric("IVA", f"${iva:.2f}")
with col3:
    st.metric("Total", f"${total_factura:.2f}")

# Notas
notas = st.text_area("Notas adicionales", "Gracias por su compra")

# Generar PDF
if st.button("📥 Descargar Factura en PDF"):
    if not cliente_nombre or not productos:
        st.error("Por favor completa el nombre del cliente y agrega al menos un producto")
    else:
        # Crear PDF
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Encabezado
        titulo = Paragraph(f"<b>FACTURA</b>", styles['Title'])
        elements.append(titulo)
        elements.append(Spacer(1, 0.2*inch))
        
        # Información empresa y cliente
        info_empresa = f"<b>{empresa_nombre}</b><br/>RFC: {empresa_rfc}<br/>{empresa_direccion}<br/>Tel: {empresa_telefono}<br/>Email: {empresa_email}"
        elements.append(Paragraph(info_empresa, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        info_cliente = f"<b>Cliente:</b> {cliente_nombre}<br/>RFC: {cliente_rfc}<br/>Dirección: {cliente_direccion}<br/>Teléfono: {cliente_telefono}<br/>Email: {cliente_email}"
        elements.append(Paragraph(info_cliente, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Datos de factura
        datos_factura = f"<b>Factura Nº:</b> {numero_factura} | <b>Fecha:</b> {fecha_factura.strftime('%d/%m/%Y')}"
        elements.append(Paragraph(datos_factura, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Tabla de productos
        tabla_data = [["Descripción", "Cantidad", "Precio Unitario", "Total"]]
        for p in productos:
            tabla_data.append([
                p["descripcion"],
                str(p["cantidad"]),
                f"${p['precio']:.2f}",
                f"${p['total']:.2f}"
            ])
        
        tabla_data.append(["", "", "SUBTOTAL:", f"${subtotal:.2f}"])
        tabla_data.append(["", "", f"IVA ({iva_porcentaje*100:.1f}%):", f"${iva:.2f}"])
        tabla_data.append(["", "", "TOTAL:", f"${total_factura:.2f}"])
        
        tabla = Table(tabla_data)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#cccccc'),
            ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -3), (-1, -1), '#f0f0f0'),
            ('GRID', (0, 0), (-1, -1), 1, '#000000'),
        ]))
        elements.append(tabla)
        elements.append(Spacer(1, 0.3*inch))
        
        # Notas
        elements.append(Paragraph(f"<b>Notas:</b> {notas}", styles['Normal']))
        
        # Crear PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        
        st.download_button(
            label="Descargar PDF",
            data=pdf_buffer,
            file_name=f"Factura_{numero_factura}.pdf",
            mime="application/pdf"
        )
        st.success("✅ Factura generada correctamente")
