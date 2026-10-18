"""Roda o projeto inteiro, na ordem: auditoria -> base -> descritiva -> inferência -> modelo -> gráficos -> relatório -> análises extras -> dados do dashboard."""
import runpy
from pathlib import Path

AQUI = Path(__file__).resolve().parent
for etapa in ["01_auditoria.py", "02_base.py", "03_descritiva.py", "04_inferencia.py", "05_modelo.py", "06_graficos.py", "08_relatorio.py", "09_analises_extra.py", "10_dados_dashboard.py"]:
    print(f"\n===== {etapa} =====")
    runpy.run_path(str(AQUI / etapa), run_name="__main__")
