from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):

    class Meta:

        model = UserProfile

        fields = [

            'keyword1',

            'keyword2',

            'keyword3',

        ]

        labels = {

            'keyword1': '興味①',

            'keyword2': '興味②',

            'keyword3': '興味③',

        }

        widgets = {

            'keyword1': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '例：Python'
                }
            ),

            'keyword2': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '例：AI'
                }
            ),

            'keyword3': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '例：フィリピン'
                }
            ),

        }
