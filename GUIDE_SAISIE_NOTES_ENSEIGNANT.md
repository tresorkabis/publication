# Guide : Saisie des Notes par l'Enseignant

## Accès au système

1. **Se connecter** : Aller sur http://localhost:8000/connexion/
2. **Identifiants** :
   - Username : `ens_math2` (ou tout autre enseignant avec cours)
   - Mot de passe : `demo`

## Processus de saisie des notes

### Étape 1 : Accéder au dashboard enseignant
- Après connexion, l'enseignant est automatiquement redirigé vers son dashboard
- URL : http://localhost:8000/dashboard/enseignant/

### Étape 2 : Voir les évaluations à venir
- Dans le dashboard, section "Évaluations à venir"
- Cliquer sur le bouton **"Saisir notes"** (badge orange) pour l'évaluation souhaitée

**OU**

- Aller dans "Mes Cours Assignés" → "Voir tout"
- Cliquer sur le bouton "Saisir notes" sous chaque évaluation non publiée

### Étape 3 : Saisir les notes
- La page affiche tous les étudiants inscrits dans la filière du cours
- Pour chaque étudiant :
  - Nom complet
  - Matricule
  - Champ de saisie de la note (0 à 20, pas de 0.25)
  
- Saisir la note dans le champ prévu
- Les notes déjà saisies apparaissent avec un fond vert

### Étape 4 : Enregistrer
- Cliquer sur le bouton **"Enregistrer les notes"**
- Un message de confirmation apparaît
- Redirection automatique vers la page des cours

## Exemple concret

**Enseignant** : Enseignant_MATH_2 Mukendi Anne (ens_math2)

**Cours assignés** :
1. Marketing (GESTL102) - Gestion des Entreprises - Semestre 2
2. Astrophysique (PHYL204) - Physique Fondamentale - Semestre 4

**Pour saisir les notes du cours "Marketing"** :
1. Se connecter avec ens_math2 / demo
2. Dans "Évaluations à venir", cliquer sur "Saisir notes" pour l'évaluation de Marketing
3. Saisir les notes pour chaque étudiant (ex: 14.5, 16, 12.25)
4. Cliquer sur "Enregistrer les notes"

## Points importants

- ✅ L'enseignant ne peut saisir des notes que pour ses propres cours
- ✅ Les notes sont sauvegardées automatiquement (création ou modification)
- ✅ Les notes sont sur 20 points
- ✅ Seul le chef de filière peut publier les évaluations
- ✅ L'enseignant peut modifier les notes tant que l'évaluation n'est pas publiée

## Structure des URLs

- Dashboard enseignant : `/dashboard/enseignant/`
- Mes cours : `/dashboard/enseignant/cours/`
- Saisie des notes : `/dashboard/enseignant/saisie-notes/<evaluation_id>/`

## Comptes de test

| Username | Nom | Mot de passe | Cours assignés |
|----------|-----|--------------|----------------|
| ens_math2 | Enseignant_MATH_2 Mukendi Anne | demo | 2 cours |
| ens_gest1 | Enseignant_GEST_1 Kabila Jean | demo | 1 cours |
| ens_gest2 | Enseignant_GEST_2 Mutombo Paul | demo | 2 cours |

## Support

Pour toute question, contacter l'administrateur système.