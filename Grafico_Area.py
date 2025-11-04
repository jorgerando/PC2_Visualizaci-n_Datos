import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# --- GRÁFICO DE ÁREA (Plotly) ---
df_area = px.data.gapminder().query("country == 'Spain'")
fig_area = px.area(
    df_area,
    x="year",
    y="gdpPercap",
    title="Gráfico de Área – PIB per cápita de España (1952–2007)",
    labels={"gdpPercap": "PIB per cápita (USD)", "year": "Año"},
    template="plotly_white"
)
fig_area.update_traces(line_color="royalblue", fillcolor="lightblue", line_width=3)
html_area = fig_area.to_html(full_html=False, include_plotlyjs='cdn')


# --- SMALL MULTIPLES (Plotly) ---
df_small = px.data.gapminder().query("continent == 'Europe'")
fig_small = px.line(
    df_small,
    x="year",
    y="lifeExp",
    color="country",
    facet_col="country",
    facet_col_wrap=4,
    title="Small Multiples – Esperanza de vida en países europeos",
    template="plotly_white"
)
fig_small.update_traces(line=dict(width=2))
fig_small.update_layout(showlegend=False)
html_small = fig_small.to_html(full_html=False, include_plotlyjs=False)


# --- SWARM PLOT (Seaborn) ---
df_swarm = sns.load_dataset("iris")
plt.figure(figsize=(8, 6))
sns.swarmplot(data=df_swarm, x="species", y="petal_length", palette="viridis")
plt.title("Swarm Plot – Longitud del pétalo por especie de flor")
plt.xlabel("Especie")
plt.ylabel("Longitud del pétalo (cm)")
plt.grid(True, linestyle="--", alpha=0.5)

# Convertir el gráfico de Matplotlib a imagen base64 para incrustar en HTML
buffer = BytesIO()
plt.tight_layout()
plt.savefig(buffer, format='png', bbox_inches='tight')
buffer.seek(0)
img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
plt.close()

# Crear HTML del Swarm Plot
html_swarm = f'<img src="data:image/png;base64,{img_base64}" width="800">'

html_final = f"""
<html>
<head>
    <meta charset="utf-8">
    <title>Visualizaciones – Área, Small Multiples y Swarm</title>
</head>
<body style="font-family:Arial; margin:40px;">
    <h1 style="text-align:center;">Visualizaciones Interactivas</h1>
    <hr>
    <h2>Gráfico de Área</h2>
    {html_area}
    <hr>
    <h2>Small Multiples</h2>
    {html_small}
    <hr>
    <h2>Swarm Plot</h2>
    <div style="text-align:center;">{html_swarm}</div>
    <hr>
    <p style="text-align:center; color:gray;">© PEC Visualización de Datos – 2025</p>
</body>
</html>
"""

with open("index.html", "w") as f:
    f.write(html_final)
