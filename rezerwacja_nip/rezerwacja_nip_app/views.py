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
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from .models import Settings
from django.utils.encoding import force_str


@login_required
def user_nip_list(request):
    user_nips = NIPRecord.objects.filter(email_uzytkownika=request.user.email)
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


from django.http import HttpResponseBadRequest

def register_nip(request):
    registration_form = NIPRegistrationForm()  # Move the form instantiation outside the if-else block

    if request.method == 'POST':
        registration_form = NIPRegistrationForm(request.POST)
        nip = registration_form.data['nip']
        provided_email = registration_form.data['email']
        if not provided_email:
            messages.error(request, 'Podaj email')
            return render(request, 'registration_template.html', {'registration_form': registration_form})
        if not nip:
            messages.error(request, 'Podaj nip')
            return render(request, 'registration_template.html', {'registration_form': registration_form})


        if registration_form.is_valid():
            nazwa = registration_form.cleaned_data['nazwa']
            numer_telefonu_klienta = registration_form.cleaned_data['numer_telefonu_klienta']
            if not nazwa and not numer_telefonu_klienta:
                messages.error(request, 'Podaj numer lub nazwę.')
            else:
                user = request.user

                # Check if the user is assigned to the provided email

                try:
                    email_instance = EmailAddress.objects.get(user=user, email=provided_email)
                except EmailAddress.DoesNotExist:
                    messages.error(request, 'Brak uprawnień do tego adresu email.')
                    return render(request, 'registration_template.html', {'registration_form': registration_form})

                try:
                    # Check if the NIP already exists for any email
                    existing_nip_records = NIPRecord.objects.filter(nip=nip)

                    if existing_nip_records.exists():
                        # If the NIP exists, check expiration and status before updating
                        conflicting_record = existing_nip_records.first()

                        if conflicting_record.data_koncowa < timezone.now() or conflicting_record.status == 'Wolny do rezerwacji':
                            # Update the existing record
                            messages.success(request, 'NIP już istnieje. Aktualizuję dane.')
                            conflicting_record.nazwa = nazwa
                            conflicting_record.numer_telefonu_klienta = numer_telefonu_klienta
                            conflicting_record.data_poczatkowa = timezone.now()
                            settings_instance = Settings.objects.first()
                            expiration_days_value = settings_instance.expiration_days
                            expiration_date = timezone.now() + timedelta(days=expiration_days_value)
                            conflicting_record.data_koncowa = expiration_date
                            conflicting_record.status = 'Zarejestrowany'
                            conflicting_record.save()
                            return HttpResponseRedirect(reverse('home'))
                        else:
                            messages.error(request, 'NIP jest aktualnie zajęty. Spróbuj ponownie później.')
                    else:
                        try:
                            # If the NIP doesn't exist, create a new record
                            settings_instance = Settings.objects.first()  # Get the Settings instance
                            expiration_days_value = settings_instance.expiration_days
                            expiration_date = timezone.now() + timedelta(days=expiration_days_value)
                            NIPRecord.objects.create(
                                nip=nip,
                                email_uzytkownika=email_instance,
                                data_poczatkowa=timezone.now(),
                                data_koncowa=expiration_date,
                                nazwa=nazwa,
                                numer_telefonu_klienta=numer_telefonu_klienta
                            )
                            messages.success(request, 'NIP został zarejestrowany pomyślnie.')
                            return HttpResponseRedirect(reverse('home'))
                        except IntegrityError as e:
                            messages.error(request, 'Błąd podczas rejestracji NIP: {}'.format(str(e)))
                except EmailAddress.DoesNotExist:
                    messages.error(request, 'Błąd w bazie danych: nie znaleziono adresu email.')
        else:
            messages.error(request, 'Nieprawidłowy NIP lub numer telefonu.')

    # If the code reaches here, it means either the request method is not 'POST' or the form is not valid
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
    return len(str(nip)) == 10 and str(nip).isdigit()


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
                    NIPRecord.objects.create(nip=nip, nazwa=nazwa, email_uzytkownika=email,
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

def update_expiration_days(request, record_id):
    # Assuming you have a model named YourModel with an attribute named 'expiration_days'
    record = get_object_or_404(NIPRecord, id=record_id)

    if request.method == 'POST':
        # Handle form submission or any logic to update expiration_days
        # For example, you might have a form with a field named 'new_expiration_days'
        new_expiration_days = request.POST.get('new_expiration_days')
        record.expiration_days = new_expiration_days
        record.save()

        # Redirect to a success page or back to the admin page
        return HttpResponseRedirect(reverse('admin:your_model_change', args=[record.id]))

    # Render a template for the update_expiration_days page
    return render(request, 'update_expiration_days.html', {'record': record})



