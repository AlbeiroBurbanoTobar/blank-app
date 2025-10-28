import time
from datetime import datetime

import pandas as pd
import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Productos", layout="wide")


@st.cache_resource
def init_supabase():
    SUPABASE_URL = "https://jhlvvdidpftgtuwjikuy.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpobHZ2ZGlkcGZ0Z3R1d2ppa3V5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjA2ODczMTksImV4cCI6MjA3NjI2MzMxOX0.6BuSkxCU4MpfGYhCsUI8ArztYWrDziV-ewGJv1L2kFE"
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("Configura SUPABASE_URL y SUPABASE_ANON_KEY.")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

st.title("PRUEBA")

col1, col2 = st.columns([1, 2])


def generar_id_bigint():
   
    return int(time.time() * 1000)


with col1:
    st.subheader("+ Agregar Producto")
    with st.form("form_producto", clear_on_submit=True):
        nombre = st.text_input("Nombre del producto")
        precio = st.number_input("Precio", min_value=0.0, step=0.01, format="%.2f")

        submit = st.form_submit_button("Guardar Producto", use_container_width=True)

        if submit:
            if not nombre or not nombre.strip():
                st.warning(" Ingresa un nombre válido")
            else:
                try:
                    data = {
                        "id": generar_id_bigint(),      
                        "nombre": nombre.strip(),
                        "precio": float(precio),
                    }
                    supabase.table("productos").insert(data).execute()
                    st.success(f" Producto '{nombre}' agregado")
                    st.rerun()
                except Exception as e:
                    st.error(f" Error al insertar: {str(e)}")


with col2:
    st.subheader("Lista de Productos")

    try:
        response = (
            supabase.table("productos")
            .select("*")
            .order("id", desc=True)  
            .execute()
        )

        rows = response.data or []

        if len(rows) == 0:
            st.info("🔍 No hay productos. ¡Agrega el primero!")
        else:
            df = pd.DataFrame(rows)


            if "precio" in df.columns:
                df["precio"] = pd.to_numeric(df["precio"], errors="coerce").fillna(0.0)


            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Total Productos", int(len(df)))

            with m2:
                avg_price = df["precio"].mean() if "precio" in df else 0.0
                st.metric("Precio Promedio", f"${avg_price:.2f}")

            with m3:
                total_price = df["precio"].sum() if "precio" in df else 0.0
                st.metric("Precio Total", f"${total_price:.2f}")

            st.divider()

            # Tabla
            mostrar_cols = [c for c in ["id", "nombre", "precio"] if c in df.columns]
            display_df = df[mostrar_cols].copy()
            if "precio" in display_df:
                display_df["precio"] = display_df["precio"].apply(lambda x: f"${x:.2f}")

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": "ID",
                    "nombre": "Nombre",
                    "precio": "Precio",
                },
            )

            st.divider()

        
            with st.expander(" Eliminar Producto"):
                if "id" not in df.columns:
                    st.error("La tabla no tiene columna 'id'.")
                else:
                    opciones = df["id"].tolist()

                    def _fmt(x):
                        try:
                            fila = df[df["id"] == x].iloc[0]
                            return f"{fila.get('nombre','(sin nombre)')} - ${float(fila.get('precio',0.0)):.2f}"
                        except Exception:
                            return str(x)

                    producto_a_eliminar = st.selectbox(
                        "Selecciona un producto",
                        options=opciones,
                        format_func=_fmt,
                    )

                    if st.button("Eliminar", type="secondary", use_container_width=True):
                        try:
                            supabase.table("productos").delete().eq("id", producto_a_eliminar).execute()
                            st.success(" Producto eliminado")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error al eliminar: {str(e)}")

    except Exception as e:
        st.error(f"❌ Error al cargar datos: {str(e)}")
