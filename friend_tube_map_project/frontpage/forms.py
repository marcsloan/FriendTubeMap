from django import forms
from django.forms import ModelForm
from frontpage.models import SocialData

class UploadFileForm(forms.Form):
#class UploadFileForm(ModelForm):
    #path = forms.CharField(required=False)
    docfile = forms.FileField(label='docfile')
    #class Meta:
    #    model = SocialData
    # title = forms.CharField(max_length=50)
    # file = forms.FileField(label='docFile')
    # docfile = forms.FileField(
    #     label='Select a file',
    #     help_text='max. 42 megabytes')