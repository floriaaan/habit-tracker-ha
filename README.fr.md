# Habit Tracker pour Home Assistant

**Vos habitudes, anneaux de progression et réalisations quotidiennes dans Home Assistant.**

[English](README.md) · Français

Cette intégration connecte un backend Habit Tracker existant à Home Assistant.
Elle crée les entités de vos habitudes et fournit une carte Lovelace : anneaux par
catégorie, cases à cocher, quantités, comparaison hebdomadaire et heatmap sur 13 semaines.
Les boutons enregistrent de vrais événements côté backend. Les changements arrivent
par une connexion SSE, avec un rafraîchissement de secours toutes les 60 secondes.

La carte est incluse et déclarée automatiquement quand les ressources Lovelace
sont gérées dans l'interface HA. Pour des ressources YAML, suivez la déclaration
ci-dessous. Aucune carte Mushroom ni entité helper n'est nécessaire.

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
| `habits:write` | Créer des habitudes depuis HA ; facultatif pour la consultation et les réalisations |

Demandez à l'administrateur du backend son **URL de base** et un token avec une
expiration adaptée. Utilisez un token Habit Tracker, distinct des credentials
GitHub ou d'un token longue durée Home Assistant. Les habitudes se créent depuis **Configurer** sur l’intégration HA, avec un preset
ou un formulaire libre.

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

#### Si les ressources Lovelace sont gérées en YAML

Depuis la version 0.1.2, l’intégration enregistre la carte comme ressource Lovelace en mode UI/storage.
Si votre configuration utilise `resource_mode: yaml`, ajoutez plutôt cette entrée
à votre bloc `lovelace` existant dans `configuration.yaml` :

```yaml
lovelace:
  resource_mode: yaml
  resources:
    - url: /habit_tracker/frontend/0.2.0/habit-tracker-card.js
      type: module
```

Conservez les autres ressources. Rechargez les ressources Lovelace ou redémarrez
HA, puis rechargez le navigateur. Actualisez la version dans cette URL lors des
mises à jour ; l'intégration ne modifie pas vos fichiers YAML.

### 4. Créer vos habitudes dans HA

Mettez à jour le backend pour disposer de `POST /api/v1/habits/setup` (image GHCR
actuelle). Dans **Paramètres → Appareils et services → Habit Tracker**, cliquez
sur **Configurer** pour ouvrir le parcours de création :

1. Choisissez **Partir d’un preset** ou **Créer une habitude libre**.
2. Adaptez nom, catégorie, type, unité, objectif, période, pas des boutons et fuseau.
3. Validez : l’habitude et sa présentation sont enregistrées ensemble dans le backend.
4. Ajoutez une autre habitude ou choisissez **Terminer**. Les nouvelles entités et
   les cartes sont actualisées automatiquement.

| Preset | Objectif proposé | Pas +/− |
| --- | --- | --- |
| Lecture | Oui/non quotidien | 1 réalisation |
| Méditation | 600 secondes par jour | 60 secondes |
| Rangement | Oui/non quotidien | 1 réalisation |
| Hydratation | 2 000 mL par jour | 250 mL |
| Fruits et légumes | 5 portions par jour | 1 portion |
| Course | 25 000 mètres par semaine | 1 000 mètres |
| Natation | 3 000 mètres par semaine | 100 mètres |

Ce sont des suggestions : rien n’est créé avant validation. Le fuseau HA est
proposé par défaut ; unités et objectifs restent ceux affichés dans le formulaire.
Une erreur réseau réutilise la même clé de création pour éviter un doublon.
Les jours d’éligibilité sont tous les jours par défaut ; les fenêtres horaires,
exceptions et modifications d’habitudes existantes restent accessibles via l’API.

Si le token actuel n’a pas `habits:write`, émettez un token de remplacement pour
le même utilisateur avec ce scope et les trois scopes précédents. Dans le menu
**⋮ de l’entrée d’intégration → Reconfigurer**, remplacez le token ; conservez
l’entrée et les entités existantes. Un refus de création ne bloque pas les lectures.

