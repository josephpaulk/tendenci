import imghdr
from os.path import splitext, basename

from tendenci.addons.locations.models import Location
from tendenci.core.perms.forms import TendenciBaseForm
from django import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _ 

from tendenci.core.base.fields import EmailVerificationField
from tendenci.core.files.utils import get_max_file_upload_size


ALLOWED_LOGO_EXT = (
    '.jpg',
    '.jpeg',
    '.gif',
    '.png'
)


class LocationForm(TendenciBaseForm):

    photo_upload = forms.FileField(label=_('Logo'), required=False)
    remove_photo = forms.BooleanField(label=_('Remove the current logo'), required=False)

    status_detail = forms.ChoiceField(
        choices=(('active','Active'),('inactive','Inactive'), ('pending','Pending'),))

    email = EmailVerificationField(label=_("Email"), required=False)

    class Meta:
        model = Location
        fields = (
        'location_name',
        'description',
        'contact',
        'address',
        'address2',
        'city',
        'state',
        'zipcode',
        'country',
        'phone',
        'fax',
        'email',
        'website',
        'latitude',
        'longitude',
        'photo_upload',
        'hq',
        'allow_anonymous_view',
        'user_perms',
        'member_perms',
        'group_perms',
        'status_detail',
        )

        fieldsets = [('Location Information', {
                      'fields': ['location_name',
                                 'description',
                                 'latitude',
                                 'longitude',
                                 'photo_upload',
                                 'hq',
                                 ],
                      'legend': ''
                      }),
                      ('Contact', {
                      'fields': ['contact',
                                 'address',
                                 'address2',
                                 'city',
                                 'state',
                                 'zipcode',
                                 'country',
                                 'phone',
                                 'fax',
                                 'email',
                                 'website'
                                 ],
                        'classes': ['contact'],
                      }),
                      ('Permissions', {
                      'fields': ['allow_anonymous_view',
                                 'user_perms',
                                 'member_perms',
                                 'group_perms',
                                 ],
                      'classes': ['permissions'],
                      }),
                     ('Administrator Only', {
                      'fields': ['status_detail'], 
                      'classes': ['admin-only'],
                    })]   
           
    def __init__(self, *args, **kwargs): 
        super(LocationForm, self).__init__(*args, **kwargs)

        if not self.user.profile.is_superuser:
            if 'status_detail' in self.fields: self.fields.pop('status_detail')

        if self.instance.logo:
            self.fields['photo_upload'].help_text = '<input name="remove_photo" id="id_remove_photo" type="checkbox"/> Remove current image: <a target="_blank" href="/files/%s/">%s</a>' % (self.instance.logo.pk, basename(self.instance.logo.file.name))
        else:
            self.fields.pop('remove_photo')

    def clean_photo_upload(self):
        photo_upload = self.cleaned_data['photo_upload']
        if photo_upload:
            extension = splitext(photo_upload.name)[1]

            # check the extension
            if extension.lower() not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError('The logo must be of jpg, gif, or png image type.')

            # check the image header
            image_type = '.%s' % imghdr.what('', photo_upload.read())
            if image_type not in ALLOWED_LOGO_EXT:
                raise forms.ValidationError('The logo is an invalid image. Try uploading another logo.')

            max_upload_size = get_max_file_upload_size()
            if photo_upload.size > max_upload_size:
                raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(max_upload_size), filesizeformat(photo_upload.size)))

        return photo_upload

    def save(self, *args, **kwargs):
        location = super(LocationForm, self).save(*args, **kwargs)

        if self.cleaned_data.get('remove_photo'):
            location.logo = None
        return location
