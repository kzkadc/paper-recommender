from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs["class"] = "form-control"
        self.fields["password"].widget.attrs["class"] = "form-control"


class SignupForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for k in ("username", "password1", "password2"):
            self.fields[k].widget.attrs["class"] = "form-control"


class SettingForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for k in ("old_password", "new_password1", "new_password2"):
            self.fields[k].widget.attrs["class"] = "form-control"
