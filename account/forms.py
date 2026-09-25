from django import forms
from .models import User
from location.models import City, Province


class CitySelect(forms.Select):

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(
            name, value, label, selected, index, subindex=subindex, attrs=attrs
        )

        instance = getattr(value, "instance", None)
        if instance is not None:
            option["attrs"]["data-province"] = instance.province_id

        return option


class EditProfileForm(forms.Form):
    username = forms.CharField(max_length=50)
    avatar = forms.ImageField(required=False)
    city = forms.ModelChoiceField(
        queryset=City.objects.order_by("name"),
        widget=CitySelect,
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user

        self.provinces = Province.objects.order_by("name")

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("این نام کاربری قبلا استفاده شده است")

        return username