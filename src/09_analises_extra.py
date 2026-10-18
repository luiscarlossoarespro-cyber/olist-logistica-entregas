"""Etapa 9: análises complementares de operação logística.

1. Variabilidade do prazo (percentis P50, P90, P95), base de qualquer SLA.
2. Promessa atual x prazo real P90 por UF (prazo sugerido).
3. Rotas: UF do vendedor (origem) x região do cliente (destino).
4. Dia da semana da compra.
5. Pareto de vendedores (concentração dos atrasos).
6. Avaliações negativas a mais causadas pelo atraso.
7. Faixas de risco do modelo (o que a operação veria na prática).
"""
import numpy as np
import pandas as pd
from comum import RES, RAIZ, carregar_base

df = carregar_base()
df["atrasou"] = df["atrasou"].astype(int)
REG = {"AC": "Norte", "AP": "Norte", "AM": "Norte", "PA": "Norte", "RO": "Norte", "RR": "Norte", "TO": "Norte",
       "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste", "PB": "Nordeste", "PE": "Nordeste",
       "PI": "Nordeste", "RN": "Nordeste", "SE": "Nordeste", "DF": "Centro-Oeste", "GO": "Centro-Oeste",
       "MT": "Centro-Oeste", "MS": "Centro-Oeste", "SP": "Sudeste", "MG": "Sudeste", "ES": "Sudeste",
       "RJ": "Sudeste", "PR": "Sul", "SC": "Sul", "RS": "Sul"}
df["regiao_cliente"] = df["uf_cliente"].map(REG)

# ---- 1. percentis
def pcts(s):
    return pd.Series({"p50": s.quantile(.5), "p75": s.quantile(.75), "p90": s.quantile(.9), "p95": s.quantile(.95), "media": s.mean()})
perc = pd.DataFrame({
    "Compra até postagem": pcts(df["dias_ate_postagem"]),
    "Transporte": pcts(df["dias_transporte"]),
    "Prazo total (compra até entrega)": pcts(df["dias_total"]),
    "Prazo prometido": pcts(df["dias_prometidos"]),
}).T.reset_index().rename(columns={"index": "etapa"})
perc.round(2).to_csv(RES / "09_percentis_prazo.csv", index=False)

# ---- 2. promessa x P90 real por UF
pu = df.groupby("uf_cliente").agg(pedidos=("atrasou", "size"), pct_atraso=("atrasou", lambda s: 100 * s.mean()),
                                  prometido_mediana=("dias_prometidos", "median"),
                                  real_p50=("dias_total", "median"), real_p90=("dias_total", lambda s: s.quantile(.9)))
pu = pu[pu["pedidos"] >= 300].copy()
pu["prazo_sugerido_p90"] = np.ceil(pu["real_p90"])
pu["diferenca_promessa_menos_sugerido"] = pu["prometido_mediana"] - pu["prazo_sugerido_p90"]
pu = pu.sort_values("diferenca_promessa_menos_sugerido").reset_index()
pu.round(2).to_csv(RES / "09_promessa_vs_p90_por_uf.csv", index=False)

# ---- 3. rotas
top_origem = ["SP", "MG", "PR", "RJ", "SC", "RS"]
df["origem"] = df["uf_vendedor"].where(df["uf_vendedor"].isin(top_origem), "Outras")
rot = df.groupby(["origem", "regiao_cliente"]).agg(pedidos=("atrasou", "size"), pct_atraso=("atrasou", lambda s: 100 * s.mean()),
                                                   dias_total_mediana=("dias_total", "median")).reset_index()
rot.round(2).to_csv(RES / "09_rotas_origem_destino.csv", index=False)
top_rotas = (df.groupby(["uf_vendedor", "uf_cliente"]).agg(pedidos=("atrasou", "size"), pct_atraso=("atrasou", lambda s: 100 * s.mean()),
             dias_total_mediana=("dias_total", "median")).reset_index().query("pedidos >= 500").sort_values("pct_atraso", ascending=False))
top_rotas.round(2).to_csv(RES / "09_rotas_uf_500mais.csv", index=False)

# ---- 4. dia da semana (0 = domingo)
nomes = ["domingo", "segunda", "terça", "quarta", "quinta", "sexta", "sábado"]
ds = df.groupby("dia_semana").agg(pedidos=("atrasou", "size"), pct_atraso=("atrasou", lambda s: 100 * s.mean()),
                                  postagem_media=("dias_ate_postagem", "mean"), total_medio=("dias_total", "mean")).reset_index()
ds["dia"] = ds["dia_semana"].map(dict(enumerate(nomes)))
ds.round(2).to_csv(RES / "09_dia_semana.csv", index=False)

