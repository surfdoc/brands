# config_retriever/forms.py

from django import forms

class UriForm(forms.Form):
    base_uri = forms.URLField(label='Base URI')
