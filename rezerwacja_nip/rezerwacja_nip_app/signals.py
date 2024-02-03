## signals.py
#from django.db.models.signals import post_save
#from django.dispatch import receiver
#from django.contrib.admin.models import LogEntry, CHANGE
#from django.contrib.contenttypes.models import ContentType
#from django.contrib.auth.models import User

#from .models import NIPRecord, EmailAddress

#@receiver(post_save, sender=NIPRecord)
#@receiver(post_save, sender=EmailAddress)
#def log_change(sender, instance, user=None, **kwargs):
    # Check if the action is a change
 #   if kwargs.get('created') or kwargs.get('update_fields'):
  #      change_message = "Record updated"
   #     if kwargs.get('update_fields'):
    #        # If specific fields were updated, customize the message accordingly
     #       changed_fields = kwargs['update_fields']
      #      change_message = f"Record updated. Fields changed: {', '.join(changed_fields)}"
#
 #       # Create a more user-friendly log entry
  #      LogEntry.objects.create(
   #         user=user,
    #        content_type=ContentType.objects.get_for_model(sender),
     #       object_id=instance.id,
      #      object_repr=str(instance),
       #     action_flag=CHANGE,
        #    change_message=change_message,
        #)
