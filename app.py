st.write(
    "La auditoría permite detectar problemas antes de graficar o interpretar datos. "
    "En este caso se revisaron duplicados, fechas, años fuera de rango, valores nulos "
    "y columnas con muchos valores únicos."
)

st.subheader("Cardinalidad por columna")
cardinalidad = df_original.nunique().sort_values(ascending=False).to_frame("valores_unicos")
st.dataframe(cardinalidad, use_container_width=True)

section_divider()

# ==============================
# 4. Limpieza
# ==============================

st.header("4. Limpieza de datos")
st.write(
    "La limpieza se hizo sin borrar información de forma agresiva. "
    "Los campos faltantes como director, elenco, país o clasificación se marcaron con "
    "etiquetas explícitas, porque la ausencia de información también es útil para auditar calidad."
)

st.subheader("Decisiones aplicadas")
st.write("1. Se quitaron espacios sobrantes en columnas de texto.")
st.write("2. Se eliminaron duplicados exactos.")
st.write("3. La columna date_added se convirtió a formato de fecha.")
st.write("4. Los faltantes categóricos se reemplazaron por No especificado o Sin clasificación.")
st.write("5. La duración se separó en número y unidad.")
st.write("6. Se validó que release_year estuviera entre 1900 y el año actual.")
st.write("7. Se crearon variables nuevas para facilitar el análisis.")

r1, r2, r3, r4 = st.columns(4)
r1.metric("Filas iniciales", f"{resumen_limpieza['filas_inicio']:,}")
r2.metric("Filas finales", f"{resumen_limpieza['filas_final']:,}")
r3.metric("Filas eliminadas", f"{resumen_limpieza['filas_eliminadas']:,}")
r4.metric("Duplicados eliminados", f"{resumen_limpieza['duplicados_eliminados']:,}")

left2, right2 = st.columns(2)
with left2:
    st.subheader("Faltantes antes")
    st.dataframe(missing_table(df_original), use_container_width=True)
with right2:
    st.subheader("Faltantes después")
    st.dataframe(missing_table(df_limpio), use_container_width=True)

section_divider()

# ==============================
# 5. Variables nuevas
# ==============================

st.header("5. Variables nuevas")

new_columns = [
    "date_added_missing",
    "year_added",
    "month_added",
    "content_age_when_added",
    "main_country",
    "main_genre",
    "cast_count",
    "genre_count",
    "duration_number",
    "duration_unit",
    "movie_minutes",
    "tv_seasons",
]

st.write(
    "Las variables nuevas ayudan a convertir columnas de texto en información más fácil de analizar. "
    "Por ejemplo, main_country toma el primer país listado, main_genre toma el primer género, "
    "y movie_minutes permite estudiar solo la duración de películas."
)

st.dataframe(df_limpio[new_columns].head(15), use_container_width=True)

section_divider()

# ==============================
# 6. Visualizaciones
# ==============================

st.header("6. Visualizaciones exploratorias")

viz1, viz2 = st.columns(2)
with viz1:
    st.subheader("Películas vs series")
    plot_bar(
        df_limpio["type"].value_counts(),
        "Cantidad de títulos por tipo",
        "Tipo",
        "Cantidad",
    )

with viz2:
    st.subheader("Clasificaciones más frecuentes")
    plot_bar(
        df_limpio["rating"].value_counts().head(10),
        "Top 10 clasificaciones",
        "Rating",
        "Cantidad",
        rotation=45,
    )

viz3, viz4 = st.columns(2)
with viz3:
    st.subheader("Top países principales")
    top_countries = (
        df_limpio[df_limpio["main_country"] != "No especificado"]["main_country"]
        .value_counts()
        .head(10)
    )
    plot_bar(top_countries, "Top 10 países principales", "País", "Cantidad", rotation=45)

with viz4:
    st.subheader("Top géneros principales")
    plot_bar(
        df_limpio["main_genre"].value_counts().head(10),
        "Top 10 géneros principales",
        "Género",
        "Cantidad",
        rotation=45,
    )

st.subheader("Títulos agregados por año")
yearly = df_limpio["year_added"].dropna().astype(int).value_counts().sort_index()
fig, ax = plt.subplots(figsize=(10, 5))
yearly.plot(kind="line", marker="o", ax=ax)
ax.set_title("Cantidad de títulos agregados por año")
ax.set_xlabel("Año agregado")
ax.set_ylabel("Cantidad de títulos")
ax.grid(alpha=0.3)
st.pyplot(fig)

st.subheader("Distribución de duración de películas")
movie_minutes = df_limpio["movie_minutes"].dropna()
fig, ax = plt.subplots(figsize=(10, 5))
movie_minutes.plot(kind="hist", bins=30, ax=ax)
ax.set_title("Duración de películas")
ax.set_xlabel("Minutos")
ax.set_ylabel("Cantidad de películas")
ax.grid(alpha=0.3)
st.pyplot(fig)

section_divider()

# ==============================
# 7. Explorador interactivo
# ==============================

st.header("7. Explorador interactivo")
st.write("Usa los filtros para revisar el catálogo limpio.")

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    selected_type = st.multiselect(
        "Tipo",
        sorted(df_limpio["type"].dropna().astype(str).unique()),
    )

with filter_col2:
    selected_rating = st.multiselect(
        "Clasificación",
        sorted(df_limpio["rating"].dropna().astype(str).unique()),
    )

with filter_col3:
    selected_country = st.multiselect(
        "País principal",
        sorted(df_limpio["main_country"].dropna().astype(str).unique()),
    )

filtered = df_limpio.copy()
if selected_type:
    filtered = filtered[filtered["type"].astype(str).isin(selected_type)]
if selected_rating:
    filtered = filtered[filtered["rating"].astype(str).isin(selected_rating)]
if selected_country:
    filtered = filtered[filtered["main_country"].astype(str).isin(selected_country)]

st.metric("Registros filtrados", f"{len(filtered):,}")
st.dataframe(
    filtered[
        [
            "title",
            "type",
            "main_country",
            "main_genre",
            "release_year",
            "rating",
            "duration",
            "year_added",
        ]
    ].head(300),
    use_container_width=True,
)

section_divider()

# ==============================
# 8. Descarga y cierre
# ==============================

st.header("8. Descarga del dataset limpio")

st.download_button(
    label="Descargar CSV limpio",
    data=df_limpio.to_csv(index=False).encode("utf-8"),
    file_name="netflix_titles_limpio.csv",
    mime="text/csv",
)

st.header("Conclusión")
st.write(
    "En esta práctica se realizó un proceso completo de manejo de datos: carga, revisión inicial, "
    "auditoría, limpieza, creación de variables, visualización y descarga del resultado. "
    "El punto más importante es que limpiar datos no significa borrar todo lo incompleto, sino tomar "
    "decisiones justificadas para que el análisis sea más confiable."
)
