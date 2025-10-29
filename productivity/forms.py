from django import forms
from .models import ProductivityEntry, User, Section

class ProductivityEntryForm(forms.ModelForm):
    class Meta:
        model = ProductivityEntry
        fields = [
            'lead', 'section', 'date', 'bundle_opening', 'sorting', 'loading',
            'sticker', 'scanning', 'put_away', 'picking', 'remarks'
        ]
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    def clean(self):
        cleaned = super().clean()
        lead = cleaned.get('lead')
        section = cleaned.get('section')
        date = cleaned.get('date')

        if lead and section:
            # ✅ Automatically assign the section if not already linked
            if not lead.sections.filter(pk=section.pk).exists():
                lead.sections.add(section)

            # ✅ Prevent duplicate entries (same lead-section-date)
            qs = ProductivityEntry.objects.filter(lead=lead, section=section, date=date)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    'An entry for this lead, section, and date already exists.'
                )

        return cleaned


from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Username',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )
