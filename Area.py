import pandas as pd
import plotly.express as px
import json

with open("owid-energy-data.json", "r") as f:
    data = json.load(f)

world_data = data["World"]["data"]

df = pd.DataFrame(world_data)

available_cols = df.columns.tolist()

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

fig = px.area(
    df_melted,
    x="year",
    y="Electricidad (TWh)",
    color="Fuente de energía",
    title="Evolución mundial de la electricidad por fuente de energía (1965–2023)",
    template="plotly_white"
)

fig.update_traces(opacity=0.8)
fig.update_layout(
    xaxis_title="Año",
    yaxis_title="Electricidad producida (TWh)",
    legend_title_text="Fuente de energía",
    hovermode="x unified"
)

fig.show()
