import logging
from functools import wraps

from flask import request

logger = logging.getLogger(__name__)


def token_required(real_token):
    """Decorator checks static Authorization token"""
    def decorator(f):
        f.gw_method = f.__name__

        @wraps(f)
        def wrapper(*args, **kwargs):
            token = _get_token(request)
            is_valid, message = _check_token(token, real_token)
            if not is_valid:
                logger.warning('{} Invalid token: {}: {}'.format(request.url_rule, message, token))
                return {'errors': {'auth': message}}, 401

            return f(*args, **kwargs)

        return wrapper
    return decorator


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

    if token != real_token:
        return False, "Invalid token"

    return True, 'Token is valid'
