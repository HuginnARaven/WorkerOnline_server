from django.db import models
from django.utils.translation import gettext_lazy as _

from companies.models import Company
from workers.models import Worker


class Supervisor(models.Model):
    in_admin_mode = models.BooleanField(default=False, null=False)
    is_active = models.BooleanField(default=False, null=False)
    last_active = models.DateTimeField(null=True, blank=True)
    serial_number = models.CharField(max_length=255,
                                     unique=True,
                                     help_text="Mast be unique, and implemented in iot program code!",
                                     null=False,
                                     blank=False)

    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = _('supervisor')
        verbose_name_plural = _('supervisors')

    def __str__(self):
        return f"Supervisor #{self.id}({self.company.name})"


class Offer(models.Model):
    OFFER_SATUS = [
        ('CR', _('Created')),
        ('RC', _('Received')),
        ('IC', _('IoT creating')),
        ('DL', _('Delivering')),
        ('CM', _('Completed')),
        ('RJ', _('Rejected')),
    ]
    status = models.CharField(max_length=2, choices=OFFER_SATUS, default='CR')
    last_changed = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False)
    address_of_delivery = models.CharField(max_length=255)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _('offer')
        verbose_name_plural = _('offers')

    def __str__(self):
        return f"Offer #{self.id}({self.company.name})"


