-- Centro geográfico de cada prefixo de CEP (5 dígitos).
-- A tabela de geolocalização tem vários pontos por prefixo; usamos a MEDIANA de
-- latitude e longitude (robusta a pontos errados) e descartamos coordenadas fora do Brasil.
CREATE OR REPLACE TABLE geo_prefixo AS
SELECT
    geolocation_zip_code_prefix AS cep_prefixo,
    MEDIAN(geolocation_lat)     AS lat,
    MEDIAN(geolocation_lng)     AS lng
FROM geo
WHERE geolocation_lat BETWEEN -34 AND 6
  AND geolocation_lng BETWEEN -74 AND -32
GROUP BY 1;
