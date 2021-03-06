from django.conf.urls.defaults import *

import utilities

from django.contrib import admin # Django admin UI
admin.autodiscover()             # Django admin UI

urlpatterns = patterns('',
    # Repository application
    url(r'^rg/', include('opentrials.repository.urls')),

    # Tickets application
    url(r'^ticket/', include('opentrials.tickets.urls')),

    # Assistance application
    url(r'^assistance/', include('opentrials.assistance.urls')),

    # Review application
    url(r'^', include('opentrials.reviewapp.urls')),

    # Django admin UI and documentation
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^decs/', include('opentrials.decsclient.urls')),

    # django-registration views
    url(r'^accounts/', include('registration.backends.default.urls')),

    # system diagnostic views (may be disabled in production)
    url(r'^diag/', include('opentrials.diagnostic.urls')),


)

from django.conf import settings
if settings.DEBUG:
    # serve static files from develpment server
    from django.views import static
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^rosetta/', include('rosetta.urls')),
    )
