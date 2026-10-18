"""Etapa 1: auditoria de qualidade dos dados.

Antes de qualquer análise, medimos o que está errado ou faltando nos dados.
Cada verificação gera uma linha em resultados/01_auditoria_qualidade.csv.
"""
import pandas as pd
from comum import conectar, RES

con = conectar()
linhas = []


def q(sql):
    return con.execute(sql).fetchone()[0]


def add(tabela, verificacao, qtd, base, decisao):
    linhas.append({
        "tabela": tabela, "verificacao": verificacao, "ocorrencias": qtd, "base": base,
        "pct": round(100 * qtd / base, 3) if base else None, "decisao": decisao,
    })


n_ped = q("SELECT count(*) FROM pedidos")
add("pedidos", "pedidos duplicados (order_id repetido)", n_ped - q("SELECT count(DISTINCT order_id) FROM pedidos"), n_ped, "nenhuma ação necessária")

status = con.execute("SELECT order_status, count(*) n FROM pedidos GROUP BY 1 ORDER BY 2 DESC").df()
status.to_csv(RES / "01_status_pedidos.csv", index=False)

ent = q("SELECT count(*) FROM pedidos WHERE order_status='delivered'")
add("pedidos", "pedidos com status 'entregue'", ent, n_ped, "universo da análise de atraso")
add("pedidos", "entregue sem data de entrega ao cliente", q("SELECT count(*) FROM pedidos WHERE order_status='delivered' AND order_delivered_customer_date IS NULL"), ent, "excluídos")
add("pedidos", "entregue sem data de postagem", q("SELECT count(*) FROM pedidos WHERE order_status='delivered' AND order_delivered_carrier_date IS NULL"), ent, "excluídos")
add("pedidos", "entregue sem data de aprovação", q("SELECT count(*) FROM pedidos WHERE order_status='delivered' AND order_approved_at IS NULL"), ent, "excluídos")

base_ok = "order_status='delivered' AND order_delivered_customer_date IS NOT NULL AND order_delivered_carrier_date IS NOT NULL AND order_approved_at IS NOT NULL"
n_ok = q(f"SELECT count(*) FROM pedidos WHERE {base_ok}")
add("pedidos", "entregues com as 3 datas preenchidas (base utilizável)", n_ok, ent, "base analítica")

add("pedidos", "aprovado antes da compra", q(f"SELECT count(*) FROM pedidos WHERE {base_ok} AND order_approved_at < order_purchase_timestamp"), n_ok, "excluídos")
add("pedidos", "postado antes da aprovação do pagamento", q(f"SELECT count(*) FROM pedidos WHERE {base_ok} AND order_delivered_carrier_date < order_approved_at"), n_ok, "mantidos; as etapas são medidas a partir da compra, então não geram tempo negativo")
add("pedidos", "entregue ao cliente antes da postagem", q(f"SELECT count(*) FROM pedidos WHERE {base_ok} AND order_delivered_customer_date < order_delivered_carrier_date"), n_ok, "excluídos (impossível fisicamente)")
add("pedidos", "entrega demorou mais de 90 dias (compra até entrega)", q(f"SELECT count(*) FROM pedidos WHERE {base_ok} AND date_diff('day', order_purchase_timestamp, order_delivered_customer_date) > 90"), n_ok, "mantidos; são casos extremos reais, tratados com mediana e testes não paramétricos")
add("pedidos", "prazo prometido menor que 1 dia", q(f"SELECT count(*) FROM pedidos WHERE {base_ok} AND date_diff('day', order_purchase_timestamp, order_estimated_delivery_date) < 1"), n_ok, "nenhuma ação necessária")

add("itens", "itens por pedido: pedidos com mais de 1 vendedor", q("SELECT count(*) FROM (SELECT order_id FROM itens GROUP BY 1 HAVING count(DISTINCT seller_id)>1)"), q("SELECT count(DISTINCT order_id) FROM itens"), "mantidos; vendedor de referência = o do primeiro item (menor order_item_id)")
add("itens", "itens com frete zero", q("SELECT count(*) FROM itens WHERE freight_value=0"), q("SELECT count(*) FROM itens"), "mantidos")

add("produtos", "produto sem categoria", q("SELECT count(*) FROM produtos WHERE product_category_name IS NULL"), q("SELECT count(*) FROM produtos"), "categoria 'sem_categoria'")
add("produtos", "produto sem peso", q("SELECT count(*) FROM produtos WHERE product_weight_g IS NULL"), q("SELECT count(*) FROM produtos"), "peso ausente (não imputado; usado só onde existe)")
add("produtos", "produto com peso zero", q("SELECT count(*) FROM produtos WHERE product_weight_g=0"), q("SELECT count(*) FROM produtos"), "tratado como ausente")

add("avaliacoes", "pedidos com mais de uma avaliação", q("SELECT count(*) FROM (SELECT order_id FROM avaliacoes GROUP BY 1 HAVING count(*)>1)"), q("SELECT count(DISTINCT order_id) FROM avaliacoes"), "nota do pedido = média das notas")
add("avaliacoes", "pedidos entregues sem nenhuma avaliação", q(f"SELECT count(*) FROM pedidos p WHERE {base_ok.replace('order_', 'p.order_')} AND NOT EXISTS (SELECT 1 FROM avaliacoes a WHERE a.order_id=p.order_id)"), n_ok, "análises de nota usam só pedidos avaliados (possível viés de resposta)")

# geolocalização: cobertura e valores impossíveis
add("geo", "linhas de geolocalização fora do retângulo do Brasil", q("SELECT count(*) FROM geo WHERE geolocation_lat NOT BETWEEN -34 AND 6 OR geolocation_lng NOT BETWEEN -74 AND -32"), q("SELECT count(*) FROM geo"), "excluídas antes de calcular o centro de cada prefixo de CEP")
n_pref = q("SELECT count(DISTINCT geolocation_zip_code_prefix) FROM geo")
add("geo", "prefixos de CEP distintos na tabela de geolocalização", n_pref, n_pref, "centro do prefixo = mediana de lat e lng")
add("clientes", "clientes cujo prefixo de CEP não tem geolocalização", q("SELECT count(*) FROM clientes c WHERE NOT EXISTS (SELECT 1 FROM geo g WHERE g.geolocation_zip_code_prefix=c.customer_zip_code_prefix)"), q("SELECT count(*) FROM clientes"), "distância ausente (pedido mantido nas demais análises)")
add("vendedores", "vendedores cujo prefixo de CEP não tem geolocalização", q("SELECT count(*) FROM vendedores s WHERE NOT EXISTS (SELECT 1 FROM geo g WHERE g.geolocation_zip_code_prefix=s.seller_zip_code_prefix)"), q("SELECT count(*) FROM vendedores"), "distância ausente (pedido mantido nas demais análises)")

# cobertura temporal por mês (alerta de meses incompletos)
cobertura = con.execute(f"""
    SELECT strftime(order_purchase_timestamp,'%Y-%m') mes, count(*) pedidos_entregues
    FROM pedidos WHERE {base_ok} GROUP BY 1 ORDER BY 1""").df()
cobertura.to_csv(RES / "01_cobertura_mensal.csv", index=False)

aud = pd.DataFrame(linhas)
aud.to_csv(RES / "01_auditoria_qualidade.csv", index=False)
pd.set_option("display.width", 250, "display.max_colwidth", 70)
print(aud[["tabela", "verificacao", "ocorrencias", "pct"]].to_string(index=False))
print(status.to_string(index=False))
print(cobertura.to_string(index=False))
