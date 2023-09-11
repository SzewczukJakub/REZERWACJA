from django import forms
from django.core.exceptions import ValidationError


class NIPRegistrationForm(forms.Form):
    email = forms.EmailField(label='email_klienta')
    nip = forms.CharField(label='NIP')
    nazwa= forms.CharField(label='nazwa')
    numer_telefonu_klienta= forms.CharField(label='Numer telefonu klienta', required=False)

    def clean_numer_telefonu_klienta(self):
        numer_telefonu_klienta = self.cleaned_data.get('numer_telefonu_klienta')

        # Jeśli numer telefonu nie został podany, to jest poprawny (opcjonalny)
        if not numer_telefonu_klienta:
            return numer_telefonu_klienta

        # Usunięcie spacji i myślników, aby pozostały tylko cyfry
        cleaned_numer_telefonu = ''.join(filter(str.isdigit, numer_telefonu_klienta))

        # Sprawdzenie, czy numer telefonu ma dokładnie 9 cyfr
        if len(cleaned_numer_telefonu) != 9:
            raise forms.ValidationError('Numer telefonu musi zawierać dokładnie 9 cyfr.')

        return cleaned_numer_telefonu

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
