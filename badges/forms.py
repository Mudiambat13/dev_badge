from django import forms
from .models import DeveloperProfile
from PIL import Image
import os

class DeveloperProfileForm(forms.ModelForm):
    class Meta:
        model = DeveloperProfile
        fields = [
            'profile_picture',
            'job_title',
            'location',
            'bio',
            'linkedin_url',
            'github_url',
            'tech_stack'
        ]
        widgets = {
            'tech_stack': forms.CheckboxSelectMultiple(),
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }

    def clean_profile_picture(self):
        image = self.cleaned_data.get('profile_picture')
        if not image:
            return image

        if image:
            if image.size > 5*1024*1024:  # 5MB
                raise forms.ValidationError("L'image ne doit pas dépasser 5MB")

            try:
                # Vérifier que c'est bien une image
                img = Image.open(image)
                img.verify()

                # Vérifier les extensions autorisées
                ext = os.path.splitext(image.name)[1].lower()
                if ext not in ['.jpg', '.jpeg', '.png', '.gif']:
                    raise forms.ValidationError("Format d'image non supporté. Utilisez JPG, PNG ou GIF.")

            except Exception:
                raise forms.ValidationError("Le fichier n'est pas une image valide")

        return image
