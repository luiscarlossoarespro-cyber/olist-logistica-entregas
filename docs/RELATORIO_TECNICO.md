# Relatório técnico

Gerado automaticamente por `src/08_relatorio.py` a partir de `resultados/`.

## 1. Auditoria de qualidade

| tabela | verificacao | ocorrencias | base | pct | decisao |
|---|---|---|---|---|---|
| pedidos | pedidos duplicados (order_id repetido) | 0 | 99441 | 0,00 | nenhuma ação necessária |
| pedidos | pedidos com status 'entregue' | 96478 | 99441 | 97,02 | universo da análise de atraso |
| pedidos | entregue sem data de entrega ao cliente | 8 | 96478 | 0,01 | excluídos |
| pedidos | entregue sem data de postagem | 2 | 96478 | 0,00 | excluídos |
| pedidos | entregue sem data de aprovação | 14 | 96478 | 0,01 | excluídos |
| pedidos | entregues com as 3 datas preenchidas (base utilizável) | 96455 | 96478 | 99,98 | base analítica |
| pedidos | aprovado antes da compra | 0 | 96455 | 0,00 | excluídos |
| pedidos | postado antes da aprovação do pagamento | 1350 | 96455 | 1,40 | mantidos; as etapas são medidas a partir da compra, então não geram tempo negativo |
| pedidos | entregue ao cliente antes da postagem | 23 | 96455 | 0,02 | excluídos (impossível fisicamente) |
| pedidos | entrega demorou mais de 90 dias (compra até entrega) | 77 | 96455 | 0,08 | mantidos; são casos extremos reais, tratados com mediana e testes não paramétricos |
| pedidos | prazo prometido menor que 1 dia | 0 | 96455 | 0,00 | nenhuma ação necessária |
| itens | itens por pedido: pedidos com mais de 1 vendedor | 1278 | 98666 | 1,29 | mantidos; vendedor de referência = o do primeiro item (menor order_item_id) |
| itens | itens com frete zero | 383 | 112650 | 0,34 | mantidos |
| produtos | produto sem categoria | 610 | 32951 | 1,85 | categoria 'sem_categoria' |
| produtos | produto sem peso | 2 | 32951 | 0,01 | peso ausente (não imputado; usado só onde existe) |
| produtos | produto com peso zero | 4 | 32951 | 0,01 | tratado como ausente |
| avaliacoes | pedidos com mais de uma avaliação | 547 | 98673 | 0,55 | nota do pedido = média das notas |
| avaliacoes | pedidos entregues sem nenhuma avaliação | 646 | 96455 | 0,67 | análises de nota usam só pedidos avaliados (possível viés de resposta) |
| geo | linhas de geolocalização fora do retângulo do Brasil | 31 | 1000163 | 0,00 | excluídas antes de calcular o centro de cada prefixo de CEP |
| geo | prefixos de CEP distintos na tabela de geolocalização | 19015 | 19015 | 100,00 | centro do prefixo = mediana de lat e lng |
| clientes | clientes cujo prefixo de CEP não tem geolocalização | 278 | 99441 | 0,28 | distância ausente (pedido mantido nas demais análises) |
| vendedores | vendedores cujo prefixo de CEP não tem geolocalização | 7 | 3095 | 0,23 | distância ausente (pedido mantido nas demais análises) |


## 2. Indicadores gerais

| indicador | valor |
|---|---|
| pedidos | 96.432,00 |
| atrasados | 6.533,00 |
| pct_atraso | 6,77 |
| ic95_inf | 6,62 |
| ic95_sup | 6,94 |
| pct_atraso_por_horario (definição antiga) | 8,11 |
| dias_total_mediana | 10,22 |
| dias_total_media | 12,56 |
| dias_prometidos_mediana | 23,23 |
| dias_prometidos_media | 23,73 |
| folga_mediana_dias | 11,94 |
| nota_media | 4,16 |
| pedidos_avaliados | 95.786,00 |
| mediana_distancia_km | 433,86 |
| pct_mesma_uf | 35,97 |


## 3. Atraso por mês (IC 95% de Wilson)

