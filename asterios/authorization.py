from aiohttp_security.abc import AbstractAuthorizationPolicy, AbstractIdentityPolicy
from basicauth import decode


class AuthorizationPolicy(AbstractAuthorizationPolicy):

    PERMISSIONS = {
        'superuser': (
            'gameconfig.create',
            'gameconfig.update',
            'gameconfig.delete'
        )
    }

    def __init__(self, user_map):
        super().__init__()
        self.user_map = user_map

    async def authorized_userid(self, identity):
        """Retrieve authorized user id.
        Return the user_id of the user identified by the identity
        or 'None' if no user exists related to the identity.
        """
        if identity in self.user_map:
            return identity
        return None

    async def permits(self, identity, permission, context=None):
        """Check user permissions.
        Return True if the identity is allowed the permission in the
        current context, else return False.
        """
        # pylint: disable=unused-argument
        user = self.user_map.get(identity)
        if not user:
            return False

        return permission in self.PERMISSIONS[user['role']]


class BasicAuthIdentityPolicy(AbstractIdentityPolicy):
    """
    Remember and forget are not implemented because we
    don't use session or cookies
    """

    def __init__(self, user_map):
        super().__init__()
        self.user_map = user_map

    async def identify(self, request):
        value = request.headers.get('Authorization')
        if not value:
            return None

        user, password = decode(value)
        if user in self.user_map \
                and self.user_map[user]['password'] == password:
            return user
        return None

    async def remember(self, request, response, identity, **kwargs):
        return None

    async def forget(self, request, response, identity, **kwargs):
        return None
