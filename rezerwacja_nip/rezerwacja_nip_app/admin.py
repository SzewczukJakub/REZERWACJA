from django.contrib import admin
import csv
import pandas as pd
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from django.urls import path
from django.utils.timezone import localtime

from .forms import NIPRecordImportForm
from .models import NIPRecord, EmailAddress
from django.shortcuts import render
from django_object_actions import DjangoObjectActions
from .models import User
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_str
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='import_log.txt', level=logging.DEBUG)

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
                        df = pd.read_csv(uploaded_file, dtype={'numer_telefonu_klienta': str})
                        df = df[~df['nip'].astype(str).str.startswith('#')]
                        df.columns = df.columns.str.strip()
                        print(df)
                        denied_records = []
                        successful_imports = 0

                        user = request.user

                        # Ensure that 'nip' column exists in the DataFrame
                        if 'nip' not in df.columns:
                            return HttpResponse("Error: 'nip' column not found in the CSV file.")

                        for index, row in df.iterrows():
                            try:
                                nip = row['nip']  # Correctly reference the 'nip' column
                                logging.debug(f'nip: {nip}')
                                name = row['nazwa']
                                email = row['email_uzytkownika']
                                phone_number = str(row['numer_telefonu_klienta']).strip()
                                logging.debug(f'Type of phone_number: {type(phone_number)}')
                                start_date = row.get('data_poczatkowa', None)
                                end_date = row.get('data_koncowa', None)

                                if not name and not phone_number:
                                    denied_records.append(f"{nip} (Both name and phone_number are empty)")
                                    continue

                                if name and not phone_number:
                                    phone_number = None

                                if phone_number and not name:
                                    name = None

                                if NIPRecord.objects.filter(nip=nip).exists():
                                    denied_records.append(f"{nip} (This Nip already exists)")
                                else:
                                    start_date = pd.to_datetime(start_date, errors='coerce')  # Handle errors by converting them to NaT
                                    if pd.isna(start_date):
                                        denied_records.append(f"{nip} (invalid start_date)")
                                        continue  # Skip to the next iteration if start_date is invalid

                                    if end_date is not None:
                                        end_date = pd.to_datetime(end_date, errors='coerce')  # Handle errors by converting them to NaT
                                        if pd.isna(end_date):
                                            denied_records.append(f"{nip} (invalid end_date)")
                                            continue  # Skip to the next iteration if end_date is invalid

                                    # Create the NIPRecord object
                                    NIPRecord.objects.create(nip=nip, nazwa=name, email_uzytkownika=email,
                                                             numer_telefonu_klienta=phone_number,
                                                             data_poczatkowa=start_date, data_koncowa=end_date)

                                    # Log the action
                                    LogEntry.objects.log_action(
                                        user_id=user.id,
                                        content_type_id=ContentType.objects.get_for_model(NIPRecord).pk,
                                        object_id=None,
                                        object_repr=force_str('NIP Data Import'),
                                        action_flag=CHANGE,
                                        change_message=f'NIP Data imported from CSV file. Added record with NIP: {nip}',
                                    )

                                    successful_imports += 1
                            except KeyError:
                                denied_records.append("NIP value missing in the CSV file")
                            except Exception as e:
                                denied_records.append(f"An error occurred: {e}")
                        if successful_imports > 0:
                            denied_nips_str = ', '.join(map(str, denied_records))
                            return HttpResponse(
                                f'Import completed. Imported {successful_imports} records. Denied NIPs: {denied_nips_str}<br><a href="http://elomotonip.eu.pythonanywhere.com/admin/rezerwacja_nip_app/niprecord/import_records/">Powrót</a>')
                        elif denied_records:
                            denied_nips_str = ', '.join(map(str, denied_records))
                            return HttpResponse(f'Import failed. Denied NIPs: {denied_nips_str}<br><a href="http://elomotonip.eu.pythonanywhere.com/admin/rezerwacja_nip_app/niprecord/import_records/">Powrót</a>')
                        else:
                            return HttpResponse("No records were imported.")
                    except ValueError as ve:
                        return HttpResponse("Error importing NIP records: start_date is required")
                    except Exception as e:
                        return HttpResponse(f"Error importing NIP records: {e}")
                else:
                    return HttpResponse('Invalid file format. Please import a CSV file.')
            else:
                return HttpResponse('No file uploaded.')
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
        writer.writerow(
            ['nip', 'nazwa', 'email_uzytkownika', 'numer_telefonu_klienta', 'data_poczatkowa', 'data_koncowa',
             'status'])

        for record in queryset:
            # Formatujemy daty do odpowiedniego formatu tekstowego
            start_date = localtime(record.data_poczatkowa).strftime('%d.%m.%Y %H:%M:%S')
            end_date = localtime(record.data_koncowa).strftime('%d.%m.%Y %H:%M:%S') if record.data_koncowa else ''
            writer.writerow([record.nip, record.nazwa, record.email_uzytkownika, record.numer_telefonu_klienta,
                             start_date, end_date, record.status])

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
