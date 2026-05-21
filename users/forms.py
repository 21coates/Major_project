from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(max_length=30, required=True)
    surname = forms.CharField(max_length=30, required=True, label="Last name")
    nickname = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        # No 'username' here — we set it from email in save()
        fields = ['email', 'password1', 'password2', 'first_name']

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        # since username = email, ensure no existing username/email matches
        if User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_nickname(self):
        nick = self.cleaned_data.get("nickname", "").strip()
        if not nick:
            raise forms.ValidationError("Nickname is required.")
        from .models import Profile
        if Profile.objects.filter(nickname__iexact=nick).exists():
            raise forms.ValidationError("This nickname is already taken.")
        return nick

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email'].strip().lower()
        user.username = email            # username mirrors email
        user.email = email
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['surname']

        if commit:
            user.save()
            # ensure profile & nickname
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.nickname = self.cleaned_data['nickname']
            profile.save(update_fields=['nickname'])
        return user


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autofocus": True})
    )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'age', 'gender', 'weight_kg', 'height_cm']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Full name'}),
            'age': forms.NumberInput(attrs={'min': 0}),
            'gender': forms.Select(),
            'weight_kg': forms.NumberInput(attrs={'step': '0.01', 'min': 0}),
            'height_cm': forms.NumberInput(attrs={'step': '0.01', 'min': 0}),
        }

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is not None and (age <= 0 or age > 120):
            raise forms.ValidationError('Please enter a valid age.')
        return age

    def clean_weight_kg(self):
        w = self.cleaned_data.get('weight_kg')
        if w is not None and w <= 0:
            raise forms.ValidationError('Please enter a valid weight.')
        return w

    def clean_height_cm(self):
        h = self.cleaned_data.get('height_cm')
        if h is not None and h <= 0:
            raise forms.ValidationError('Please enter a valid height.')
        return h


class UserRegistrationWithProfileForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(max_length=30, required=True)
    surname = forms.CharField(max_length=30, required=True, label="Last name")
    nickname = forms.CharField(max_length=30, required=True)
    # Profile fields (removed full_name)
    age = forms.IntegerField(min_value=1, max_value=120, required=True)
    gender = forms.ChoiceField(choices=Profile.GENDER_CHOICES, required=True)
    weight_kg = forms.DecimalField(max_digits=6, decimal_places=2, min_value=1, required=True)
    height_cm = forms.DecimalField(max_digits=6, decimal_places=2, min_value=1, required=True)

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'first_name', 'surname', 'nickname', 'age', 'gender', 'weight_kg', 'height_cm']

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_nickname(self):
        nick = self.cleaned_data.get("nickname", "").strip()
        if not nick:
            raise forms.ValidationError("Nickname is required.")
        if Profile.objects.filter(nickname__iexact=nick).exists():
            raise forms.ValidationError("This nickname is already taken.")
        return nick

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email'].strip().lower()
        user.username = email
        user.email = email
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['surname']
        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.nickname = self.cleaned_data['nickname']
            # profile.full_name is not set here
            profile.age = self.cleaned_data['age']
            profile.gender = self.cleaned_data['gender']
            profile.weight_kg = self.cleaned_data['weight_kg']
            profile.height_cm = self.cleaned_data['height_cm']
            profile.save()
        return user