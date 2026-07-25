# Diagramme de Séquence - Consultation des Résultats par un Étudiant

## Flux Principal

```mermaid
sequenceDiagram
    actor Étudiant
    participant Application
    
    Étudiant->>Application: Se connecter (username, password)
    

        
        Étudiant->>Application: Consulter /resultats/
        Application->>Application: Vérifier droits d'accès
        Application->>Application: Récupérer les notes
        Application-->>Étudiant: Afficher les résultats
        
        opt Impression
            Étudiant->>Application: Demander impression
            Application-->>Étudiant: Afficher version imprimable
        end
    else Identifiants incorrects
        Application-->>Étudiant: Afficher erreur d'authentification
        Étudiant->>Application: Saisir à nouveau les identifiants
    end
```

## Étapes du Processus

1. **Connexion** - L'étudiant s'authentifie
2. **Vérification** - Le système vérifie les droits
3. **Récupération** - Chargement des notes depuis la base de données
4. **Affichage** - Présentation des résultats
5. **Impression** (optionnel) - Génération de la version imprimable

## Règles d'Accès

- ✅ Étudiant authentifié uniquement
- ✅ Filtrage par étudiant connecté
- ✅ Affichage de toutes les notes (consultation)
- ✅ Affichage des notes publiées uniquement (impression)

## Données Affichées

- Cours
- Type d'évaluation
- Date
- Note (/20)
- Résultat (Validé ≥10 / Échec <10)