try:
    from django.conf.urls import patterns
except:
    from django.conf.urls.defaults import patterns

urlpatterns = patterns(
    'django_test.views',
    ('^regular_form/$', 'regular_form'),
    ('^regular_form/(?P<id>\d+)/$', 'regular_form_edit'),
    ('^model_form/$', 'model_form'),
    ('^model_form/(?P<id>\d+)/$', 'model_form_edit'),
    
)
