WITH CTE AS (
SELECT 
    ANNEE AS annee,
    MOIS AS mois,
    -- On garde AAAAMM pour le tri ou l'affichage chronologique
    AAAAMM AS date_key, 

    -- Somme des précipitations pour la période donnée
    AVG(RR) AS Cumul_Mensuel_Pluie_Total,

    --  'NBRR', c'est le nombre de jours de pluie

    -- RRAB précipitation maximale tombée en 24 heures au cours du mois (Average)
    AVG(RRAB) AS Cumul_MAxi_par_mois,

    -- Nombre de jours > 100mm
    AVG(NBJRR100) AS Nb_Jours_Sup_100mm

FROM `cc-reunion.data_meteofrance.stg_mensq_pluviometrie`
-- Indispensable pour fusionner les données de toutes les stations par mois
GROUP BY 
    ANNEE, 
    MOIS, 
    AAAAMM

-- Tri par ordre chronologique (ce qui réglera aussi ton problème de tri dans le graph)
ORDER BY 
    AAAAMM ASC
)

SELECT *
FROM CTE
WHERE Nb_Jours_Sup_100mm > 1
