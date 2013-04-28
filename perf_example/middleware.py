from django.http import StreamingHttpResponse
from django.core.cache import cache
from django.template.loader import stream
from django.conf import settings
from django.core.handlers.base import BaseHandler

def stream_cached(cache_key, template):
    cached_header = cache.get(cache_key)
    if cached_header:
        yield cached_header
    else:
        chunks = []
        for chunk in stream(template):
            chunks.append(chunk)
            yield chunk
        cache.set(cache_key, ''.join(chunks))

def stream_early_view(view, request, *args, **kwargs):
    for chunk in stream_cached("EAGER_STREAMING_HEADER", getattr(settings, 'EAGER_STREAMING_HEADER_TEMPLATE', 'header.html')):
        yield chunk

    response = view(request, *args, **kwargs)
    if response.streaming:
        for chunk in response.streaming_content:
            yield chunk
    else:
        yield response.content

    for chunk in stream_cached("EAGER_STREAMING_FOOTER", getattr(settings, 'EAGER_STREAMING_FOOTER_TEMPLATE', 'footer.html')):
        yield chunk

class EagerStreamingResponseMiddleware():
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if getattr(callback, 'eager_streaming', False):
            wrapped_callback = BaseHandler().make_view_atomic(callback)
            return StreamingHttpResponse(stream_early_view(wrapped_callback, request, *callback_args, **callback_kwargs))
        else:
            return None
