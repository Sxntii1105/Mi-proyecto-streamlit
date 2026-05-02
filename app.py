import streamlit as st
import pandas as pd
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import os

st.set_page_config(page_title="Sistema de Facturación", layout="wide", initial_sidebar_state="expanded")

# Inicializar sesión
if 'products_db' not in st.session_state:
    st.session_state.products_db = pd.DataFrame(columns=['Código', 'Nombre', 'Precio', 'Stock'])
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'invoice_number' not in st.session_state:
    st.session_state.invoice_number = 1001

# Título principal
st.title("💼 Sistema de Facturación y Precios")
st.markdown("---")

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs(["📦 Base de Datos", "🛒 Facturación", "📊 Reportes", "⚙️ Configuración"])

# TAB 1: Base de Datos de Productos
with tab1:
    st.header("Gestión de Base de Datos de Productos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Subir archivo CSV")
        uploaded_file = st.file_uploader("Carga un CSV con columnas: Código, Nombre, Precio, Stock", 
                                         type=['csv', 'xlsx'], key="upload_db")
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df_upload = pd.read_csv(uploaded_file)
                else:
                    df_upload = pd.read_excel(uploaded_file)
                
                # Validar columnas
                required_cols = ['Código', 'Nombre', 'Precio', 'Stock']
                if all(col in df_upload.columns for col in required_cols):
                    st.session_state.products_db = df_upload[required_cols].copy()
                    st.success(f"✅ {len(df_upload)} productos cargados correctamente")
                else:
                    st.error(f"❌ El archivo debe contener las columnas: {', '.join(required_cols)}")
            except Exception as e:
                st.error(f"Error al cargar archivo: {e}")
    
    with col2:
        st.subheader("Agregar producto manualmente")
        with st.form("add_product_form"):
            codigo = st.text_input("Código del producto")
            nombre = st.text_input("Nombre del producto")
            precio = st.number_input("Precio", min_value=0.0, step=0.01)
            stock = st.number_input("Stock", min_value=0, step=1)
            
            if st.form_submit_button("➕ Agregar Producto"):
                if codigo and nombre:
                    new_product = pd.DataFrame({
                        'Código': [codigo],
                        'Nombre': [nombre],
                        'Precio': [precio],
                        'Stock': [stock]
                    })
                    st.session_state.products_db = pd.concat(
                        [st.session_state.products_db, new_product], 
                        ignore_index=True
                    )
                    st.success("✅ Producto agregado")
                else:
                    st.error("❌ Completa todos los campos")
    
    st.subheader("Base de Datos Actual")
    if not st.session_state.products_db.empty:
        st.dataframe(st.session_state.products_db, use_container_width=True, hide_index=True)
        
        # Opciones de edición
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Limpiar base de datos"):
                st.session_state.products_db = pd.DataFrame(columns=['Código', 'Nombre', 'Precio', 'Stock'])
                st.rerun()
        
        with col2:
            csv = st.session_state.products_db.to_csv(index=False)
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name="productos.csv",
                mime="text/csv"
            )
    else:
        st.info("📭 No hay productos en la base de datos. Carga un archivo o agrega productos manualmente.")

