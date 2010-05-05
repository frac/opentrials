# coding: utf-8

from clinicaltrials.reviewapp.models import Attachment
from django import forms
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User

from repository.models import Institution, CountryCode

ACCESS = [
    ('public', 'Public'),
    ('private', 'Private'),
]


class InitialTrialForm(forms.Form):
    form_title = _('Initial Trial Data')
    scientific_title = forms.CharField(widget=forms.Textarea, label=_('Scientific Title'), max_length=2000)
    recruitment_country = forms.MultipleChoiceField(choices=((cc.pk,cc.description) for cc in CountryCode.objects.iterator()) )

class PrimarySponsorForm(forms.ModelForm):
    class Meta:
        model = Institution
        exclude = ['address']
    form_title = _('Primary Sponsor')

class ExistingAttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        exclude = ['submission']

    title = _('Existing Attachment')
    file = forms.CharField(required=False,label=_('File'),max_length=255)

class NewAttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file','description','submission','public']

    title = _('New Attachment')
    submission = forms.CharField(widget=forms.HiddenInput,required=False)

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','email']

    title = _('User Profile')

class UploadTrial(forms.Form):
    submission_xml = forms.CharField(widget=forms.FileInput,required=True)
