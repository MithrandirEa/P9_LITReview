from django import forms

from flux.models import Ticket, Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['headline', 'body', 'rating']
        labels = {
            'headline': 'Titre',
            'body': 'Commentaire',
            'rating': 'Note',
        }
        widgets = {
            'rating': forms.RadioSelect(
                choices=[
                    (i, f'{i} étoile{"s" if i > 1 else ""}')
                    for i in range(5, 0, -1)
                ]
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].widget.attrs.update({'class': 'star-rating'})


class ReviewReplyForm(forms.ModelForm):
    """Formulaire pour répondre à un ticket existant (sans titre)"""
    class Meta:
        model = Review
        fields = ['body', 'rating']
        labels = {
            'body': 'Commentaire',
            'rating': 'Note',
        }
        widgets = {
            'rating': forms.RadioSelect(
                choices=[
                    (i, f'{i} étoile{"s" if i > 1 else ""}')
                    for i in range(5, 0, -1)
                ]
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].widget.attrs.update({'class': 'star-rating'})


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']
        labels = {
            'title': 'Titre',
            'description': 'Description',
            'image': 'Image',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
