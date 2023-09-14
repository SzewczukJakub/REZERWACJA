from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import NIPRegistrationForm, AdminLoginForm
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import AdminLoginForm
from .models import NIPRecord
from .decorators import admin_required
from .models import EmailAddress
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect
import pandas as pd
from django.http import HttpResponse

@login_required
def user_nip_list(request):
    user_nips = NIPRecord.objects.filter(email_klienta=request.user.email)
    return render(request, 'user_nip_list.html', {'user_nips': user_nips})

@admin_required
def admin_nip_list(request):
    all_nips = NIPRecord.objects.all()
    return render(request, 'admin_nip_list.html', {'all_nips': all_nips})

@admin_required
def admin_panel(request):
    emails = EmailAddress.objects.all()
    nips = NIPRecord.objects.all()
    return render(request, 'admin_panel.html', {'emails': emails, 'nip_records': nips})


@admin_required
def nip_list(request):
    records = NIPRecord.objects.all()
    emails = EmailAddress.objects.all()

    if request.method == 'POST':
        for email in emails:
            email_id = email.id
            new_email = request.POST.get(f'email_{email_id}')
            email.email = new_email
            email.save()
        for record in records:
            email = request.POST.get(f'email_{record.id}')
            #status = request.POST.get(f'status_{record.id}')
            expiration = request.POST.get(f'expiration_{record.id}')

            record.email = email
            #record.status = status
            record.expiration = expiration
            record.save()

        return redirect('admin_panel')  # Przekierowanie z powrotem do panelu admina

    return render(request, 'admin_panel.html', {'records': records})




def admin_login(request):
    if request.method == 'POST':
        login_form = AdminLoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user and user.is_staff:
                login(request, user)
                return redirect('admin_panel')  # Przekierowanie do panelu administratora
    else:
        login_form = AdminLoginForm()
    return render(request, 'admin_login.html', {'login_form': login_form})


def login_view(request):
    if request.method == 'POST':
        login_form = AuthenticationForm(request, data=request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('/admin' if user.is_staff else '/user_nip_list')

        # Jeśli dane logowania są nieprawidłowe, przekieruj z komunikatem o błędzie
        return render(request, 'login.html',
                      {'login_form': login_form, 'error_message': 'Nieprawidłowe dane logowania.'})

    else:
        login_form = AuthenticationForm()

    return render(request, 'login.html', {'login_form': login_form})
def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/admin')
        else:
            return redirect('user_nip_list')
    else:
        registration_form = NIPRegistrationForm()
        return redirect('login_view')  # Przekieruj do strony logowania

from .models import NIPRecord

def register_nip(request):
    if request.method == 'POST':
        registration_form = NIPRegistrationForm(request.POST)
        if registration_form.is_valid():
            email = registration_form.cleaned_data['email']
            nip = registration_form.cleaned_data['nip']

            try:
                email_instance = EmailAddress.objects.get(email=email)

                # Sprawdź, czy numer NIP jest prawidłowy (10 cyfr)
                if not validate_nip(nip):
                    messages.error(request, 'Numer NIP musi składać się z 10 cyfr.')
                else:
                    # Sprawdź, czy numer NIP już istnieje w bazie danych
                    existing_nip_record = NIPRecord.objects.filter(nip=nip).first()
                    if existing_nip_record:
                        # Jeśli istniejący numer NIP ma inny adres e-mail, wyświetl tylko status
                        if existing_nip_record.email_klienta != email_instance:
                            status = existing_nip_record.current_status()
                            messages.error(request, f'Status NIP: {status}')
                        else:
                            # Jeśli istniejący numer NIP jest przypisany do tego samego e-maila,
                            # wyświetl wszystkie dostępne dane o tym numerze NIP
                            status = existing_nip_record.current_status()
                            reservation_date = existing_nip_record.data_poczatkowa
                            expiration_date = existing_nip_record.data_koncowa
                            messages.error(request, f'Ten numer NIP jest już przypisany do tego adresu email. '
                                                   f'Status: {status}, '
                                                   f'Rezerwacja od: {reservation_date}, '
                                                   f'Ważny do: {expiration_date}')
                    else:
                        expiration_date = timezone.now() + timedelta(days=60)

                        NIPRecord.objects.create(
                            nip=nip,
                            email_klienta=email_instance.email,
                            data_poczatkowa=timezone.now(),
                            data_koncowa=expiration_date
                        )
                        messages.success(request, 'NIP został zarejestrowany pomyślnie.')
                        return HttpResponseRedirect(reverse('home'))
            except EmailAddress.DoesNotExist:
                messages.error(request, 'Adres email nie istnieje w bazie danych.')
    else:
        registration_form = NIPRegistrationForm()

    return render(request, 'registration_template.html', {'registration_form': registration_form})



def check_nip_status(request):
    if request.method == 'POST':
        email = request.POST['email']
        nip = request.POST['nip']

        if EmailAddress.objects.filter(email=email).exists():
            try:
                nip_record = NIPRecord.objects.get(nip=nip, email=email)
                status = nip_record.status
                messages.info(request, f'Status NIP: {status}')
            except NIPRecord.DoesNotExist:
                messages.error(request, 'Nie znaleziono rekordu NIP.')
        else:
            messages.error(request, 'Adres email nie istnieje w bazie danych.')

    return redirect('home')  # Adjust the URL here

def validate_nip(nip):
    return len(nip) == 10 and nip.isdigit()


def import_records(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']

        # Check if the uploaded file has the .xlsx extension
        if uploaded_file.name.endswith('.xlsx'):
            try:
                # Read the Excel file into a DataFrame
                df = pd.read_excel(uploaded_file)

                # Process and save data to the NIPRecord model
                for index, row in df.iterrows():
                    nip = row['nip']
                    nazwa = row['nazwa']
                    email = row['email']
                    numer_telefonu = row['numer_telefonu']

                    # Create a new NIPRecord instance and save it
                    NIPRecord.objects.create(nip=nip, nazwa=nazwa, email_klienta=email,
                                             numer_telefonu_klienta=numer_telefonu)

                return HttpResponse('Import zakończony pomyślnie.')
            except Exception as e:
                return HttpResponse(f'Błąd podczas importowania danych: {str(e)}')
        else:
            return HttpResponse('Niewłaściwy format pliku. Zaimportuj plik Excel w formacie .xlsx.')

    return render(request, 'admin/import_records.html')

def export_records(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="rekordy_nip.xlsx"'

    # Wczytaj dane do DataFrame przy użyciu pandas
    df = pd.DataFrame(NIPRecord.objects.all().values())

    # Eksportuj dane do pliku Excel
    df.to_excel(response, index=False, engine='openpyxl')

    return response