| mes | pedidos | atrasados | pct_atraso | ic95_inf | ic95_sup | mediana_dias_total |
|---|---|---|---|---|---|---|
| 2017-01 | 747,00 | 22,00 | 2,95 | 1,95 | 4,42 | 10,71 |
| 2017-02 | 1.639,00 | 49,00 | 2,99 | 2,27 | 3,93 | 10,95 |
| 2017-03 | 2.545,00 | 116,00 | 4,56 | 3,81 | 5,44 | 10,13 |
| 2017-04 | 2.303,00 | 151,00 | 6,56 | 5,62 | 7,64 | 12,75 |
| 2017-05 | 3.544,00 | 106,00 | 2,99 | 2,48 | 3,60 | 9,79 |
| 2017-06 | 3.134,00 | 95,00 | 3,03 | 2,49 | 3,69 | 10,80 |
| 2017-07 | 3.861,00 | 108,00 | 2,80 | 2,32 | 3,37 | 10,17 |
| 2017-08 | 4.191,00 | 122,00 | 2,91 | 2,44 | 3,46 | 9,80 |
| 2017-09 | 4.149,00 | 181,00 | 4,36 | 3,78 | 5,03 | 10,31 |
| 2017-10 | 4.478,00 | 187,00 | 4,18 | 3,63 | 4,80 | 10,26 |
| 2017-11 | 7.288,00 | 904,00 | 12,40 | 11,67 | 13,18 | 12,70 |
| 2017-12 | 5.513,00 | 411,00 | 7,46 | 6,79 | 8,18 | 13,14 |
| 2018-01 | 7.069,00 | 403,00 | 5,70 | 5,18 | 6,27 | 11,83 |
| 2018-02 | 6.555,00 | 926,00 | 14,13 | 13,30 | 14,99 | 14,26 |
| 2018-03 | 7.003,00 | 1.328,00 | 18,96 | 18,06 | 19,90 | 13,37 |
| 2018-04 | 6.798,00 | 306,00 | 4,50 | 4,03 | 5,02 | 9,31 |
| 2018-05 | 6.749,00 | 443,00 | 6,56 | 6,00 | 7,18 | 9,15 |
| 2018-06 | 6.096,00 | 71,00 | 1,16 | 0,92 | 1,47 | 7,96 |
| 2018-07 | 6.156,00 | 208,00 | 3,38 | 2,96 | 3,86 | 7,50 |
| 2018-08 | 6.351,00 | 393,00 | 6,19 | 5,62 | 6,81 | 7,01 |


## 4. Etapas do prazo por mês

| mes | pedidos | pct_atraso | prometido_mediana | postagem_mediana | transporte_mediana | total_mediana |
|---|---|---|---|---|---|---|
| 2017-01 | 747 | 2,95 | 38,96 | 2,42 | 7,15 | 10,71 |
| 2017-02 | 1639 | 2,99 | 30,17 | 2,29 | 7,31 | 10,95 |
| 2017-03 | 2545 | 4,56 | 22,59 | 1,98 | 7,05 | 10,13 |
| 2017-04 | 2303 | 6,56 | 25,47 | 2,67 | 8,90 | 12,75 |
| 2017-05 | 3544 | 2,99 | 23,33 | 1,99 | 7,03 | 9,79 |
| 2017-06 | 3134 | 3,03 | 23,42 | 2,19 | 7,44 | 10,80 |
| 2017-07 | 3861 | 2,80 | 23,02 | 2,28 | 7,06 | 10,17 |
| 2017-08 | 4191 | 2,91 | 22,55 | 2,20 | 6,95 | 9,80 |
| 2017-09 | 4149 | 4,36 | 22,14 | 2,35 | 7,09 | 10,31 |
| 2017-10 | 4478 | 4,18 | 22,40 | 2,30 | 7,05 | 10,26 |
| 2017-11 | 7288 | 12,40 | 22,27 | 3,16 | 8,76 | 12,70 |
| 2017-12 | 5513 | 7,46 | 27,44 | 2,84 | 9,09 | 13,14 |
| 2018-01 | 7069 | 5,70 | 25,57 | 2,45 | 8,04 | 11,83 |
| 2018-02 | 6555 | 14,13 | 24,26 | 2,52 | 11,02 | 14,26 |
| 2018-03 | 7003 | 18,96 | 21,32 | 2,37 | 9,88 | 13,37 |
| 2018-04 | 6798 | 4,50 | 23,42 | 2,06 | 6,91 | 9,31 |
| 2018-05 | 6749 | 6,56 | 21,46 | 1,80 | 6,52 | 9,15 |
| 2018-06 | 6096 | 1,16 | 27,28 | 1,76 | 5,85 | 7,96 |
| 2018-07 | 6156 | 3,38 | 19,33 | 1,79 | 5,30 | 7,50 |
| 2018-08 | 6351 | 6,19 | 13,44 | 1,76 | 4,95 | 7,01 |


