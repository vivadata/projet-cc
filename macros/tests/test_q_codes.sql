{% test test_q_codes(model) %}

select *
from {{ model }}
where QTX = 2
   or QTXAB = 2
   or QTXMIN = 2
   or QTN = 2
   or QTNAB = 2
   or QTNMAX = 2
   or QTAMPLIM = 2
   or QTAMPLIAB = 2
   or QTMM = 2
   or QTMMIN = 2
   or QTMMAX = 2

{% endtest %}
