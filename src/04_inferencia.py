"""Etapa 4: inferência — o que explica o atraso quando olhamos vários fatores ao mesmo tempo.

1. Regressão logística: chance de atraso x região, distância, tempo até postar, peso, mês.
2. Transporte acima do esperado: compara o tempo real de transporte com o tempo
   esperado pela distância (para saber se a região é lenta por ser longe ou por outro motivo).
3. Impacto do atraso na nota, com controles.
4. Vendedores com atraso estatisticamente acima da média.
5. Picos mensais: qual etapa explica (prazo prometido x transporte x postagem).
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import mannwhitneyu, norm
from comum import RES, carregar_base

df = carregar_base()
df["atrasou"] = df["atrasou"].astype(int)
REG = {"AC": "Norte", "AP": "Norte", "AM": "Norte", "PA": "Norte", "RO": "Norte", "RR": "Norte", "TO": "Norte",
       "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste", "PB": "Nordeste", "PE": "Nordeste",
       "PI": "Nordeste", "RN": "Nordeste", "SE": "Nordeste", "DF": "Centro-Oeste", "GO": "Centro-Oeste",
       "MT": "Centro-Oeste", "MS": "Centro-Oeste", "SP": "SP", "MG": "Sudeste (MG e ES)", "ES": "Sudeste (MG e ES)",
       "RJ": "RJ", "PR": "Sul", "SC": "Sul", "RS": "Sul"}
df["regiao"] = df["uf_cliente"].map(REG)
df["log_km"] = np.log1p(df["distancia_km"])
df["log_peso"] = np.log1p(df["peso_g"])
df["postagem_d"] = df["dias_ate_postagem"].clip(0, 30)
df["mes"] = df["mes_compra"].dt.strftime("%Y-%m")
m = df.dropna(subset=["log_km", "log_peso"]).copy()
m = m[m["mes"].between("2017-01", "2018-08")]

# ---- 1. regressão logística
f = "atrasou ~ C(regiao, Treatment('SP')) + log_km + postagem_d + log_peso + C(mes)"
logit = smf.logit(f, data=m).fit(disp=False, maxiter=200)
ci = logit.conf_int()
tab = pd.DataFrame({"coef": logit.params, "odds_ratio": np.exp(logit.params),
                    "or_ic95_inf": np.exp(ci[0]), "or_ic95_sup": np.exp(ci[1]), "p_valor": logit.pvalues})
tab = tab[~tab.index.str.startswith("C(mes)")]
tab.index = (tab.index.str.replace(r"C\(regiao, Treatment\('SP'\)\)\[T\.", "região: ", regex=True).str.replace("]", ""))
tab.round(4).to_csv(RES / "04_regressao_logistica_atraso.csv")
with open(RES / "04_regressao_logistica_resumo.txt", "w") as fh:
    fh.write(f"Pedidos no modelo: {int(logit.nobs)}\nPseudo R2 (McFadden): {logit.prsquared:.4f}\n"
             "Referência de região: SP. Controles: efeito fixo de mês (jan/2017 a ago/2018).\n"
             "log_km = log(1 + distância em km); postagem_d = dias da compra até a postagem (0 a 30); log_peso = log(1 + peso em g).\n\n")
    fh.write(str(logit.summary()))

# efeito prático da distância e da postagem (mantendo o resto na média): probabilidade prevista
def prob(**kw):
    base = m.copy()
    for k, v in kw.items():
        base[k] = v
    return logit.predict(base).mean() * 100
efeitos = pd.DataFrame([
    {"cenario": "distância de 100 km", "pct_atraso_previsto": prob(log_km=np.log1p(100))},
    {"cenario": "distância de 500 km", "pct_atraso_previsto": prob(log_km=np.log1p(500))},
    {"cenario": "distância de 2.000 km", "pct_atraso_previsto": prob(log_km=np.log1p(2000))},
    {"cenario": "postagem em 1 dia", "pct_atraso_previsto": prob(postagem_d=1)},
    {"cenario": "postagem em 3 dias", "pct_atraso_previsto": prob(postagem_d=3)},
    {"cenario": "postagem em 7 dias", "pct_atraso_previsto": prob(postagem_d=7)},
])
efeitos.round(2).to_csv(RES / "04_efeitos_previstos.csv", index=False)

# ---- 2. transporte acima do esperado pela distância
t = df.dropna(subset=["log_km"]).copy()
t = t[t["dias_transporte"] > 0]
ols = smf.ols("np.log(dias_transporte) ~ log_km", data=t).fit()
t["esperado"] = np.exp(ols.fittedvalues)
t["razao"] = t["dias_transporte"] / t["esperado"]
exc = (t.groupby("uf_cliente").agg(pedidos=("razao", "size"), mediana_km=("distancia_km", "median"),
                                   transporte_mediana=("dias_transporte", "median"), esperado_mediana=("esperado", "median"),
                                   razao_mediana=("razao", "median")).reset_index())
exc["pct_acima_do_esperado"] = 100 * (exc["razao_mediana"] - 1)
exc = exc[exc["pedidos"] >= 300].sort_values("pct_acima_do_esperado", ascending=False)
exc.round(3).to_csv(RES / "04_transporte_vs_esperado_por_uf.csv", index=False)

# ---- 3. nota: atraso x no prazo
av = df.dropna(subset=["nota"]).copy()
a, b = av.loc[av.atrasou == 1, "nota"], av.loc[av.atrasou == 0, "nota"]
u = mannwhitneyu(a, b, alternative="two-sided")
diff = a.mean() - b.mean()
se = np.sqrt(a.var() / len(a) + b.var() / len(b))
av["log_km"] = np.log1p(av["distancia_km"])
av["dias_atraso_pos"] = av["dias_atraso"].clip(lower=0, upper=30)
ols_n = smf.ols("nota ~ dias_atraso_pos + I(dias_atraso_pos>0) + log_km + C(regiao) + C(mes)", data=av.dropna(subset=["log_km"])).fit(cov_type="HC1")
nota = pd.DataFrame([
    {"medida": "nota média - atrasados", "valor": a.mean()},
    {"medida": "nota média - no prazo", "valor": b.mean()},
    {"medida": "diferença (atrasados - no prazo)", "valor": diff},
    {"medida": "diferença IC95 inferior", "valor": diff - 1.96 * se},
    {"medida": "diferença IC95 superior", "valor": diff + 1.96 * se},
    {"medida": "Mann-Whitney p-valor", "valor": u.pvalue},
    {"medida": "regressão: queda na nota por atrasar (salto)", "valor": ols_n.params["I(dias_atraso_pos > 0)[T.True]"]},
    {"medida": "regressão: queda adicional por dia de atraso", "valor": ols_n.params["dias_atraso_pos"]},
])
nota.to_csv(RES / "04_impacto_nota.csv", index=False)

# ---- 4. vendedores
tx = df["atrasou"].mean()
z = norm.ppf(0.975)
v = df.groupby("vendedor_id").agg(pedidos=("atrasou", "size"), atrasados=("atrasou", "sum"),
                                  postagem_mediana=("dias_ate_postagem", "median")).reset_index()
v = v[v["pedidos"] >= 50].copy()
p = v["atrasados"] / v["pedidos"]; n = v["pedidos"]
den = 1 + z**2 / n
cen = (p + z**2 / (2 * n)) / den
h = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / den
v["pct_atraso"] = 100 * p; v["ic95_inf"] = 100 * (cen - h); v["ic95_sup"] = 100 * (cen + h)
v["acima_da_media"] = v["ic95_inf"] > 100 * tx
v = v.sort_values("pct_atraso", ascending=False)
v.round(2).to_csv(RES / "04_vendedores.csv", index=False)
crit = v[v["acima_da_media"]]
vend = pd.DataFrame([
    {"medida": "vendedores com 50+ pedidos", "valor": len(v)},
    {"medida": "vendedores com atraso estatisticamente acima da média", "valor": len(crit)},
    {"medida": "% dos pedidos (base total) desses vendedores", "valor": 100 * crit["pedidos"].sum() / len(df)},
    {"medida": "% dos atrasos (base total) desses vendedores", "valor": 100 * crit["atrasados"].sum() / df["atrasou"].sum()},
    {"medida": "mediana de dias até postar - vendedores críticos", "valor": crit["postagem_mediana"].median()},
    {"medida": "mediana de dias até postar - demais vendedores 50+", "valor": v.loc[~v["acima_da_media"], "postagem_mediana"].median()},
])
vend.to_csv(RES / "04_vendedores_resumo.csv", index=False)

# ---- 5. picos mensais: o que mudou
pm = (df[df["mes"].between("2017-01", "2018-08")].groupby("mes")
      .agg(pedidos=("atrasou", "size"), pct_atraso=("atrasou", lambda s: 100 * s.mean()),
           prometido_mediana=("dias_prometidos", "median"), postagem_mediana=("dias_ate_postagem", "median"),
           transporte_mediana=("dias_transporte", "median"), total_mediana=("dias_total", "median")).reset_index())
pm.round(2).to_csv(RES / "04_picos_mensais_etapas.csv", index=False)

pd.set_option("display.width", 250)
print(open(RES / "04_regressao_logistica_resumo.txt").read()[:400])
print(tab.round(3).to_string())
print(efeitos.round(2).to_string(index=False))
print(exc.round(2).to_string(index=False))
print(nota.to_string(index=False))
print(vend.to_string(index=False))
print(pm.round(2).to_string(index=False))
