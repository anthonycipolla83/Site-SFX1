# Guide de l'espace d'administration — site SFX1

## Ce que permet le crayon
Après connexion à `www.sfx1.org/admin`, un crayon jaune apparaît sur les blocs modifiables du site.
Il ouvre directement la bonne fiche : actualités, portes ouvertes (dont le lien de réservation des créneaux),
documents PDF, vidéos, photos, grille du tronc commun, immersion, école fondamentale, équipe, histoire, formulaire.

- **Remplacer un PDF** : Documents → choisir le document → « Fichier PDF » → déposer la nouvelle version → Enregistrer.
  Le document s'ouvre ensuite directement dans le navigateur, sans passer par Google Drive.
- **Changer une photo** : champ « Photo » → déposer l'image. Le site crée lui-même les formats optimisés.
  Vérifier les autorisations de droit à l'image (élèves mineurs).
- **Ajouter une vidéo** : Vidéos → Ajouter → déposer le fichier MP4 (idéalement moins de 50 Mo ; limite GitHub : 100 Mo par fichier).
- Le site en ligne est mis à jour automatiquement 1 à 2 minutes après l'enregistrement.

- **Ouvrir la réservation des portes ouvertes** : Portes ouvertes → coller le lien de l'application → cocher « Réservation ouverte ».
- **Brancher l'agenda** : Agenda (application de l'école) → coller l'adresse → cocher « Afficher l'agenda dans la page » si l'application le permet.
- **Réafficher les vidéos** : Options du site → « Afficher les vidéos ».

## Sécurité
Le crayon n'est qu'un raccourci d'affichage : sans connexion autorisée, aucune modification n'est possible.
Chaque administrateur dispose de son propre accès, révocable à tout moment.
Administrateurs prévus : anthony.cipolla@sfx1.org, cedric.schmetz@sfx1.org, quentin.fransolet@sfx1.org.

## Mise en place (une seule fois, par la personne technique)
1. Créer un dépôt GitHub privé (ex. `sfx1/site-sfx1`) et y placer le contenu du dossier SOURCES_V5.
2. Chaque administrateur crée un compte GitHub gratuit avec son adresse @sfx1.org ; l'inviter comme collaborateur du dépôt.
3. Dans `admin/config.yml`, le dépôt est réglé sur `anthonycipolla83/Site-SFX1` (à adapter si le dépôt change de nom ou de compte).
4. **Netlify** : « Add new site » → « Import from GitHub » → choisir le dépôt. La configuration (`netlify.toml`) est déjà prête.
   Formulaire : Netlify → Forms → Notifications → « Email notification » vers info@sfx1.org.
5. **OVH (plus tard)** : construire le site avec GitHub Actions et l'envoyer par SFTP ; dans `data/contenus/formulaire.json`,
   mettre `"mode": "ovh"` (le fichier `contact.php` envoie alors les messages à info@sfx1.org).
6. Connexion à l'administration : bouton « Se connecter avec GitHub » (ou avec un jeton personnel GitHub).

## Test en local, sans hébergement
1. Ouvrir `admin/index.html` dans Chrome ou Edge via un petit serveur local, ou choisir « Travailler avec un dépôt local »
   et sélectionner le dossier SOURCES_V5 (connexion Internet nécessaire pour charger l'interface).
2. Après modification, lancer `reconstruire-le-site` (.bat sous Windows, .command sous Mac ; Python 3.12+ et Pillow requis).
3. Ouvrir `SFX1_V5_TEST/index.html` pour voir le résultat.
