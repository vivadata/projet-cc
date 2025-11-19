-- remove RR_ME column due to 98.6% of NULL values
-- parse date AAAAMM
-- extract year and month from AAAAMM
-- remove lines where quality codes = 2 (= not validated)
-- exclude data before 1952 because data is very sparse

SELECT 
    NUM_POSTE,
    PARSE_DATE('%Y%m%d', CONCAT(AAAAMM,'01')) AS AAAAMM,
    EXTRACT(YEAR FROM PARSE_DATE('%Y%m%d', CONCAT(AAAAMM,'01'))) AS ANNEE,
    EXTRACT(MONTH FROM PARSE_DATE('%Y%m%d', CONCAT(AAAAMM,'01'))) AS MOIS,    
    RR,
    QRR,
    NBRR,
    RRAB,
    QRRAB,
    RRABDAT,
    NBJRR1,
    NBJRR5,
    NBJRR10,
    NBJRR30,
    NBJRR50,
    NBJRR100 
FROM {{ source('data_meteofrance', 'MENSQ_974_1900-2025') }}
WHERE QRR != 2
AND QRRAB != 2
AND ANNEE >= 1952
