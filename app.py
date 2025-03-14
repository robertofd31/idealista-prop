import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, HTML

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

# Crear un DataFrame de ejemplo para demostrar la funcionalidad
# ya que no tenemos acceso al archivo CSV real
data = {
    'price': np.random.randint(100000, 500000, 20),
    'rooms': np.random.randint(1, 6, 20),
    'bathrooms': np.random.randint(1, 4, 20),
    'size': np.random.randint(40, 200, 20),
    'municipality': np.random.choice(['Madrid', 'Alcobendas', 'Getafe', 'Leganés'], 20),
    'district': np.random.choice(['Centro', 'Salamanca', 'Chamberí', 'Retiro', None], 20),
    'description': [
        'Bonito piso reformado en el centro',
        'Amplio apartamento con vistas',
        'Piso en subasta judicial',
        'Vivienda ocupada actualmente',
        'Luminoso piso exterior',
        'Apartamento con terraza',
        'Local sin cambio de uso',
        'Piso a estrenar',
        'Vivienda en nuda propiedad',
        'Amplio piso con garaje',
        'Piso okupado, oportunidad inversores',
        'Bonito ático con vistas',
        'Piso alquilado, rentabilidad 5%',
        'Apartamento céntrico',
        'Piso en buen estado',
        'Vivienda en procedimiento judicial',
        'Piso luminoso y reformado',
        'Apartamento con piscina',
        'Piso con buena distribución',
        'Ático con terraza'
    ],
    'latitude': np.random.uniform(40.3, 40.5, 20),
    'longitude': np.random.uniform(-3.8, -3.6, 20),
    'url': ['https://www.idealista.com/inmueble/' + str(i) for i in range(1, 21)],
    'thumbnail': ['https://placehold.co/300x200?text=Property+' + str(i) for i in range(1, 21)]
}

df_properties = pd.DataFrame(data)

print("=== EXPLORADOR DE PROPIEDADES - ESTILO IDEALISTA ===")
print("\nFuncionalidades implementadas en el código:")
print("1. Filtro para excluir propiedades con términos específicos en la descripción")
print("2. Selección múltiple de municipios")
print("3. Filtros adicionales: tamaño mínimo, baños mínimos")
print("4. Visualización de propiedades en mapa")
print("5. Cálculo de métricas como precio por metro cuadrado")

# Demostrar el filtro de exclusión
exclude_terms = "subasta|local sin cambio de uso|cambio de uso|nuda propiedad|no se puede hipotecar|ocupado|ocupada|pujas|ocupacional|ilegal|okupado|sin posesi|procedimiento judicial|alquilado"
filtered_df = df_properties[~df_properties["description"].str.contains(exclude_terms, case=False, na=False)]

print(f"\n=== ANTES DE FILTRAR: {len(df_properties)} propiedades ===")
print(f"=== DESPUÉS DE FILTRAR TÉRMINOS EXCLUIDOS: {len(filtered_df)} propiedades ===")

# Mostrar las propiedades que fueron excluidas
excluded_df = df_properties[df_properties["description"].str.contains(exclude_terms, case=False, na=False)]
print("\nPropiedades excluidas por contener términos no deseados:")
for _, row in excluded_df.iterrows():
    print(f"- {row['description']} (Precio: {row['price']}€)")

# Demostrar la selección múltiple de municipios
print("\n=== SELECCIÓN MÚLTIPLE DE MUNICIPIOS ===")
selected_municipalities = ['Madrid', 'Alcobendas']
multi_filtered = filtered_df[filtered_df["municipality"].isin(selected_municipalities)]
print(f"Propiedades en {', '.join(selected_municipalities)}: {len(multi_filtered)}")

# Demostrar filtro de tamaño mínimo
min_size = 80
size_filtered = filtered_df[filtered_df["size"] >= min_size]
print(f"\n=== FILTRO DE TAMAÑO MÍNIMO ({min_size}m²) ===")
print(f"Propiedades con tamaño >= {min_size}m²: {len(size_filtered)}")

# Calcular y mostrar estadísticas
if len(filtered_df) > 0:
    print("\n=== ESTADÍSTICAS DE PROPIEDADES FILTRADAS ===")
    print(f"Precio medio: {int(filtered_df['price'].mean())}€")
    print(f"Tamaño medio: {int(filtered_df['size'].mean())}m²")
    avg_price_sqm = int(filtered_df['price'].sum() / filtered_df['size'].sum())
    print(f"Precio medio por m²: {avg_price_sqm}€/m²")

# Visualizar distribución de precios
plt.figure(figsize=(10, 6))
plt.hist(filtered_df['price'], bins=10, color='skyblue', edgecolor='black')
plt.title('Distribución de Precios')
plt.xlabel('Precio (€)')
plt.ylabel('Número de Propiedades')
plt.grid(True, alpha=0.3)
plt.show()

# Visualizar precio por metro cuadrado por municipio
plt.figure(figsize=(10, 6))
filtered_df['price_per_sqm'] = filtered_df['price'] / filtered_df['size']
filtered_df.groupby('municipality')['price_per_sqm'].mean().plot(kind='bar', color='lightgreen')
plt.title('Precio Medio por Metro Cuadrado por Municipio')
plt.xlabel('Municipio')
plt.ylabel('Precio/m² (€)')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# Código para el mapa (comentado ya que no podemos mostrar mapas interactivos aquí)
print("\n=== VISUALIZACIÓN DE MAPA ===")
print("En la aplicación Streamlit, se mostraría un mapa interactivo con las ubicaciones de las propiedades.")
print("Cada marcador tendría información sobre precio, habitaciones, tamaño y un enlace a la propiedad.")

# Mostrar ejemplo de cómo se vería una propiedad
print("\n=== EJEMPLO DE VISUALIZACIÓN DE PROPIEDAD ===")
example_property = filtered_df.iloc[0]
print(f"Precio: {example_property['price']}€")
print(f"Habitaciones: {example_property['rooms']}, Baños: {example_property['bathrooms']}, Tamaño: {example_property['size']}m²")
print(f"Ubicación: {example_property['municipality']}, {example_property['district'] if pd.notna(example_property['district']) else 'Sin distrito'}")
print(f"Precio/m²: {round(example_property['price'] / example_property['size'], 2)}€/m²")
print(f"Descripción: {example_property['description'][:200]}...")
print(f"URL: {example_property['url']}")

print("\n=== CÓDIGO COMPLETO PARA STREAMLIT ===")
print("El código completo incluye todas estas funcionalidades implementadas en una interfaz Streamlit interactiva.")
print("Para ejecutarlo, necesitarías instalar streamlit, pandas, folium y streamlit-folium.")
