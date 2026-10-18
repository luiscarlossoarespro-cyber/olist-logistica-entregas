-- Base analítica v2: UMA linha por pedido ENTREGUE e com datas consistentes.
-- Regras de exclusão (ver resultados/01_auditoria_qualidade.csv):
--   status = entregue; datas de aprovação, postagem e entrega preenchidas;
--   entrega ao cliente NÃO pode ser anterior à postagem (impossível fisicamente).
-- Definição de atraso: o pedido chegou em DIA posterior ao dia prometido
-- (comparação por data de calendário; a data prometida não traz horário).
CREATE OR REPLACE TABLE base_entregas AS
WITH itens_pedido AS (
    SELECT
        i.order_id,
        COUNT(*)                          AS qtd_itens,
        COUNT(DISTINCT i.seller_id)       AS qtd_vendedores,
        SUM(i.price)                      AS valor_produtos,
        SUM(i.freight_value)              AS valor_frete,
        SUM(NULLIF(p.product_weight_g, 0))                                   AS peso_g,
        SUM(NULLIF(p.product_length_cm,0) * NULLIF(p.product_height_cm,0) * NULLIF(p.product_width_cm,0)) AS volume_cm3,
        -- vendedor e produto de referência: o primeiro item do pedido
        ARG_MIN(i.seller_id, i.order_item_id)   AS vendedor_id,
        ARG_MIN(p.product_category_name, i.order_item_id) AS categoria_pt
    FROM itens i
    LEFT JOIN produtos p USING (product_id)
    GROUP BY i.order_id
),
nota AS (
    SELECT order_id, AVG(review_score) AS nota FROM avaliacoes GROUP BY order_id
)
SELECT
    o.order_id,
    c.customer_state                                    AS uf_cliente,
    s.seller_state                                      AS uf_vendedor,
    ip.vendedor_id,
    COALESCE(t.product_category_name_english, ip.categoria_pt, 'sem_categoria') AS categoria,
    o.order_purchase_timestamp                          AS data_compra,
    DATE_TRUNC('month', o.order_purchase_timestamp)     AS mes_compra,
    DAYOFWEEK(o.order_purchase_timestamp)               AS dia_semana,
    ip.qtd_itens, ip.qtd_vendedores, ip.valor_produtos, ip.valor_frete,
    ip.valor_frete / NULLIF(ip.valor_produtos, 0)       AS frete_sobre_preco,
    ip.peso_g, ip.volume_cm3,
    n.nota,
    -- distância em linha reta (haversine), vendedor -> cliente, em km
    2 * 6371 * ASIN(SQRT(
        POWER(SIN(RADIANS(gc.lat - gs.lat) / 2), 2) +
        COS(RADIANS(gs.lat)) * COS(RADIANS(gc.lat)) * POWER(SIN(RADIANS(gc.lng - gs.lng) / 2), 2)
    ))                                                  AS distancia_km,
    (c.customer_state = s.seller_state)                 AS mesma_uf,
    -- etapas, em dias corridos
    DATE_DIFF('second', o.order_purchase_timestamp, o.order_delivered_carrier_date) / 86400.0   AS dias_ate_postagem,
    DATE_DIFF('second', o.order_delivered_carrier_date, o.order_delivered_customer_date) / 86400.0 AS dias_transporte,
    DATE_DIFF('second', o.order_purchase_timestamp, o.order_delivered_customer_date) / 86400.0  AS dias_total,
    DATE_DIFF('second', o.order_purchase_timestamp, o.order_estimated_delivery_date) / 86400.0  AS dias_prometidos,
    DATE_DIFF('day', o.order_estimated_delivery_date::DATE, o.order_delivered_customer_date::DATE) AS dias_atraso,
    (o.order_delivered_customer_date::DATE > o.order_estimated_delivery_date::DATE)             AS atrasou,
    -- definição alternativa (por horário), só para teste de sensibilidade
    (o.order_delivered_customer_date > o.order_estimated_delivery_date)                          AS atrasou_por_horario
FROM pedidos o
JOIN clientes c USING (customer_id)
LEFT JOIN itens_pedido ip USING (order_id)
LEFT JOIN vendedores s ON s.seller_id = ip.vendedor_id
LEFT JOIN traducao t ON t.product_category_name = ip.categoria_pt
LEFT JOIN nota n USING (order_id)
LEFT JOIN geo_prefixo gc ON gc.cep_prefixo = c.customer_zip_code_prefix
LEFT JOIN geo_prefixo gs ON gs.cep_prefixo = s.seller_zip_code_prefix
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_delivered_carrier_date  IS NOT NULL
  AND o.order_approved_at             IS NOT NULL
  AND o.order_delivered_customer_date >= o.order_delivered_carrier_date;
