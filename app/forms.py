from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Evaluation, TypeEvaluation, Cours, Personnel, ProposalCoursEnseignant, CalendrierAcademique


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'nom',
            'postnom',
            'prenom',
            'sexe',
            'tel',
            'mat',
            'adresse',
            'photo',
            'password1',
            'password2',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': field.label,
            })
            if field_name == 'tel':
                field.label = 'Téléphone'
            if field_name == 'mat':
                field.label = 'Matricule'
            field.help_text = None

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('prenom', '')
        user.last_name = self.cleaned_data.get('nom', '')
        if commit:
            user.save()
        return user


class PlanificationExamenForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['calendrier', 'cours', 'type_evaluation', 'date', 'duree_minutes', 'coefficient']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'type_evaluation': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'cours': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'coefficient': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'min': '1'}),
            'calendrier': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'duree_minutes': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
        }

    def __init__(self, *args, **kwargs):
        filieres = kwargs.pop('filieres', None)
        super().__init__(*args, **kwargs)
        if filieres is not None:
            self.fields['cours'].queryset = Cours.objects.filter(filiere__in=filieres).order_by('libelle')
            self.fields['calendrier'].queryset = CalendrierAcademique.objects.filter(
                filiere__in=filieres,
                est_actif=True
            ).order_by('date_debut')
        self.fields['type_evaluation'].queryset = TypeEvaluation.objects.order_by('libelle')
        self.fields['calendrier'].label = 'Période du calendrier académique'
        self.fields['calendrier'].empty_label = "--- Sélectionnez une période ---"
        self.fields['cours'].label = 'Cours'
        self.fields['type_evaluation'].label = "Type d'évaluation"
        self.fields['date'].label = 'Date de l’examen'
        self.fields['duree_minutes'].label = 'Durée'
        self.fields['duree_minutes'].widget = forms.Select(choices=[
            (60, '1h'),
            (90, '1h30'),
            (120, '2h'),
            (150, '2h30'),
            (180, '3h'),
            (240, '4h'),
        ], attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'})
        self.fields['coefficient'].label = 'Coefficient'


class PropositionCoursForm(forms.ModelForm):
    class Meta:
        model = ProposalCoursEnseignant
        fields = ['cours', 'enseignant', 'message']
        widgets = {
            'cours': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'enseignant': forms.Select(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'message': forms.Textarea(attrs={'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        filieres = kwargs.pop('filieres', None)
        super().__init__(*args, **kwargs)
        if filieres is not None:
            self.fields['cours'].queryset = Cours.objects.filter(filiere__in=filieres).order_by('libelle')
        self.fields['enseignant'].queryset = Personnel.objects.filter(user__utilisateur_roles__role__libelle='enseignant').order_by('user__nom', 'user__postnom', 'user__prenom')
        self.fields['cours'].label = 'Cours'
        self.fields['enseignant'].label = 'Enseignant'
        self.fields['message'].label = 'Message'


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'email',
            'nom',
            'postnom',
            'prenom',
            'sexe',
            'tel',
            'mat',
            'adresse',
            'photo',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': field.label,
            })
            if field_name == 'tel':
                field.label = 'Téléphone'
            if field_name == 'mat':
                field.label = 'Matricule'
            field.help_text = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('prenom', '')
        user.last_name = self.cleaned_data.get('nom', '')
        if commit:
            user.save()
        return user
