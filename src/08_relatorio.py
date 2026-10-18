"""Etapa 8: gera docs/RELATORIO_TECNICO.md direto dos CSVs (sem digitar números à mão)."""
import pandas as pd
from comum import RES, RAIZ


def md(df, dec=2):
    df = df.copy()
    for c in df.columns:
        if pd.api.types.is_float_dtype(df[c]):
            df[c] = df[c].map(lambda v: "" if pd.isna(v) else f"{v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", "."))
    cab = "| " + " | ".join(map(str, df.columns)) + " |\n|" + "---|" * len(df.columns) + "\n"
    return cab + "".join("| " + " | ".join(map(str, r)) + " |\n" for r in df.itertuples(index=False))


r = lambda f: pd.read_csv(RES / f)
partes = ["# Relatório técnico\n\nGerado automaticamente por `src/08_relatorio.py` a partir de `resultados/`.\n"]
partes += ["## 1. Auditoria de qualidade\n", md(r("01_auditoria_qualidade.csv")),
           "\n## 2. Indicadores gerais\n", md(pd.read_csv(RES / "03_indicadores_gerais.csv").rename(columns={"Unnamed: 0": "indicador"})),
           "\n## 3. Atraso por mês (IC 95% de Wilson)\n", md(r("03_atraso_por_mes.csv")),
           "\n## 4. Etapas do prazo por mês\n", md(r("04_picos_mensais_etapas.csv")),
           "\n## 5. Atraso por UF do cliente (300+ pedidos)\n", md(r("03_atraso_por_uf.csv")),
           "\n## 6. Atraso por distância vendedor-cliente\n", md(r("03_atraso_por_distancia.csv")),
           "\n## 7. Etapas: no prazo x atrasou (dias)\n", md(r("03_etapas_prazo_vs_atraso.csv")),
           "\n## 8. Regressão logística (chance de atraso)\n",
           "Referência: SP. Controles: efeito fixo de mês. Razão de chances > 1 = mais chance de atraso.\n\n",
           md(pd.read_csv(RES / "04_regressao_logistica_atraso.csv").rename(columns={"Unnamed: 0": "variavel"}), 3),
           "\n```\n" + open(RES / "04_regressao_logistica_resumo.txt").read().split("\n\n")[0] + "\n```\n",
           "\n### Probabilidade prevista (demais variáveis como observadas)\n", md(r("04_efeitos_previstos.csv")),
           "\n## 9. Transporte real x esperado pela distância\n",
           "Modelo: log(dias de transporte) ~ log(1 + km). Razão = real / esperado (mediana por UF).\n\n", md(r("04_transporte_vs_esperado_por_uf.csv")),
           "\n## 10. Impacto na nota\n", md(r("04_impacto_nota.csv"), 4), "\n", md(r("03_nota_por_faixa_atraso.csv")),
           "\n## 11. Vendedores\n", md(r("04_vendedores_resumo.csv")),
           "\n## 12. Categorias (500+ pedidos)\n", md(r("03_atraso_por_categoria.csv")),
           "\n## 13. Folga do prazo prometido por UF\n", md(r("03_folga_prazo_por_uf.csv")),
           "\n## 14. Cenários de impacto\n", md(r("03_cenarios.csv")),
           "\n## 15. Modelo de risco de atraso\n```\n" + open(RES / "05_modelo_resumo.txt").read() + "```\n", md(r("05_modelo_metricas.csv"), 3),
           "\n### Importância das variáveis (queda de PR-AUC ao embaralhar)\n", md(r("05_importancia_variaveis.csv"), 4)]
(RAIZ / "docs").mkdir(exist_ok=True)
(RAIZ / "docs" / "RELATORIO_TECNICO.md").write_text("\n".join(partes), encoding="utf-8")
print("docs/RELATORIO_TECNICO.md gerado")
