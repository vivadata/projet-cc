-- staging table simu
-- Chloé
-- Sélection de variables
-- Mise au bon format

WITH base AS (
  SELECT
    Point - 200000 AS Point,
    CASE `Période` 
      WHEN 'RWL15' THEN '+1.5°C'
      WHEN 'RWL20' THEN '+2.0°C'
      WHEN 'RWL29' THEN '+2.9°C'
    END AS Scenario, -- RWL15, RWL20, RWL29
    CASE `Période`
      WHEN 'RWL15' THEN DATE(2030, 6, 1)
      WHEN 'RWL20' THEN DATE(2050, 6, 1)
      WHEN 'RWL29' THEN DATE(2100, 6, 1)
    END AS Horizon,
    NORTMm AS TM,
    NORETR AS TAMPLIAB,
    NORDTRm AS TAMPLIM,
    NORSU AS NBJTX25,
    NORTN25D AS NBJTNS25,
    NORTNn AS TNAB,
    NORTNx AS TNMAX,
    NORTX32D AS NBJTXS32,
    NORTX35D AS NBJTX35,
    NORTXn AS TXMIN,
    NORTXx AS TXAB,
    NORPXCDD,
    NORPRCPTOT AS RR,
    NORRR10D AS NBJRR10,
    NORRR100D AS NBJRR100,
    NORRx1D AS RRAB
  FROM `cc-reunion.data_meteofrance.simu_all_RWL`
)

SELECT
  *,
  DATE(2100, 6, 1) AS date_2100,
  DATE_DIFF(
    DATE(EXTRACT(YEAR FROM Horizon) + 1, 1, 1),
    DATE(EXTRACT(YEAR FROM Horizon), 1, 1),
    DAY
  ) - NORPXCDD AS NBRR -- nb de jours de non-sécheresse = nb de jours avec précip ?
FROM base