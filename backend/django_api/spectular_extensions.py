"""
Custom drf-spectacular extensions for better API documentation
"""

from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object


class SupabaseJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    """
    Custom authentication scheme for Supabase JWT Authentication
    """
    target_class = 'django_api.authentication.SupabaseJWTAuthentication'
    name = 'bearerAuth'
    priority = -1

    def get_security_definition(self, auto_schema):
        """
        Return the security definition for Supabase JWT authentication
        """
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            'description': 'JWT token obtained from login endpoint. Format: Bearer <your_token>'
        }

    def get_security_requirement(self, auto_schema):
        """
        Return the security requirement for endpoints using this authentication
        """
        return {self.name: []}