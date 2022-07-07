from django import forms
from license_api.models import UserDetails


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
