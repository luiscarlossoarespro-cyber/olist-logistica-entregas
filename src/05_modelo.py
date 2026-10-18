"""Etapa 5: modelo de risco de atraso.

Uso de negócio: no momento em que o pedido é POSTADO, estimar a chance de ele atrasar,
para a operação priorizar acompanhamento (contato com transportadora, aviso ao cliente).

Só usamos informações conhecidas até a postagem (nada da entrega, para não "vazar" a resposta).
Validação temporal: treino com compras até mar/2018, teste com abr a ago/2018
(simula usar o modelo no futuro, como aconteceria de verdade).
"""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from comum import RES, carregar_base

df = carregar_base()
df["atrasou"] = df["atrasou"].astype(int)
df["mes"] = df["mes_compra"].dt.strftime("%Y-%m")
df = df[df["mes"].between("2017-01", "2018-08")].copy()
df["mes_do_ano"] = df["data_compra"].dt.month
df["log_km"] = np.log1p(df["distancia_km"])
df["log_peso"] = np.log1p(df["peso_g"])
df["log_volume"] = np.log1p(df["volume_cm3"])
df["log_frete"] = np.log1p(df["valor_frete"])
df["log_preco"] = np.log1p(df["valor_produtos"])
df["mesma_uf"] = df["mesma_uf"].astype(float)
df["prazo_restante_na_postagem"] = df["dias_prometidos"] - df["dias_ate_postagem"]
top_cat = df["categoria"].value_counts().index[:25]
df["categoria_m"] = df["categoria"].where(df["categoria"].isin(top_cat), "outras")

NUM = ["log_km", "log_peso", "log_volume", "log_frete", "log_preco", "qtd_itens", "mesma_uf",
       "dias_prometidos", "dias_ate_postagem", "prazo_restante_na_postagem", "mes_do_ano", "dia_semana"]
CAT = ["uf_cliente", "uf_vendedor", "categoria_m"]
X, y = df[NUM + CAT], df["atrasou"]
treino = df["mes"] <= "2018-03"
Xtr, Xte, ytr, yte = X[treino], X[~treino], y[treino], y[~treino]

prep_lin = ColumnTransformer([
    ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), NUM),
    ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=30), CAT)])
prep_arv = ColumnTransformer([
    ("num", SimpleImputer(strategy="median"), NUM),
    ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=30, sparse_output=False), CAT)])

modelos = {
    "Regressão logística": Pipeline([("prep", prep_lin), ("m", LogisticRegression(max_iter=2000, C=1.0))]),
    "Gradient boosting": Pipeline([("prep", prep_arv), ("m", HistGradientBoostingClassifier(
        max_iter=300, learning_rate=0.05, max_leaf_nodes=31, l2_regularization=1.0, random_state=42))]),
}


def topk(y_true, score, frac):
    k = int(len(score) * frac)
    idx = np.argsort(-score)[:k]
    capt = y_true.iloc[idx].sum() / y_true.sum()
    prec = y_true.iloc[idx].mean()
    return capt, prec


linhas, scores = [], {}
for nome, mod in modelos.items():
    mod.fit(Xtr, ytr)
    s = mod.predict_proba(Xte)[:, 1]
    scores[nome] = s
    c10, p10 = topk(yte, s, 0.10)
    c20, p20 = topk(yte, s, 0.20)
    linhas.append({"modelo": nome, "roc_auc": roc_auc_score(yte, s), "pr_auc": average_precision_score(yte, s),
                   "taxa_base_teste_pct": 100 * yte.mean(), "brier": brier_score_loss(yte, s),
                   "top10_pct_dos_atrasos_capturados": 100 * c10, "top10_precisao_pct": 100 * p10,
                   "top20_pct_dos_atrasos_capturados": 100 * c20, "top20_precisao_pct": 100 * p20})
met = pd.DataFrame(linhas)
met.loc[len(met)] = {"modelo": "Sem modelo (escolha aleatória)", "roc_auc": 0.5, "pr_auc": yte.mean(),
                     "taxa_base_teste_pct": 100 * yte.mean(), "brier": np.nan,
                     "top10_pct_dos_atrasos_capturados": 10.0, "top10_precisao_pct": 100 * yte.mean(),
                     "top20_pct_dos_atrasos_capturados": 20.0, "top20_precisao_pct": 100 * yte.mean()}
met.round(4).to_csv(RES / "05_modelo_metricas.csv", index=False)

# predições do melhor modelo no teste (para faixas de risco no dashboard)
melhor_tmp = met.iloc[:2].sort_values("pr_auc", ascending=False)["modelo"].iloc[0]
pd.DataFrame({"order_id": df.loc[~treino, "order_id"].values, "risco": scores[melhor_tmp], "atrasou": yte.values}).to_csv(
    RES.parent / "dados" / "derivados" / "predicoes_teste.csv", index=False)

# curva de captura (para gráfico): % dos atrasos capturados x % dos pedidos monitorados
melhor = met.iloc[:2].sort_values("pr_auc", ascending=False)["modelo"].iloc[0]
s = scores[melhor]
ordem = np.argsort(-s)
cum = yte.iloc[ordem].cumsum().values / yte.sum()
fr = np.arange(1, len(s) + 1) / len(s)
pts = np.linspace(0.01, 1, 100)
pd.DataFrame({"pct_pedidos_monitorados": 100 * pts,
              "pct_atrasos_capturados": 100 * np.interp(pts, fr, cum)}).round(2).to_csv(RES / "05_curva_captura.csv", index=False)

# importância por permutação (no teste), medida pela queda de PR-AUC
pi = permutation_importance(modelos[melhor], Xte, yte, scoring="average_precision", n_repeats=5, random_state=42, n_jobs=-1)
imp = pd.DataFrame({"variavel": X.columns, "queda_pr_auc": pi.importances_mean, "desvio": pi.importances_std}).sort_values("queda_pr_auc", ascending=False)
imp.round(4).to_csv(RES / "05_importancia_variaveis.csv", index=False)

with open(RES / "05_modelo_resumo.txt", "w") as fh:
    fh.write(f"Treino: compras jan/2017 a mar/2018 ({len(Xtr)} pedidos, {100*ytr.mean():.2f}% atrasados)\n")
    fh.write(f"Teste: compras abr a ago/2018 ({len(Xte)} pedidos, {100*yte.mean():.2f}% atrasados)\n")
    fh.write(f"Melhor modelo (PR-AUC no teste): {melhor}\n")
print(open(RES / "05_modelo_resumo.txt").read())
pd.set_option("display.width", 250)
print(met.round(3).to_string(index=False))
print(imp.round(4).to_string(index=False))
