-- Q6. Quais categorias de produto mais atrasam? (mín. 500 itens para ser comparável)
SELECT
    COALESCE(t.product_category_name_english, p.product_category_name, 'sem_categoria') AS categoria,
    COUNT(*)                                       AS itens,
    ROUND(100.0 * AVG(b.atrasou::INT), 2)          AS pct_atraso,
    ROUND(AVG(b.dias_total), 1)                    AS dias_total_medio,
    ROUND(AVG(b.nota), 2)                          AS nota_media
FROM order_items oi
JOIN base_entregas b USING (order_id)
JOIN products p USING (product_id)
LEFT JOIN cat t ON t.product_category_name = p.product_category_name
GROUP BY categoria
HAVING COUNT(*) >= 500
ORDER BY pct_atraso DESC;
