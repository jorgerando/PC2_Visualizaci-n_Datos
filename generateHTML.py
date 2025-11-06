import pandas as pd
import plotly.express as px
import json
from pathlib import Path
import numpy as np

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

df = pd.read_csv("drug200.csv")
df["Drug"] = df["Drug"].replace("drugX", "Placebo")

min_val, max_val = df["Na_to_K"].min(), df["Na_to_K"].max()
df["Na_to_K_scaled"] = 1 + 4 * (df["Na_to_K"] - min_val) / (max_val - min_val)

def thin_group(values, min_dist):
    """
    values: 1D numpy array ya ordenado
    min_dist: distancia mínima entre valores consecutivos a mantener
    Devuelve índices relativos (en values) de los elementos que se mantienen.
    """
    kept_idx = []
    last_kept_val = None
    for i, v in enumerate(values):
        if last_kept_val is None or abs(v - last_kept_val) >= min_dist:
            kept_idx.append(i)
            last_kept_val = v
    return np.array(kept_idx, dtype=int)

def remove_close_points(df, group_col, value_col, min_dist):
    """
    Devuelve un DataFrame filtrado donde, dentro de cada grupo,
    se han eliminado puntos demasiado próximos en value_col.
    """
    keep_indices = []
    for name, group in df.groupby(group_col):
        # ordenar por el valor para calcular distancias adyacentes
        g = group.sort_values(value_col).reset_index()
        vals = g[value_col].to_numpy()
        kept_local = thin_group(vals, min_dist)
        # transformar índices locales a índices originales del df
        keep_indices.extend(g.loc[kept_local, "index"].tolist())
    # mantener el orden original del DataFrame
    keep_indices = sorted(keep_indices)
    return df.loc[keep_indices].reset_index(drop=True), len(df) - len(keep_indices)

# ---------- Opción automática para elegir min_dist (opcional) ----------
def auto_min_dist(df, group_col, value_col, quantile=0.05, factor=1.0):
    """
    Calcula distancias adyacentes por grupo y devuelve un valor sugerido
    para min_dist: el quantile de esas distancias multiplicado por factor.
    quantile pequeño => más conservador (elimina menos).
    """
    all_adj_diffs = []
    for _, g in df.groupby(group_col):
        vals = np.sort(g[value_col].to_numpy())
        if len(vals) > 1:
            diffs = np.diff(vals)
            all_adj_diffs.extend(diffs.tolist())
    if len(all_adj_diffs) == 0:
        return 0.0
    q = np.quantile(all_adj_diffs, quantile)
    # evitar 0
    return max(q * factor, 1e-6)


min_dist = 0.05

filtered_df, removed_count = remove_close_points(df, group_col="Drug", value_col="Na_to_K_scaled", min_dist=min_dist)
print(f"Total original: {len(df)} — Total filtrado: {len(filtered_df)} — Eliminados: {removed_count}")

fig3 = px.strip(
    filtered_df,
    x="Drug",
    y="Na_to_K_scaled",
    color="Drug",
    stripmode="overlay",
    title="Relación sodio/potasio (Na/K) por tipo de medicamento — puntos filtrados",
    template="plotly_white",
    hover_data=["Age", "Sex", "BP", "Cholesterol", "Na_to_K"]
)

fig3.update_traces(jitter=0.15, marker=dict(size=8, opacity=0.85))
fig3.update_layout(
    yaxis_title="Relación sodio/potasio (Na/K) — valores normalizados",
    xaxis_title="Tipo de medicamento",
    title_x=0.5,
    showlegend=False
)

fig3.write_html("SwarmPlot_NaK_Normalizado_filtrado.html", auto_open=False)
fig3.show()
print("✅ Gráfico filtrado guardado como SwarmPlot_NaK_Normalizado_filtrado.html")


# -------------------- COMBINAR EN UN SOLO HTML --------------------
output_path = Path("graficos_energia.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(fig1.to_html(full_html=False, include_plotlyjs='cdn'))
    f.write("<hr><h2 style='text-align:center;'>Consumo energético por país</h2>")
    f.write(fig2.to_html(full_html=False, include_plotlyjs=False))
    f.write("<hr><h2 style='text-align:center;'>Relación Na/K por medicamento</h2>")
    f.write(fig3.to_html(full_html=False, include_plotlyjs=False))

print(f"✅ Archivo HTML generado correctamente: {output_path.resolve()}")