# TAB 2: Facturación
with tab2:
    st.header("Crear Factura")
    
    if st.session_state.products_db.empty:
        st.warning("⚠️ Primero debe cargar productos en la Base de Datos")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Información del Cliente")
            client_col1, client_col2 = st.columns(2)
            with client_col1:
                cliente_nombre = st.text_input("Nombre del cliente", key="client_name")
                cliente_email = st.text_input("Email del cliente", key="client_email")
            with client_col2:
                cliente_telefono = st.text_input("Teléfono del cliente", key="client_phone")
                cliente_ruc = st.text_input("RUC/NIT del cliente", key="client_ruc")
        
        with col2:
            st.subheader("Información de Factura")
            numero_factura = st.number_input("# Factura", value=st.session_state.invoice_number, step=1)
            fecha_factura = st.date_input("Fecha")
        
        st.markdown("---")
        st.subheader("Agregar Productos al Carrito")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            codigo_producto = st.selectbox(
                "Selecciona por código o busca",
                options=st.session_state.products_db['Código'].tolist(),
                key="product_select"
            )
        with col2:
            cantidad = st.number_input("Cantidad", min_value=1, value=1, key="quantity_input")
        with col3:
            if st.button("➕ Agregar al Carrito", use_container_width=True):
                # Buscar producto
                producto = st.session_state.products_db[
                    st.session_state.products_db['Código'] == codigo_producto
                ]
                
                if not producto.empty:
                    prod_row = producto.iloc[0]
                    precio_unitario = float(prod_row['Precio'])
                    stock_disponible = int(prod_row['Stock'])
                    
                    if cantidad <= stock_disponible:
                        # Verificar si ya está en el carrito
                        item_existente = False
                        for item in st.session_state.cart:
                            if item['Código'] == codigo_producto:
                                item['Cantidad'] += cantidad
                                item_existente = True
                                break
                        
                        if not item_existente:
                            st.session_state.cart.append({
                                'Código': codigo_producto,
                                'Nombre': prod_row['Nombre'],
                                'Precio Unitario': precio_unitario,
                                'Cantidad': cantidad,
                                'Subtotal': precio_unitario * cantidad
                            })
                        st.success(f"✅ {prod_row['Nombre']} agregado al carrito")
                    else:
                        st.error(f"❌ Stock insuficiente. Disponible: {stock_disponible}")
        
        st.markdown("---")
        st.subheader("Carrito de Compras")
        
        if st.session_state.cart:
            # Mostrar carrito
            cart_data = []
            total = 0
            for item in st.session_state.cart:
                subtotal = item['Precio Unitario'] * item['Cantidad']
                cart_data.append({
                    'Código': item['Código'],
                    'Producto': item['Nombre'],
                    'P. Unitario': f"${item['Precio Unitario']:.2f}",
                    'Cantidad': item['Cantidad'],
                    'Subtotal': f"${subtotal:.2f}"
                })
                total += subtotal
            
            df_cart = pd.DataFrame(cart_data)
            st.dataframe(df_cart, use_container_width=True, hide_index=True)
            
            # Resumen de totales
            col1, col2, col3 = st.columns([2, 1, 1])
            with col3:
                st.metric("Total", f"${total:.2f}")
            
            # Opciones de carrito
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🗑️ Limpiar Carrito"):
                    st.session_state.cart = []
                    st.rerun()
            
            with col2:
                producto_eliminar = st.selectbox(
                    "Eliminar producto:",
                    options=[item['Nombre'] for item in st.session_state.cart] if st.session_state.cart else [],
                    key="remove_product"
                )
                if st.button("❌ Eliminar"):
                    st.session_state.cart = [item for item in st.session_state.cart if item['Nombre'] != producto_eliminar]
                    st.rerun()
            
            with col3:
                descuento = st.number_input("Descuento %", min_value=0.0, max_value=100.0, value=0.0)
            
            # Calcular total con descuento
            descuento_monto = (total * descuento) / 100
            total_final = total - descuento_monto
            
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 1, 1])
            with col3:
                st.metric("Descuento", f"-${descuento_monto:.2f}")
                st.metric("Total a Pagar", f"${total_final:.2f}", delta=None)
            
            # Generar factura PDF
            if st.button("📄 Generar Factura PDF", use_container_width=True, type="primary"):
                if cliente_nombre:
                    pdf_buffer = generar_factura_pdf(
                        numero_factura=numero_factura,
                        fecha=fecha_factura,
                        cliente_nombre=cliente_nombre,
                        cliente_email=cliente_email,
                        cliente_telefono=cliente_telefono,
                        cliente_ruc=cliente_ruc,
                        items=st.session_state.cart,
                        subtotal=total,
                        descuento=descuento,
                        total=total_final
                    )
                    
                    st.download_button(
                        label="📥 Descargar Factura PDF",
                        data=pdf_buffer,
                        file_name=f"Factura_{numero_factura}.pdf",
                        mime="application/pdf"
                    )
                    
                    # Actualizar número de factura
                    st.session_state.invoice_number = numero_factura + 1
                    st.success("✅ Factura generada correctamente")
                else:
                    st.error("❌ Ingresa el nombre del cliente")
        else:
            st.info("🛒 El carrito está vacío. Agrega productos.")

# TAB 3: Reportes
with tab3:
    st.header("Reportes y Análisis")
    
    if not st.session_state.products_db.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Productos en Stock")
            st.metric("Total de productos", len(st.session_state.products_db))
            st.metric("Stock total", int(st.session_state.products_db['Stock'].sum()))
        
        with col2:
            st.subheader("Análisis de Precios")
            st.metric("Precio promedio", f"${st.session_state.products_db['Precio'].mean():.2f}")
            st.metric("Precio máximo", f"${st.session_state.products_db['Precio'].max():.2f}")
        
        st.subheader("Distribución de Stock")
        st.bar_chart(
            st.session_state.products_db.set_index('Nombre')['Stock']
        )
        
        st.subheader("Rango de Precios")
        st.bar_chart(
            st.session_state.products_db.set_index('Nombre')['Precio']
        )
    else:
        st.info("📭 No hay datos para mostrar. Carga una base de productos.")

