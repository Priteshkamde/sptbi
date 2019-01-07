import django_filters
from hire.models import JobPost


class JobFilter(django_filters.FilterSet):
    class Meta:
        model = JobPost
        fields = ['job_type', 'intake', 'duration']
