"""Etapa 10: prepara os dados do dashboard (dashboard/dados.js).

O dashboard roda no navegador, sem servidor. Por isso os dados vão agregados:
- um "cubo" por mês x UF do cliente x categoria (para os filtros funcionarem);
- um cubo de rotas (mês x UF do cliente x categoria x UF de origem);
- tabelas fixas das análises estatísticas (regressão, modelo, vendedores etc.).
Nenhum dado pessoal: só contagens, somas e identificadores anonimizados da própria Olist.
"""
import json
import numpy as np
import pandas as pd
from comum import RES, RAIZ, carregar_base

df = carregar_base()
df["mes"] = df["mes_compra"].dt.strftime("%Y-%m")
df = df[df["mes"].between("2017-01", "2018-08")].copy()
df["atrasou"] = df["atrasou"].astype(int)
CAT_PT = {"bed_bath_table": "Cama, mesa e banho", "health_beauty": "Beleza e saúde", "sports_leisure": "Esporte e lazer",
          "computers_accessories": "Informática", "furniture_decor": "Móveis e decoração", "housewares": "Utilidades domésticas",
          "watches_gifts": "Relógios e presentes", "telephony": "Telefonia", "auto": "Automotivo", "toys": "Brinquedos",
          "cool_stuff": "Presentes criativos", "garden_tools": "Jardinagem e ferramentas"}
df["cat"] = df["categoria"].map(CAT_PT).fillna("Outras categorias")
ORIG = ["SP", "MG", "PR", "RJ", "SC", "RS"]
df["orig"] = df["uf_vendedor"].where(df["uf_vendedor"].isin(ORIG), "Outras")
faixas = [-1e9, 0, 3, 7, 14, 1e9]
df["fx"] = pd.cut(df["dias_atraso"], bins=faixas, labels=False)  # 0 = no prazo ... 4 = mais de 14 dias
df["tem_nota"] = df["nota"].notna().astype(int)
df["baixa"] = (df["nota"] <= 2).astype(int)
df["nota0"] = df["nota"].fillna(0)
df["longo"] = (df["dias_atraso"] > 3).astype(int)

meses = sorted(df["mes"].unique()); ufs = sorted(df["uf_cliente"].unique()); cats = sorted(df["cat"].unique()); origs = ORIG + ["Outras"]
im, iu, ic, io = ({v: i for i, v in enumerate(x)} for x in (meses, ufs, cats, origs))

# cubo principal: [0 mes, 1 uf, 2 cat, 3 n, 4 atrasados, 5 longos, 6 soma_total, 7 soma_prom, 8 soma_post, 9 soma_trans,
#                  10 soma_frete, 11 soma_preco, 12 soma_itens, 13-17 n_f0..f4, 18-22 avaliados_f0..f4, 23-27 soma_nota_f0..f4, 28-32 baixa_f0..f4]
g = df.groupby(["mes", "uf_cliente", "cat"])
base = g.agg(n=("atrasou", "size"), a=("atrasou", "sum"), lg=("longo", "sum"), st=("dias_total", "sum"), sp=("dias_prometidos", "sum"),
             spo=("dias_ate_postagem", "sum"), str_=("dias_transporte", "sum"), sf=("valor_frete", "sum"), spr=("valor_produtos", "sum"), si=("qtd_itens", "sum"))
por_fx = df.groupby(["mes", "uf_cliente", "cat", "fx"]).agg(n=("atrasou", "size"), nn=("tem_nota", "sum"), sn=("nota0", "sum"), b=("baixa", "sum")).unstack("fx", fill_value=0)
cubo = []
for (m, u, c), r in base.iterrows():
    linha = [im[m], iu[u], ic[c], int(r.n), int(r.a), int(r.lg)] + [round(float(x), 1) for x in (r.st, r.sp, r.spo, r.str_, r.sf, r.spr)] + [int(r.si)]
    pf = por_fx.loc[(m, u, c)]
    for met in ("n", "nn", "sn", "b"):
        linha += [round(float(pf.get((met, k), 0)), 1) if met == "sn" else int(pf.get((met, k), 0)) for k in range(5)]
    cubo.append(linha)

