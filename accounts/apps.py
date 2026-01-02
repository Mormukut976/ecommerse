from django.apps import AppConfig
from django.db.models.signals import post_migrate


def ensure_store_groups(sender, **kwargs):
    if sender.label not in {'auth', 'catalog', 'orders', 'payments'}:
        return

    from django.contrib.auth.models import Group, Permission

    store_perms = Permission.objects.filter(content_type__app_label__in=['catalog', 'orders', 'payments'])
    auth_user_perms = Permission.objects.filter(content_type__app_label='auth', content_type__model='user')

    store_admin, _ = Group.objects.get_or_create(name='Store Admin')
    store_staff, _ = Group.objects.get_or_create(name='Store Staff')

    store_staff.permissions.add(*store_perms)
    store_admin.permissions.add(*store_perms, *auth_user_perms)


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        post_migrate.connect(ensure_store_groups, dispatch_uid='accounts.ensure_store_groups')
