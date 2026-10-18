-- Q4. Em qual ETAPA o tempo se perde: aprovação, vendedor (até postar) ou transportadora?
SELECT
    CASE WHEN atrasou THEN 'Atrasou' ELSE 'No prazo' END AS grupo,
    COUNT(*)                                       AS pedidos,
    ROUND(AVG(dias_aprovacao), 1)                  AS dias_aprovacao,
    ROUND(AVG(dias_ate_postagem), 1)               AS dias_vendedor_ate_postar,
    ROUND(AVG(dias_transporte), 1)                 AS dias_transportadora,
    ROUND(AVG(dias_total), 1)                      AS dias_total
FROM base_entregas
WHERE dias_ate_postagem >= 0 AND dias_transporte >= 0 AND dias_aprovacao >= 0
GROUP BY atrasou
ORDER BY atrasou;
