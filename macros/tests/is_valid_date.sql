-- Retourne les lignes invalides, donc si le test renvoie quelque chose = test FAIL
{% test is_valid_date(model, column_name) %}

select *
from {{ model }}
where {{ column_name }} is null
   or {{ column_name }} < date('1900-01-01')
   or {{ column_name }} > date('2100-12-31')

{% endtest %}

