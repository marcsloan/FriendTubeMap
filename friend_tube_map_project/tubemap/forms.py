__author__ = 'marc'

from django import forms
from tubemap.models import Feedback

class FeedbackForm(forms.ModelForm):
    #whatLiked = forms.CharField(max_length=2000, help_text="Please write what you liked about the website")
    whatLiked = forms.CharField(max_length = 2000, widget=forms.Textarea, help_text="Please write what you liked about the website")

    whatWrong = forms.CharField( widget=forms.Textarea,max_length=2000, help_text="Please write what you didn't like")
    generalComment = forms.CharField( widget=forms.Textarea,max_length=2000, help_text="Any other comments?")


    # An inline class to provide additional information on the form.
    class Meta:
        # Provide an association between the ModelForm and a model
        model = Feedback