# histogramas esparsos (faixas de 6 horas = 1/4 de dia; o JS divide por 4) para calcular mediana e P90 com filtros: {chave_celula: [[dia, qtd], ...]}
def histos(col, teto):
    h = df.assign(_d=np.floor(4 * df[col].clip(0, teto)).astype(int)).groupby(["mes", "uf_cliente", "cat", "_d"]).size()
    out = {}
    for (m, u, c, d), q in h.items():
        out.setdefault(f"{im[m]}|{iu[u]}|{ic[c]}", []).append([int(d), int(q)])
    return out
HIST = {"total": histos("dias_total", 90), "transporte": histos("dias_transporte", 90), "postagem": histos("dias_ate_postagem", 60)}

rotas = [[im[m], iu[u], ic[c], io[o], int(r.n), int(r.a)] for (m, u, c, o), r in
         df.groupby(["mes", "uf_cliente", "cat", "orig"]).agg(n=("atrasou", "size"), a=("atrasou", "sum")).iterrows()]


def tab(arquivo, **kw):
    t = pd.read_csv(RES / arquivo, **kw)
    return json.loads(t.to_json(orient="records", force_ascii=False))


# vendedores (50+ pedidos) com nota média
v = pd.read_csv(RES / "04_vendedores.csv")
notas_v = df.groupby("vendedor_id").agg(nota=("nota", "mean"), uf=("uf_vendedor", "first"))
v = v.merge(notas_v, left_on="vendedor_id", right_index=True, how="left")
v["id"] = v["vendedor_id"].str[:6]
vend = v[["id", "uf", "pedidos", "atrasados", "pct_atraso", "ic95_inf", "ic95_sup", "postagem_mediana", "nota", "acima_da_media"]].round(2)

# ranking de vendas por vendedor: faturamento dos itens de cada vendedor nos pedidos entregues da base
import duckdb
from comum import DADOS as PASTA_DADOS
itens = duckdb.sql(f"SELECT order_id, seller_id, price FROM read_csv_auto('{(PASTA_DADOS / 'olist_order_items_dataset.csv').as_posix()}')").df()
it = itens.merge(df[["order_id", "atrasou", "nota", "cat", "uf_vendedor"]], on="order_id", how="inner")
seller_uf = duckdb.sql(f"SELECT seller_id, seller_state FROM read_csv_auto('{(PASTA_DADOS / 'olist_sellers_dataset.csv').as_posix()}')").df().set_index("seller_id")["seller_state"]
por_pedido = it.groupby(["seller_id", "order_id"]).agg(receita=("price", "sum"), itens=("price", "size"), atrasou=("atrasou", "first"), nota=("nota", "first"), cat=("cat", "first")).reset_index()
rv = por_pedido.groupby("seller_id").agg(receita=("receita", "sum"), pedidos=("order_id", "nunique"), itens=("itens", "sum"),
                                         pct_atraso=("atrasou", lambda s: 100 * s.mean()), nota=("nota", "mean"),
                                         cat=("cat", lambda s: s.value_counts().index[0])).reset_index()
rv["ticket"] = rv["receita"] / rv["pedidos"]
rv["uf"] = rv["seller_id"].map(seller_uf)
rv["id"] = rv["seller_id"].str[:6]
rv["participacao"] = 100 * rv["receita"] / rv["receita"].sum()
rv = rv.sort_values("receita", ascending=False).reset_index(drop=True)
rv["posicao"] = np.arange(1, len(rv) + 1)
resumo_vendas = {
    "vendedores_total": int(len(rv)), "receita_total": float(rv["receita"].sum()),
    "top10_participacao": float(rv.head(10)["participacao"].sum()),
    "top20pct_participacao": float(rv.head(int(np.ceil(0.2 * len(rv))))["participacao"].sum()),
    "vendedores_10mais": int((rv["pedidos"] >= 10).sum()),
}
rv[["posicao", "seller_id", "uf", "cat", "receita", "pedidos", "itens", "ticket", "participacao", "pct_atraso", "nota"]].round(2).to_csv(RES / "10_ranking_vendedores_receita.csv", index=False)
ranking_vend = json.loads(rv[rv["pedidos"] >= 10][["posicao", "id", "uf", "cat", "receita", "pedidos", "ticket", "participacao", "pct_atraso", "nota"]].round(2).to_json(orient="records", force_ascii=False))

