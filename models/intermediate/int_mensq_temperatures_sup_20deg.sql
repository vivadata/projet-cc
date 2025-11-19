WITH nuit_par_station AS (
  SELECT
      t.NUM_POSTE,
      sz.Z_GEO,
      t.ANNEE,
      SUM(t.NBJTNS20) AS nuits_ge_20_par_station
FROM `cc-reunion.data_meteofrance.stg_mens_temperatures` t
JOIN `cc-reunion.MENS_meteofrance.stations_zones` sz
      ON t.NUM_POSTE = sz.NUM_POSTE
  GROUP BY t.NUM_POSTE, sz.Z_GEO, t.ANNEE
),

par_zone AS (
  SELECT
      ANNEE,
      Z_GEO,
      COUNT(*) AS nb_stations,
      AVG(nuits_ge_20_par_station) AS moy_nuits_ge_20
  FROM nuit_par_station
  GROUP BY ANNEE, Z_GEO
)

SELECT *
FROM par_zone
ORDER BY ANNEE, Z_GEO