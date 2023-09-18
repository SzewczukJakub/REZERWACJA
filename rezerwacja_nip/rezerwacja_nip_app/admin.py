import csv

import pandas as pd
from django.contrib import admin, messages
from django.http import HttpResponse
from django.urls import reverse
from io import TextIOWrapper
from django_object_actions import DjangoObjectActions
from django.utils.html import format_html
from django.urls import path
from .forms import NIPRecordImportForm
from .models import NIPRecord, EmailAddress
from django.shortcuts import render, redirect


class ImportAdmin(DjangoObjectActions, admin.ModelAdmin):
    def imports(modeladmin, request, queryset):
        print("Imports button pushed")

    changelist_actions = ('imports', )

class NIPRecordAdmin(admin.ModelAdmin):
    list_display = (
        'nip', 'nazwa', 'email_klienta', 'numer_telefonu_klienta', 'data_poczatkowa', 'data_koncowa', 'status')

    actions = ['export_selected_records']

    def import_records_button(self):
        return format_html(
            '<a class="button" href="{}">Importuj dane z CSV</a>',
            reverse('admin:import_records')  # Użyj odpowiedniej nazwy URL dla widoku importu
        )

    import_records_button.short_description = "Importuj dane z CSV"

    def import_records(self, request):
        if request.method == 'POST':
            uploaded_file = request.FILES.get('file')

            if uploaded_file:
                # Sprawdź, czy przesłany plik ma rozszerzenie .csv
                if uploaded_file.name.endswith('.csv'):
                    try:
                        # Wczytaj plik CSV do DataFrame
                        df = pd.read_csv(uploaded_file, encoding='utf-8-sig')

                        # Przetwórz i zapisz dane do modelu NIPRecord
                        for index, row in df.iterrows():
                            nip = row['nip']
                            nazwa = row['nazwa']
                            email = row['email_klienta']
                            numer_telefonu = row['numer_telefonu_klienta']

                            # Utwórz nowy rekord NIPRecord i zapisz go w bazie danych
                            NIPRecord.objects.create(nip=nip, nazwa=nazwa, email_klienta=email,
                                                     numer_telefonu_klienta=numer_telefonu)

                        self.message_user(request, 'Import zakończony pomyślnie.')
                    except Exception as e:
                        self.message_user(request, f'Błąd podczas importowania danych: {str(e)}')
                else:
                    self.message_user(request, 'Niewłaściwy format pliku. Zaimportuj plik CSV.')

        return render(request, 'admin/import_records.html', {'form': NIPRecordImportForm()})
    def export_selected_records(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="nip_records.csv"'

        writer = csv.writer(response)
        writer.writerow(['nip', 'nazwa', 'email_klienta', 'numer_telefonu_klienta', 'data_poczatkowa', 'data_koncowa', 'status'])

        for record in queryset:
            writer.writerow([record.nip, record.nazwa, record.email_klienta, record.numer_telefonu_klienta,
                             record.data_poczatkowa, record.data_koncowa, record.status])

        return response

    export_selected_records.short_description = "Eksportuj zaznaczone rekordy"

    def get_urls(self):
        urlpatterns = super().get_urls()
        custom_urls = [
            path('import_records/', self.import_records, name='import_records'),
        ]
        return custom_urls + urlpatterns


admin.site.register(NIPRecord, NIPRecordAdmin)
admin.site.register(EmailAddress)
