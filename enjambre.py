import pandas as pd
import numpy as np
import plotly.express as px

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

fig = px.strip(
    filtered_df,
    x="Drug",
    y="Na_to_K_scaled",
    color="Drug",
    stripmode="overlay",
    title="Relación sodio/potasio (Na/K) por tipo de medicamento — puntos filtrados",
    template="plotly_white",
    hover_data=["Age", "Sex", "BP", "Cholesterol", "Na_to_K"]
)

fig.update_traces(jitter=0.15, marker=dict(size=8, opacity=0.85))
fig.update_layout(
    yaxis_title="Relación sodio/potasio (Na/K) — valores normalizados",
    xaxis_title="Tipo de medicamento",
    title_x=0.5,
    showlegend=False
)

fig.write_html("SwarmPlot_NaK_Normalizado_filtrado.html", auto_open=False)
fig.show()
print("✅ Gráfico filtrado guardado como SwarmPlot_NaK_Normalizado_filtrado.html")
