import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("Explorador de Propiedades - Estilo Idealista")

# Cargar el archivo CSV desde el mismo directorio
csv_file = "prov_mad_13032024.csv"  # Asegúrate de que el archivo esté en el mismo directorio
try:
    df = pd.read_csv(csv_file)
except FileNotFoundError:
    st.error(f"No se encontró el archivo {csv_file}. Asegúrate de que esté en el mismo directorio.")
    st.stop()

# Mostrar filtros en la barra lateral
st.sidebar.header("Filtros")

# Filtro por rango de precio
min_price, max_price = st.sidebar.slider(
    "Rango de precio (€)",
    min_value=int(df["price"].min()),
    max_value=int(df["price"].max()),
    value=(int(df["price"].min()), int(df["price"].max()))
)

# Filtro por número de habitaciones
min_rooms, max_rooms = st.sidebar.slider(
    "Número de habitaciones",
    min_value=int(df["rooms"].min()),
    max_value=int(df["rooms"].max()),
    value=(int(df["rooms"].min()), int(df["rooms"].max()))
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
    (df["rooms"] >= min_rooms) &
    (df["rooms"] <= max_rooms) &
    (df["municipality"].isin(municipalities)) &
    (df["description"].str.contains(keyword, case=False, na=False))
]

# Mostrar los resultados filtrados
st.subheader(f"Resultados encontrados: {len(filtered_df)} propiedades")

# Mostrar las propiedades como tarjetas
for _, row in filtered_df.iterrows():
    # Crear una tarjeta para cada propiedad
    st.markdown("---")
    col1, col2 = st.columns([1, 2])

    # Columna 1: Imagen de la propiedad
    with col1:
        if pd.notna(row["thumbnail"]):  # Verifica si hay una imagen disponible
            st.image(row["thumbnail"], use_column_width=True)
        else:
            st.image("https://placehold.co/300x200?text=Sin+Imagen", use_column_width=True)

    # Columna 2: Detalles de la propiedad
    with col2:
        st.markdown(f"### {row['price']} €")
        st.markdown(f"**{row['rooms']} habitaciones**, **{row['bathrooms']} baños**, **{row['size']} m²**")
        st.markdown(f"📍 {row['municipality']}, {row['district'] if pd.notna(row['district']) else 'Sin distrito'}")
        st.markdown(f"**Descripción:** {row['description'][:200]}...")  # Mostrar solo los primeros 200 caracteres
        st.markdown(f"[Ver en Idealista]({row['url']})")  # Enlace a la página de Idealista

# Si no hay resultados
if len(filtered_df) == 0:
    st.warning("No se encontraron propiedades con los filtros seleccionados.")
