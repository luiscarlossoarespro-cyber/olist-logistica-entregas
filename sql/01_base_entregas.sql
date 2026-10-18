-- Base analítica: UMA linha por pedido ENTREGUE, com os marcos de tempo da entrega.
-- Fonte: Olist Brazilian E-Commerce Public Dataset (Kaggle).
CREATE OR REPLACE VIEW base_entregas AS
WITH itens AS (
    SELECT
        order_id,
        COUNT(*)                         AS qtd_itens,
        COUNT(DISTINCT seller_id)        AS qtd_vendedores,
        SUM(price)                       AS valor_produtos,
        SUM(freight_value)               AS valor_frete
    FROM order_items
    GROUP BY order_id
),
nota AS (
    SELECT order_id, AVG(review_score) AS nota
    FROM order_reviews
    GROUP BY order_id
)
SELECT
    o.order_id,
    c.customer_state                                   AS estado,
    o.order_purchase_timestamp                         AS data_compra,
    DATE_TRUNC('month', o.order_purchase_timestamp)    AS mes_compra,
    i.qtd_itens,
    i.qtd_vendedores,
    i.valor_produtos,
    i.valor_frete,
    i.valor_frete / NULLIF(i.valor_produtos, 0)        AS frete_sobre_preco,
    n.nota,
    -- etapas do prazo, em dias
    DATE_DIFF('hour', o.order_purchase_timestamp, o.order_approved_at) / 24.0           AS dias_aprovacao,
    DATE_DIFF('hour', o.order_approved_at, o.order_delivered_carrier_date) / 24.0       AS dias_ate_postagem,   -- vendedor
    DATE_DIFF('hour', o.order_delivered_carrier_date, o.order_delivered_customer_date) / 24.0 AS dias_transporte, -- transportadora
    DATE_DIFF('hour', o.order_purchase_timestamp, o.order_delivered_customer_date) / 24.0     AS dias_total,
    DATE_DIFF('hour', o.order_purchase_timestamp, o.order_estimated_delivery_date) / 24.0     AS dias_prometidos,
    -- dias de atraso: positivo = chegou depois do prometido; negativo = adiantado
    DATE_DIFF('hour', o.order_estimated_delivery_date, o.order_delivered_customer_date) / 24.0 AS dias_atraso,
    (o.order_delivered_customer_date > o.order_estimated_delivery_date)                        AS atrasou
FROM orders o
JOIN customers c USING (customer_id)
LEFT JOIN itens i USING (order_id)
LEFT JOIN nota  n USING (order_id)
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_delivered_carrier_date  IS NOT NULL
  AND o.order_approved_at             IS NOT NULL;
