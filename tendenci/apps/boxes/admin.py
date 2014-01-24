from django.contrib import admin
from django.conf import settings
from django.template.defaultfilters import truncatewords_html

from tendenci.core.perms.admin import TendenciBaseModelAdmin
from tendenci.apps.boxes.models import Box
from tendenci.apps.boxes.forms import BoxForm
from tendenci.core.event_logs.models import EventLog
from tendenci.core.perms.utils import update_perms_and_save


class BoxAdmin(TendenciBaseModelAdmin):
    list_display = ('edit_link', 'pk', 'title', 'tags', 'short_content', 'admin_perms', 'admin_status', 'position')
    search_fields = ('title', 'content', 'tags',)
    list_editable = ['position']
    fieldsets = (
        (None, {'fields': ('title', 'content', 'photo_upload', 'link', 'link_title', 'tags')}),
        ('Permissions', {'fields': ('allow_anonymous_view',)}),
        ('Advanced Permissions', {'classes': ('collapse',), 'fields': (
            'user_perms',
            'member_perms',
            'group_perms',
        )}),
        ('Publishing Status', {'fields': (
            'status_detail',
        )}),
    )
    form = BoxForm
    ordering = ['-position']

    class Media:
        js = (
            '%sjs/jquery-1.6.2.min.js' % settings.STATIC_URL,
            '%sjs/jquery-ui-1.8.17.custom.min.js' % settings.STATIC_URL,
            '%sjs/admin/admin-list-reorder.js' % settings.STATIC_URL,
            '%sjs/global/tinymce.event_handlers.js' % settings.STATIC_URL,
        )
    
    def save_model(self, request, object, form, change):
        box = form.save(commit=False)
        box = update_perms_and_save(request, form, box)

        # save photo
        if 'photo_upload' in form.cleaned_data:
            photo = form.cleaned_data['photo_upload']
            if photo:
                box.save(photo=photo)

        log_defaults = {
            'instance': object,
            'action': "edit"
        }
        if not change:
            log_defaults['action'] = "add"

        # Handle a special case for bulk reordering via the list view.
        if form.changed_data != ['position']:
            EventLog.objects.log(**log_defaults)
        return object

    def admin_status(self, obj):
        return obj.obj_status
    admin_status.allow_tags = True
    admin_status.short_description = 'status'

    def admin_perms(self, obj):
        return obj.obj_perms
    admin_perms.allow_tags = True
    admin_perms.short_description = 'permission'

    def short_content(self, obj):
        return '<div style="max-width: 600px; overflow: hidden;">%s</div>' % truncatewords_html(obj.content, 30)
    short_content.allow_tags = True
    short_content.short_description = 'content'

admin.site.register(Box, BoxAdmin)
