"""Etapa 3: análise descritiva com intervalos de confiança.

Toda taxa de atraso sai com intervalo de confiança de 95% (método de Wilson),
para não tratar diferença pequena em amostra pequena como se fosse real.
"""
import numpy as np
import pandas as pd
from scipy.stats import norm
from comum import RES, carregar_base

df = carregar_base()
df["atrasou"] = df["atrasou"].astype(bool)
Z = norm.ppf(0.975)


def wilson(k, n):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    d = 1 + Z**2 / n
    c = (p + Z**2 / (2 * n)) / d
    h = Z * np.sqrt(p * (1 - p) / n + Z**2 / (4 * n**2)) / d
    return (100 * (c - h), 100 * (c + h))


def taxa(g):
    n, k = len(g), int(g["atrasou"].sum())
    lo, hi = wilson(k, n)
    return pd.Series({"pedidos": n, "atrasados": k, "pct_atraso": 100 * k / n, "ic95_inf": lo, "ic95_sup": hi})


# ---- A. indicadores gerais e sensibilidade da definição de atraso
n = len(df)
ger = taxa(df).to_dict()
ger.update({
    "pct_atraso_por_horario (definição antiga)": round(100 * df["atrasou_por_horario"].mean(), 2),
    "dias_total_mediana": df["dias_total"].median(), "dias_total_media": df["dias_total"].mean(),
    "dias_prometidos_mediana": df["dias_prometidos"].median(), "dias_prometidos_media": df["dias_prometidos"].mean(),
    "folga_mediana_dias": (df["dias_prometidos"] - df["dias_total"]).median(),
    "nota_media": df["nota"].mean(), "pedidos_avaliados": int(df["nota"].notna().sum()),
    "mediana_distancia_km": df["distancia_km"].median(), "pct_mesma_uf": 100 * df["mesma_uf"].mean(),
})
pd.Series(ger).to_frame("valor").to_csv(RES / "03_indicadores_gerais.csv")

# ---- B. atraso por mês (meses com >= 500 pedidos)
m = df.groupby(df["mes_compra"].dt.strftime("%Y-%m")).apply(taxa, include_groups=False)
m["mediana_dias_total"] = df.groupby(df["mes_compra"].dt.strftime("%Y-%m"))["dias_total"].median()
m = m[m["pedidos"] >= 500].reset_index().rename(columns={"mes_compra": "mes"})
m.round(2).to_csv(RES / "03_atraso_por_mes.csv", index=False)

# ---- C. atraso por UF do cliente (>= 300 pedidos)
e = df.groupby("uf_cliente").apply(taxa, include_groups=False)
agg = df.groupby("uf_cliente").agg(
    mediana_dias_total=("dias_total", "median"), mediana_transporte=("dias_transporte", "median"),
    mediana_prometidos=("dias_prometidos", "median"), mediana_km=("distancia_km", "median"),
    pct_mesma_uf=("mesma_uf", lambda s: 100 * s.mean()), frete_medio=("valor_frete", "mean"),
    nota_media=("nota", "mean"),
)
e = e.join(agg)
e = e[e["pedidos"] >= 300].sort_values("pct_atraso", ascending=False).reset_index()
e.round(2).to_csv(RES / "03_atraso_por_uf.csv", index=False)

# ---- D. etapas: no prazo x atrasou
g = df.groupby("atrasou").agg(
    pedidos=("order_id", "count"),
    ate_postagem_media=("dias_ate_postagem", "mean"), ate_postagem_mediana=("dias_ate_postagem", "median"),
    transporte_media=("dias_transporte", "mean"), transporte_mediana=("dias_transporte", "median"),
    total_media=("dias_total", "mean"), total_mediana=("dias_total", "median"),
    prometidos_mediana=("dias_prometidos", "median"),
    distancia_mediana_km=("distancia_km", "median"),
).reset_index()
g["grupo"] = g["atrasou"].map({False: "No prazo", True: "Atrasou"})
g.drop(columns="atrasou").round(2).to_csv(RES / "03_etapas_prazo_vs_atraso.csv", index=False)

# ---- E. distância
bins = [0, 100, 300, 600, 1000, 1500, 1e9]
labs = ["até 100 km", "100 a 300 km", "300 a 600 km", "600 a 1.000 km", "1.000 a 1.500 km", "mais de 1.500 km"]
df["faixa_km"] = pd.cut(df["distancia_km"], bins=bins, labels=labs, include_lowest=True)
d = df.dropna(subset=["faixa_km"]).groupby("faixa_km", observed=True).apply(taxa, include_groups=False)
d = d.join(df.groupby("faixa_km", observed=True).agg(
    mediana_transporte=("dias_transporte", "median"), mediana_prometidos=("dias_prometidos", "median"),
    mediana_total=("dias_total", "median"), frete_medio=("valor_frete", "mean"), nota_media=("nota", "mean"))).reset_index()
