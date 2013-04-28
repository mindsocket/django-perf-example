from django.conf.urls import patterns, url

urlpatterns = patterns('perf_example.views',
    url(r'^$', 'perftest', name='home'),
    url(r'^stream/$', 'streaming_perftest', name='stream'),
    url(r'^eager/$', 'eager_streaming_perftest', name='eager'),
)
