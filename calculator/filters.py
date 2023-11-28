from django.db.models.lookups import IntegerGreaterThanOrEqual, IntegerLessThan
import django_filters
from django_filters import DateFilter, NumberFilter
from .models import *

class FlatFilter(django_filters.FilterSet):
    start_area = NumberFilter(field_name = 'area', lookup_expr = 'gte')
    end_area = NumberFilter(field_name = 'area', lookup_expr = 'lte')
    start_date = DateFilter(field_name = 'append_date', lookup_expr = 'gte')
    end_date = DateFilter(field_name = 'append_date', lookup_expr = 'lte')
    class Meta:
        model = Flat
        fields = '__all__'
        exclude = ['building', 'created_date', 'append_date', 'area', 'appltypes', 'lastyr_units', 'twoyrbfr_units', 'threeyrbfr_units', 'solarreport']
