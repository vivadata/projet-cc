{% test test_mois(model, column_name) %}

select *
from {{ model }}
where {{ column_name }} < 1 or {{ column_name }} > 12

{% endtest %}