## 5. Atraso por UF do cliente (300+ pedidos)

| uf_cliente | pedidos | atrasados | pct_atraso | ic95_inf | ic95_sup | mediana_dias_total | mediana_transporte | mediana_prometidos | mediana_km | pct_mesma_uf | frete_medio | nota_media |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AL | 397,00 | 85,00 | 21,41 | 17,66 | 25,71 | 22,33 | 18,12 | 31,42 | 1.915,07 | 0,00 | 38,58 | 3,85 |
| MA | 716,00 | 125,00 | 17,46 | 14,85 | 20,41 | 19,19 | 15,70 | 30,19 | 2.196,92 | 1,96 | 42,97 | 3,83 |
| SE | 335,00 | 51,00 | 15,22 | 11,77 | 19,46 | 18,01 | 14,20 | 29,55 | 1.720,99 | 0,00 | 40,94 | 3,91 |
| PI | 476,00 | 66,00 | 13,87 | 11,05 | 17,26 | 16,29 | 13,48 | 29,49 | 2.056,28 | 0,21 | 42,98 | 3,99 |
| CE | 1.278,00 | 176,00 | 13,77 | 11,99 | 15,77 | 18,21 | 14,70 | 31,24 | 2.292,58 | 0,70 | 36,50 | 3,94 |
| BA | 3.256,00 | 396,00 | 12,16 | 11,08 | 13,33 | 16,91 | 13,84 | 29,01 | 1.422,40 | 2,03 | 29,96 | 3,93 |
| RJ | 12.347,00 | 1.495,00 | 12,11 | 11,54 | 12,70 | 12,04 | 8,35 | 24,61 | 394,23 | 7,73 | 23,95 | 3,97 |
| PA | 946,00 | 106,00 | 11,21 | 9,35 | 13,37 | 21,08 | 17,28 | 36,12 | 2.394,12 | 0,00 | 39,70 | 3,91 |
| ES | 1.995,00 | 214,00 | 10,73 | 9,44 | 12,16 | 13,64 | 9,97 | 25,03 | 761,80 | 0,35 | 24,57 | 4,08 |
| PB | 517,00 | 54,00 | 10,44 | 8,09 | 13,38 | 18,15 | 14,12 | 32,47 | 2.162,25 | 0,19 | 48,84 | 4,08 |
| MS | 701,00 | 68,00 | 9,70 | 7,72 | 12,12 | 13,94 | 11,06 | 25,90 | 863,61 | 0,00 | 27,02 | 4,16 |
| PE | 1.593,00 | 153,00 | 9,60 | 8,25 | 11,15 | 15,70 | 12,85 | 31,02 | 2.082,57 | 1,44 | 35,83 | 4,08 |
| RN | 474,00 | 44,00 | 9,28 | 6,99 | 12,23 | 16,06 | 13,08 | 31,87 | 2.264,75 | 4,43 | 39,26 | 4,15 |
| SC | 3.544,00 | 291,00 | 8,21 | 7,35 | 9,16 | 13,02 | 9,60 | 25,12 | 528,54 | 7,20 | 24,82 | 4,13 |
| GO | 1.957,00 | 128,00 | 6,54 | 5,53 | 7,72 | 13,95 | 10,99 | 26,96 | 804,09 | 1,58 | 26,25 | 4,10 |
| RS | 5.341,00 | 325,00 | 6,09 | 5,47 | 6,76 | 13,18 | 10,01 | 28,03 | 855,54 | 5,39 | 24,81 | 4,19 |
| MT | 886,00 | 53,00 | 5,98 | 4,60 | 7,74 | 16,11 | 13,20 | 31,21 | 1.333,06 | 0,68 | 32,77 | 4,15 |
| DF | 2.080,00 | 118,00 | 5,67 | 4,76 | 6,75 | 11,36 | 8,09 | 24,10 | 866,82 | 2,36 | 23,86 | 4,13 |
| MG | 11.346,00 | 519,00 | 4,57 | 4,20 | 4,97 | 10,31 | 7,19 | 23,60 | 490,27 | 13,42 | 23,46 | 4,19 |
| SP | 40.474,00 | 1.819,00 | 4,49 | 4,30 | 4,70 | 7,21 | 4,41 | 18,74 | 162,95 | 75,90 | 17,33 | 4,25 |
| PR | 4.923,00 | 199,00 | 4,04 | 3,53 | 4,63 | 10,43 | 7,18 | 24,05 | 426,32 | 14,50 | 23,49 | 4,24 |


