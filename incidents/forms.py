from django import forms


class DocumentUploadForm(forms.Form):
    docfile = forms.FileField(label='Select a file: ')
