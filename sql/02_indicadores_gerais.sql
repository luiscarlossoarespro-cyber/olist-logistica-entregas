-- Q1. Quanto atrasa, quanto demora e quanta folga o prazo prometido tinha?
SELECT
    COUNT(*)                                       AS pedidos_entregues,
    ROUND(100.0 * AVG(atrasou::INT), 2)            AS pct_atraso,
    ROUND(AVG(dias_total), 1)                      AS dias_total_medio,
    ROUND(AVG(dias_prometidos), 1)                 AS dias_prometidos_medio,
    ROUND(AVG(dias_prometidos - dias_total), 1)    AS folga_media_dias,
    ROUND(AVG(nota), 2)                            AS nota_media
FROM base_entregas;
