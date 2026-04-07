from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import bleach


def sanitize(value):
    """Strip all HTML tags from input to prevent XSS."""
    if isinstance(value, str):
        return bleach.clean(value, tags=[], strip=True).strip()
    return value


class SafeCharField(forms.CharField):
    def clean(self, value):
        value = super().clean(value)
        return sanitize(value)


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        return sanitize(self.cleaned_data['username'])

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email


class LoginForm(AuthenticationForm):
    pass


class BodyWeightForm(forms.Form):
    weight = forms.DecimalField(
        max_digits=5, decimal_places=1,
        validators=[MinValueValidator(20), MaxValueValidator(300)],
        widget=forms.NumberInput(attrs={
            'step': '0.1', 'min': '20', 'max': '300',
            'placeholder': 'e.g. 85.0',
            'class': 'form-input',
        })
    )


class ExerciseLogForm(forms.Form):
    """Form for a single set within an exercise."""
    weight = forms.DecimalField(
        max_digits=6, decimal_places=1,
        validators=[MinValueValidator(0)],
        widget=forms.NumberInput(attrs={
            'step': '0.5', 'min': '0',
            'class': 'form-input weight-input',
            'placeholder': 'kg',
        })
    )
    reps = forms.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        widget=forms.NumberInput(attrs={
            'min': '0', 'max': '100',
            'class': 'form-input reps-input',
        })
    )
    difficulty = forms.ChoiceField(
        choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')],
        widget=forms.RadioSelect(attrs={'class': 'difficulty-radio'}),
        initial='medium',
    )


class ProfileForm(forms.Form):
    height_cm = forms.IntegerField(
        required=False,
        validators=[MinValueValidator(100), MaxValueValidator(250)],
        widget=forms.NumberInput(attrs={
            'min': '100', 'max': '250',
            'placeholder': 'cm',
            'class': 'form-input',
        })
    )
    target_weight = forms.DecimalField(
        required=False,
        max_digits=5, decimal_places=1,
        validators=[MinValueValidator(30), MaxValueValidator(250)],
        widget=forms.NumberInput(attrs={
            'step': '0.1', 'min': '30', 'max': '250',
            'placeholder': 'kg',
            'class': 'form-input',
        })
    )
