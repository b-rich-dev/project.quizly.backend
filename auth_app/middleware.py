class JWTAuthCookieMiddleware:
    """Middleware to extract JWT access token from cookies and set it in the Authorization header."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        access_token = request.COOKIES.get("access")
        if access_token:
            request.META["HTTP_AUTHORIZATION"] = f"Bearer {access_token}"
        return self.get_response(request)
    