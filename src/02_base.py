"""Etapa 2: monta a base analítica (geo + base_entregas) e salva em Parquet para as próximas etapas."""
from comum import conectar, rodar_sql, RES, RAIZ

con = conectar()
rodar_sql(con, "01_geo_prefixo.sql")
rodar_sql(con, "02_base_entregas.sql")
(RAIZ / "dados" / "derivados").mkdir(exist_ok=True)
con.execute(f"COPY base_entregas TO '{(RAIZ / 'dados' / 'derivados' / 'base_entregas.parquet').as_posix()}' (FORMAT PARQUET)")
r = con.execute("""
SELECT count(*) pedidos, round(100*avg(atrasou::int),2) pct_atraso,
       round(100*avg(atrasou_por_horario::int),2) pct_atraso_horario,
       count(distancia_km) com_distancia, round(median(distancia_km),0) mediana_km,
       count(peso_g) com_peso, count(nota) com_nota,
       sum((uf_vendedor IS NULL)::int) sem_vendedor
FROM base_entregas""").df()
print(r.T)
