# Diagramme de Séquence - Inscription d'un Étudiant

## Acteurs
- **Étudiant** : Personne souhaitant créer un compte
- **Navigateur** : Interface web de l'étudiant
- **RegisterView** : Vue d'inscription (views.register)
- **UserRegistrationForm** : Formulaire d'inscription
- **User Model** : Modèle utilisateur Django
- **Etudiant Model** : Modèle profil étudiant
- **Role Model** : Modèle des rôles
- **UtilisateurRole** : Table d'association User-Role
- **Dashboard** : Page d'accueil après inscription

---

## Flux Principal (Succès)

```
Étudiant -> Navigateur: Accède à /inscription/
Navigateur -> RegisterView: GET /inscription/
RegisterView -> RegisterView: Vérifie si utilisateur déjà connecté
RegisterView -> UserRegistrationForm: Crée formulaire vide
UserRegistrationForm -> RegisterView: Retourne formulaire vide
RegisterView -> Navigateur: Affiche formulaire d'inscription (register.html)
Navigateur -> Étudiant: Affiche page avec formulaire

Étudiant -> Navigateur: Remplit formulaire (username, email, nom, postnom, prenom, sexe, tel, mat, adresse, photo, password1, password2)
Étudiant -> Navigateur: Clique sur "S'inscrire"
Navigateur -> RegisterView: POST /inscription/ (données formulaire + fichiers)

RegisterView -> RegisterView: Vérifie si utilisateur déjà authentifié
RegisterView -> UserRegistrationForm: Crée formulaire avec données POST et FILES
UserRegistrationForm -> UserRegistrationForm: Valide les champs
UserRegistrationForm -> UserRegistrationForm: Vérifie unicité email (clean_email)
UserRegistrationForm -> UserRegistrationForm: Valide correspondance password1/password2

alt Formulaire valide
    UserRegistrationForm -> RegisterView: Retourne formulaire valide
    RegisterView -> UserRegistrationForm: Appelle form.save(commit=False)
    UserRegistrationForm -> User Model: Crée objet User (non sauvegardé)
    User Model -> UserRegistrationForm: Retourne objet User
    UserRegistrationForm -> UserRegistrationForm: Définit is_active=False, is_validated=False
    UserRegistrationForm -> UserRegistrationForm: Sauvegarde User dans BD
    User Model -> UserRegistrationForm: User créé avec ID

    RegisterView -> Etudiant Model: Crée profil Etudiant (get_or_create)
    Etudiant Model -> RegisterView: Retourne objet Etudiant

    RegisterView -> Role Model: Récupère ou crée rôle "etudiant" (get_or_create)
    Role Model -> RegisterView: Retourne rôle etudiant

    RegisterView -> UtilisateurRole: Crée association User-Role (get_or_create)
    UtilisateurRole -> RegisterView: Association créée

    RegisterView -> Navigateur: Message de succès + redirection vers /
    Navigateur -> Dashboard: GET /
    Dashboard -> Étudiant: Affiche page d'accueil
else Formulaire invalide
    UserRegistrationForm -> RegisterView: Retourne formulaire avec erreurs
    RegisterView -> Navigateur: Affiche formulaire avec messages d'erreur
    Navigateur -> Étudiant: Affiche erreurs de validation
end
```

---

## Flux Alternatif - Utilisateur Déjà Connecté

```
Étudiant -> Navigateur: Accède à /inscription/ (déjà connecté)
Navigateur -> RegisterView: GET /inscription/
RegisterView -> RegisterView: Vérifie request.user.is_authenticated
RegisterView -> Navigateur: Redirection HTTP 302 vers /dashboard/
Navigateur -> Dashboard: GET /dashboard/
Dashboard -> Étudiant: Affiche tableau de bord
```

---

## Flux d'Erreur - Email Déjà Utilisé

```
Étudiant -> Navigateur: Soumet formulaire avec email existant
Navigateur -> RegisterView: POST /inscription/
RegisterView -> UserRegistrationForm: Validation du formulaire
UserRegistrationForm -> UserRegistrationForm: clean_email() vérifie unicité
UserRegistrationForm -> UserRegistrationForm: Lève ValidationError "Cette adresse email est déjà utilisée"
UserRegistrationForm -> RegisterView: Retourne formulaire avec erreur
RegisterView -> Navigateur: Affiche formulaire avec message d'erreur
Navigateur -> Étudiant: Affiche erreur sur le champ email
```

---

## Composants Techniques

