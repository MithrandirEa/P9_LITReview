from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm


class SignupForm(UserCreationForm):
    """
    Formulaire d'inscription pour les utilisateurs.
    Hérite de UserCreationForm et utilise Crispy Forms pour une mise en page personnalisée.
    """
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-6 mb-3'),
                Column('email', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('password1', css_class='form-group col-md-6 mb-3'),
                Column('password2', css_class='form-group col-md-6 mb-3'),
            ),
        )


class ChangePasswordForm(PasswordChangeForm):
    """
    Formulaire pour permettre aux utilisateurs de changer leur mot de passe.
    Hérite de PasswordChangeForm.
    """
    model = get_user_model()
    fields = ('password1', 'password2')
