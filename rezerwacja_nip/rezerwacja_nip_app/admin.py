from django.contrib import admin
import csv
import pandas as pd
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from django.urls import path
from .forms import NIPRecordImportForm
from .models import NIPRecord, EmailAddress
from django.shortcuts import render
from django_object_actions import DjangoObjectActions
from .models import User
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_str

class CustomLogEntryAdmin(admin.ModelAdmin):
    list_display = ['action_time', 'user', 'content_type', 'object_repr', 'change_message']

class NIPRecordAdmin(admin.ModelAdmin):
    list_display = (
        'nip', 'nazwa', 'email_uzytkownika', 'numer_telefonu_klienta', 'data_poczatkowa', 'data_koncowa', 'status')
    list_filter = ('email_uzytkownika', 'status','nazwa')
    search_fields = ('nip', 'nazwa', 'email_uzytkownika', 'numer_telefonu_klienta')

    actions = ['export_selected_records']

    def import_records_button(self):
        return format_html(
            '<a class="button" href="{}">Importuj dane z CSV</a>',
            reverse('admin:import_records')  # Use the appropriate URL name for the import view
        )

    import_records_button.short_description = "Importuj dane z CSV"

    def import_records(self, request):
        if request.method == 'POST':
            uploaded_file = request.FILES.get('file')

            if uploaded_file:
                if uploaded_file.name.endswith('.csv'):
                    try:
                        df = pd.read_csv(uploaded_file, encoding='utf-8-sig')

                        denied_records = []  # Store denied NIP records
                        successful_imports = 0

                        # Pobierz użytkownika wykonującego import
                        user = request.user

                        for index, row in df.iterrows():
                            nip = row['nip']
                            nazwa = row['nazwa']
                            email = row['email_uzytkownika']
                            numer_telefonu = row['numer_telefonu_klienta']
                            data_poczatkowa = row.get('data_poczatkowa', None)

                            # Check if the NIP record already exists
                            if NIPRecord.objects.filter(nip=nip).exists():
                                denied_records.append(f"{nip} (Ten Nip jest już zajęty)")
                            else:
                                try:
                                    # Check if data_poczatkowa is provided
                                    if data_poczatkowa is not None:
                                        data_poczatkowa = pd.to_datetime(data_poczatkowa)
                                        if data_poczatkowa == pd.NaT:
                                            raise ValueError("Invalid or empty data_poczatkowa")
                                    else:
                                        raise ValueError("data_poczatkowa is required")

                                    NIPRecord.objects.create(nip=nip, nazwa=nazwa, email_uzytkownika=email,
                                                             numer_telefonu_klienta=numer_telefonu,
                                                             data_poczatkowa=data_poczatkowa)

                                    # Dodaj wpis do logów administracyjnych
                                    LogEntry.objects.log_action(
                                        user_id=user.id,
                                        content_type_id=ContentType.objects.get_for_model(NIPRecord).pk,
                                        object_id=None,
                                        object_repr=force_str('Import danych NIP'),
                                        action_flag=CHANGE,
                                        change_message=f'Import danych NIP z pliku CSV. Dodano rekord o NIP: {nip}',
                                    )

                                    successful_imports += 1
                                except Exception as e:
                                    # Handle the specific error related to missing data_poczatkowa
                                    denied_records.append(f"{nip} (data_poczatkowa jest wymagana)")

                        if successful_imports > 0:
                            denied_nips_str = ', '.join(map(str, denied_records))
                            return HttpResponse(f"Import completed. Imported {successful_imports} records. Denied NIPs: {denied_nips_str}")
                        elif denied_records:
                            denied_nips_str = ', '.join(map(str, denied_records))
                            return HttpResponse(f"Import failed. Denied NIPs: {denied_nips_str}")
                        else:
                            return HttpResponse("No records were imported.")
                    except ValueError as ve:
                        # Handle the specific error related to invalid or empty data_poczatkowa
                        denied_records.append(f"{nip} (data_poczatkowa is required)")
                    except Exception as e:
                        return HttpResponse(f"Error importing NIP records: {e}")
                else:
                    return HttpResponse('Invalid file format. Please import a CSV file.')

        return render(request, 'admin/import_records.html')

    def import_users(request):
        if request.method == 'POST':
            uploaded_file = request.FILES.get('file')

            if uploaded_file:
                if uploaded_file.name.endswith('.csv'):
                    try:
                        df = pd.read_csv(uploaded_file, encoding='utf-8-sig')

                        for index, row in df.iterrows():
                            # Process and save user data to the User model
                            user_data = {
                                'username': row['username'],
                                'email': row['email'],
                                # Add other user data fields here
                            }
                            user, created = User.objects.get_or_create(email=user_data['email'], defaults=user_data)
                            if not created:
                                # User with the same email already exists, handle it as needed
                                # For example, you can update the existing user or log the conflict
                                pass

                        return HttpResponse("User import completed successfully.")
                    except Exception as e:
                        return HttpResponse(f"Error importing users: {e}")
                else:
                    return HttpResponse('Invalid file format. Please import a CSV file.')
            else:
                return HttpResponse('No file selected.')

        return render(request, 'admin/import_users.html')


    def export_selected_records(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="nip_records.csv"'

        writer = csv.writer(response)
        writer.writerow(['nip', 'nazwa', 'email_uzytkownika', 'numer_telefonu_klienta', 'data_poczatkowa', 'data_koncowa', 'status'])

        for record in queryset:
            writer.writerow([record.nip, record.nazwa, record.email_uzytkownika, record.numer_telefonu_klienta,
                             record.data_poczatkowa, record.data_koncowa, record.status])

        return response

    export_selected_records.short_description = "Eksportuj zaznaczone rekordy"

    def get_urls(self):
        urlpatterns = super().get_urls()
        custom_urls = [
            path('import_records/', self.import_records, name='import_records'),
            path('import_users/', self.import_users, name='import_users'),
        ]
        return custom_urls + urlpatterns

admin.site.register(NIPRecord, NIPRecordAdmin)
admin.site.register(EmailAddress)
admin.site.register(LogEntry, CustomLogEntryAdmin)

from .models import Settings
admin.site.register(Settings)
