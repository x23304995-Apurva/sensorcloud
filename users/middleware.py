class DisableDjangoAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Clear any Django auth user before processing the request
        if hasattr(request, 'user'):
            request.user = None
        response = self.get_response(request)
        return response