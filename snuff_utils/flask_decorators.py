import logging
from functools import wraps

from flask import request

logger = logging.getLogger(__name__)


def token_required(real_token):
    """Decorator checks Bearer (static) Authorization token

    Usage:
    import os

    from dotenv import load_dotenv
    from flask_restful import Resource
    from snuff_utils.flask_decorators import token_required

    # Get token from .env file
    load_dotenv()
    MY_TOKEN = os.getenv('MY_TOKEN', '')


    class CallbackEvents(Resource):

        @token_required(MY_TOKEN)
        def post(self):
            # some code here
            return {}
    """
    def decorator(f):
        f.gw_method = f.__name__

        @wraps(f)
        def wrapper(*args, **kwargs):
            def _get_token(request):
                """Gets token from request"""
                token = request.headers.get("Authorization")
                if not token and request.method == "GET":
                    token = request.args.get("token")
                elif request.method in ["POST", "PUT"]:
                    token = request.headers.get("Authorization")

                return token

            def _check_token(token, real_token):
                """Checks token"""
                if not token:
                    return False, "No token provided"

                if token != real_token and token != f'Bearer {real_token}':
                    return False, "Invalid token"

                return True, 'Token is valid'

            token = _get_token(request)
            is_valid, message = _check_token(token, real_token)
            if not is_valid:
                logger.warning('{} Invalid token: {}: {}'.format(request.url_rule, message, token))
                return {'errors': {'auth': message}}, 401

            return f(*args, **kwargs)
        return wrapper
    return decorator
