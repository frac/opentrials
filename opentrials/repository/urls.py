from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_detail, object_list

from repository.models import ClinicalTrial

from repository.views import edit_trial_index, full_view, index, step_1, step_2, step_3
from repository.views import step_4, step_5, step_6, step_7, step_8, step_9, new_institution
from repository.views import list_all, trial_registered, trial_view


info_dict_xml = {
    'queryset': ClinicalTrial.objects.all(),
    'template_name': 'repository/clinicaltrial_detail.xml',
    'mimetype': 'text/xml',
}

urlpatterns = patterns('',
    url(r'^list/$', list_all, name='repository.list_all'),
    url(r'^edit/(\d+)/$', edit_trial_index, name='repository.edittrial'),
    url(r'^view/(?P<trial_pk>\d+)/$', trial_view, name='repository.trialview'),
    url(r'^xml/(?P<object_id>\d+)/$', object_detail, info_dict_xml,
        name='repository.xml'),
    url(r'^new_institution/$', new_institution, name='new_institution'),
    url(r'^step_1/(\d+)/$', step_1, name='step_1'),
    url(r'^step_2/(\d+)/$', step_2, name='step_2'),
    url(r'^step_3/(\d+)/$', step_3, name='step_3'),
    url(r'^step_4/(\d+)/$', step_4, name='step_4'),
    url(r'^step_5/(\d+)/$', step_5, name='step_5'),
    url(r'^step_6/(\d+)/$', step_6, name='step_6'),
    url(r'^step_7/(\d+)/$', step_7, name='step_7'),
    url(r'^step_8/(\d+)/$', step_8, name='step_8'),
    url(r'^step_9/(\d+)/$', step_9, name='step_9'),
    #public
    url(r'^(?P<trial_id>[0-9A-Za-z-]+)/$', trial_registered, name='repository.trial_registered'),
    url(r'^$', index, name='repository.index'),
)
