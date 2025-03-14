import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import numpy as np

# Función para aplanar diccionarios
def flatten_dict(d, parent_key='', sep='_'):
    """
    Función auxiliar para aplanar un diccionario de forma recursiva.
    """
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items

# Cargar el archivo CSV desde el mismo directorio
csv_file = "prov_mad_13032024.csv"
try:
    df_properties = pd.read_csv(csv_file)
except FileNotFoundError:
    st.error(f"No se encontró el archivo {csv_file}. Asegúrate de que esté en el mismo directorio.")
    st.stop()

# Procesar la columna 'priceInfo' para aplanar el diccionario anidado
if "priceInfo" in df_properties.columns:
    flattened_price = df_properties["priceInfo"].apply(lambda x: flatten_dict(eval(x)) if isinstance(x, str) else {})
    price_df = pd.DataFrame(flattened_price.tolist())
    df_properties = pd.concat([df_properties.drop(columns=["priceInfo"]), price_df], axis=1)

# Título de la aplicación
st.title("Explorador de Propiedades - Estilo Idealista")

# Mostrar filtros en la barra lateral
st.sidebar.header("Filtros")

# Filtro por rango de precio
min_price, max_price = st.sidebar.slider(
    "Rango de precio (€)",
    min_value=int(df_properties["price"].min()),
    max_value=int(df_properties["price"].max()),
    value=(int(df_properties["price"].min()), int(df_properties["price"].max()))
)

# Filtro por número de habitaciones
min_rooms, max_rooms = st.sidebar.slider(
    "Número de habitaciones",
    min_value=int(df_properties["rooms"].min()),
    max_value=int(df_properties["rooms"].max()),
    value=(int(df_properties["rooms"].min()), int(df_properties["rooms"].max()))
)

# Filtro por tamaño mínimo
min_size = st.sidebar.number_input(
    "Tamaño mínimo (m²)",
    min_value=int(df_properties["size"].min()),
    max_value=int(df_properties["size"].max()),
    value=int(df_properties["size"].min())
)

# Filtro por número mínimo de baños
min_bathrooms = st.sidebar.number_input(
    "Baños mínimos",
    min_value=int(df_properties["bathrooms"].min()),
    max_value=int(df_properties["bathrooms"].max()),
    value=int(df_properties["bathrooms"].min())
)

# Filtro por municipio (multiselección)
municipalities = list(df_properties["municipality"].unique())
selected_municipalities = st.sidebar.multiselect(
    "Selecciona municipios",
    options=municipalities,
    default=[]
)

# Filtro por distrito (desplegable)
district = st.sidebar.selectbox(
    "Selecciona el distrito",
    options=["Todos"] + list(df_properties["district"].dropna().unique())
)

# Filtro por texto a excluir en la descripción
exclude_text = st.sidebar.text_input("Excluir si contiene en descripción", "")

# Filtro por descripción (palabras clave a incluir)
include_keyword = st.sidebar.text_input("Buscar en descripción", "")

# Aplicar los filtros básicos
filtered_df = df_properties[
    (df_properties["price"] >= min_price) &
    (df_properties["price"] <= max_price) &
    (df_properties["rooms"] >= min_rooms) &
    (df_properties["rooms"] <= max_rooms) &
    (df_properties["size"] >= min_size) &
    (df_properties["bathrooms"] >= min_bathrooms)
]

# Filtrar por municipios seleccionados
if selected_municipalities:
    filtered_df = filtered_df[filtered_df["municipality"].isin(selected_municipalities)]

# Filtrar por distrito si no es "Todos"
if district != "Todos":
    filtered_df = filtered_df[filtered_df["district"] == district]

# Filtrar por texto a incluir en la descripción
if include_keyword:
    filtered_df = filtered_df[filtered_df["description"].str.contains(include_keyword, case=False, na=False)]

