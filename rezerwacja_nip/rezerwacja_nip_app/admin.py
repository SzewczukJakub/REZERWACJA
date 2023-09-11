import csv

from django.contrib import admin, messages
from django.shortcuts import render
from django.urls import reverse

from .models import NIPRecord
from .models import EmailAddress
from django.http import HttpResponse, HttpResponseRedirect
from .forms import NIPRecordImportForm

class NIPRecordAdmin(admin.ModelAdmin):
 list_display = ('nip', 'nazwa', 'email_klienta', 'numer_telefonu_klienta', 'data_poczatkowa', 'data_koncowa', 'status')

 # Dodaj własny formularz importu rekordów
 change_list_template = 'admin/import_records.html'

 actions = ['export_selected_records']

 def import_nip_records(request):
     if request.method == 'POST':
         form = NIPRecordImportForm(request.POST, request.FILES)
         if form.is_valid():
             file = form.cleaned_data['file']
             # Obsługa importu rekordów z pliku Excel
             # ...
             messages.success(request, 'Rekordy NIP zostały zaimportowane pomyślnie.')
             return HttpResponseRedirect(reverse('admin:niprecord_changelist'))
         else:
             messages.error(request, 'Wystąpił błąd podczas importowania rekordów NIP.')
     else:
         form = NIPRecordImportForm()

     context = {'form': form}

     return render(request, 'admin/niprecord/niprecord_import.html', context)

 def export_selected_records(self, request, queryset):
     response = HttpResponse(content_type='text/csv')
     response['Content-Disposition'] = 'attachment; filename="nip_records.csv"'

     writer = csv.writer(response)
     writer.writerow(['NIP', 'Nazwa', 'Email', 'Numer Telefonu', 'Data Początkowa', 'Data Końcowa', 'Status'])

     for record in queryset:
         writer.writerow([record.nip, record.nazwa, record.email_klienta, record.numer_telefonu_klienta,
                          record.data_poczatkowa, record.data_koncowa, record.status])

     return response

 export_selected_records.short_description = "Eksportuj zaznaczone rekordy"

 def get_urls(self):
     from django.urls import path
     from . import views

     # Dodaj ścieżki dla twoich własnych widoków
     urlpatterns = super().get_urls()
     urlpatterns += [
         path('import-records/', self.admin_site.admin_view(views.import_records), name='import_records'),
         # Dodaj inne widoki i ich ścieżki tutaj
     ]
     return urlpatterns


admin.site.register(EmailAddress)
admin.site.register(NIPRecord, NIPRecordAdmin)
