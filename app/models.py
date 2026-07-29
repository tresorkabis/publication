from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='app_user_set',
        related_query_name='app_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='app_user_set',
        related_query_name='app_user',
    )

    SEXES_CHOIX = [('M','Masculin'),('F','Feminim')]
    nom = models.CharField(max_length=50, blank=True, null=True)
    postnom = models.CharField(max_length=50, blank=True, null=True)
    prenom = models.CharField(max_length=50, blank=True, null=True)
    sexe = models.CharField(max_length=1, choices=SEXES_CHOIX, blank=True, null=True)
    tel = models.CharField(max_length=20, blank=True, null=True)
    mat = models.CharField(max_length=50, blank=True, null=True)
    tel_2 = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    adresse = models.CharField(max_length=50, blank=True, null=True)
    photo = models.FileField(upload_to='profile_pics/', blank=True, null=True)
    is_validated = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.nom} {self.postnom} {self.prenom}"

    def get_full_name(self):
        parts = []
        if self.nom:
            parts.append(self.nom)
        if self.postnom:
            parts.append(self.postnom)
        if self.prenom:
            parts.append(self.prenom)
        return ' '.join(parts) if parts else super().get_full_name()

    @property
    def telephone(self):
        return self.tel

    @property
    def matricule(self):
        return self.mat

    @property
    def role_labels(self):
        return list(self.utilisateur_roles.select_related('role').values_list('role__libelle', flat=True))

    @property
    def display_role(self):
        """
        Retourne le rôle principal d'un utilisateur pour l'affichage,
        en donnant la priorité aux rôles du personnel.
        """
        labels = self.role_labels
        if 'president' in labels:
            return 'Président'
        if hasattr(self, 'personnel'):
            if 'chef de filière' in labels:
                return 'Chef de Filière'
            if 'enseignant' in labels:
                return 'Enseignant'
        if hasattr(self, 'etudiant'):
            return 'Étudiant'
        if self.is_superuser:
            return 'Super Admin'
        if self.is_staff:
            return 'Staff'
        return "Utilisateur"

    def has_role(self, libelle):
        return libelle in self.role_labels

    def get_roles_display(self):
        """Retourne les rôles formatés pour l'affichage dans les listes CRUD"""
        return ", ".join(self.role_labels) if self.role_labels else "-"
    get_roles_display.short_description = 'Rôles'

class Role(models.Model):
    idrole = models.AutoField(primary_key=True)
    libelle = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.libelle

    @classmethod
    def default_roles(cls):
        return [
            'enseignant',
            'chef de filière',
            'secretaire',
            'president',
            'etudiant',
            'administrateur',
        ]

    @classmethod
    def ensure_default_roles(cls):
        for libelle in cls.default_roles():
            cls.objects.get_or_create(libelle=libelle)

class UtilisateurRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='utilisateur_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='utilisateur_roles')
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'role')

class Fonction(models.Model):
    idfonction = models.AutoField(primary_key=True)
    intitule = models.CharField(max_length=100)

    def __str__(self):
        return self.intitule

class Personnel(models.Model):
    idpersonnel = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fonction = models.ForeignKey(Fonction, on_delete=models.SET_NULL, null=True)
    grade = models.CharField(max_length=100)

    def __str__(self):
        return f"Personnel: {self.user.last_name}"

class Etudiant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    matricule = models.CharField(max_length=20, unique=True, blank=True, null=True)
    date_inscription = models.DateField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Etudiant: {self.user.last_name} ({self.matricule or 'N/A'})"

    @property
    def user_display(self):
        """Nom complet formaté pour l'affichage dans les listes"""
        full = self.user.get_full_name()
        return full if full else self.user.username


class Filiere(models.Model):
    code = models.CharField(max_length=20, unique=True)
    libelle = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    chef = models.ForeignKey(Personnel, on_delete=models.SET_NULL, null=True, blank=True, related_name='filieres_dirigees')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['code'], name='unique_filiere_code')
        ]

    def __str__(self):
        return self.libelle

class Promotion(models.Model):
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE)
    libelle = models.CharField(max_length=100)   

    def __str__(self):
        return f"{self.libelle}"

class Inscription(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='inscriptions')
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='inscriptions')
    annee = models.CharField(max_length=9)  # Format: "YYYY-YYYY"
    est_validee = models.BooleanField(default=False, verbose_name="Validée")
    
    class Meta:
        unique_together = ('etudiant', 'promotion')

    def __str__(self):
        return f"{self.etudiant.user.first_name} {self.etudiant.user.last_name} - {self.promotion.libelle}"
    
