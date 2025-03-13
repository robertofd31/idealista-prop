import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("Visualización y Filtro de Casas")

# Subir el archivo CSV
uploaded_file = st.file_uploader("Sube el archivo CSV con los datos de las casas", type=["csv"])

if uploaded_file is not None:
    # Leer el archivo CSV
    df = pd.read_csv(uploaded_file)

    # Mostrar el DataFrame completo
    st.subheader("Datos completos")
    st.dataframe(df)

    # Filtros interactivos
    st.sidebar.header("Filtros")

    # Filtro por rango de precio
    min_price, max_price = st.sidebar.slider(
        "Rango de precio",
        min_value=int(df["price"].min()),
        max_value=int(df["price"].max()),
        value=(int(df["price"].min()), int(df["price"].max()))
    )

    # Filtro por municipio
    municipalities = st.sidebar.multiselect(
        "Selecciona el municipio",
        options=df["municipality"].unique(),
        default=df["municipality"].unique()
    )

    # Filtro por descripción (palabras clave)
    keyword = st.sidebar.text_input("Buscar en descripción", "")

    # Aplicar los filtros
    filtered_df = df[
        (df["price"] >= min_price) &
        (df["price"] <= max_price) &
        (df["municipality"].isin(municipalities)) &
        (df["description"].str.contains(keyword, case=False, na=False))
    ]

    # Mostrar los resultados filtrados
    st.subheader("Resultados filtrados")
    st.dataframe(filtered_df)

    # Descargar los resultados filtrados
    st.download_button(
        label="Descargar resultados filtrados",
        data=filtered_df.to_csv(index=False),
        file_name="filtered_houses.csv",
        mime="text/csv"
    )
else:
    st.write("Por favor, sube un archivo CSV para comenzar.")
