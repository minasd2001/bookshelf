from django import forms
from .models import Profile

MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2 MB, in bytes

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio", "avatar"]

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        # Only a freshly uploaded file has content_type. If the user saved
        # without choosing a new file, avatar is the existing one (or empty).
        if avatar and hasattr(avatar, "content_type") and avatar.size > MAX_AVATAR_SIZE:
            raise forms.ValidationError("Image must be under 2 MB.")
        return avatar