## 6. Atraso por distância vendedor-cliente

| faixa_km | pedidos | atrasados | pct_atraso | ic95_inf | ic95_sup | mediana_transporte | mediana_prometidos | mediana_total | frete_medio | nota_media |
|---|---|---|---|---|---|---|---|---|---|---|
| até 100 km | 17.890,00 | 797,00 | 4,46 | 4,16 | 4,77 | 2,09 | 14,28 | 5,09 | 13,45 | 4,27 |
| 100 a 300 km | 13.339,00 | 692,00 | 5,19 | 4,82 | 5,58 | 5,65 | 20,25 | 8,20 | 18,75 | 4,25 |
| 300 a 600 km | 31.473,00 | 2.127,00 | 6,76 | 6,49 | 7,04 | 7,14 | 23,25 | 10,32 | 22,39 | 4,13 |
| 600 a 1.000 km | 17.907,00 | 1.273,00 | 7,11 | 6,74 | 7,49 | 9,09 | 26,16 | 12,52 | 24,81 | 4,12 |
| 1.000 a 1.500 km | 6.580,00 | 579,00 | 8,80 | 8,14 | 9,51 | 11,81 | 28,53 | 14,90 | 29,82 | 4,05 |
| mais de 1.500 km | 8.764,00 | 1.020,00 | 11,64 | 10,98 | 12,33 | 14,19 | 32,13 | 17,86 | 39,89 | 4,00 |


## 7. Etapas: no prazo x atrasou (dias)

| pedidos | ate_postagem_media | ate_postagem_mediana | transporte_media | transporte_mediana | total_media | total_mediana | prometidos_mediana | distancia_mediana_km | grupo |
|---|---|---|---|---|---|---|---|---|---|
| 89899 | 3,02 | 2,15 | 7,99 | 6,95 | 11,00 | 9,81 | 23,27 | 426,39 | No prazo |
| 6533 | 6,06 | 3,50 | 27,89 | 26,20 | 33,95 | 31,25 | 22,48 | 529,01 | Atrasou |


## 8. Regressão logística (chance de atraso)

Referência: SP. Controles: efeito fixo de mês. Razão de chances > 1 = mais chance de atraso.


| variavel | coef | odds_ratio | or_ic95_inf | or_ic95_sup | p_valor |
|---|---|---|---|---|---|
| Intercept | -5,006 | 0,007 | 0,004 | 0,011 | 0,000 |
| região: Centro-Oeste | 0,333 | 1,395 | 1,221 | 1,594 | 0,000 |
| região: Nordeste | 1,084 | 2,956 | 2,649 | 3,299 | 0,000 |
| região: Norte | 0,631 | 1,880 | 1,542 | 2,292 | 0,000 |
| região: RJ | 1,106 | 3,022 | 2,784 | 3,281 | 0,000 |
| região: Sudeste (MG e ES) | 0,119 | 1,126 | 1,019 | 1,244 | 0,020 |
| região: Sul | 0,225 | 1,252 | 1,135 | 1,381 | 0,000 |
| log_km | 0,069 | 1,072 | 1,041 | 1,104 | 0,000 |
| postagem_d | 0,157 | 1,170 | 1,163 | 1,177 | 0,000 |
| log_peso | -0,011 | 0,989 | 0,970 | 1,008 | 0,262 |


```
Pedidos no modelo: 95668
Pseudo R2 (McFadden): 0.1555
Referência de região: SP. Controles: efeito fixo de mês (jan/2017 a ago/2018).
log_km = log(1 + distância em km); postagem_d = dias da compra até a postagem (0 a 30); log_peso = log(1 + peso em g).
```


### Probabilidade prevista (demais variáveis como observadas)

| cenario | pct_atraso_previsto |
|---|---|
| distância de 100 km | 6,25 |
| distância de 500 km | 6,85 |
| distância de 2.000 km | 7,41 |
| postagem em 1 dia | 4,40 |
| postagem em 3 dias | 5,84 |
| postagem em 7 dias | 10,02 |


## 9. Transporte real x esperado pela distância

Modelo: log(dias de transporte) ~ log(1 + km). Razão = real / esperado (mediana por UF).


