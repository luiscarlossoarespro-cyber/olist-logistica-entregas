"""Gera os gráficos (PNG) e o painel interativo (HTML) a partir de resultados/*.csv"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

RAIZ = Path(__file__).parent
RES, GRAF = RAIZ / "resultados", RAIZ / "graficos"
GRAF.mkdir(exist_ok=True)

AZUL, VERMELHO, CINZA, VERDE = "#2F5D8C", "#C8453B", "#B8BEC6", "#4C8C6B"
plt.rcParams.update({
    "figure.figsize": (11, 6), "figure.dpi": 110, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.alpha": .25,
    "axes.axisbelow": True, "font.size": 11, "axes.titleweight": "bold",
    "axes.titlesize": 14, "axes.titlelocation": "left",
})
FONTE = "Fonte: Olist Brazilian E-Commerce Public Dataset (Kaggle), pedidos entregues 2016–2018"


def rodape(fig):
    fig.text(0.01, 0.01, FONTE, fontsize=8, color="#666")


geral = pd.read_csv(RES / "02_indicadores_gerais.csv").iloc[0]
mes = pd.read_csv(RES / "03_atraso_por_mes.csv")
est = pd.read_csv(RES / "04_atraso_por_estado.csv").sort_values("pct_atraso")
etapa = pd.read_csv(RES / "05_gargalo_por_etapa.csv")
nota = pd.read_csv(RES / "06_impacto_na_nota.csv")
vend = pd.read_csv(RES / "08_vendedores.csv").sort_values("itens_atrasados", ascending=False)

# 1) Atraso por mês
fig, ax = plt.subplots()
ax.plot(mes["mes"], mes["pct_atraso"], color=AZUL, lw=2.5, marker="o")
for m in ("2017-11", "2018-02", "2018-03"):
    v = float(mes.loc[mes.mes == m, "pct_atraso"].iloc[0])
    ax.scatter([m], [v], color=VERMELHO, zorder=5, s=70)
    ax.annotate(f"{v:.1f}%".replace(".", ","), (m, v), textcoords="offset points", xytext=(0, 9), ha="center", color=VERMELHO, fontweight="bold")
ax.set_title("O atraso não é constante: explode em nov/2017 e em fev–mar/2018")
ax.set_ylabel("% de pedidos entregues com atraso")
ax.set_xticks(range(len(mes))); ax.set_xticklabels(mes["mes"], rotation=60)
rodape(fig); fig.tight_layout(rect=(0, .03, 1, 1)); fig.savefig(GRAF / "01_atraso_por_mes.png"); plt.close(fig)

# 2) Atraso por estado
fig, ax = plt.subplots(figsize=(11, 7))
cores = [VERMELHO if v >= 12 else AZUL for v in est.pct_atraso]
ax.barh(est.estado, est.pct_atraso, color=cores)
media = geral.pct_atraso
ax.axvline(media, color="#333", ls="--", lw=1)
ax.text(media + .3, 0.2, f"média nacional {media:.1f}%".replace(".", ","), fontsize=9)
for y, v in enumerate(est.pct_atraso):
    ax.text(v + .25, y, f"{v:.1f}%".replace(".", ","), va="center", fontsize=9)
ax.set_title("Estados do Nordeste e o RJ lideram os atrasos; PR, MG e SP têm os menores")
ax.set_xlabel("% de pedidos com atraso (estados com 300+ pedidos)")
ax.grid(axis="y", visible=False)
rodape(fig); fig.tight_layout(rect=(0, .03, 1, 1)); fig.savefig(GRAF / "02_atraso_por_estado.png"); plt.close(fig)

# 3) Gargalo por etapa
fig, ax = plt.subplots(figsize=(11, 5.5))
cols = [("dias_aprovacao", "Aprovação do pagamento", CINZA),
        ("dias_vendedor_ate_postar", "Vendedor (até postar)", AZUL),
        ("dias_transportadora", "Transportadora", VERMELHO)]
base = [0, 0]
for col, nome, cor in cols:
    vals = etapa[col].tolist()
    ax.barh(etapa.grupo, vals, left=base, color=cor, label=nome)
    for i, v in enumerate(vals):
        if v >= 1.5:
            ax.text(base[i] + v / 2, i, f"{v:.1f}".replace(".", ","), ha="center", va="center", color="white", fontweight="bold")
    base = [b + v for b, v in zip(base, vals)]
ax.set_title("Pedidos atrasados ficam mais de 3x mais tempo com a transportadora")
ax.set_xlabel("Dias médios por etapa"); ax.legend(loc="lower right"); ax.grid(axis="y", visible=False)
rodape(fig); fig.tight_layout(rect=(0, .03, 1, 1)); fig.savefig(GRAF / "03_gargalo_por_etapa.png"); plt.close(fig)

# 4) Nota por faixa de atraso
fig, ax = plt.subplots()
rot = [f.split(". ", 1)[1] for f in nota.faixa]
cores = [VERDE] + [VERMELHO] * (len(nota) - 1)
ax.bar(rot, nota.nota_media, color=cores)
for i, (v, p) in enumerate(zip(nota.nota_media, nota.pct_notas_1_ou_2)):
    ax.text(i, v + .05, f"{v:.2f}".replace(".", ","), ha="center", fontweight="bold")
    ax.text(i, v / 2, f"{p:.0f}%\nnotas 1–2".replace(".", ","), ha="center", color="white", fontsize=9)
ax.set_ylim(0, 5); ax.set_ylabel("Nota média do cliente (1 a 5)")
ax.set_title("Com mais de 3 dias de atraso, a nota cai de 4,3 para 2,3 ou menos")
ax.set_xticks(range(len(rot))); ax.set_xticklabels([r.replace(" de ", "\nde ", 1) if "Atraso" in r else r for r in rot], fontsize=9)
rodape(fig); fig.tight_layout(rect=(0, .03, 1, 1)); fig.savefig(GRAF / "04_impacto_na_nota.png"); plt.close(fig)

# 5) Concentração de atrasos entre vendedores
v = vend.reset_index(drop=True)
x = (v.index + 1) / len(v) * 100
y_atr = v.itens_atrasados.cumsum() / v.itens_atrasados.sum() * 100
y_vol = v.itens.cumsum() / v.itens.sum() * 100
fig, ax = plt.subplots()
ax.plot(x, y_atr, color=VERMELHO, lw=2.5, label="% acumulado dos itens atrasados")
ax.plot(x, y_vol, color=AZUL, lw=2.5, label="% acumulado do volume de itens")
ax.plot([0, 100], [0, 100], color="#999", ls=":", label="distribuição igual")
k = int(len(v) * .2)
ax.annotate(f"20% dos vendedores:\n{y_atr[k-1]:.0f}% dos atrasos, {y_vol[k-1]:.0f}% do volume".replace(".", ","),
            (x[k-1], y_atr[k-1]), xytext=(35, 25), arrowprops=dict(arrowstyle="->"), fontsize=10)
ax.set_xlabel("% dos vendedores (ordenados do que mais atrasa em volume para o que menos)")
ax.set_ylabel("%"); ax.legend(loc="lower right")
ax.set_title("Poucos vendedores não explicam o atraso: o problema é espalhado")
rodape(fig); fig.tight_layout(rect=(0, .03, 1, 1)); fig.savefig(GRAF / "05_concentracao_vendedores.png"); plt.close(fig)

# ---------- Painel interativo (HTML) ----------
fig = make_subplots(
    rows=3, cols=2, vertical_spacing=.12, horizontal_spacing=.1,
    subplot_titles=("% de atraso por mês", "% de atraso por estado", "Dias por etapa: no prazo x atrasou",
                    "Nota média por faixa de atraso", "Concentração entre vendedores", ""),
    specs=[[{}, {}], [{}, {}], [{}, {"type": "table"}]])
fig.add_trace(go.Scatter(x=mes.mes, y=mes.pct_atraso, mode="lines+markers", line=dict(color=AZUL, width=3), name="% atraso",
                         hovertemplate="%{x}: %{y:.1f}%<extra></extra>"), 1, 1)
fig.add_trace(go.Bar(y=est.estado, x=est.pct_atraso, orientation="h", marker_color=[VERMELHO if v >= 12 else AZUL for v in est.pct_atraso],
                     name="% atraso", hovertemplate="%{y}: %{x:.1f}%<extra></extra>"), 1, 2)
for col, nome, cor in cols:
    fig.add_trace(go.Bar(y=etapa.grupo, x=etapa[col], orientation="h", name=nome, marker_color=cor,
                         hovertemplate=nome + ": %{x:.1f} dias<extra></extra>"), 2, 1)
fig.update_layout(barmode="stack")
fig.add_trace(go.Bar(x=rot, y=nota.nota_media, marker_color=[VERDE] + [VERMELHO] * (len(nota) - 1), name="nota",
                     hovertemplate="%{x}: %{y:.2f}<extra></extra>"), 2, 2)
fig.add_trace(go.Scatter(x=x, y=y_atr, name="% dos atrasos", line=dict(color=VERMELHO, width=3)), 3, 1)
fig.add_trace(go.Scatter(x=x, y=y_vol, name="% do volume", line=dict(color=AZUL, width=3)), 3, 1)
fig.add_trace(go.Table(header=dict(values=["Indicador", "Valor"], fill_color=AZUL, font=dict(color="white")),
    cells=dict(values=[["Pedidos entregues", "% com atraso", "Prazo prometido (médio)", "Prazo real (médio)", "Folga média", "Nota média"],
                       [f"{int(geral.pedidos_entregues):,}".replace(",", "."), f"{geral.pct_atraso:.1f}%".replace(".", ","),
                        f"{geral.dias_prometidos_medio:.1f} dias".replace(".", ","), f"{geral.dias_total_medio:.1f} dias".replace(".", ","),
                        f"{geral.folga_media_dias:.1f} dias".replace(".", ","), f"{geral.nota_media:.2f}".replace(".", ",")]])), 3, 2)
fig.update_yaxes(dtick=1, row=1, col=2)
fig.update_xaxes(title_text="% de pedidos com atraso", row=1, col=2)
fig.update_yaxes(title_text="% de pedidos com atraso", row=1, col=1)
fig.update_xaxes(title_text="dias", row=2, col=1)
fig.update_yaxes(title_text="nota média (1 a 5)", row=2, col=2)
fig.update_xaxes(title_text="% dos vendedores (vermelho: atrasos | azul: volume)", row=3, col=1)
fig.update_yaxes(title_text="% acumulado", row=3, col=1)
fig.update_layout(title="Olist: desempenho de entregas no e-commerce brasileiro (2016–2018)", height=1150, template="plotly_white",
                  showlegend=False, font=dict(size=13),
                  annotations=list(fig.layout.annotations) + [dict(text=FONTE, x=0, y=-0.05, xref="paper", yref="paper", showarrow=False, xanchor="left", font=dict(size=10, color="#666"))])
fig.write_html(RAIZ / "painel.html", include_plotlyjs="cdn", full_html=True)
print("ok")
