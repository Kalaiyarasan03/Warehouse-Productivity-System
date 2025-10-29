from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin','Admin'),
        ('manager','Manager'),
        ('lead','Lead'),
        ('employee','Employee'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    sections = models.ManyToManyField('Section', blank=True, related_name='employees')
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Section(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name

class ProductivityEntry(models.Model):
    lead = models.ForeignKey(User, limit_choices_to={'role':'employee'}, on_delete=models.CASCADE, related_name='entries')
    section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name='entries')
    date = models.DateField()
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    bundle_opening = models.IntegerField(default=0)
    sorting = models.IntegerField(default=0)
    loading = models.IntegerField(default=0)
    sticker = models.PositiveIntegerField(default=0)
    scanning = models.PositiveIntegerField(default=0)
    put_away = models.PositiveIntegerField(default=0)
    picking = models.PositiveIntegerField(default=0)




    class Meta:
        unique_together = ('lead','section','date')
        ordering = ['-date','-created_at']

    def clean(self):
        # Ensure lead assigned to section
        from django.core.exceptions import ValidationError
        if not self.lead.sections.filter(pk=self.section.pk).exists():
            raise ValidationError('Selected lead does not belong to the chosen section.')
    def __str__(self):
        return f"{self.lead} - {self.section} - {self.date}"
