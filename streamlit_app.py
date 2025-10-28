import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gestión de Productos", page_icon="📦", layout="wide")

@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

st.title("📦 Gestión de Productos")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("➕ Agregar Producto")
    
    with st.form("form_producto", clear_on_submit=True):
        nombre = st.text_input("Nombre del producto")
        precio = st.number_input("Precio", min_value=0.0, step=0.01, format="%.2f")
        
        submit = st.form_submit_button("Guardar Producto", use_container_width=True)
        
        if submit:
            if nombre.strip():
                try:
                    data = {
                        "nombre": nombre,
                        "precio": precio,
                        "created_at": datetime.now().isoformat()
                    }
                    
                    response = supabase.table("Productos").insert(data).execute()
                    st.success(f"✅ Producto '{nombre}' agregado!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Ingresa un nombre válido")

with col2:
    st.subheader("📋 Lista de Productos")
    
    try:
        response = supabase.table("Productos").select("*").order("created_at", desc=True).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Total Productos", len(df))
            with col_m2:
                st.metric("Precio Promedio", f"${df['precio'].mean():.2f}")
            with col_m3:
                st.metric("Precio Total", f"${df['precio'].sum():.2f}")
            
            st.divider()
            
            display_df = df[["id", "nombre", "precio", "created_at"]].copy()
            display_df["precio"] = display_df["precio"].apply(lambda x: f"${x:.2f}")
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": "ID",
                    "nombre": "Nombre",
                    "precio": "Precio",
                    "created_at": st.column_config.DatetimeColumn(
                        "Fecha de Creación",
                        format="DD/MM/YYYY HH:mm"
                    )
                }
            )
            
            st.divider()
            with st.expander("🗑️ Eliminar Producto"):
                producto_a_eliminar = st.selectbox(
                    "Selecciona un producto",
                    options=df["id"].tolist(),
                    format_func=lambda x: f"{df[df['id']==x]['nombre'].values[0]} - ${df[df['id']==x]['precio'].values[0]:.2f}"
                )
                
                if st.button("Eliminar", type="secondary"):
                    try:
                        supabase.table("Productos").delete().eq("id", producto_a_eliminar).execute()
                        st.success("✅ Producto eliminado")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        else:
            st.info("🔍 No hay productos. ¡Agrega el primero!")
            
    except Exception as e:
        st.error(f"❌ Error al cargar: {str(e)}")
```

**requirements.txt:**
```
streamlit
supabase
pandas
