-- Q3. Onde (estado do cliente) o atraso e o prazo são piores?
SELECT
    estado,
    COUNT(*)                                       AS pedidos,
    ROUND(100.0 * AVG(atrasou::INT), 2)            AS pct_atraso,
    ROUND(AVG(dias_total), 1)                      AS dias_total_medio,
    ROUND(AVG(valor_frete), 2)                     AS frete_medio,
    ROUND(AVG(frete_sobre_preco) * 100, 1)         AS frete_pct_do_preco,
    ROUND(AVG(nota), 2)                            AS nota_media
FROM base_entregas
GROUP BY estado
HAVING COUNT(*) >= 300
ORDER BY pct_atraso DESC;
