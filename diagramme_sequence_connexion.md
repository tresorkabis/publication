# Diagramme de Séquence - Processus de Connexion

## Acteurs
- **Utilisateur** : Personne souhaitant se connecter
- **Navigateur** : Interface web
- **LoginView** : Vue Django d'authentification
- **User Model** : Modèle utilisateur Django
- **Session** : Gestion des sessions
- **Dashboard** : Page après connexion

---

## Flux Principal (Succès)

```
Utilisateur -> Navigateur: Accède à /connexion/
Navigateur -> LoginView: GET /connexion/
LoginView -> Navigateur: Affiche formulaire de connexion
Navigateur -> Utilisateur: Affiche page avec champs username/password

Utilisateur -> Navigateur: Saisit username et password
Utilisateur -> Navigateur: Clique sur "Se connecter"
Navigateur -> LoginView: POST /connexion/ (username, password, csrf_token)

LoginView -> LoginView: Valide le token CSRF
LoginView -> User Model: authenticate(username, password)
User Model -> User Model: Vérifie les identifiants
User Model -> LoginView: Retourne objet User (si valide)

alt Identifiants valides
    LoginView -> Session: Crée session utilisateur
    Session -> Session: Stocke user_id en session
    LoginView -> Navigateur: Redirection HTTP 302 vers /dashboard/
    Navigateur -> Dashboard: GET /dashboard/
    Dashboard -> Dashboard: Vérifie authentification (@login_required)
    Dashboard -> Navigateur: Affiche tableau de bord approprié
    Navigateur -> Utilisateur: Affiche dashboard
else Identifiants invalides
    LoginView -> Navigateur: Redirection vers /connexion/ avec erreur
    Navigateur -> Utilisateur: Affiche message d'erreur
end
```

---

## Flux Alternatif - Vérification des Rôles

```
Utilisateur -> Navigateur: Accède au dashboard
Navigateur -> Dashboard: GET /dashboard/
Dashboard -> Session: Récupère user_id de la session
Session -> Dashboard: Retourne user_id
Dashboard -> User Model: Récupère objet User
User Model -> Dashboard: Retourne User avec rôles

alt Utilisateur est Étudiant
    Dashboard -> Dashboard: Affiche résultats et notes
else Utilisateur est Enseignant
    Dashboard -> Dashboard: Redirige vers dashboard_enseignant
else Utilisateur est Chef de Filière
    Dashboard -> Dashboard: Affiche statistiques de la filière
else Utilisateur est Président
    Dashboard -> Dashboard: Affiche validations en attente
end

Dashboard -> Navigateur: Affiche page HTML appropriée
Navigateur -> Utilisateur: Présente le tableau de bord
```

---

## Flux d'Erreur - Compte Non Validé

```
Utilisateur -> Navigateur: POST /connexion/ (identifiants valides mais compte non activé)
LoginView -> User Model: Vérifie is_active et is_validated
User Model -> LoginView: Compte trouvé mais is_active=False

LoginView -> Navigateur: Redirection avec message d'erreur
Navigateur -> Utilisateur: Affiche "Votre compte doit être validé par le secrétariat"
```

---

## Composants Techniques

### 1. Template de Connexion
- **Champs** : username, password
- **Méthode** : POST avec CSRF token
- **Validation** : Côté client (HTML5) + côté serveur (Django)

### 2. Vue d'Authentification
- **URL** : `/connexion/`
- **Template** : `login.html`
- **Authentification** : `django.contrib.auth.authenticate()`
- **Login** : `django.contrib.auth.login()`

### 3. Modèle Utilisateur
- **Champs principaux** : username, password, is_active, is_validated
- **Rôles** : via UtilisateurRole et Role
- **Profils** : Etudiant, Personnel (Enseignant, Chef, Président)

### 4. Gestion des Sessions
- **Stockage** : Cookie de session avec session_id
- **Données** : user_id, _auth_user_id
- **Expiration** : Selon configuration Django

---

## Scénarios d'Utilisation

### Scénario 1 : Connexion Réussie - Étudiant
1. Utilisateur saisit identifiants valides
2. Authentification réussie
3. Session créée
4. Redirection vers dashboard étudiant
5. Affichage des notes et résultats

### Scénario 2 : Connexion Réussie - Enseignant
1. Utilisateur saisit identifiants valides
2. Authentification réussie
3. Session créée
4. Redirection vers dashboard enseignant
5. Affichage des cours et évaluations

### Scénario 3 : Échec d'Authentification
1. Utilisateur saisit identifiants incorrects
2. Échec de l'authentification
3. Message d'erreur affiché
4. Retour au formulaire de connexion

### Scénario 4 : Compte Non Activé
1. Utilisateur saisit identifiants valides
2. Compte existe mais is_active=False
3. Message "compte en attente de validation"
4. Pas de création de session

---

## Points de Sécurité

1. **CSRF Protection** : Token CSRF obligatoire dans le formulaire
2. **Hash du mot de passe** : Django hash automatiquement les mots de passe
3. **Session sécurisée** : Session ID stocké dans cookie HttpOnly
4. **Validation des rôles** : Vérification à chaque accès aux pages protégées
5. **Messages d'erreur génériques** : Pas de distinction entre "utilisateur inexistant" et "mot de passe incorrect"

---

## Technologies Utilisées

- **Framework** : Django 6.0
- **Authentification** : Django Auth System
- **Template Engine** : Django Templates
- **CSS Framework** : Bootstrap 5.3
- **Gestion de session** : Django Sessions (base de données par défaut)