from django.core.exceptions import ValidationError


class ContainsLetterValidator:
    def validate(self, password, user=None):
        if not any(char.isalpha() for char in password):
            raise ValidationError(
                'Le mot de passe doit contenir au moins une lettre.',
                code='password_no_letter'
            )
        
    def get_help_text(self):
        return "Le mot de passe doit contenir au moins une lettre majuscule ou minuscule."
    

class ContainsNumberValidator:
    def validate(self, password, user=None):
        if not any(char.isdigit() for char in password):
            raise ValidationError(
                'Le mot de passe doit contenir au moins un chiffre.',
                code='password_no_number'
            )
        
    def get_help_text(self):
        return "Le mot de passe doit contenir au moins un chiffre (0-9)."


class ContainsSpecialCharacterValidator:
    def validate(self, password, user=None):
        special_characters = "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~"
        if not any(char in special_characters for char in password):
            raise ValidationError(
                'Le mot de passe doit contenir au moins un caractère spécial.',
                code='password_no_special_character'
            )
        
    def get_help_text(self):
        return "Le mot de passe doit contenir au moins un caractère spécial (par exemple !, @, #, etc.)."