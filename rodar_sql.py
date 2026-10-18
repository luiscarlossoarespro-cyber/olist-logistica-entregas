"""Executa as consultas SQL sobre os CSVs da Olist e salva os resultados em resultados/*.csv"""
from pathlib import Path
import duckdb

RAIZ = Path(__file__).parent
DADOS = RAIZ / "dados"
SQL = RAIZ / "sql"
SAIDA = RAIZ / "resultados"


def conectar():
    con = duckdb.connect()
    tabelas = {
        "orders": "olist_orders_dataset.csv",
        "order_items": "olist_order_items_dataset.csv",
        "customers": "olist_customers_dataset.csv",
        "sellers": "olist_sellers_dataset.csv",
        "products": "olist_products_dataset.csv",
        "order_reviews": "olist_order_reviews_dataset.csv",
        "cat": "product_category_name_translation.csv",
    }
    for nome, arquivo in tabelas.items():
        caminho = DADOS / arquivo
        if not caminho.exists():
            raise SystemExit(f"Arquivo não encontrado: {caminho}\nBaixe a base no Kaggle (veja o README).")
        con.execute(f"CREATE VIEW {nome} AS SELECT * FROM read_csv_auto('{caminho.as_posix()}')")
    con.execute((SQL / "01_base_entregas.sql").read_text(encoding="utf-8"))
    return con


def main():
    SAIDA.mkdir(exist_ok=True)
    con = conectar()
    for arq in sorted(SQL.glob("0[2-9]_*.sql")):
        df = con.execute(arq.read_text(encoding="utf-8")).df()
        df.to_csv(SAIDA / f"{arq.stem}.csv", index=False)
        print(f"== {arq.stem} ({len(df)} linhas)")
        print(df.head(12).to_string(index=False))
        print()


if __name__ == "__main__":
    main()
