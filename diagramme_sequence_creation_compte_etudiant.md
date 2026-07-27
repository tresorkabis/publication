# Diagramme de Séquence - Création de Compte Étudiant

## Participants
- Étudiant
- Navigateur
- Vue Inscription
- Formulaire
- Base de Données

---

## Séquence

```
Étudiant -> Navigateur: Accède à /inscription/
Navigateur -> Vue Inscription: GET /inscription/
Vue Inscription -> Formulaire: Crée formulaire vide
Formulaire -> Vue Inscription: Retourne formulaire
Vue Inscription -> Navigateur: Affiche register.html
Navigateur -> Étudiant: Affiche formulaire

Étudiant -> Navigateur: Remplit formulaire (username, email, nom, postnom, prenom, sexe, tel, mat, adresse, photo, password1, password2)
Étudiant -> Navigateur: Clique "S'inscrire"
Navigateur -> Vue Inscription: POST /inscription/ (données + fichier)

Vue Inscription -> Formulaire: Crée formulaire avec POST + FILES
Formulaire -> Formulaire: Valide champs
Formulaire -> Formulaire: Vérifie unicité email
Formulaire -> Formulaire: Vérifie password1 == password2

alt Formulaire valide
    Formulaire -> Vue Inscription: Retourne formulaire valide
    Vue Inscription -> Base de Données: Crée User (is_active=False, is_validated=False)
    Base de Données -> Vue Inscription: User créé
    
    Vue Inscription -> Base de Données: Crée profil Etudiant
    Base de Données -> Vue Inscription: Etudiant créé
    
    Vue Inscription -> Base de Données: Récupère rôle "etudiant"
    Base de Données -> Vue Inscription: Rôle récupéré
    
    Vue Inscription -> Base de Données: Crée UtilisateurRole
    Base de Données -> Vue Inscription: Association créée
    
    Vue Inscription -> Navigateur: Message succès + redirection /
    Navigateur -> Étudiant: Affiche page d'accueil
    
else Formulaire invalide
    Formulaire -> Vue Inscription: Retourne erreurs
    Vue Inscription -> Navigateur: Affiche formulaire avec erreurs
    Navigateur -> Étudiant: Affiche messages d'erreur
end