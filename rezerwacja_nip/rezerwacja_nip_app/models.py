from django.db import models
from django.contrib.auth.models import User


class Administrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nip_limit = models.PositiveIntegerField(default=10)

    class Meta:
        app_label = 'rezerwacja_nip_app'


class EmailAddress(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


from django.db import models
from django.utils import timezone

class NIPRecord(models.Model):
    nip = models.CharField(max_length=10, unique=True)
    nazwa = models.CharField(max_length=255, default="")
    email_klienta = models.EmailField(default="")
    numer_telefonu_klienta = models.CharField(max_length=9, blank=True, null=True)
    data_poczatkowa = models.DateTimeField(default=timezone.now)
    data_koncowa = models.DateTimeField(default=timezone.now() + timezone.timedelta(days=60))
    STATUS_CHOICES = (
        ('ZABLOKOWANY', 'Zablokowany'),
        ('WOLNY DO REZERWACJI', 'Wolny do rezerwacji'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='WOLNY DO REZERWACJI')

    def save(self, *args, **kwargs):
        if not self.data_koncowa:
            self.data_koncowa = self.data_poczatkowa + timezone.timedelta(days=60)
        super().save(*args, **kwargs)

    def current_status(self):
        now = timezone.now()
        if now < self.data_poczatkowa:
            return 'Wolny do rezerwacji'
        elif self.data_poczatkowa <= now <= self.data_koncowa:
            return 'Zablokowany'
        else:
            return 'Rezerwacja wygasła'

    def __str__(self):
        return self.nip

