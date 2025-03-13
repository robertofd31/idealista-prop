import streamlit as st
import pandas as pd
import requests

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
csv_file = "prov_mad_13032024.csv"  # Asegúrate de que el archivo esté en el mismo directorio
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

# Filtrar propiedades no deseadas en la descripción
df_properties = df_properties[
    ~df_properties['description'].str.contains(
        'subasta|nuda propiedad|no se puede hipotecar|ocupado|ocupada|pujas|ocupacional|ilegal|okupado|sin posesi|procedimiento judicial|alquilado',
        case=False, na=False
    )
]

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

# Filtro por municipio (desplegable)
municipality = st.sidebar.selectbox(
    "Selecciona el municipio",
    options=["Todos"] + list(df_properties["municipality"].unique())
)

# Filtro por distrito (desplegable)
district = st.sidebar.selectbox(
    "Selecciona el distrito",
    options=["Todos"] + list(df_properties["district"].dropna().unique())
)

# Filtro por descripción (palabras clave)
keyword = st.sidebar.text_input("Buscar en descripción", "")

# Aplicar los filtros
filtered_df = df_properties[
    (df_properties["price"] >= min_price) &
    (df_properties["price"] <= max_price) &
    (df_properties["rooms"] >= min_rooms) &
    (df_properties["rooms"] <= max_rooms) &
    (df_properties["description"].str.contains(keyword, case=False, na=False))
]

# Filtrar por municipio si no es "Todos"
if municipality != "Todos":
    filtered_df = filtered_df[filtered_df["municipality"] == municipality]

# Filtrar por distrito si no es "Todos"
if district != "Todos":
    filtered_df = filtered_df[filtered_df["district"] == district]

# Mostrar los resultados filtrados
st.subheader(f"Resultados encontrados: {len(filtered_df)} propiedades")

# Mostrar las propiedades como tarjetas
for _, row in filtered_df.iterrows():
    st.markdown("---")
    col1, col2 = st.columns([1, 2])

    # Columna 1: Imagen de la propiedad
    with col1:
        if pd.notna(row["thumbnail"]):  # Verifica si hay una imagen disponible
            st.image(row["thumbnail"], use_container_width=True)
        else:
            st.image("https://placehold.co/300x200?text=Sin+Imagen", use_container_width=True)

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
