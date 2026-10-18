# Dicionário de dados: `base_entregas`

Uma linha por pedido **entregue** com datas consistentes (96.432 pedidos). Criada por [`sql/02_base_entregas.sql`](../sql/02_base_entregas.sql).

| Coluna | Tipo | Descrição |
|---|---|---|
| order_id | texto | Identificador do pedido |
| uf_cliente | texto | UF do cliente |
| uf_vendedor | texto | UF do vendedor de referência (primeiro item do pedido) |
| vendedor_id | texto | Identificador do vendedor de referência (anonimizado pela Olist) |
| categoria | texto | Categoria do primeiro item (em inglês; "sem_categoria" se ausente) |
| data_compra | data e hora | Momento da compra |
| mes_compra | data | Mês da compra |
| dia_semana | inteiro | Dia da semana da compra (0 = domingo) |
| qtd_itens | inteiro | Itens no pedido |
| qtd_vendedores | inteiro | Vendedores distintos no pedido |
| valor_produtos | decimal | Soma dos preços dos itens (R$) |
| valor_frete | decimal | Soma do frete (R$) |
| frete_sobre_preco | decimal | Frete / valor dos produtos |
| peso_g | decimal | Soma do peso dos itens (g); peso zero tratado como ausente |
| volume_cm3 | decimal | Soma do volume dos itens (cm³) |
| nota | decimal | Média das notas de avaliação do pedido (1 a 5); vazio se não avaliado |
| distancia_km | decimal | Distância em linha reta vendedor-cliente (haversine), entre os centros dos prefixos de CEP |
| mesma_uf | lógico | Vendedor e cliente na mesma UF |
| dias_ate_postagem | decimal | Dias da compra até a entrega à transportadora |
| dias_transporte | decimal | Dias da postagem até a entrega ao cliente |
| dias_total | decimal | Dias da compra até a entrega ao cliente |
| dias_prometidos | decimal | Dias da compra até a data prometida |
| dias_atraso | inteiro | Dia da entrega menos dia prometido (positivo = atraso) |
| atrasou | lógico | Entregue em dia posterior ao prometido (**definição usada**) |
| atrasou_por_horario | lógico | Definição alternativa por horário (só para teste de sensibilidade) |