ger = pd.read_csv(RES / "03_indicadores_gerais.csv", index_col=0)["valor"]
# ---- perguntas do gerente: respostas calculadas a partir dos resultados (nada digitado à mão)
br = lambda x, d=1: f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
base_full = carregar_base(); base_full["atrasou"] = base_full["atrasou"].astype(int)
tot_atr = int(base_full["atrasou"].sum())
rota = base_full[(base_full.uf_vendedor == "SP") & (base_full.uf_cliente == "RJ")]
r_atr = int(rota["atrasou"].sum())
et = pd.read_csv(RES / "03_etapas_prazo_vs_atraso.csv").set_index("grupo")
vr = pd.read_csv(RES / "04_vendedores_resumo.csv").set_index("medida")["valor"]
crit = v[v["acima_da_media"]].sort_values("atrasados", ascending=False).head(3)
nb = pd.read_csv(RES / "09_notas_baixas_por_atraso.csv").set_index("medida")["valor"]
imp = pd.read_csv(RES / "04_impacto_nota.csv").set_index("medida")["valor"]
pp = pd.read_csv(RES / "09_promessa_vs_p90_por_uf.csv")
abaixo = pp[pp["diferenca_promessa_menos_sugerido"] < 0]["uf_cliente"].tolist()
sp = pp.set_index("uf_cliente").loc["SP"]
pk = pd.read_csv(RES / "04_picos_mensais_etapas.csv").set_index("mes")
fx = pd.read_csv(RES / "09_faixas_risco_modelo.csv").set_index("faixa")
cen = pd.read_csv(RES / "03_cenarios.csv")
top1 = rv.iloc[0]
top1_crit = top1["seller_id"] in set(v.loc[v["acima_da_media"], "vendedor_id"])
perguntas = [
    {"p": "Qual é a nossa taxa de entrega no prazo?", "r": f"{br(100 - ger['pct_atraso'])}% dos pedidos chegam até o dia prometido. Os outros {br(ger['pct_atraso'])}% atrasam ({br(ger['atrasados'], 0)} pedidos).", "aba": "geral"},
    {"p": "Qual rota mais gera atraso?", "r": f"SP → RJ: {br(len(rota), 0)} pedidos, {br(100 * rota['atrasou'].mean())}% atrasados. Sozinha, responde por {br(100 * r_atr / tot_atr)}% de todos os atrasos ({br(r_atr, 0)}).", "aba": "rotas"},
    {"p": "Em que etapa perdemos mais tempo?", "r": f"No transporte. Pedidos atrasados ficaram em média {br(et.loc['Atrasou', 'transporte_media'])} dias com a transportadora, contra {br(et.loc['No prazo', 'transporte_media'])} nos pedidos no prazo. Até a postagem: {br(et.loc['Atrasou', 'ate_postagem_media'])} contra {br(et.loc['No prazo', 'ate_postagem_media'])} dias.", "aba": "prazo"},
    {"p": "Quais vendedores devo cobrar primeiro?", "r": f"{int(vr.iloc[1])} vendedores atrasam acima da média com 95% de confiança ({br(vr.iloc[3])}% dos atrasos). Começar por " + ", ".join(f"{r.vendedor_id[:6]} ({int(r.atrasados)} atrasos)" for r in crit.itertuples()) + ".", "aba": "vendedores"},
    {"p": "Quanto o atraso custa em satisfação?", "r": f"A nota cai {br(-imp.iloc[2], 2)} pontos em média. Cerca de {br(nb.iloc[3], 0)} notas 1 ou 2 a mais estão associadas ao atraso: {br(nb.iloc[5])}% de todas as avaliações negativas.", "aba": "satisfacao"},
    {"p": "A promessa de prazo está correta?", "r": f"Em {len(abaixo)} UFs ({', '.join(abaixo)}) o prazo prometido fica abaixo do prazo em que 90% dos pedidos chegam (P90): risco de atraso. Em SP dá para prometer menos: {br(sp['prometido_mediana'])} dias hoje contra um P90 real de {br(sp['real_p90'])}.", "aba": "rotas"},
    {"p": "O que aconteceu na Black Friday de 2017?", "r": f"O atraso foi a {br(pk.loc['2017-11', 'pct_atraso'])}%. A postagem subiu para {br(pk.loc['2017-11', 'postagem_mediana'])} dias e o transporte para {br(pk.loc['2017-11', 'transporte_mediana'])} (medianas), contra {br(pk.loc['2017-10', 'postagem_mediana'])} e {br(pk.loc['2017-10', 'transporte_mediana'])} em outubro.", "aba": "geral"},
    {"p": "Dá para prever quais pedidos vão atrasar?", "r": f"Sim. Os 10% de pedidos com maior risco concentram {br(fx.loc['Alto (10% maiores)', 'pct_dos_atrasos'])}% dos atrasos: {br(fx.loc['Alto (10% maiores)', 'pct_atraso_real'])}% deles atrasam, contra {br(fx.loc['Baixo (70% restantes)', 'pct_atraso_real'])}% na faixa de risco baixo.", "aba": "risco"},
    {"p": "Quem vende mais? E isso tem relação com atraso?", "r": f"O maior vendedor ({top1['id']}, {top1['uf']}) faturou R$ {br(top1['receita'], 0)} ({br(top1['participacao'], 2)}% do total)" + (f" e está entre os vendedores críticos, com {br(top1['pct_atraso'])}% de atraso: crescer sem logística aumenta o risco." if top1_crit else ".") + f" Os 10 maiores somam {br(resumo_vendas['top10_participacao'])}% do faturamento.", "aba": "vendas"},
    {"p": "Quanto melhora se atacarmos as UFs de maior atraso?", "r": f"Se AL, MA, PI, CE, SE, BA, RJ, PA e ES tivessem o atraso das demais UFs, seriam {br(cen.iloc[0]['pedidos_atrasados_evitados'], 0)} atrasos a menos ({br(cen.iloc[0]['pct_do_total_de_atrasos'])}% do total). Os atrasos longos (mais de 3 dias) são {br(cen.iloc[1]['pct_do_total_de_atrasos'])}% dos atrasos.", "aba": "rotas"},
]
pd.DataFrame(perguntas).to_csv(RES / "10_perguntas_do_gerente.csv", index=False)