class AnneeEtude(models.Model):
    """Année d'étude dans le système LMD : L1, L2, L3"""
    code = models.CharField(max_length=5, unique=True, verbose_name="Code")
    libelle = models.CharField(max_length=100, verbose_name="Libellé")
    ordre = models.PositiveIntegerField(default=1, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = "Année d'étude"
        verbose_name_plural = "Années d'étude"
        ordering = ['ordre']

    def __str__(self):
        return self.libelle

class Semestre(models.Model):
    libelle = models.CharField(max_length=50)
    
    def __str__(self):
        return self.libelle

class Cours(models.Model):
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name='cours')
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE)
    annee_etude = models.ForeignKey(AnneeEtude, on_delete=models.CASCADE, null=True, blank=True, related_name='cours', verbose_name="Année d'étude")
    code = models.CharField(max_length=20)
    libelle = models.CharField(max_length=100)
    volume_horaire = models.IntegerField()
    credit = models.PositiveIntegerField(default=0, verbose_name="Crédit")

    def __str__(self):
        return self.libelle

class CalendrierAcademique(models.Model):
    class TypePeriode(models.TextChoices):
        S1 = 'S1', 'Session 1er semestre'
        RATTRAPAGE_S1 = 'RATTRAPAGE_S1', 'Rattrapage 1er semestre'
        S2 = 'S2', 'Session 2ème semestre'
        RATTRAPAGE_S2 = 'RATTRAPAGE_S2', 'Rattrapage 2ème semestre'
        RATTRAPAGE_CREDITS = 'RATTRAPAGE_CREDITS', 'Rattrapage de crédits'

    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name='calendriers')
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='calendriers')
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE, related_name='calendriers')
    annee_etude = models.ForeignKey(AnneeEtude, on_delete=models.CASCADE, null=True, blank=True, related_name='calendriers', verbose_name="Année d'étude")
    annee_academique = models.CharField(max_length=9, verbose_name="Année académique")
    type_periode = models.CharField(max_length=20, choices=TypePeriode.choices, default=TypePeriode.S1, verbose_name="Type de période")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    intitule = models.CharField(max_length=200, verbose_name="Intitulé de la période")
    est_actif = models.BooleanField(default=True, verbose_name="Période active")

    class Meta:
        verbose_name = "Calendrier académique"
        verbose_name_plural = "Calendriers académiques"
        ordering = ['annee_academique', 'annee_etude', 'date_debut']

    def __str__(self):
        annee = f"{self.annee_etude} - " if self.annee_etude else ""
        return f"{self.get_type_periode_display()} - {annee}{self.filiere.libelle} ({self.annee_academique})"

    @property
    def est_en_cours(self):
        from django.utils import timezone
        today = timezone.now().date()
        return self.date_debut <= today <= self.date_fin

    @property
    def est_rattrapage(self):
        return self.type_periode in ['RATTRAPAGE_S1', 'RATTRAPAGE_S2', 'RATTRAPAGE_CREDITS']

    @property
    def est_rattrapage_credits(self):
        return self.type_periode == 'RATTRAPAGE_CREDITS'

class TypeEvaluation(models.Model):
    libelle = models.CharField(max_length=100)

    def __str__(self):
        return self.libelle

class Evaluation(models.Model):
    type_evaluation = models.ForeignKey(TypeEvaluation, on_delete=models.CASCADE)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    date = models.DateField()
    duree_minutes = models.PositiveIntegerField(default=120, verbose_name="Durée (minutes)")
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    coefficient = models.PositiveIntegerField(default=1)
    calendrier = models.ForeignKey(
        CalendrierAcademique,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evaluations',
        verbose_name="Période du calendrier"
    )

    @property
    def type_eval(self):
        return self.type_evaluation

    @property
    def idevaluation(self):
        return self.id

    @property
    def lib(self):
        return self.cours.libelle if self.cours else ''

    def __str__(self):
        return f"{self.id} - {self.cours.libelle}"

class Cotation(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='cotations')
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='cotations')
    note = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        unique_together = ('etudiant', 'evaluation')


class ProposalCoursEnseignant(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='propositions_enseignants')
    enseignant = models.ForeignKey(Personnel, on_delete=models.CASCADE, related_name='propositions_cours')
    message = models.TextField(blank=True, null=True)
    date_proposition = models.DateTimeField(auto_now_add=True)
    est_accepte = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.cours.libelle} -> {self.enseignant.user.get_full_name()}"

class ValidationNotes(models.Model):
    """Traçabilité des validations de notes par le président"""
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='validations')
    validateur = models.ForeignKey(Personnel, on_delete=models.CASCADE, related_name='validations_notes')
    date_validation = models.DateTimeField(auto_now_add=True)
    commentaire = models.TextField(blank=True, null=True)
    est_valide = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_validation']
        verbose_name = "Validation de notes"
        verbose_name_plural = "Validations de notes"

    def __str__(self):
        return f"Validation {self.evaluation} par {self.validateur.user.get_full_name()} - {'Validé' if self.est_valide else 'Rejeté'}"