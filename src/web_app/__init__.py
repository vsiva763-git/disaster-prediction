"""
Web Application Module
Flask-based web interface and REST API
"""

from .app import create_app


def register_api_routes(app):
	from .api_routes import register_api_routes as _register_api_routes
	return _register_api_routes(app)

__all__ = ['create_app', 'register_api_routes']
