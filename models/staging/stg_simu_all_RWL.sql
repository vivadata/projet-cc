-- staging table simu
-- Chloé
-- Sélection de variables
-- Mise au bon format

SELECT
  Point-200000 AS Point,
  CASE `Période` 
    WHEN 'RWL15' THEN '+1.5°C'
    WHEN 'RWL20' THEN '+2.0°C'
    WHEN 'RWL29' THEN '+2.9°C'
    END
    AS Scenario, #RWL15, RWL20, RWL29
  CASE `Période`
    WHEN 'RWL15' THEN DATE(2030,06,01)
    WHEN 'RWL20' THEN DATE(2050,06,01)
    WHEN 'RWL29' THEN DATE(2100,06,01)
    END
    AS Horizon,
  CASE `Période`
    WHEN 'RWL15' THEN DATE(2100,06,01)
    WHEN 'RWL20' THEN DATE(2100,06,01)
    WHEN 'RWL29' THEN DATE(2100,06,01)
    END
    AS date_2100,
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
  365 - NORPXCDD AS NBRR, #nb de jours de non-sécheresse = nb de jours avec précip ?
  NORPRCPTOT AS NBJRR1,
  NORRR10D AS NBJRR10,
  NORRR100D AS NBJRR100,
  NORRx1D AS RRAB
FROM `cc-reunion.data_meteofrance.simu_all_RWL`