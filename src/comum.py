"""Funções comuns: caminhos e conexão DuckDB com as tabelas da Olist."""
from pathlib import Path
import duckdb

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"
RES = RAIZ / "resultados"
GRAF = RAIZ / "graficos"
SQL = RAIZ / "sql"
for p in (RES, GRAF):
    p.mkdir(exist_ok=True)

TABELAS = {
    "pedidos": "olist_orders_dataset.csv",
    "itens": "olist_order_items_dataset.csv",
    "clientes": "olist_customers_dataset.csv",
    "vendedores": "olist_sellers_dataset.csv",
    "produtos": "olist_products_dataset.csv",
    "avaliacoes": "olist_order_reviews_dataset.csv",
    "pagamentos": "olist_order_payments_dataset.csv",
    "geo": "olist_geolocation_dataset.csv",
    "traducao": "product_category_name_translation.csv",
}


def conectar():
    con = duckdb.connect()
    for nome, arq in TABELAS.items():
        con.execute(f"CREATE VIEW {nome} AS SELECT * FROM read_csv_auto('{(DADOS / arq).as_posix()}', header=true)")
    return con


def carregar_base():
    """Lê a base analítica (Parquet) como DataFrame, sem precisar do pyarrow."""
    return duckdb.sql(f"SELECT * FROM '{(DADOS / 'derivados' / 'base_entregas.parquet').as_posix()}' ORDER BY order_id").df()


def rodar_sql(con, arquivo):
    return con.execute((SQL / arquivo).read_text(encoding="utf-8"))
