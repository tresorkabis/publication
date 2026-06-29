from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

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
        return f"{self.nom} {self.postnom} {self.prenom}" if self.nom or self.postnom or self.prenom else super().get_full_name()

    @property
    def telephone(self):
        return self.tel

    @property
    def matricule(self):
        return self.mat

    @property
    def role_labels(self):
        return list(self.utilisateur_roles.select_related('role').values_list('role__libelle', flat=True))

    def has_role(self, libelle):
        return libelle in self.role_labels

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

class ChefFiliere(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    grade = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Chef Filière: {self.user.last_name}"

class Filiere(models.Model):
    idfiliere = models.AutoField(primary_key=True)
    codfiliere = models.CharField(max_length=20)
    libelle = models.CharField(max_length=100)
    descript = models.TextField(blank=True, null=True)
    chef = models.ForeignKey(ChefFiliere, on_delete=models.SET_NULL, null=True, blank=True, related_name='filieres_dirigees')

    def __str__(self):
        return self.libelle

class Promotion(models.Model):
    idprom = models.AutoField(primary_key=True)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE)
    libnom = models.CharField(max_length=100)
    annee = models.IntegerField()
    niveau = models.CharField(max_length=50)
   

    def __str__(self):
        return f"{self.libnom} ({self.annee})"

class Inscription(models.Model):
    idinscription = models.AutoField(primary_key=True)
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='inscriptions')
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, related_name='inscriptions')
    annee = models.IntegerField()
    
    class Meta:
        unique_together = ('etudiant', 'promotion')

    def __str__(self):
        return f"{self.etudiant.user.nom} - {self.promotion.libnom}"
    
class Semestre(models.Model):
    idsemestre = models.AutoField(primary_key=True)
    libsemestre = models.CharField(max_length=50)
    datedeb = models.DateField()
    datefin = models.DateField()

    def __str__(self):
        return self.libsemestre

class Cours(models.Model):
    idcours = models.AutoField(primary_key=True)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name='cours')
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE)
    codcours = models.CharField(max_length=20)
    libelle = models.CharField(max_length=100)

    def __str__(self):
        return self.libelle

class TypeEvaluation(models.Model):
    idtype = models.AutoField(primary_key=True)
    libelle = models.CharField(max_length=100)
    descript = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.libelle

class Evaluation(models.Model):
    idevaluation = models.AutoField(primary_key=True)
    type_eval = models.ForeignKey(TypeEvaluation, on_delete=models.CASCADE)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    lib = models.CharField(max_length=100)
    coefficient = models.IntegerField(default=1)
    duree = models.DurationField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.lib} - {self.cours.libelle}"

class Cotation(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='cotations')
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='cotations')
    note = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = ('etudiant', 'evaluation')
