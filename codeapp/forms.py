from django import forms

class CodeUploadForm(forms.Form):
    code_file = forms.FileField(label='', required=True)
