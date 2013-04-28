import time
from django.shortcuts import render_to_response, stream_to_response

def stream(count=50):
    for _ in xrange(count):
        yield "Polo! " * 100
        time.sleep(0.1)

# standard view, 1 second in-view delay, 5 seconds of streaming data
def perftest(request, func=render_to_response, template="index.html"):
    # Simulate some slow work
    time.sleep(1)
    # Now render
    return func("index.html", { 'range': stream() })

# stream_to_response version - still affected by initial 1 second delay
def streaming_perftest(request, template="index.html"):
    return perftest(request, func=stream_to_response, template=template)

# eager streamed version, only streams template body as middleware has already streamed header
def eager_streaming_perftest(request):
    return streaming_perftest(request, template="body.html")
eager_streaming_perftest.eager_streaming = True
