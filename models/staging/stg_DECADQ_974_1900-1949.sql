select
  *
from {{ source('data_meteofrance', 'DECADQ_974_1900-1949') }}