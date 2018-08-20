import pytest


@pytest.fixture()
def normal_user(db, django_user_model, django_username_field):
    """A Django normal user.
    This uses an existing user with username "user", or creates a new one with
    password "password".
    """
    UserModel = django_user_model
    username_field = django_username_field

    try:
        user = UserModel._default_manager.get(**{username_field: 'user'})
    except UserModel.DoesNotExist:
        extra_fields = {}
        if username_field != 'username':
            extra_fields[username_field] = 'user'
        user = UserModel._default_manager.create_user(
            'user', 'user@example.com', 'password', **extra_fields)

    return user
