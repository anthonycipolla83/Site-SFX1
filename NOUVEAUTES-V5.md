# SFX1 — Nouveautés de la V5 par rapport à la V4

Toutes les rubriques et tous les contenus de la V4 sont conservés. Rien n'a été supprimé.

## Architecture
- **Site multipage** : 18 vraies pages HTML (une par rubrique) au lieu d'une page unique générée par JavaScript. Le contenu s'affiche même sans JavaScript, chaque page a son propre titre et sa propre description, et les liens partagés montrent un aperçu.
- Le test local reste simple : double-clic sur `index.html`.
- Générateur `build.py` + contenus séparés dans `data/*.json` (actualités, agenda, documents, vidéos, grilles), prêts pour un futur outil d'administration.
- Nouveaux fichiers : `404.html`, `sitemap.xml`, `robots.txt` (indexation bloquée pendant les tests), favicon, `netlify.toml` et `.htaccess` (OVH) avec en-têtes de sécurité.

## Nouvelles pages et sections
- **Grilles & options** (`grilles.html`) : les 3 grilles retranscrites en tableaux interactifs, interrupteur « Cours en néerlandais », options présentées ligne par ligne avec les règles de choix, descriptions dépliables, PDF officiels toujours disponibles. La grille D2, qui n'était qu'une image, est désormais lisible et accessible.
- **Accueil** : chiffres clés animés, blocs « Actualités » et « Agenda », vidéos.
- **Le Collège** : galerie « Cadre de vie », emplacement réservé pour la frise historique (dates à fournir).
- **Immersion** : frise du parcours D1 → D3 avec les cours en néerlandais, intérêt pédagogique, deuxième photo de classe.
- **Fondamental** : projets éducatifs, contacts propres, informations pratiques.
- **Inscriptions** : contacts secondaire et fondamental, questions fréquentes, emplacement réservé aux documents à fournir.
- **Contact** : carte OpenStreetMap chargée uniquement au clic.
- **Mon espace** : architecture recommandée (accès sécurisés par Google Workspace @sfx1.org).
- **Mentions légales** et **Confidentialité** : modèles à compléter.

## Navigation
- Sous-menus (Le Collège, Secondaire, Fondamental, Vie à SFX1), accessibles au clavier.
- Bouton « S'inscrire » toujours visible ; « Mon espace » rendu plus discret (fonction future).
- Fil d'Ariane sur chaque page ; la rubrique parente est surlignée sur les sous-pages.

## Images
- Fichiers renommés selon leur contenu réel. **Correction** : la photo de chorale nommée `batiments.jpg` illustrait « Une histoire forte » et la vidéo « Visite du Collège » ; elle est remplacée par une vraie vue des bâtiments.
- Diaporama d'accueil ouvert sur la cour animée (au lieu du jardin d'hiver sombre).
- Cadres « polaroïd », horodatage et mention « NOTE 10 » supprimés par recadrage.
- Formats WebP + JPEG en plusieurs tailles, dimensions déclarées : chargement plus rapide sur mobile.
- Les 6 icônes de documents sont détourées et utilisées dans la bibliothèque. `rencontre.jpg` et `image2.jpg` sont préparées pour de futures actualités.

## Dynamisme et ergonomie
- Apparitions en cascade, compteurs animés, barre de progression du diaporama, zooms doux sur les photos, transitions de page.
- Bibliothèque de documents : recherche + filtres + badges de type (PDF, dossier Google Drive, ancien site).
- Toutes les animations sont désactivées si le visiteur a choisi de réduire les mouvements.

## Accessibilité
- Onglets utilisables aux flèches du clavier, avec liens onglet ↔ panneau.
- Diaporama mis en pause au focus clavier (et plus seulement au survol).
- Menu mobile refermable avec Échap ; contour de focus bien visible.
- Annonces vocales lors des filtrages ; textes alternatifs revus.

