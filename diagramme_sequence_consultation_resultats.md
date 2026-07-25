# Diagramme de Séquence - Consultation des Résultats

## Flux Principal : Étudiant consulte ses résultats

```mermaid
sequenceDiagram
    actor Étudiant
    participant Navigateur as Navigateur Web
    participant Django as Serveur Django
    participant Auth as Système d'Authentification
    participant View as Vue results_list
    participant Model as Modèle Cotation
    participant Template as Template student_results.html

    Étudiant->>Navigateur: Accéder à /resultats/
    Navigateur->>Django: GET /resultats/
    
    Django->>Auth: Vérifier authentification
    
    alt Non authentifié
        Auth-->>Django: Utilisateur non authentifié
        Django-->>Navigateur: Redirection vers /connexion/
        Navigateur-->>Étudiant: Afficher page de connexion
    else Authentifié
        Auth-->>Django: Utilisateur authentifié
        
        Django->>Django: Vérifier si utilisateur est un étudiant
        
        alt Utilisateur est un étudiant
            Django->>View: Appeler results_list(request)
            View->>Model: Cotation.objects.filter(etudiant=etudiant)
            Note right of Model: select_related('evaluation', 'evaluation__cours')
            Model-->>View: Retourner les cotations
            
            View->>Template: render(request, 'results/student_results.html', {'cotations': cotations})
            Template-->>Navigateur: Page HTML avec les résultats
            Navigateur-->>Étudiant: Afficher les résultats
            
            opt Impression des résultats
                Étudiant->>Navigateur: Cliquer sur "Imprimer les résultats"
                Navigateur->>Django: GET /resultats/imprimer/
                Django->>View: Appeler print_results(request)
                View->>Model: Cotation.objects.filter(etudiant=etudiant, evaluation__is_published=True)
                Model-->>View: Retourner les cotations publiées
                View->>Template: render(request, 'results/print_results.html', {...})
                Template-->>Navigateur: Page d'impression
                Navigateur-->>Étudiant: Afficher aperçu avant impression
            end
        else Utilisateur n'est pas un étudiant
            Django-->>Navigateur: Redirection vers /dashboard/
            Navigateur-->>Étudiant: Afficher le dashboard
        end
    end
```

## Légende des Acteurs et Composants

| Acteur/Composant | Rôle |
|------------------|------|
| **Étudiant** | Utilisateur du système qui consulte ses résultats |
| **Navigateur Web** | Interface client (HTML/CSS/JS) |
| **Serveur Django** | Framework web Python |
| **Système d'Authentification** | Vérifie les permissions d'accès |
| **Vue results_list** | Logique métier de consultation des résultats |
| **Modèle Cotation** | Accès aux données des notes |
| **Template student_results.html** | Affichage des résultats |

## Chemins d'URL Impliqués

| URL | Vue | Description |
|-----|-----|-------------|
| `/resultats/` | `results_list` | Liste des résultats de l'étudiant |
| `/resultats/imprimer/` | `print_results` | Version imprimable des résultats |

## Modèles de Données Utilisés

```
User (Étudiant)
    └── Etudiant
        └── Cotation (note)
            └── Evaluation
                ├── Cours
                │   └── Filiere
                └── TypeEvaluation
```

## Conditions d'Accès

1. **Authentification requise** : L'utilisateur doit être connecté
2. **Rôle étudiant** : Seuls les utilisateurs avec le profil `Etudiant` peuvent accéder à cette page
3. **Évaluations publiées** : Pour l'impression, seules les évaluations avec `is_published=True` sont affichées

## Points d'Attention

- La vue `results_list` ne filtre pas par `is_published`, elle affiche toutes les cotations
- La vue `print_results` filtre uniquement les évaluations publiées
- Les notes sont affichées sur 20 avec un badge de validation (≥10 = Validé, <10 = Échec)