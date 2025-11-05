import pandas as pd
import plotly.express as px

df = pd.read_csv("drug200.csv")

df["Drug"] = df["Drug"].replace("drugX", "Placebo")

min_val, max_val = df["Na_to_K"].min(), df["Na_to_K"].max()
df["Na_to_K_scaled"] = 1 + 4 * (df["Na_to_K"] - min_val) / (max_val - min_val)

fig = px.strip(
    df,
    x="Drug",
    y="Na_to_K_scaled",
    color="Drug",
    stripmode="overlay",
    title="Relación sodio/potasio (Na/K) por tipo de medicamento",
    template="plotly_white"
)

fig.update_traces(jitter=0.4, marker=dict(size=8, opacity=0.7))
fig.update_layout(
    yaxis_title="Relación sodio/potasio (Na/K) — valores normalizados",
    xaxis_title="Tipo de medicamento",
    title_x=0.5,
    showlegend=False
)

fig.show()
fig.write_html("SwarmPlot_NaK_Normalizado.html", auto_open=False)
print("✅ Gráfico guardado como SwarmPlot_NaK_Normalizado.html")
