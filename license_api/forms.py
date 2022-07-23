from dataclasses import field
from django import forms
from license_api.models import UpdateFile, UserDetails


class UserForm(forms.ModelForm):

    class Meta:
        model = UserDetails
        fields = [
            "licenseActivated",
        ]

        widgets = {
            'licenseActivated': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input ms-auto'
                }
            )
        }


class AppForm(forms.ModelForm):
    class Meta:
        model = UpdateFile
        fields = [
            "appFile", "appVersion"
        ]

        widgets = {
            "appVersion": forms.TextInput(
                attrs={
                    'class': "form-control"
                }
            ),
            "appFile": forms.FileInput()
        }

        # widgets = {
        #     "appFile": forms.FileInput(attr={
        #         'class': ''
        #     })
        # }
