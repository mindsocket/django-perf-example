import time
from django.shortcuts import render_to_response, stream_to_response
from django.views.generic.base import StreamingTemplateView

def stream(count=30):
    """Slow generator"""
    for _ in xrange(count):
        yield "Polo! " * 100
        time.sleep(0.1)

def broken_stream(count=20):
    """Slow generator that throws an exception"""
    for _ in xrange(count):
        yield ("%d " % _) * 100
        time.sleep(0.1)
    raise ValueError("Whups, you gone dun broken it")
    for _ in xrange(count):
        yield ("%d " % _) * 100
        time.sleep(0.1)

# standard view, 1 second in-view delay, 3 seconds of streaming data
def perftest(request, func=render_to_response, stream_func=stream, template="index.html"):
    # Simulate some slow work
    time.sleep(1)
    # Now render
    return func(template, { 'range': stream_func() })

# stream_to_response version - still affected by initial 1 second delay
def streaming_perftest(request, template="index.html", **kwargs):
    result = perftest(request, func=stream_to_response, template=template, **kwargs)
    return result

# eager streamed version, only streams template body as middleware has already streamed header
def eager_streaming_perftest(request):
    return streaming_perftest(request, template="body.html")
eager_streaming_perftest.eager_streaming = True

# broken versions to test 500 error handling
def broken_perftest(request):
    return perftest(request, stream_func=broken_stream)

def broken_streaming_perftest(request):
    return streaming_perftest(request, stream_func=broken_stream)

def broken_eager_streaming_perftest(request):
    return streaming_perftest(request, template="body.html", stream_func=broken_stream)
broken_eager_streaming_perftest.eager_streaming = True

# generic views version
class StreamingTemplatePerformanceTestView(StreamingTemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        time.sleep(1)
        return { 'range': stream() }

def generic_stream(request):
    return StreamingTemplatePerformanceTestView.as_view()(request)

def eager_generic_stream(request):
    return StreamingTemplatePerformanceTestView.as_view(template_name="body.html")(request)
eager_generic_stream.eager_streaming = True