DADOS = {
    "dims": {"meses": meses, "ufs": ufs, "cats": cats, "origs": origs},
    "cubo": cubo, "rotas": rotas, "hist": HIST,
    "geral": {k: float(v) for k, v in ger.items()},
    "regressao": tab("04_regressao_logistica_atraso.csv"),
    "efeitos": tab("04_efeitos_previstos.csv"),
    "transporte_esperado": tab("04_transporte_vs_esperado_por_uf.csv"),
    "promessa_p90": tab("09_promessa_vs_p90_por_uf.csv"),
    "top_rotas": tab("09_rotas_uf_500mais.csv"),
    "percentis": tab("09_percentis_prazo.csv"),
    "distancia": tab("03_atraso_por_distancia.csv"),
    "dia_semana": tab("09_dia_semana.csv"),
    "etapas": tab("03_etapas_prazo_vs_atraso.csv"),
    "vendedores": json.loads(vend.to_json(orient="records", force_ascii=False)),
    "vendedores_resumo": tab("04_vendedores_resumo.csv"),
    "pareto": tab("09_pareto_vendedores.csv"),
    "pareto_curva": tab("09_pareto_curva.csv"),
    "notas_baixas": tab("09_notas_baixas_por_atraso.csv"),
    "impacto_nota": tab("04_impacto_nota.csv"),
    "faixas_risco": tab("09_faixas_risco_modelo.csv"),
    "modelo": tab("05_modelo_metricas.csv"),
    "curva_captura": tab("05_curva_captura.csv"),
    "importancia": tab("05_importancia_variaveis.csv"),
    "auditoria": tab("01_auditoria_qualidade.csv"),
    "cenarios": tab("03_cenarios.csv"),
    "picos": tab("04_picos_mensais_etapas.csv"),
    "ranking_vendedores": ranking_vend, "resumo_vendas": resumo_vendas, "perguntas": perguntas,
}
destino = RAIZ / "dashboard"
destino.mkdir(exist_ok=True)
txt = "window.DADOS = " + json.dumps(DADOS, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + ";\n"
(destino / "dados.js").write_text(txt, encoding="utf-8")
print(f"dashboard/dados.js: {len(txt)/1024:.0f} KB · cubo {len(cubo)} linhas · rotas {len(rotas)} linhas · pedidos no cubo {sum(r[3] for r in cubo)}")
