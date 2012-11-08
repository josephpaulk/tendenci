from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models.loading import get_models
from django.db import connection, transaction


class Command(BaseCommand):
    """
    Loop through all models that are subclasses of the TendenciBaseModel
    and populate the entity with the default entity (id=1). If no entity
    exists, create one first.

    Also, check if we have a group with the same name of site
    display name and associated to the default entity (id=1).
    If not found, create one.

    Usage:
        .manage.py populate_default_entity --verbosity=2
    """
    def handle(self, *args, **options):
        from tendenci.apps.entities.models import Entity
        from tendenci.apps.user_groups.models import Group
        from tendenci.core.site_settings.utils import get_setting
        from tendenci.core.perms.models import TendenciBaseModel

        verbosity = int(options['verbosity'])

        [entity] = Entity.objects.all()[:1] or [None]
        user = User.objects.get(pk=1)

        site_display_name = get_setting('site',
                                        'global',
                                        'sitedisplayname')
        site_contact_name = get_setting('site',
                                        'global',
                                        'sitecontactname')
        site_contact_email = get_setting('site',
                                        'global',
                                        'sitecontactemail')
        site_phone_number = get_setting('site',
                                        'global',
                                        'sitephonenumber')
        site_url = get_setting('site',
                                'global',
                                'siteurl')
        # if there is no entity, create one.
        if not entity:
            entity = Entity(
                    entity_name=site_display_name,
                    entity_type='',
                    contact_name=site_contact_name,
                    phone=site_phone_number,
                    email=site_contact_email,
                    fax='',
                    website=site_url,
                    summary='',
                    notes='',
                    admin_notes='system auto created',
                    allow_anonymous_view=True,
                    creator=user,
                    creator_username=user.username,
                    owner=user,
                    owner_username=user.username,
                    status=True,
                    status_detail='active')

            entity.save()
            print 'entity created: ', entity.name

        # loop through all the tables and populate
        # the entity field only if it's null.
        sql_template = """
                    UPDATE %s
                    SET entity_id=1
                    WHERE entity_id is NULL
                """
        #cursor = connection.cursor()
        models = get_models()
        table_updated = []
        for model in models:
            if TendenciBaseModel in model.__bases__:
                if hasattr(model, 'entity'):
                    table_name = model._meta.db_table
                    for row in model.objects.all():
                        if not row.entity:
                            row.entity = entity
                            row.save()
#                    sql = sql_template % table_name
#                    model.objects.raw(sql)
#                    cursor.execute(sql)
#                    transaction.commit_unless_managed()
                    table_updated.append(table_name)

        if verbosity >= 2:
            print 'List of table updated: '
            print '\n'.join(table_updated)

        # GROUP - check if we have a group associated with
        group_exists = Group.objects.filter(
                                name=site_display_name).exists()
        if not group_exists:
            group = Group(
                          name=site_display_name,
                          entity=entity,
                          type='distribution',
                          email_recipient=site_contact_email,
                          allow_anonymous_view=True,
                          creator=user,
                          creator_username=user.username,
                          owner=user,
                          owner_username=user.username,
                          status=True,
                          status_detail='active'
                          )

            group.save()
            print 'Group created: ', group.name

        print 'All done.'