| uf_cliente | pedidos | mediana_km | transporte_mediana | esperado_mediana | razao_mediana | pct_acima_do_esperado |
|---|---|---|---|---|---|---|
| AL | 396 | 1.915,07 | 18,14 | 13,89 | 1,38 | 37,65 |
| PA | 944 | 2.394,12 | 17,30 | 15,25 | 1,19 | 19,28 |
| SC | 3535 | 528,54 | 9,48 | 8,11 | 1,19 | 18,56 |
| RJ | 12294 | 394,21 | 8,34 | 7,17 | 1,16 | 15,85 |
| GO | 1944 | 804,09 | 10,99 | 9,66 | 1,15 | 15,35 |
| BA | 3238 | 1.422,40 | 13,84 | 12,27 | 1,15 | 15,31 |
| SE | 334 | 1.720,99 | 14,19 | 13,29 | 1,14 | 13,83 |
| MS | 699 | 863,61 | 11,06 | 9,96 | 1,12 | 12,36 |
| MA | 712 | 2.196,92 | 15,45 | 14,71 | 1,12 | 12,14 |
| MT | 881 | 1.333,06 | 13,21 | 11,94 | 1,11 | 10,84 |
| ES | 1984 | 761,80 | 9,97 | 9,45 | 1,05 | 4,67 |
| RS | 5324 | 855,54 | 10,01 | 9,92 | 1,02 | 2,38 |
| CE | 1270 | 2.292,70 | 14,79 | 14,98 | 1,01 | 0,67 |
| PB | 511 | 2.162,25 | 14,15 | 14,62 | 0,99 | -0,61 |
| PR | 4899 | 426,32 | 7,17 | 7,41 | 0,99 | -1,28 |
| PI | 473 | 2.056,28 | 13,47 | 14,31 | 0,95 | -4,49 |
| MG | 11308 | 490,27 | 7,19 | 7,86 | 0,94 | -6,06 |
| RN | 472 | 2.264,75 | 13,06 | 14,90 | 0,94 | -6,54 |
| PE | 1588 | 2.082,57 | 12,85 | 14,39 | 0,91 | -9,30 |
| SP | 40380 | 162,96 | 4,41 | 4,96 | 0,86 | -13,70 |
| DF | 1914 | 866,82 | 8,07 | 9,97 | 0,84 | -15,64 |


## 10. Impacto na nota

| medida | valor |
|---|---|
| nota média - atrasados | 2,2714 |
| nota média - no prazo | 4,2910 |
| diferença (atrasados - no prazo) | -2,0196 |
| diferença IC95 inferior | -2,0588 |
| diferença IC95 superior | -1,9803 |
| Mann-Whitney p-valor | 0,0000 |
| regressão: queda na nota por atrasar (salto) | -1,4554 |
| regressão: queda adicional por dia de atraso | -0,0553 |



| dias_atraso_faixa | pedidos_avaliados | nota_media | nota_mediana | pct_notas_1_ou_2 | pedidos_total | pct_dos_pedidos |
|---|---|---|---|---|---|---|
| No prazo ou adiantado | 89406 | 4,29 | 5,00 | 9,22 | 89899 | 93,23 |
| Atraso de 1 a 3 dias | 1852 | 3,29 | 4,00 | 32,18 | 1870 | 1,94 |
| Atraso de 4 a 7 dias | 1747 | 2,10 | 1,00 | 67,60 | 1801 | 1,87 |
| Atraso de 8 a 14 dias | 1446 | 1,67 | 1,00 | 80,08 | 1478 | 1,53 |
| Atraso de mais de 14 dias | 1335 | 1,73 | 1,00 | 78,20 | 1384 | 1,44 |


## 11. Vendedores

| medida | valor |
|---|---|
| vendedores com 50+ pedidos | 419,00 |
| vendedores com atraso estatisticamente acima da média | 59,00 |
| % dos pedidos (base total) desses vendedores | 16,59 |
| % dos atrasos (base total) desses vendedores | 28,03 |
| mediana de dias até postar - vendedores críticos | 3,10 |
| mediana de dias até postar - demais vendedores 50+ | 1,97 |


## 12. Categorias (500+ pedidos)

