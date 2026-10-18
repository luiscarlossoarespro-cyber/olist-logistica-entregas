-- Q7. O atraso está espalhado ou concentrado em poucos vendedores? (mín. 100 itens)
SELECT
    oi.seller_id,
    s.seller_state                                 AS estado_vendedor,
    COUNT(*)                                       AS itens,
    SUM(b.atrasou::INT)                            AS itens_atrasados,
    ROUND(100.0 * AVG(b.atrasou::INT), 2)          AS pct_atraso,
    ROUND(AVG(b.dias_ate_postagem), 1)             AS dias_ate_postar_medio,
    ROUND(AVG(b.nota), 2)                          AS nota_media
FROM order_items oi
JOIN base_entregas b USING (order_id)
JOIN sellers s USING (seller_id)
GROUP BY oi.seller_id, s.seller_state
HAVING COUNT(*) >= 100
ORDER BY itens_atrasados DESC;
