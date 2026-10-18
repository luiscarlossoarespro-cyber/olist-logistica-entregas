-- Q5. Quanto o atraso machuca a satisfação do cliente?
SELECT
    CASE
        WHEN dias_atraso <= 0  THEN '1. No prazo ou adiantado'
        WHEN dias_atraso <= 3  THEN '2. Atraso de até 3 dias'
        WHEN dias_atraso <= 7  THEN '3. Atraso de 4 a 7 dias'
        WHEN dias_atraso <= 14 THEN '4. Atraso de 8 a 14 dias'
        ELSE                        '5. Atraso de mais de 14 dias'
    END                                            AS faixa,
    COUNT(*)                                       AS pedidos,
    ROUND(AVG(nota), 2)                            AS nota_media,
    ROUND(100.0 * AVG((nota <= 2)::INT), 1)        AS pct_notas_1_ou_2
FROM base_entregas
WHERE nota IS NOT NULL
GROUP BY faixa
ORDER BY faixa;
