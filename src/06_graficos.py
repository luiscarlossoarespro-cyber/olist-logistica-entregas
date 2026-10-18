"""Etapa 6: gráficos estáticos (PNG, para o README) a partir de resultados/."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, MultipleLocator
from comum import RES, GRAF

AZUL, LARANJA, CINZA = "#2a78d6", "#eb6834", "#b8b7b1"
TX1, TX2, GRID, BG = "#0b0b0b", "#52514e", "#e7e6e2", "#fcfcfb"
FONTE = "Fonte: Olist Brazilian E-Commerce Public Dataset (Kaggle). Pedidos entregues de 2016 a 2018."
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11, "axes.edgecolor": GRID, "axes.labelcolor": TX2,
    "xtick.color": TX2, "ytick.color": TX2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "figure.facecolor": BG, "axes.facecolor": BG,
    "savefig.facecolor": BG, "axes.titleweight": "bold", "axes.titlesize": 14, "axes.titlecolor": TX1,
})
pct = FuncFormatter(lambda v, _: f"{v:.0f}%".replace(".", ","))
br = lambda v, d=1: f"{v:.{d}f}".replace(".", ",")


def salvar(fig, nome, sub=None):
    if sub:
        ax0 = fig.axes[0]
        ax0.text(0, 1.025, sub, transform=ax0.transAxes, color=TX2, fontsize=10, ha="left", va="bottom")
    fig.text(0.01, -0.035, FONTE, color=TX2, fontsize=8.5, ha="left")
    fig.savefig(GRAF / nome, dpi=160, bbox_inches="tight")
    plt.close(fig)


ger = pd.read_csv(RES / "03_indicadores_gerais.csv", index_col=0)["valor"]
MEDIA = float(ger["pct_atraso"])

# 01 — atraso por mês com intervalo de confiança
m = pd.read_csv(RES / "03_atraso_por_mes.csv")
fig, ax = plt.subplots(figsize=(11, 5))
x = range(len(m))
ax.fill_between(x, m["ic95_inf"], m["ic95_sup"], color=AZUL, alpha=0.15, linewidth=0, label="intervalo de confiança 95%")
ax.plot(x, m["pct_atraso"], color=AZUL, lw=2, marker="o", ms=4, label="% de pedidos atrasados")
ax.axhline(MEDIA, color=TX2, lw=1, ls="--")
ax.text(len(m) - 0.5, MEDIA + 0.4, f"média {br(MEDIA)}%", color=TX2, ha="right", fontsize=9.5)
for mes, rot in [("2017-11", "nov/17 (Black Friday)"), ("2018-03", "mar/18")]:
    i = m.index[m["mes"] == mes][0]
    ax.annotate(f"{rot}: {br(m.loc[i, 'pct_atraso'])}%", (i, m.loc[i, "pct_atraso"]), xytext=(-10, 10),
                textcoords="offset points", ha="right", color=TX1, fontsize=10, fontweight="bold")
ax.set_xticks(list(x)[::2], [f"{s[5:]}/{s[2:4]}" for s in m["mes"]][::2])
ax.yaxis.set_major_formatter(pct); ax.yaxis.set_major_locator(MultipleLocator(5)); ax.set_ylim(0, 22)
ax.set_title("O atraso tem picos: Black Friday de 2017 e fevereiro a março de 2018", loc="left", pad=34)
ax.legend(loc="upper left", frameon=False, fontsize=9.5)
salvar(fig, "01_atraso_por_mes.png", "% de pedidos entregues depois do dia prometido, por mês da compra (meses com 500+ pedidos)")

# 02 — atraso por UF com IC
e = pd.read_csv(RES / "03_atraso_por_uf.csv").sort_values("pct_atraso")
fig, ax = plt.subplots(figsize=(10, 7.5))
cor = [LARANJA if lo > MEDIA else AZUL for lo in e["ic95_inf"]]
ax.barh(e["uf_cliente"], e["pct_atraso"], color=cor, height=0.66)
ax.errorbar(e["pct_atraso"], e["uf_cliente"], xerr=[e["pct_atraso"] - e["ic95_inf"], e["ic95_sup"] - e["pct_atraso"]],
            fmt="none", ecolor=TX2, elinewidth=1, capsize=2)
for _, r in e.iterrows():
    ax.text(r["ic95_sup"] + 0.4, r["uf_cliente"], f"{br(r['pct_atraso'])}%", va="center", fontsize=9, color=TX1)
ax.axvline(MEDIA, color=TX2, lw=1, ls="--"); ax.text(MEDIA + 0.2, -0.9, f"média {br(MEDIA)}%", color=TX2, fontsize=9)
ax.xaxis.set_major_formatter(pct); ax.grid(axis="y", visible=False)
ax.set_title("Nordeste e Rio de Janeiro ficam acima da média, mesmo com a margem de erro", loc="left", pad=34)
salvar(fig, "02_atraso_por_uf.png", "% de atraso por UF do cliente (UFs com 300+ pedidos). Laranja: intervalo de 95% inteiro acima da média")

# 03 — razão de chances por região (forest plot)
lg = pd.read_csv(RES / "04_regressao_logistica_atraso.csv", index_col=0)
rg = lg[lg.index.str.startswith("região")].copy()
rg.index = rg.index.str.replace("região: ", "")
rg = rg.sort_values("odds_ratio")
fig, ax = plt.subplots(figsize=(10, 5))
y = range(len(rg))
ax.hlines(y, rg["or_ic95_inf"], rg["or_ic95_sup"], color=TX2, lw=1.5)
ax.scatter(rg["odds_ratio"], y, s=70, color=[LARANJA if v >= 2 else AZUL for v in rg["odds_ratio"]], zorder=3)
for i, (_, r) in enumerate(rg.iterrows()):
    ax.text(r["or_ic95_sup"] + 0.05, i, f"{br(r['odds_ratio'], 2)}x", va="center", fontsize=10, color=TX1)
ax.axvline(1, color=TX2, lw=1, ls="--")
ax.set_yticks(list(y), rg.index); ax.grid(axis="y", visible=False); ax.set_xlim(0.8, 3.7)
ax.set_xlabel("chance de atraso em relação a SP (razão de chances; linha tracejada = SP = 1)")
ax.set_title("Mesmo com distância, peso, tempo de postagem e mês iguais, RJ e Nordeste\natrasam cerca de 3 vezes mais que SP", loc="left", pad=34)
salvar(fig, "03_chance_atraso_por_regiao.png", "Regressão logística com 95.668 pedidos. Linhas: intervalo de confiança de 95%")

# 04 — transporte acima do esperado
t = pd.read_csv(RES / "04_transporte_vs_esperado_por_uf.csv").sort_values("pct_acima_do_esperado")
fig, ax = plt.subplots(figsize=(10, 7.5))
ax.barh(t["uf_cliente"], t["pct_acima_do_esperado"], color=[LARANJA if v > 0 else AZUL for v in t["pct_acima_do_esperado"]], height=0.66)
for _, r in t.iterrows():
    v = r["pct_acima_do_esperado"]
    ax.text(v + (0.8 if v >= 0 else -0.8), r["uf_cliente"], f"{'+' if v > 0 else ''}{br(v, 0)}%", va="center",
            ha="left" if v >= 0 else "right", fontsize=9, color=TX1)
ax.axvline(0, color=TX2, lw=1); ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:+.0f}%")); ax.grid(axis="y", visible=False)
ax.set_xlim(-25, 45)
ax.set_title("Transporte mais lento do que a distância explica: AL, PA, SC e RJ", loc="left", pad=34)
salvar(fig, "04_transporte_vs_esperado.png", "Tempo real de transporte comparado ao esperado para a mesma distância (mediana por UF, 300+ pedidos)")

# 05 — alavancas: postagem e distância (probabilidade prevista)
ef = pd.read_csv(RES / "04_efeitos_previstos.csv")
fig, axs = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
for ax, chave, tit in [(axs[0], "postagem", "Dias da compra até a postagem"), (axs[1], "distância", "Distância vendedor-cliente")]:
    s = ef[ef["cenario"].str.startswith(chave)]
    rot = s["cenario"].str.replace("postagem em ", "").str.replace("distância de ", "")
    ax.bar(rot, s["pct_atraso_previsto"], color=AZUL if chave == "distância" else LARANJA, width=0.55)
    for i, v in enumerate(s["pct_atraso_previsto"]):
        ax.text(i, v + 0.25, f"{br(v)}%", ha="center", fontsize=11, color=TX1, fontweight="bold")
    ax.set_title(tit, fontsize=12, loc="left"); ax.grid(axis="x", visible=False)
axs[0].yaxis.set_major_formatter(pct); axs[0].yaxis.set_major_locator(MultipleLocator(2)); axs[0].set_ylim(0, 12)
fig.suptitle("Postar mais rápido reduz o atraso muito mais do que estar perto do cliente", x=0.01, ha="left", fontweight="bold", fontsize=14, y=1.06)
salvar(fig, "05_alavancas_postagem_distancia.png", None)
fig = None

# 06 — nota por faixa de atraso
nf = pd.read_csv(RES / "03_nota_por_faixa_atraso.csv")
fig, ax = plt.subplots(figsize=(10.5, 5))
rot = ["No prazo", "1 a 3 dias", "4 a 7 dias", "8 a 14 dias", "+ de 14 dias"]
ax.bar(rot, nf["nota_media"], color=[AZUL] + [LARANJA] * 4, width=0.6)
for i, r in nf.iterrows():
    ax.text(i, r["nota_media"] + 0.08, br(r["nota_media"], 2), ha="center", fontsize=12, fontweight="bold", color=TX1)
    ax.text(i, 0.15, f"{br(r['pct_notas_1_ou_2'], 0)}% deram\nnota 1 ou 2", ha="center", fontsize=9, color="white")
ax.set_ylim(0, 5); ax.grid(axis="x", visible=False); ax.set_ylabel("nota média (1 a 5)")
ax.set_title("A partir de 4 dias de atraso, a maioria dos clientes dá nota 1 ou 2", loc="left", pad=34)
salvar(fig, "06_nota_por_atraso.png", "Nota média da avaliação por faixa de atraso (95.786 pedidos avaliados)")

# 07 — vendedores críticos
vr = pd.read_csv(RES / "04_vendedores_resumo.csv").set_index("medida")["valor"]
ped, atr = vr["% dos pedidos (base total) desses vendedores"], vr["% dos atrasos (base total) desses vendedores"]
fig, ax = plt.subplots(figsize=(10, 3.8))
ax.barh(["% dos atrasos", "% dos pedidos"], [atr, ped], color=[LARANJA, AZUL], height=0.55)
for i, v in enumerate([atr, ped]):
    ax.text(v + 0.5, i, f"{br(v)}%", va="center", fontsize=12, fontweight="bold", color=TX1)
ax.xaxis.set_major_formatter(pct); ax.set_xlim(0, 35); ax.grid(axis="y", visible=False)
ax.set_title(f"{int(vr['vendedores com atraso estatisticamente acima da média'])} vendedores concentram quase o dobro de atrasos que de pedidos", loc="left", pad=34)
salvar(fig, "07_vendedores_criticos.png",
       f"Vendedores com 50+ pedidos e atraso acima da média com 95% de confiança. Postam em {br(vr['mediana de dias até postar - vendedores críticos'])} dias (mediana) contra {br(vr['mediana de dias até postar - demais vendedores 50+'])} dos demais")

# 08 — curva de captura do modelo
cc = pd.read_csv(RES / "05_curva_captura.csv")
met = pd.read_csv(RES / "05_modelo_metricas.csv")
gb = met[met["modelo"] == "Gradient boosting"].iloc[0]
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.plot(cc["pct_pedidos_monitorados"], cc["pct_atrasos_capturados"], color=LARANJA, lw=2.2, label="modelo (gradient boosting)")
ax.plot([0, 100], [0, 100], color=CINZA, lw=1.5, ls="--", label="sem modelo (aleatório)")
ax.scatter([10], [gb["top10_pct_dos_atrasos_capturados"]], color=LARANJA, s=60, zorder=3)
ax.annotate(f"monitorando 10% dos pedidos,\ncaptura {br(gb['top10_pct_dos_atrasos_capturados'])}% dos atrasos",
            (10, gb["top10_pct_dos_atrasos_capturados"]), xytext=(18, 28), textcoords="offset points", fontsize=10.5, color=TX1)
ax.xaxis.set_major_formatter(pct); ax.yaxis.set_major_formatter(pct)
ax.set_xlabel("% dos pedidos monitorados (os de maior risco primeiro)"); ax.set_ylabel("% dos atrasos capturados")
ax.legend(loc="lower right", frameon=False)
ax.set_title("Modelo de risco: atenção certa nos pedidos certos", loc="left", pad=34)
salvar(fig, "08_modelo_curva_captura.png", "Teste em pedidos de abr a ago/2018, que o modelo não viu no treino")
print(sorted(p.name for p in GRAF.glob("*.png")))