# ---- 5. Pareto de vendedores
v = df.groupby("vendedor_id").agg(pedidos=("atrasou", "size"), atrasados=("atrasou", "sum")).sort_values("atrasados", ascending=False)
v["pct_acum_atrasos"] = 100 * v["atrasados"].cumsum() / v["atrasados"].sum()
v["pct_acum_vendedores"] = 100 * np.arange(1, len(v) + 1) / len(v)
v["pct_acum_pedidos"] = 100 * v["pedidos"].cumsum() / v["pedidos"].sum()
com_atraso = int((v["atrasados"] > 0).sum())
def ate(p):
    r = v[v["pct_acum_atrasos"] >= p].iloc[0]
    return r
p50, p80 = ate(50), ate(80)
par = pd.DataFrame([
    {"medida": "vendedores com pelo menos 1 pedido entregue", "valor": len(v)},
    {"medida": "vendedores com pelo menos 1 atraso", "valor": com_atraso},
    {"medida": "% dos vendedores que somam 50% dos atrasos", "valor": p50["pct_acum_vendedores"]},
    {"medida": "% dos pedidos desses vendedores (50%)", "valor": p50["pct_acum_pedidos"]},
    {"medida": "% dos vendedores que somam 80% dos atrasos", "valor": p80["pct_acum_vendedores"]},
    {"medida": "% dos pedidos desses vendedores (80%)", "valor": p80["pct_acum_pedidos"]},
])
par.round(2).to_csv(RES / "09_pareto_vendedores.csv", index=False)
pts = np.linspace(0, 100, 51)
pd.DataFrame({"pct_vendedores": pts, "pct_atrasos": np.interp(pts, np.r_[0, v["pct_acum_vendedores"]], np.r_[0, v["pct_acum_atrasos"]]),
              "pct_pedidos": np.interp(pts, np.r_[0, v["pct_acum_vendedores"]], np.r_[0, v["pct_acum_pedidos"]])}).round(2).to_csv(RES / "09_pareto_curva.csv", index=False)

# ---- 6. notas baixas a mais por causa do atraso
av = df.dropna(subset=["nota"]).copy()
av["baixa"] = av["nota"].le(2)
tx_prazo = av.loc[av.atrasou == 0, "baixa"].mean()
tx_atr = av.loc[av.atrasou == 1, "baixa"].mean()
n_atr = int((av.atrasou == 1).sum())
excesso = n_atr * (tx_atr - tx_prazo)
nb = pd.DataFrame([
    {"medida": "pedidos atrasados com avaliação", "valor": n_atr},
    {"medida": "% notas 1 ou 2 - atrasados", "valor": 100 * tx_atr},
    {"medida": "% notas 1 ou 2 - no prazo", "valor": 100 * tx_prazo},
    {"medida": "notas 1 ou 2 a mais associadas ao atraso", "valor": excesso},
    {"medida": "total de notas 1 ou 2 na base", "valor": int(av["baixa"].sum())},
    {"medida": "% das notas 1 ou 2 associadas ao atraso", "valor": 100 * excesso / av["baixa"].sum()},
])
nb.round(2).to_csv(RES / "09_notas_baixas_por_atraso.csv", index=False)

# ---- 7. faixas de risco do modelo (teste)
pr = pd.read_csv(RAIZ / "dados" / "derivados" / "predicoes_teste.csv").sort_values("risco", ascending=False).reset_index(drop=True)
n = len(pr)
pr["faixa"] = np.select([pr.index < 0.10 * n, pr.index < 0.30 * n], ["Alto (10% maiores)", "Médio (próximos 20%)"], "Baixo (70% restantes)")
fx = pr.groupby("faixa", sort=False).agg(pedidos=("atrasou", "size"), atrasados=("atrasou", "sum"), risco_medio_previsto=("risco", "mean")).reset_index()
fx["pct_atraso_real"] = 100 * fx["atrasados"] / fx["pedidos"]
fx["pct_dos_atrasos"] = 100 * fx["atrasados"] / pr["atrasou"].sum()
fx["risco_medio_previsto"] = 100 * fx["risco_medio_previsto"]
fx.round(2).to_csv(RES / "09_faixas_risco_modelo.csv", index=False)

pd.set_option("display.width", 250)
for nome, t in [("percentis", perc), ("promessa x p90", pu), ("rotas", rot.pivot(index="origem", columns="regiao_cliente", values="pct_atraso").round(1)),
                ("top rotas", top_rotas.head(10)), ("dia semana", ds), ("pareto", par), ("notas baixas", nb), ("faixas risco", fx)]:
    print("==", nome); print(t.round(2).to_string(index=False if nome != "rotas" else True))