# TAB 4: Configuración
with tab4:
    st.header("Configuración del Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Información de la Empresa")
        empresa_nombre = st.text_input("Nombre de la Empresa", value="Mi Empresa")
        empresa_ruc = st.text_input("RUC/NIT de la Empresa")
        empresa_telefono = st.text_input("Teléfono")
        empresa_email = st.text_input("Email")
    
    with col2:
        st.subheader("Configuración General")
        st.session_state.invoice_number = st.number_input(
            "Próximo número de factura", 
            value=st.session_state.invoice_number, 
            min_value=1000
        )
        moneda = st.selectbox("Moneda", ["USD", "EUR", "MXN", "ARS", "COP", "PEN", "CLP"])
        mostrar_iva = st.checkbox("¿Aplicar IVA?", value=False)
        iva_porcentaje = st.number_input("Porcentaje de IVA", min_value=0.0, max_value=100.0, value=0.0) if mostrar_iva else 0.0
    
    if st.button("💾 Guardar Configuración"):
        st.success("✅ Configuración guardada")

# Función para generar PDF
def generar_factura_pdf(numero_factura, fecha, cliente_nombre, cliente_email, 
                       cliente_telefono, cliente_ruc, items, subtotal, descuento, total):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Estilo personalizado
    titulo_style = ParagraphStyle(
        'titulo',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Encabezado
    story.append(Paragraph("FACTURA", titulo_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Información de factura y cliente
    info_data = [
        ['FACTURA #:', str(numero_factura), 'FECHA:', fecha.strftime('%d/%m/%Y')],
        ['CLIENTE:', cliente_nombre, 'RUC/NIT:', cliente_ruc or 'N/A'],
        ['EMAIL:', cliente_email or 'N/A', 'TELÉFONO:', cliente_telefono or 'N/A']
    ]
    
    info_table = Table(info_data, colWidths=[1.2*inch, 2*inch, 1.2*inch, 2*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Tabla de items
    items_data = [['CÓDIGO', 'DESCRIPCIÓN', 'CANTIDAD', 'P. UNITARIO', 'SUBTOTAL']]
    
    for item in items:
        subtotal_item = item['Precio Unitario'] * item['Cantidad']
        items_data.append([
            item['Código'],
            item['Nombre'],
            str(item['Cantidad']),
            f"${item['Precio Unitario']:.2f}",
            f"${subtotal_item:.2f}"
        ])
    
    items_table = Table(items_data, colWidths=[1*inch, 2.5*inch, 1*inch, 1.2*inch, 1.3*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 1), (1, -1), 'LEFT'),
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Totales
    descuento_monto = (subtotal * descuento) / 100
    totales_data = [
        ['', '', 'SUBTOTAL:', f"${subtotal:.2f}"],
        ['', '', 'DESCUENTO ({:.0f}%):'.format(descuento), f"-${descuento_monto:.2f}"],
        ['', '', 'TOTAL:', f"${total:.2f}"]
    ]
    
    totales_table = Table(totales_data, colWidths=[1.5*inch, 2.5*inch, 1.2*inch, 1.3*inch])
    totales_table.setStyle(TableStyle([
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (2, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (2, 0), (-1, 1), 10),
        ('FONTSIZE', (2, 2), (-1, 2), 12),
        ('TEXTCOLOR', (2, 2), (-1, 2), colors.HexColor('#1f77b4')),
        ('BACKGROUND', (2, 2), (-1, 2), colors.HexColor('#e6f2ff')),
        ('GRID', (2, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
        ('TOPPADDING', (2, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (2, 0), (-1, -1), 8),
    ]))
    
    story.append(totales_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Pie de página
    footer_style = ParagraphStyle(
        'footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("Gracias por su compra • Fecha de generación: " + datetime.now().strftime('%d/%m/%Y %H:%M'), footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Pie de página global
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray; font-size: 12px;'>Sistema de Facturación v1.0 | Desarrollado con Streamlit</p>", unsafe_allow_html=True)
