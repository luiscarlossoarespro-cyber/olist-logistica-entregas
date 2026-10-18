-- Q2. O atraso é constante ao longo do tempo ou tem picos?
SELECT
    STRFTIME(mes_compra, '%Y-%m')                  AS mes,
    COUNT(*)                                       AS pedidos,
    ROUND(100.0 * AVG(atrasou::INT), 2)            AS pct_atraso,
    ROUND(AVG(dias_total), 1)                      AS dias_total_medio
FROM base_entregas
WHERE mes_compra >= DATE '2017-01-01' AND mes_compra < DATE '2018-09-01'   -- meses com volume relevante
GROUP BY mes_compra
ORDER BY mes_compra;