| categoria | pedidos | atrasados | pct_atraso | ic95_inf | ic95_sup | mediana_dias_total | nota_media | mediana_peso_g | frete_medio |
|---|---|---|---|---|---|---|---|---|---|
| baby | 2.763,00 | 226,00 | 8,18 | 7,21 | 9,26 | 10,08 | 4,12 | 750,00 | 24,02 |
| office_furniture | 1.246,00 | 101,00 | 8,11 | 6,72 | 9,75 | 18,90 | 3,65 | 11.880,00 | 53,55 |
| electronics | 2.507,00 | 192,00 | 7,66 | 6,68 | 8,77 | 11,01 | 4,13 | 200,00 | 18,35 |
| musical_instruments | 608,00 | 46,00 | 7,57 | 5,72 | 9,94 | 10,51 | 4,24 | 950,00 | 29,50 |
| health_beauty | 8.608,00 | 649,00 | 7,54 | 7,00 | 8,12 | 9,58 | 4,24 | 450,00 | 20,77 |
| bed_bath_table | 9.167,00 | 689,00 | 7,52 | 6,99 | 8,07 | 10,77 | 4,01 | 1.383,00 | 22,00 |
| watches_gifts | 5.470,00 | 406,00 | 7,42 | 6,76 | 8,15 | 10,36 | 4,13 | 350,00 | 17,96 |
| construction_tools_construction | 728,00 | 54,00 | 7,42 | 5,73 | 9,55 | 8,75 | 4,13 | 1.500,00 | 28,03 |
| auto | 3.792,00 | 278,00 | 7,33 | 6,54 | 8,20 | 9,78 | 4,15 | 950,00 | 23,83 |
| furniture_decor | 6.201,00 | 445,00 | 7,18 | 6,56 | 7,85 | 10,89 | 4,07 | 1.800,00 | 27,13 |
| telephony | 4.075,00 | 291,00 | 7,14 | 6,39 | 7,97 | 10,81 | 4,06 | 250,00 | 17,00 |
| sem_categoria | 1.331,00 | 95,00 | 7,14 | 5,87 | 8,65 | 10,77 | 4,06 | 450,00 | 19,19 |
| sports_leisure | 7.489,00 | 495,00 | 6,61 | 6,07 | 7,19 | 10,12 | 4,23 | 800,00 | 21,78 |
| garden_tools | 3.412,00 | 225,00 | 6,59 | 5,81 | 7,48 | 11,75 | 4,19 | 1.750,00 | 28,30 |
| stationery | 2.248,00 | 148,00 | 6,58 | 5,63 | 7,68 | 10,21 | 4,30 | 1.200,00 | 20,41 |
| perfumery | 3.075,00 | 202,00 | 6,57 | 5,75 | 7,50 | 9,43 | 4,27 | 400,00 | 17,29 |
| computers_accessories | 6.500,00 | 417,00 | 6,42 | 5,85 | 7,04 | 11,11 | 4,08 | 338,00 | 22,13 |
| toys | 3.777,00 | 241,00 | 6,38 | 5,64 | 7,21 | 9,42 | 4,24 | 850,00 | 20,09 |
| consoles_games | 1.013,00 | 62,00 | 6,12 | 4,80 | 7,77 | 11,29 | 4,18 | 283,00 | 18,81 |
| cool_stuff | 3.528,00 | 209,00 | 5,92 | 5,19 | 6,75 | 10,42 | 4,23 | 1.500,00 | 23,14 |
| fashion_bags_accessories | 1.813,00 | 102,00 | 5,63 | 4,66 | 6,78 | 9,01 | 4,24 | 200,00 | 16,90 |
| housewares | 5.694,00 | 307,00 | 5,39 | 4,83 | 6,01 | 8,93 | 4,20 | 1.450,00 | 25,15 |
| pet_shop | 1.681,00 | 86,00 | 5,12 | 4,16 | 6,28 | 9,55 | 4,28 | 974,00 | 23,24 |
| small_appliances | 605,00 | 29,00 | 4,79 | 3,36 | 6,80 | 8,98 | 4,27 | 1.200,00 | 25,44 |
| home_appliances | 747,00 | 33,00 | 4,42 | 3,16 | 6,14 | 9,41 | 4,22 | 475,00 | 19,37 |
| luggage_accessories | 1.008,00 | 43,00 | 4,27 | 3,18 | 5,70 | 9,07 | 4,38 | 1.250,00 | 29,63 |


## 13. Folga do prazo prometido por UF