### 5. Ajouter et configurer une carte visuellement

1. Rechargez le navigateur après configuration ou mise à jour de l’intégration.
2. Ouvrez un dashboard modifiable, puis **Modifier → Ajouter une carte**.
3. Recherchez **Habit Tracker**, sélectionnez la carte, puis choisissez son capteur
   **Dashboard** et sa **Vue** dans l’éditeur visuel.
4. Pour la vue **Habitudes**, choisissez éventuellement une catégorie ; sans filtre,
   toutes les catégories sont affichées.
5. Enregistrez. L’édition ultérieure utilise le même formulaire : aucun YAML requis.

Le capteur Dashboard est proposé automatiquement lorsqu’il est disponible.
Si aucune habitude n’existe, la carte propose **Créer mes habitudes**, qui renvoie
vers la configuration de l’intégration.

<details>
<summary>Configuration YAML équivalente</summary>

```yaml
type: custom:habit-tracker-card
entity: sensor.habit_tracker_dashboard
mode: rings
```

Adaptez `entity` si HA a choisi un autre identifiant. Pour la disposition complète,
utilisez [dashboard.yaml](custom_components/habit_tracker/www/dashboard.yaml) dans
l’éditeur de configuration brute d’un tableau de bord. Les anciennes cartes YAML
restent compatibles avec l’éditeur visuel.

</details>

### 6. Choisir les vues

Choisissez une vue dans l’éditeur visuel, ou son équivalent `mode` en YAML :

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

Installez les mises à jour depuis HACS, redémarrez HA puis rechargez complètement le navigateur.
En mode ressources UI/storage, la déclaration est créée ou mise à jour sans doublon ;
en mode ressources YAML, actualisez aussi l’URL versionnée ci-dessus.
Les config entries et identifiants des entités sont conservés ; les données restent
dans le backend. En migration depuis une carte installée manuellement, retirez
l'ancienne ressource Lovelace `/local/habit-tracker/habit-tracker-card.js?...`
pour charger la carte embarquée. Conservez l'intégration existante.

## Dépannage

| Symptôme | À vérifier |
| --- | --- |
| Connexion impossible | URL accessible depuis HA, chemin de base, certificat et reverse proxy |
| Authentification invalide ou actions refusées | Expiration/révocation du token et les scopes requis pour l’action ; utiliser Reconfigurer pour remplacer le token |
| Type de carte inconnu | Intégration configurée et chargée, navigateur complètement rechargé ; carte présente dans les ressources Lovelace en type Module JavaScript ; en YAML, ajouter la déclaration ci-dessus |
| Carte vide ou indisponible | Identifiant réel du capteur Dashboard, disponibilité du backend, habitudes créées via Configurer ou son API |
| Mises à jour lentes | Buffering SSE désactivé au proxy et connexions longues autorisées ; secours toutes les 60 secondes |

Pour débloquer une version **0.1.1**, ajoutez manuellement
`/habit_tracker/frontend/0.1.1/habit-tracker-card.js` comme ressource de type
**Module JavaScript** dans Paramètres → Tableaux de bord → ⋮ → Ressources, puis
rechargez le navigateur. Une réponse 404 sur cette URL indique que l'intégration
n'est pas chargée, que la version est différente ou que le proxy bloque ce chemin.
La mise à jour 0.1.2 remplace cette ressource automatiquement en mode UI/storage.

Les tokens restent côté serveur dans les config entries HA. Protégez `.storage`
et ses sauvegardes, et partagez les entités uniquement avec les utilisateurs HA
autorisés à accéder aux données. Exclure les gros attributs du capteur Dashboard
de Recorder peut éviter de stocker deux fois l'historique si celui du backend suffit.

L'installation manuelle reste possible : copiez `custom_components/habit_tracker`
dans la configuration HA, puis reprenez aux étapes de redémarrage et configuration.

Licence MIT — [LICENSE](LICENSE).