d.round(2).to_csv(RES / "03_atraso_por_distancia.csv", index=False)

# ---- F. nota por faixa de atraso
df["dias_atraso_faixa"] = pd.cut(df["dias_atraso"], bins=[-1e9, 0, 3, 7, 14, 1e9],
                                 labels=["No prazo ou adiantado", "Atraso de 1 a 3 dias", "Atraso de 4 a 7 dias", "Atraso de 8 a 14 dias", "Atraso de mais de 14 dias"])
av = df.dropna(subset=["nota"]).copy()
av["nota_baixa"] = av["nota"].le(2)
nf = av.groupby("dias_atraso_faixa", observed=True).agg(
    pedidos_avaliados=("nota", "size"), nota_media=("nota", "mean"), nota_mediana=("nota", "median"),
    pct_notas_1_ou_2=("nota_baixa", lambda s: 100 * s.mean())).reset_index()
tot = df.groupby("dias_atraso_faixa", observed=True).size().rename("pedidos_total").reset_index()
nf = nf.merge(tot, on="dias_atraso_faixa")
nf["pct_dos_pedidos"] = 100 * nf["pedidos_total"] / len(df)
nf.round(2).to_csv(RES / "03_nota_por_faixa_atraso.csv", index=False)

# ---- G. categorias (>= 500 pedidos)
cat = df.groupby("categoria").apply(taxa, include_groups=False)
cat = cat.join(df.groupby("categoria").agg(mediana_dias_total=("dias_total", "median"), nota_media=("nota", "mean"),
                                           mediana_peso_g=("peso_g", "median"), frete_medio=("valor_frete", "mean")))
cat = cat[cat["pedidos"] >= 500].sort_values("pct_atraso", ascending=False).reset_index()
cat.round(2).to_csv(RES / "03_atraso_por_categoria.csv", index=False)

# ---- H. cenários quantificados
atr_total = int(df["atrasou"].sum())
ne_rj = ["AL", "MA", "PI", "CE", "SE", "BA", "RJ", "PA", "ES"]
base_ref = df[~df["uf_cliente"].isin(ne_rj)]
tx_ref = base_ref["atrasou"].mean()
alvo = df[df["uf_cliente"].isin(ne_rj)]
evitaveis = int(alvo["atrasou"].sum() - tx_ref * len(alvo))
longos = int((df["dias_atraso"] > 3).sum())
cen = pd.DataFrame([
    {"cenario": "Atraso nas UFs de maior atraso (AL, MA, PI, CE, SE, BA, RJ, PA, ES) cair ao nível das demais UFs",
     "pedidos_atrasados_evitados": evitaveis, "pct_do_total_de_atrasos": round(100 * evitaveis / atr_total, 1),
     "queda_pontos_percentuais_no_atraso_geral": round(100 * evitaveis / len(df), 2)},
    {"cenario": "Eliminar atrasos longos (mais de 3 dias)", "pedidos_atrasados_evitados": longos,
     "pct_do_total_de_atrasos": round(100 * longos / atr_total, 1), "queda_pontos_percentuais_no_atraso_geral": round(100 * longos / len(df), 2)},
])
cen["pct_pedidos_nas_UFs_alvo"] = [round(100 * len(alvo) / len(df), 1), np.nan]
cen.to_csv(RES / "03_cenarios.csv", index=False)

# ---- I. promessa de prazo por UF: folga mediana
fol = (df.assign(folga=df["dias_prometidos"] - df["dias_total"]).groupby("uf_cliente")
       .agg(pedidos=("folga", "size"), prometido_mediana=("dias_prometidos", "median"), real_mediana=("dias_total", "median"),
            folga_mediana=("folga", "median"), pct_folga_negativa=("folga", lambda s: 100 * (s < 0).mean())).reset_index())
fol = fol[fol["pedidos"] >= 300].sort_values("folga_mediana")
fol.round(2).to_csv(RES / "03_folga_prazo_por_uf.csv", index=False)

pd.set_option("display.width", 250, "display.max_columns", 30)
print(pd.Series(ger).round(3).to_string())
print(m.round(2).to_string(index=False))
print(e.round(2).head(30).to_string(index=False))
print(g.round(2).to_string(index=False))
print(d.round(2).to_string(index=False))
print(nf.round(2).to_string(index=False))
print(cat.round(2).head(8).to_string(index=False)); print(cat.round(2).tail(5).to_string(index=False))
print(cen.to_string(index=False))
print(fol.round(2).head(8).to_string(index=False))
