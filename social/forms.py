from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "text"]
        widgets = {
                "rating": forms.RadioSelect(attrs={"class": "form-check-input"}),
                "text": forms.Textarea(attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Write a comment (optional)",
                }),
}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields["rating"].choices = [
            c for c in self.fields["rating"].choices if c[0] != ""
        ]

