# Habit Tracker pour Home Assistant

**Vos habitudes, anneaux de progression et réalisations quotidiennes dans Home Assistant.**

[English](README.md) · Français

Cette intégration connecte un backend Habit Tracker existant à Home Assistant.
Elle crée les entités de vos habitudes et fournit une carte Lovelace : anneaux par
catégorie, cases à cocher, quantités, comparaison hebdomadaire et heatmap sur 13 semaines.
Les boutons enregistrent de vrais événements côté backend. Les changements arrivent
par une connexion SSE, avec un rafraîchissement de secours toutes les 60 secondes.

La carte est incluse et chargée automatiquement. Aucune interface séparée, carte
Mushroom, ressource JavaScript manuelle ou entité helper n'est nécessaire.

## Installation

### 1. Préparer la connexion au backend

Prérequis :

- **Home Assistant 2026.10.2 ou plus récent** et [HACS](https://www.hacs.dev/docs/use/).
- Un backend Habit Tracker existant, avec `/api/v1/dashboard` et
  `/api/v1/dashboard/events`, accessible depuis le serveur HA.
- Un PAT Habit Tracker ou un token de compte de service avec ces scopes :

| Scope | Utilité |
| --- | --- |
| `habits:read` | Lire les habitudes et leurs paramètres |
| `statistics:read` | Lire les progressions et l'historique du dashboard |
| `entries:write` | Cocher/décocher et ajouter/retirer des quantités |

Demandez à l'administrateur du backend son **URL de base** et un token avec une
expiration adaptée. Utilisez un token Habit Tracker, distinct des credentials
GitHub ou d'un token longue durée Home Assistant. Les habitudes sont créées via
l'API backend ; cette intégration les affiche et enregistre leurs réalisations.

### 2. Ajouter le dépôt dans HACS

1. Ouvrez **HACS** dans Home Assistant.
2. Ouvrez **⋮ → Dépôts personnalisés**.
3. Ajoutez cette URL :

   ```text
   https://github.com/floriaaan/habit-tracker-ha
   ```

4. Choisissez le type **Integration / Intégration**, puis **Ajouter**.
5. Recherchez **Habit Tracker**, ouvrez sa page et téléchargez la dernière release.
6. **Redémarrez Home Assistant** pour charger l'intégration Python.

Cette seule entrée HACS fournit l'intégration et la carte.

### 3. Configurer Habit Tracker dans Home Assistant

1. Ouvrez **Paramètres → Appareils et services → Ajouter une intégration**.
2. Recherchez et sélectionnez **Habit Tracker**.
3. Remplissez le formulaire :

   | Champ | Valeur |
   | --- | --- |
   | **URL de l'API** | URL de base du backend, sans `/api/v1` |
   | **Token API** | Token Habit Tracker préparé à l'étape 1 |
   | **Autoriser HTTP sur une liaison locale de confiance** | À cocher seulement pour une liaison HTTP locale fiable ; HTTPS est le défaut |

4. Validez. HA vérifie l'URL, le token et les scopes de lecture avant d'enregistrer.
5. Ouvrez les entités de l'intégration et trouvez le capteur **Dashboard**. Son
   identifiant habituel est `sensor.habit_tracker_dashboard` ; copiez celui réellement
   attribué par HA.

L'URL doit fonctionner **depuis le serveur HA**. `localhost` désigne HA lui-même ;
un nom interne Docker fonctionne seulement si les conteneurs partagent ce réseau.
Avec HTTPS, le certificat doit être reconnu par HA. L'intégration ne suit pas les
redirections avec votre token.

### 4. Ajouter la première carte

1. Rechargez le navigateur après configuration de l'intégration.
2. Ouvrez un dashboard modifiable, ou créez-en un dans **Paramètres → Tableaux de bord**.
3. Choisissez **Modifier le tableau de bord → Ajouter une carte → Manuel**.
4. Collez ce YAML, en adaptant l'identifiant du capteur si nécessaire :

   ```yaml
   type: custom:habit-tracker-card
   entity: sensor.habit_tracker_dashboard
   mode: rings
   ```

5. Enregistrez. La carte affiche les vraies progressions des habitudes du backend.

Pour la disposition complète, utilisez [dashboard.yaml](custom_components/habit_tracker/www/dashboard.yaml)
dans l'**éditeur de configuration brute** d'un nouveau tableau de bord, en remplaçant
partout l'identifiant du capteur. Le fichier contient un dashboard entier avec vues
et sections.

### 5. Choisir les vues

Ajoutez d'autres cartes manuelles avec la même `entity` et l'un de ces modes :

| `mode` | Vue |
| --- | --- |
| `rings` | Anneaux par catégorie et score global |
| `habits` | Groupes, compteurs et cases à cocher |
| `nutrition` | Hydratation et alimentation avec commandes +/− |
| `sport` | Objectifs sportifs et commandes de quantité |
| `weekly` | Semaine actuelle comparée à la précédente |
| `heatmap` | 13 semaines d'historique réel |

Pour filtrer un groupe d'habitudes :

```yaml
type: custom:habit-tracker-card
entity: sensor.habit_tracker_dashboard
mode: habits
category: mind
```

Les catégories sont `mind` (Esprit), `daily` (Quotidien), `sport` et `nutrition`
(Alimentation). Icônes, couleurs, ordre, poids, pas de quantité et rappels viennent
des paramètres backend. La configuration est traduite en anglais et en français ;
les libellés actuels de la carte sont en français.

## Utilisation

HA crée un capteur Dashboard, un capteur de progression par habitude, des switches
pour les habitudes booléennes et des boutons ajouter/retirer pour les autres types.
Les nouvelles habitudes apparaissent automatiquement ; celles archivées deviennent
indisponibles. La carte utilise les états HA et appelle `habit_tracker.perform_action`,
sans stocker de credential API dans Lovelace.

Les cases et les commandes +/− mettent à jour les réalisations et les statistiques
du backend. Retirer une quantité corrige ou annule les entrées manuelles ; les
entrées Strava sont conservées. Le backend gère repos, fuseaux horaires, éligibilité
et idempotence. Les notifications nécessitent une configuration distincte du
connecteur HA sortant sur le backend.

## Mises à jour

Installez les mises à jour depuis HACS, redémarrez HA puis rechargez le navigateur.
Les config entries et identifiants des entités sont conservés ; les données restent
dans le backend. En migration depuis une carte installée manuellement, retirez
l'ancienne ressource Lovelace `/local/habit-tracker/habit-tracker-card.js?...`
pour charger la carte embarquée. Conservez l'intégration existante.

## Dépannage

| Symptôme | À vérifier |
| --- | --- |
| Connexion impossible | URL accessible depuis HA, chemin de base, certificat et reverse proxy |
| Authentification invalide ou actions refusées | Expiration/révocation du token et les trois scopes ; utiliser la réauthentification proposée par HA |
| Type de carte inconnu | Intégration chargée, navigateur complètement rechargé, ancienne ressource JS manuelle retirée |
| Carte vide ou indisponible | Identifiant réel du capteur Dashboard, disponibilité du backend, habitudes créées via son API |
| Mises à jour lentes | Buffering SSE désactivé au proxy et connexions longues autorisées ; secours toutes les 60 secondes |

Les tokens restent côté serveur dans les config entries HA. Protégez `.storage`
et ses sauvegardes, et partagez les entités uniquement avec les utilisateurs HA
autorisés à accéder aux données. Exclure les gros attributs du capteur Dashboard
de Recorder peut éviter de stocker deux fois l'historique si celui du backend suffit.

L'installation manuelle reste possible : copiez `custom_components/habit_tracker`
dans la configuration HA, puis reprenez aux étapes de redémarrage et configuration.

Licence MIT — [LICENSE](LICENSE).