### 1. Template d'Inscription (register.html)
- **URL d'accès** : `/inscription/`
- **Méthode** : POST avec CSRF token et enctype multipart/form-data
- **Champs du formulaire** :
  - username (unique)
  - email (unique, validé)
  - nom, postnom, prenom
  - sexe (choix)
  - tel (téléphone)
  - mat (matricule)
  - adresse
  - photo (upload fichier)
  - password1, password2 (confirmation)

### 2. Formulaire d'Inscription (UserRegistrationForm)
- **Héritage** : UserCreationForm
- **Validation** :
  - unicité email
  - correspondance des mots de passe
  - validation des champs requis
- **Méthode save()** : Personnalisée pour mapper prenom/nom vers first_name/last_name

### 3. Vue d'Inscription (views.register)
- **Logique** :
  1. Vérifie si utilisateur déjà authentifié → redirection
  2. Traite POST : validation formulaire
  3. Crée User avec is_active=False, is_validated=False
  4. Crée profil Etudiant
  5. Assigne rôle "etudiant"
  6. Affiche message de succès
  7. Redirige vers home

### 4. Modèles Impliqués

**User Model**
- Champs : username, email, password, first_name, last_name, is_active, is_validated
- Relations : UtilisateurRole (plusieurs)

**Etudiant Model**
- Relation OneToOne avec User
- Stocke les informations spécifiques à l'étudiant

**Role Model**
- libelle : "etudiant", "enseignant", "chef de filière", "president"
- Utilisé pour le système d'autorisation

**UtilisateurRole**
- Table d'association Many-to-Many entre User et Role
- Permet à un utilisateur d'avoir plusieurs rôles

---

## États du Compte Étudiant

### État 1 : En attente de validation
- **is_active** : False
- **is_validated** : False
- **Accès** : Impossible de se connecter
- **Action requise** : Validation par le secrétariat ou président

### État 2 : Compte activé
- **is_active** : True
- **is_validated** : True
- **Accès** : Connexion possible
- **Rôle** : "etudiant" assigné

---

## Scénarios d'Utilisation

### Scénario 1 : Inscription Réussie
1. Étudiant remplit tous les champs du formulaire
2. Email unique, mots de passe correspondent
3. Compte créé avec is_active=False
4. Profil Etudiant créé
5. Rôle "etudiant" assigné
6. Message "Inscription enregistrée. Votre compte doit être validé par le secrétariat avant activation."
7. Redirection vers page d'accueil

### Scénario 2 : Inscription avec Email Existant
1. Étudiant saisit un email déjà utilisé
2. Validation échoue sur clean_email()
3. Message d'erreur affiché sur le champ email
4. Formulaire réaffiché avec autres données conservées

### Scénario 3 : Inscription avec Mots de Passe Non Correspondants
1. Étudiant saisit deux mots de passe différents
2. UserCreationForm détecte l'erreur
3. Message d'erreur affiché
4. Formulaire réaffiché

### Scénario 4 : Tentative d'Inscription Déjà Connecté
1. Étudiant déjà connecté accède à /inscription/
2. Vue détecte request.user.is_authenticated
3. Redirection immédiate vers /dashboard/

---

## Points de Sécurité

1. **CSRF Protection** : Token CSRF obligatoire dans le formulaire
2. **Validation côté serveur** : Toutes les validations sont refaites côté serveur
3. **Hash du mot de passe** : UserCreationForm hash automatiquement les mots de passe
4. **Compte inactif par défaut** : is_active=False empêche la connexion avant validation
5. **Validation email unique** : Empêche les doublons
6. **Upload de photo sécurisé** : Gestion via request.FILES avec validation

---

## Workflow de Validation Post-Inscription

```
Secrétariat/Président -> Navigateur: Accède à /validations/
Navigateur -> PendingValidationsView: GET /validations/
PendingValidationsView -> User Model: Récupère users avec is_active=False, is_validated=False
User Model -> PendingValidationsView: Retourne liste des utilisateurs en attente
PendingValidationsView -> Navigateur: Affiche liste des comptes à valider
Navigateur -> Secrétariat: Présente la liste

Secrétariat -> Navigateur: Clique sur "Valider" pour un utilisateur
Navigateur -> ValidateUserView: POST /validations/valider/<user_id>/
ValidateUserView -> User Model: Met à jour is_validated=True, is_active=True
User Model -> ValidateUserView: Utilisateur activé
ValidateUserView -> Navigateur: Message de succès + redirection
Navigateur -> Secrétariat: Confirme la validation
```

---

## Technologies Utilisées

- **Framework** : Django 6.0
- **Formulaires** : Django Forms (UserCreationForm, ModelForm)
- **Authentification** : Django Auth System
- **Template Engine** : Django Templates
- **Upload fichiers** : Django FileField/ImageField
- **Validation** : Django validators + validators personnalisés