# Filtrar por texto a excluir en la descripción
if exclude_text:
    exclude_terms = exclude_text.split('|')
    for term in exclude_terms:
        filtered_df = filtered_df[~filtered_df["description"].str.contains(term.strip(), case=False, na=False)]

# Añadir filtro predefinido para excluir propiedades problemáticas
exclude_default = "subasta| puja|local sin cambio de uso|cambio de uso|posisio|nuda propiedad|no se puede hipotecar|ocupado|ocupada|pujas|ocupacional|ilegal|okupada|okupado|sin posesi|procedimiento judicial|alquilado"
filtered_df = filtered_df[~filtered_df["description"].str.contains(exclude_default, case=False, na=False)]

# Mostrar los resultados filtrados
st.subheader(f"Resultados encontrados: {len(filtered_df)} propiedades")

# Crear mapa si hay coordenadas disponibles
if "latitude" in filtered_df.columns and "longitude" in filtered_df.columns:
    st.subheader("Mapa de propiedades")

    # Crear un mapa centrado en Madrid
    m = folium.Map(location=[40.4168, -3.7038], zoom_start=10)

    # Añadir marcadores para cada propiedad
    for _, row in filtered_df.iterrows():
        if pd.notna(row["latitude"]) and pd.notna(row["longitude"]):
            popup_text = f"""
            <b>Precio:</b> {row['price']}€<br>
            <b>Habitaciones:</b> {row['rooms']}<br>
            <b>Tamaño:</b> {row['size']}m²<br>
            <a href="{row['url']}" target="_blank">Ver en Idealista</a>
            """
            folium.Marker(
                [row["latitude"], row["longitude"]],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"{row['price']}€ - {row['rooms']} hab.",
                icon=folium.Icon(color="red", icon="home")
            ).add_to(m)

    # Mostrar el mapa
    folium_static(m)

# Mostrar estadísticas básicas
if len(filtered_df) > 0:
    st.subheader("Estadísticas de las propiedades filtradas")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Precio medio", f"{int(filtered_df['price'].mean())}€")
    with col2:
        st.metric("Tamaño medio", f"{int(filtered_df['size'].mean())}m²")
    with col3:
        avg_price_sqm = int(filtered_df['price'].sum() / filtered_df['size'].sum())
        st.metric("Precio medio por m²", f"{avg_price_sqm}€/m²")

# Mostrar las propiedades como tarjetas
for _, row in filtered_df.iterrows():
    st.markdown("---")
    col1, col2 = st.columns([1, 2])

    # Columna 1: Imagen de la propiedad
    with col1:
        if pd.notna(row.get("thumbnail")):  # Verifica si hay una imagen disponible
            st.image(row["thumbnail"], use_container_width=True)
        else:
            st.image("https://placehold.co/300x200?text=Sin+Imagen", use_container_width=True)

    # Columna 2: Detalles de la propiedad
    with col2:
        st.markdown(f"### {row['price']} €")
        st.markdown(f"**{row['rooms']} habitaciones**, **{row['bathrooms']} baños**, **{row['size']} m²**")
        st.markdown(f"📍 {row['municipality']}, {row['district'] if pd.notna(row['district']) else 'Sin distrito'}")

        # Calcular precio por metro cuadrado
        price_per_sqm = round(row['price'] / row['size'], 2) if row['size'] > 0 else "N/A"
        st.markdown(f"**Precio/m²:** {price_per_sqm} €/m²")

       
        # Por esta versión más segura:
        if pd.notna(row.get('description')) and isinstance(row['description'], str):
            desc_text = row['description'][:200] + "..."
        else:
            desc_text = "Sin descripción disponible"
        st.markdown(f"**Descripción:** {desc_text}")
        # Mostrar solo los primeros 200 caracteres
        st.markdown(f"[Ver en Idealista]({row['url']})")  # Enlace a la página de Idealista

# Si no hay resultados
if len(filtered_df) == 0:
    st.warning("No se encontraron propiedades con los filtros seleccionados.")
