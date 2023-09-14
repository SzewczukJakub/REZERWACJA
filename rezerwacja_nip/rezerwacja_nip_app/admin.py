import csv
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

    def import_records_button(self, obj):
        return format_html(
            '<a class="button" href="{}">Importuj dane z CSV</a>',
            reverse('admin:import_records')  # Użyj odpowiedniej nazwy URL dla widoku importu
        )

    import_records_button.short_description = "Importuj dane z CSV"

    def import_records(self, request):
        if request.method == "POST" and request.FILES.get("file"):
            csv_file = request.FILES["file"]

            if csv_file.name.endswith('.csv'):
                csv_file_wrapper = TextIOWrapper(csv_file.file, encoding='utf-8-sig')
                csv_reader = csv.reader(csv_file_wrapper)

                for row in csv_reader:
                    if len(row) >= len(NIPRecord._meta.fields):
                        data_dict = {}
                        for i, field in enumerate(NIPRecord._meta.fields):
                            column_name = field.name
                            data_dict[column_name] = row[i]

                        NIPRecord.objects.create(**data_dict)

                self.message_user(request, "Rekordy zostały zaimportowane pomyślnie.")
            else:
                self.message_user(request, "Wybierz poprawny plik CSV do importu.")

        else:
            form = NIPRecordImportForm()
            return render(request, 'admin/import_records.html', {'form': form})
        return HttpResponse("File upload complete. <a href='../'>Return to import page</a>")

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
