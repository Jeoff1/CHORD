from django.http import Http404

from . import services


class ModuleGateMiddleware:
    """Refuse every URL of a disabled module with a 404.

    Modules are identified by their top-level URL namespace. This only hides
    disabled modules; each view still enforces its own permissions.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        namespaces = request.resolver_match.namespaces
        if namespaces and not services.is_module_enabled(namespaces[0]):
            raise Http404("This module is disabled for this church.")
        return None
