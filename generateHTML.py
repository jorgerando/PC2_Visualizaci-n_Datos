import pandas as pd
import plotly.express as px
import json
from pathlib import Path

# -------------------- PRIMER GRÁFICO: Electricidad mundial por fuente --------------------
with open("owid-energy-data.json", "r") as f:
    data = json.load(f)

world_data = data["World"]["data"]
df = pd.DataFrame(world_data)

energy_sources = [
    "year",
    "coal_electricity",
    "oil_electricity",
    "gas_electricity",
    "nuclear_electricity",
    "hydro_electricity",
    "solar_electricity",
    "wind_electricity",
    "biofuel_electricity",
    "other_renewable_electricity"
]

cols = [c for c in energy_sources if c in df.columns]
df = df[cols].dropna(subset=["year"])
df = df[df["year"] >= 1985]

rename_dict = {
    "coal_electricity": "Carbón",
    "oil_electricity": "Petróleo",
    "gas_electricity": "Gas",
    "nuclear_electricity": "Nuclear",
    "hydro_electricity": "Hidroeléctrica",
    "solar_electricity": "Solar",
    "wind_electricity": "Eólica",
    "biofuel_electricity": "Biocombustibles",
    "other_renewable_electricity": "Otras renovables"
}

df = df.rename(columns=rename_dict)
df_melted = df.melt(id_vars="year", var_name="Fuente de energía", value_name="Electricidad (TWh)")

fig1 = px.area(
    df_melted,
    x="year",
    y="Electricidad (TWh)",
    color="Fuente de energía",
    title="Evolución mundial de la electricidad por fuente de energía (1965–2023)",
    template="plotly_white"
)
fig1.update_traces(opacity=0.8)
fig1.update_layout(
    xaxis_title="Año",
    yaxis_title="Electricidad producida (TWh)",
    legend_title_text="Fuente de energía",
    hovermode="x unified"
)

# -------------------- SEGUNDO GRÁFICO: Consumo energético por país --------------------
paises = ["China", "United States", "Russia", "India", "Japan", "Germany"]
fuentes = ["coal_consumption", "oil_consumption", "gas_consumption", "nuclear_consumption", "renewables_consumption"]

df_list = []
for pais in paises:
    if pais in data:
        df_temp = pd.DataFrame(data[pais]["data"])
        cols_presentes = [c for c in fuentes if c in df_temp.columns]
        if cols_presentes:
            df_temp = df_temp[["year"] + cols_presentes]
            df_temp["País"] = pais
            df_list.append(df_temp)

df = pd.concat(df_list, ignore_index=True)
df = df[df["year"] >= 1965]
df_melted = df.melt(id_vars=["year", "País"], var_name="Fuente", value_name="Consumo (TWh)")
df_melted["Fuente"] = df_melted["Fuente"].replace({
    "coal_consumption": "Carbón",
    "oil_consumption": "Petróleo",
    "gas_consumption": "Gas natural",
    "nuclear_consumption": "Nuclear",
    "renewables_consumption": "Renovables"
})

fig2 = px.area(
    df_melted,
    x="year",
    y="Consumo (TWh)",
    color="Fuente",
    facet_col="País",
    facet_col_wrap=3,
    title="Consumo energético por fuente y país (1965–2023)",
    template="plotly_white"
)
fig2.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
fig2.update_layout(
    title_x=0.5,
    title_font_size=20,
    height=800,
    showlegend=True,
    legend_title_text="Fuente de energía"
)

# -------------------- TERCER GRÁFICO: Relación Na/K por medicamento --------------------
df_drug = pd.read_csv("drug200.csv")
df_drug["Drug"] = df_drug["Drug"].replace("drugX", "Placebo")
min_val, max_val = df_drug["Na_to_K"].min(), df_drug["Na_to_K"].max()
df_drug["Na_to_K_scaled"] = 1 + 4 * (df_drug["Na_to_K"] - min_val) / (max_val - min_val)

fig3 = px.strip(
    df_drug,
    x="Drug",
    y="Na_to_K_scaled",
    color="Drug",
    stripmode="overlay",
    title="Relación sodio/potasio (Na/K) por tipo de medicamento",
    template="plotly_white"
)
fig3.update_traces(jitter=0.4, marker=dict(size=8, opacity=0.7))
fig3.update_layout(
    yaxis_title="Relación sodio/potasio (Na/K) — valores normalizados",
    xaxis_title="Tipo de medicamento",
    title_x=0.5,
    showlegend=False
)

# -------------------- COMBINAR EN UN SOLO HTML --------------------
output_path = Path("graficos_energia.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(fig1.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write("<hr><h2 style='text-align:center;'>Consumo energético por país</h2>")
    f.write(fig2.to_html(full_html=False, include_plotlyjs=False))
    f.write("<hr><h2 style='text-align:center;'>Relación Na/K por medicamento</h2>")
    f.write(fig3.to_html(full_html=False, include_plotlyjs=False))

print(f"✅ Archivo HTML generado correctamente: {output_path.resolve()}")