| uf_cliente | pedidos | prometido_mediana | real_mediana | folga_mediana | pct_folga_negativa |
|---|---|---|---|---|---|
| AL | 397 | 31,42 | 22,33 | 9,43 | 23,93 |
| MA | 716 | 30,19 | 19,19 | 10,00 | 19,69 |
| SP | 40474 | 18,74 | 7,21 | 10,28 | 5,90 |
| ES | 1995 | 25,03 | 13,64 | 11,15 | 12,23 |
| MS | 701 | 25,90 | 13,94 | 11,44 | 11,55 |
| BA | 3256 | 29,01 | 16,91 | 11,56 | 14,04 |
| DF | 2080 | 24,10 | 11,36 | 12,06 | 7,07 |
| SC | 3544 | 25,12 | 13,02 | 12,08 | 9,76 |
| SE | 335 | 29,55 | 18,01 | 12,13 | 15,22 |
| RJ | 12347 | 24,61 | 12,04 | 12,25 | 13,48 |
| CE | 1278 | 31,24 | 18,21 | 12,27 | 15,34 |
| GO | 1957 | 26,96 | 13,95 | 12,31 | 8,18 |
| PI | 476 | 29,49 | 16,29 | 13,08 | 15,97 |
| PR | 4923 | 24,05 | 10,43 | 13,09 | 5,00 |
| MG | 11346 | 23,60 | 10,31 | 13,12 | 5,61 |
| PB | 517 | 32,47 | 18,15 | 13,36 | 11,03 |
| PE | 1593 | 31,02 | 15,70 | 13,58 | 10,80 |
| RS | 5341 | 28,03 | 13,18 | 14,03 | 7,15 |
| MT | 886 | 31,21 | 16,11 | 14,26 | 6,77 |
| RN | 474 | 31,87 | 16,06 | 14,35 | 10,76 |
| PA | 946 | 36,12 | 21,08 | 15,08 | 12,37 |


## 14. Cenários de impacto

| cenario | pedidos_atrasados_evitados | pct_do_total_de_atrasos | queda_pontos_percentuais_no_atraso_geral | pct_pedidos_nas_UFs_alvo |
|---|---|---|---|---|
| Atraso nas UFs de maior atraso (AL, MA, PI, CE, SE, BA, RJ, PA, ES) cair ao nível das demais UFs | 1602 | 24,50 | 1,66 | 22,60 |
| Eliminar atrasos longos (mais de 3 dias) | 4663 | 71,40 | 4,84 |  |


## 15. Modelo de risco de atraso
```
Treino: compras jan/2017 a mar/2018 (64019 pedidos, 7.98% atrasados)
Teste: compras abr a ago/2018 (32150 pedidos, 4.42% atrasados)
Melhor modelo (PR-AUC no teste): Gradient boosting
```

| modelo | roc_auc | pr_auc | taxa_base_teste_pct | brier | top10_pct_dos_atrasos_capturados | top10_precisao_pct | top20_pct_dos_atrasos_capturados | top20_precisao_pct |
|---|---|---|---|---|---|---|---|---|
| Regressão logística | 0,816 | 0,257 | 4,420 | 0,041 | 44,335 | 19,596 | 63,195 | 13,966 |
| Gradient boosting | 0,816 | 0,384 | 4,420 | 0,033 | 49,543 | 21,897 | 65,376 | 14,448 |
| Sem modelo (escolha aleatória) | 0,500 | 0,044 | 4,420 |  | 10,000 | 4,420 | 20,000 | 4,420 |


### Importância das variáveis (queda de PR-AUC ao embaralhar)

| variavel | queda_pr_auc | desvio |
|---|---|---|
| prazo_restante_na_postagem | 0,3100 | 0,0017 |
| dias_ate_postagem | 0,0757 | 0,0023 |
| log_km | 0,0520 | 0,0022 |
| uf_cliente | 0,0174 | 0,0015 |
| mes_do_ano | 0,0166 | 0,0025 |
| log_frete | 0,0105 | 0,0013 |
| mesma_uf | 0,0091 | 0,0012 |
| dias_prometidos | 0,0046 | 0,0007 |
| uf_vendedor | 0,0012 | 0,0010 |
| qtd_itens | 0,0010 | 0,0010 |
| log_volume | 0,0006 | 0,0009 |
| log_preco | 0,0006 | 0,0002 |
| categoria_m | 0,0005 | 0,0004 |
| log_peso | 0,0001 | 0,0005 |
| dia_semana | -0,0005 | 0,0005 |
