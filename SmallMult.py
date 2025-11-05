import pandas as pd
import plotly.express as px
import json

with open("owid-energy-data.json", "r") as f:
    data = json.load(f)

paises = [ "China","United States","Russia","India","Japan","Germany"]

fuentes = [
    "coal_consumption",
    "oil_consumption",
    "gas_consumption",
    "nuclear_consumption",
    "renewables_consumption"
]

df_list = []

for pais in paises:
    if pais in data:
        df_temp = pd.DataFrame(data[pais]["data"])
        cols_presentes = [c for c in fuentes if c in df_temp.columns]
        if len(cols_presentes) > 0:
            df_temp = df_temp[["year"] + cols_presentes]
            df_temp["País"] = pais
            df_list.append(df_temp)


df = pd.concat(df_list, ignore_index=True)

df = df[df["year"] >= 1965]

df_melted = df.melt(
    id_vars=["year", "País"],
    var_name="Fuente",
    value_name="Consumo (TWh)"
)

df_melted["Fuente"] = df_melted["Fuente"].replace({
    "coal_consumption": "Carbón",
    "oil_consumption": "Petróleo",
    "gas_consumption": "Gas natural",
    "nuclear_consumption": "Nuclear",
    "renewables_consumption": "Renovables"
})

fig = px.area(
    df_melted,
    x="year",
    y="Consumo (TWh)",
    color="Fuente",
    facet_col="País",
    facet_col_wrap=3,
    title="Consumo energético por fuente y país (1965–2023)",
    template="plotly_white"
)

fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
fig.update_layout(
    title_x=0.5,
    title_font_size=20,
    height=800,
    showlegend=True,
    legend_title_text="Fuente de energía"
)

fig.show()
fig.write_html("SmallMultiples_Energia.html", auto_open=False)
print("✅ Gráfico generado y guardado como 'SmallMultiples_Energia.html'")
