from django import forms
from django.core.exceptions import ValidationError

from .models import Follow


class FollowForm(forms.ModelForm):
    class Meta:
        model = Follow
        fields = ("user", "follower")

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        follower = cleaned_data.get("follower")
        if user == follower:
            raise ValidationError("Вы не можете подписаться на самого себя.")