## RGPD et performance
- Polices Inter hébergées sur le site (aucune connexion à Google Fonts).
- YouTube (youtube-nocookie) et la carte ne se chargent qu'après un clic.
- Aucune mesure d'audience, aucun cookie.
- Étiquettes « À VALIDER » sur tous les contenus provisoires.

## Points relevés dans les documents (à faire valider)
- D3 : le PDF renvoie à des conditions « ci-après » pour dépasser 32 périodes, absentes des documents.
- D2 (description) : l'activité scientifique d'immersion prépare à « sciences 6 heures en 5e », alors que la grille D3 indique sciences 7h.
- D1 : la grille cite « Activités musicales » et « Arts de la parole », la description « Activités artistiques 2h ou 4h ».
- Millésimes des fichiers différents (2021 / 2024 / « Copie »).

## Mise à jour V5.1 (20/11/2026, après-midi)
- **170 ans** : « 150+ ans » remplacé par « Depuis 1855 » et « 170 ans d'histoire » (chiffre clé animé sur l'accueil). Source : reportage Vedia du 03/12/2025. Reste marqué « À valider ».
- **Frise historique** sur la page Le Collège : 1855, 1968, 1980, 1984, 2025 (sources : Wikipédia, Vedia), à valider par la direction.
- **Dans les médias** : nouvelle section « Ils parlent de nous » (accueil + Vie à SFX1) avec 5 reportages et articles (Vedia, jesuites.com, L'Avenir). Liens vers les sites des médias, sans intégrer leurs lecteurs.
- **Nouvelles vidéos YouTube** :
  - « Développer le maximum des possibilités de chacun » : en vedette (grand format) sur l'accueil et sur Le Collège.
  - « Immersion en néerlandais » : accueil et page Immersion.
  - « Un accompagnement personnalisé » : page Secondaire.
- **8 vidéos Google Drive** dans une nouvelle section « Les plus récentes » en haut de la page Vidéos, de la plus récente à la plus ancienne (lecteur chargé au clic). Titres à préciser ; les fichiers doivent être partagés « Tous les utilisateurs disposant du lien » pour être lus par le public.
- **Semaine RCD** : reportage vidéo et article de RTL info (10/01/2025) ajoutés en tête de la section « Dans les médias », visibles aussi sur l'accueil. Reportage Vedia : lien encore à fournir.

## Mise à jour V5.2 (24/11/2026)
- **Onglet « Inscriptions » retiré** (menu, bouton d'en-tête, pied de page et page). Les liens qui y menaient pointent désormais vers les portes ouvertes ou le contact.
- **Accès très visible au site de l'école fondamentale** :
  - bandeau permanent tout en haut de chaque page (« École fondamentale — Accéder au site du fondamental ↗ ») ;
  - premier lien du menu Fondamental, bouton dans le héros de l'accueil, tuile « École fondamentale » ;
  - grand encadré vert sur l'accueil, la page Fondamental et la page Portes ouvertes ;
  - adresse réglable dans `data/contenus.json` → `fondamental_url` (actuellement l'espace fondamental du Google Sites, à confirmer).
- **Onglet « Portes ouvertes » temporaire** (samedi 30 janvier 2027, 9h - 11h - 14h - 16h) :
  - visible automatiquement du 24/11/2026 au 31/01/2027, puis masqué sans intervention (dates dans `data/contenus.json` → `portes_ouvertes`) ;
  - nouvelle page `portes-ouvertes.html` : affiche, créneaux, compte à rebours, pourquoi choisir SFXun, projets, téléchargement de l'affiche A4 et du visuel réseaux sociaux ;
  - grand bloc sur l'accueil, lien dans le bandeau du haut et bouton d'en-tête.
  - Lien d'inscription aux visites : à fournir (`inscription_url`) ; en attendant, renvoi vers info@sfx1.org.
- **Contenus de la brochure 2026 intégrés, avec la nouvelle appellation S1 / S2** :
  - Grilles & options : nouvel onglet « Tronc commun » (S1 dès 2026-2027, S2 dès 2027-2028, 3e), options actuelles et activités complémentaires ; l'ancienne grille du 1er degré reste disponible pour la 2e année 2026-2027 ;
  - Secondaire : « L'excellence, un chemin accompagné » (8 dispositifs), transition fondamental-secondaire, après le premier degré, informations pratiques (numérique, encadrement, temps de midi), école au cœur de la ville ;
  - Immersion : cours en néerlandais de la S1 à la 6e, évaluation, atouts, activités (Hasselt, séjours), langues modernes 1-2-3 ;
  - Le Collège : projet éducatif et 4 engagements, équipe de direction (d'après la présentation 2026).
- **Documents** : les grilles et descriptions renvoient aux nouvelles versions SFX1 (originaux toujours disponibles) ; nouvelle catégorie « Portes ouvertes ».
- À vérifier : 8 périodes d'« activités orientantes » en 3e (la réforme évoque 6 périodes).

## Mise à jour V5.3 (24/11/2026) — page Facebook du Collège
- **Actualités réelles et datées** (Vie à SFX1 + accueil), reprises de la page Facebook @collegesfx1, avec lien vers la publication : chorale sélectionnée au concours « Kachpatavoix » de l'IMEP (18/12/2025), correspondants néerlandais et séjour à Zutphen (16/11/2025), Concours Corsica 2025 avec l'ULiège (25/04/2025), stage Arts d'expression au Château de Courrière (24/03/2025), théâtre « Pouvoir » pour les 3e (24/01/2025), correspondants flamands des 1re et 2e (24/01/2025). Les anciennes cartes « exemples » sont remplacées. Les photos sont des photos d'illustration (mention sur chaque carte).
- **« Idées reçues ? »** : cartes à retourner (accueil et page Portes ouvertes) reprenant la campagne Facebook de janvier 2026 — centre-ville, élitisme, entre-soi, immersion.
- **Immersion** : certificat B2 délivré par la KU Leuven, 8 à 12 heures de cours en néerlandais selon l'année, échanges avec Hasselt et Zutphen.
- **Liens Facebook et YouTube** dans le pied de page ; bandeau « Suivez-nous sur Facebook » dans Vie à SFX1.

## Mise à jour V5.4 (24/11/2026) — livre des 150 ans
- **Nouvelle page « Notre histoire »** (`histoire.html`, menu Le Collège) d'après le livre « Un Collège, une tradition jésuite. 1855-2005 » (scan de 112 pages, texte récupéré par reconnaissance de caractères) :
  - chiffres clés animés (1855, 1978, 1980, 170) ;
  - 9 grandes périodes de 1845 à aujourd'hui, avec navigation rapide et 6 illustrations d'époque tirées du livre (place Verte vers 1830, maquette du Collège, église du Sacré-Cœur, croquet vers 1895, cour dans les années 60, bâtiments de 1977) ;
  - chronologie de 16 dates ;
  - « Des maîtres de l'ombre » et « Les anciens à l'œuvre » (d'après le sommaire du livre).
- **Page Le Collège** : la frise utilise désormais les dates du livre (les repères issus de Wikipédia sont retirés) et renvoie vers la page Histoire.
- Textes résumés et reformulés à partir du livre ; à relire par la direction.

## V5.5 — Site plus fluide, plus court, plus vendeur
- Retrait des deux articles de presse évoquant SFX2 (semaine jésuite commune).
- Accueil resserré : « Pourquoi choisir SFX1 ? » (6 arguments + chiffres clés), idées reçues, parcours, une vidéo, 3 actualités, fondamental, appel final. Retirés de l'accueil (toujours disponibles sur leurs pages) : présentation en double, cartes parcours, 4C, presse, agenda provisoire, grille vidéos.
- Histoire raccourcie : 5 moments clés illustrés en défilement horizontal + 6 anciens célèbres. Page Collège : mini-frise de 6 dates.
- Fluidité : transitions animées entre pages (View Transitions), préchargement des pages au survol (Speculation Rules, CSP adaptée), barre d'accès rapides sur mobile (Appeler · Portes ouvertes · Fondamental · Itinéraire).

## V5.6 — Corrections de la direction
- Presse : retour des articles « semaine jésuite » SFX1/SFX2. Aucune mention des Saints-Anges/SFX2 (1984) dans la ligne du temps.
- Immersion : heures comptées avec le cours de néerlandais (S1 8 h, S2 10 h, 3e ancien système 11 h = maximum, S3 10 h, 4e 9 h sans sciences mais avec 1 h d’actualité, 5e-6e 8 h). Accueil : « jusqu’à 11 h ».
- Tronc commun : colonne S3 (dès 2028-2029) ; LM1 4 h en S1, 3 h en S2 et S3 (totaux à confirmer).
- Secondaire : nouveau bloc « Deux systèmes cohabitent » (2026-2027 à 2028-2029).
- Portes ouvertes : bouton « Réserver mon créneau » prêt ; il s’active partout dès que l’adresse est saisie dans data/contenus.json → portes_ouvertes.inscription_url.

## V5.7 — Tronc commun S1-S3 et vraies pages du fondamental
- Grille du tronc commun S1 / S2 / S3 selon la grille de référence transmise (32 périodes de 50 min, sans colonne d’observations, domaines d’orientation en S3). Nouveau PDF « TC-Grille-horaire-tronc-commun-SFX1.pdf ».
- Documents classés en Grilles · tronc commun / 2e degré / 3e degré.
- Plus de mention « ancien système » pour la 4e ; bloc « La réforme, année après année » : tronc commun, ancien 1er/2e degré, grilles 4e-6e inchangées.
- École fondamentale : vraies pages (accueil, maternelle, primaire) au ton plus joyeux, infos reprises de l’ancien site (présentation, accès par le parc Fabiola, horaires, projets, contacts). Plus aucun lien vers l’ancien site du fondamental.

## V5.8 — Formulaire réel, immersion surlignée, espace administrateur
- Formulaire de contact réel vers info@sfx1.org : Netlify Forms (anti-robots) ou contact.php pour OVH (réglage « mode » dans data/contenus/formulaire.json). En test local, la messagerie s’ouvre avec le message prêt. Page de remerciement merci.html. Politique de confidentialité mise à jour.
- « Cours en immersion » (au lieu de « cours en néerlandais ») ; cours en immersion surlignés en jaune dans toutes les grilles, cours de néerlandais (LM I) compris, y compris dans le PDF du tronc commun.
- Espace d’administration /admin (Sveltia CMS, compatible Decap) : actualités, portes ouvertes (lien de réservation), documents PDF (dépôt direct, ouverture dans le navigateur), vidéos (MP4 hébergées sur le site, YouTube ou Drive), photos, grilles du tronc commun, immersion, fondamental, équipe, histoire, formulaire.
- Crayons jaunes sur les blocs modifiables, visibles seulement après passage par /admin ; la sécurité repose sur la connexion GitHub (comptes autorisés uniquement).
- Contenus découpés en un fichier par rubrique (data/contenus/*.json). Les photos déposées sont redimensionnées automatiquement (WebP + JPEG).
- Sources prêtes pour GitHub + Netlify (netlify.toml, requirements.txt) ; scripts « reconstruire-le-site » pour le test local.

## V5.9 — Remarques de la direction (25/11/2026)
- Vidéos masquées partout (accueil, pages, menu, pied de page) en attendant le choix des vidéos ; réactivables dans l’administration (Options du site).
- Portes ouvertes : bouton « Je réserve mon créneau de visite » dans le bandeau et sur la page ; affiché « ouverture prochaine » tant que la réservation n’est pas ouverte (administration : case « Réservation ouverte » + lien de l’application).
- Le Collège : phrase « développement de toute la personne » supprimée ; le bloc « Le centre-ville, un véritable atout » rejoint la présentation « Une école ancrée dans la ville » (retiré de la page Secondaire).
- Temps de midi : « Interdiction pour les élèves de S1, S2 et S3 (1re, 2e et 3e années) de quitter l’école », sans mention d’autorisation parentale.
- Descriptions des options (1er, 2e et 3e degrés) réécrites en paragraphes développés, d’après les documents officiels.
- Agenda : page prête à intégrer l’agenda en ligne de l’école (adresse à saisir dans l’administration ; intégration dans la page ou bouton).
- Documents : charte numérique retirée ; illustrations remplacées par des icônes sobres et identiques (document, dossier).
- Équipe : ajout de M. Bernard Goedseels, gestionnaire économe (bâtiments et réservations), ligne directe 087 39 39 10 ; il remplace Mme Simon dans les contacts du fondamental.
- Fondamental : les photos d’élèves du secondaire sont remplacées par des illustrations dessinées (enfants de 3 à 10 ans).

## V5.10 — Mentions « à valider » levées
- Bandeau bordeaux foncé du haut (liens fondamental / portes ouvertes) supprimé : ces accès sont déjà juste en dessous.
- Retrait de l’annotation « D’après la campagne Idées reçues… », des mentions « à valider » sur les contacts du fondamental et sur les heures d’immersion (4 h de néerlandais en 4e, 5e et 6e).
- Instagram : prêt à s’afficher à côté de Facebook (bandeau « Suivez la vie du Collège » et pied de page) dès que l’adresse est saisie (administration → Réseaux sociaux · Instagram).
- En-tête : sur les écrans de portable, le bouton « Portes ouvertes » en double est masqué (l’onglet reste dans le menu) pour que tout tienne sur une ligne.

## V6.0 — Version publiée
- Fin de la version de test : plus de bandeau « version de test », plus aucune mention « à valider », indexation par les moteurs de recherche autorisée (sauf /admin). Mentions légales et confidentialité complétées (liens vers les CGU et la déclaration de confidentialité intégrale).
- Instagram (instagram.com/collegesfx1) à côté de Facebook.
- Bloc « Notre réseau » au-dessus du pied de page : Jésuites d’Europe occidentale francophone, COCEJE, JECSE, Educate Magis (logos ajoutables via l’administration).
- Le Collège · « Notre pédagogie » : les 4C avec un exemple concret à SFX1, le cycle d’apprentissage ignatien, les six thèmes d’année en cartes à retourner (thème en cours mis en avant via l’administration), encadré « Non multa, sed multum ».
- Nouvelles photos (séance photo 2023) : diaporama d’accueil (la photo de la cour est conservée en premier), galerie du Collège, cartes, parcours, pédagogie. Photo de l’entrée remise à l’endroit (elle était en miroir).
- Bouton d’en-tête « Mon espace » : ouvre directement le Google Site réservé aux enseignants (sites.google.com/view/sfx1-verviers), connexion par compte @sfx1.org. Page « Espace numérique » : portail des enseignants + Classroom, Gmail, Drive. Adresse du portail modifiable via l’administration (Options du site).
- Bouton « Portes ouvertes » retiré de l’en-tête (l’onglet reste dans le menu).
- Barre d’accès rapides mobile : absente de la page Contact, se retire en descendant et en bas de page, revient en remontant, disparaît pendant la saisie d’un formulaire.
- Adresse officielle du site : https://sfx1.org (www.sfx1.org redirige). Balises canoniques, sitemap et robots.txt mis à jour.
- Référencement : titres « Collège SFX1 Verviers », données structurées « School » (nom, adresse, téléphone, Facebook, Instagram) pour Google.
