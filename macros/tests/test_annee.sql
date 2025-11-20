{% test test_annee(model, column_name) %}

select *
from {{ model }}
where {{ column_name }} < 1900 or {{ column_name }} > 2100

{% endtest %}
