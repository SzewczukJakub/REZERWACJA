from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.contrib import messages
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


def validate_ten_digit_nip(value):
    if len(str(value)) != 10:
        raise ValidationError(_('NIP must be a 10-digit number.'), code='invalid_nip')

def validate_nine_digit_phone(value):
    if len(str(value)) != 9:
        raise ValidationError(_('Numer telefonu musi mieć dziewięć cyfr'), code='invalid_numer_telefonu')

class NIPRegistrationForm(forms.Form):
    email = forms.EmailField(label='email_uzytkownika')
    nip = forms.IntegerField(
        validators=[validate_ten_digit_nip],
        label='NIP'
    )
    nazwa= forms.CharField(label='nazwa',required=False)
    numer_telefonu_klienta= forms.IntegerField(
        validators=[validate_nine_digit_phone],
        label='Numer telefonu klienta',
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data.get('nazwa')
        cleaned_data.get('numer_telefonu_klienta')
        return cleaned_data

    def dataEmailNip(self):
        data=super()
        data.get('email')
        data.get('nip')
        return data


class AdminLoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class NIPRecordImportForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        file = self.cleaned_data['file']
        if not file.name.endswith('.xlsx'):
            raise ValidationError('Należy załadować plik Excela (rozszerzenie .xlsx).')
        return file
