-- remove RR_ME column due to 98.6% of NULL values
-- parse date AAAAMM

SELECT 
  NUM_POSTE,
  PARSE_DATE('%Y%m%d',CONCAT(AAAAMM,'01'))
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
from {{ source('data_meteofrance', 'MENSQ_974_1900-2025') }}