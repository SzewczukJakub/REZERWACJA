# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.encoding import force_str
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator

class Administrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        app_label = 'rezerwacja_nip_app'


class EmailAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


#@receiver(post_save, sender=User)
#def create_or_update_email_address(sender, instance, created, **kwargs):
    # Check if the user already has an associated EmailAddress
#    try:
#        email_address = instance.emailaddress
#    except EmailAddress.DoesNotExist:
#        email_address = None
#
#    if email_address:
#        # Update the email field based on the user's email
#        email_address.email = instance.email
#        email_address.save()
#    else:
        # Create a new EmailAddress instance
#        EmailAddress.objects.create(user=instance, email=instance.email)

# Connect the signal
#post_save.connect(create_or_update_email_address, sender=User)

class NIPRecord(models.Model):
    nip = models.IntegerField(
        validators=[
            MinValueValidator(1000000000, message="NIP must be a 10-digit number."),
            MaxValueValidator(9999999999, message="NIP must be a 10-digit number.")
        ],
        unique=True
    )
    nazwa = models.CharField(max_length=255)
    email_uzytkownika = models.EmailField(default="")
    numer_telefonu_klienta = models.CharField(max_length=9, blank=True, null=True)
    data_poczatkowa = models.DateTimeField(default=timezone.now)
    data_koncowa = models.DateTimeField()
    STATUS_CHOICES = (
        ('WOLNY', 'Wolny do rezerwacji'),
        ('ZABLOKOWANY', 'Zablokowany'),
        ('WYGASLO', 'Rezerwacja wygasła'),
    )
    status = models.CharField(max_length=11, choices=STATUS_CHOICES)

    def save(self, *args, **kwargs):
        try:
            now = timezone.now()

            if not timezone.is_aware(self.data_poczatkowa):
                self.data_poczatkowa = timezone.make_aware(self.data_poczatkowa)

            if self.data_koncowa and not timezone.is_aware(self.data_koncowa):
                self.data_koncowa = timezone.make_aware(self.data_koncowa)

            if now < self.data_poczatkowa:
                self.status = 'WOLNY'
            elif self.data_poczatkowa <= now <= self.data_koncowa if self.data_koncowa else False:
                self.status = 'ZABLOKOWANY'
            else:
                self.status = 'WYGASLO'

            if not self.data_koncowa:
                # Ustaw domyślną wartość, jeśli nie została podana
                settings = Settings.objects.first()
                expiration_days = settings.expiration_days if settings else 60
                self.data_koncowa = self.data_poczatkowa + timezone.timedelta(days=expiration_days)

            super().save(*args, **kwargs)

        except Exception as e:
            import logging
            logging.error(f"Error in NIPRecord save method: {e}")
            raise

    #def clean(self):
    #   if not self.nip.isdigit() or len(self.nip) != 10:
    #        raise ValidationError(
    #            _('NIP must be a 10-digit number.'),
    #            code='invalid_nip'
    #        )


    def validate_nip(nip):
        return len(str(nip)) == 10 and str(nip).isdigit()

    def __str__(self):
        return str(self.nip) if self.nip else ""


class Settings(models.Model):
    expiration_days = models.IntegerField(default=60)

    def __str__(self):
        return f"Czas rezerwacji (dni): {self.expiration_days}"

