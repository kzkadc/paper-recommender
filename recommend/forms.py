from django import forms

from .models import UserPaper


class AddPaperForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["title"].widget = forms.Textarea(
            attrs={"class": "form-control", "rows": 1})
        self.fields["abstract"].widget = forms.Textarea(
            attrs={"class": "form-control", "rows": 3})
        self.fields["memo"].widget = forms.Textarea(
            attrs={"class": "form-control", "rows": 1})
        self.fields["memo"].required = False

    class Meta:
        model = UserPaper
        fields = ("title", "abstract", "memo")
