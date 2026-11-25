<?php
/* SFX1 — envoi du formulaire de contact (hébergement OVH).
   Activé quand data/contenus/formulaire.json contient "mode": "ovh". */
$destinataire = 'info@sfx1.org';
$expediteur   = 'site@sfx1.org';   // adresse du domaine (à créer ou adapter sur OVH)

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Location: contact.html'); exit; }
if (!empty($_POST['site-web'])) { header('Location: merci.html'); exit; }   // robot (champ piège)

function champ($n, $max) { return trim(mb_substr(strip_tags($_POST[$n] ?? ''), 0, $max)); }
$nom = champ('nom', 120); $email = champ('email', 160); $sujet = champ('sujet', 80); $message = champ('message', 5000);
if ($nom === '' || $message === '' || !filter_var($email, FILTER_VALIDATE_EMAIL) || empty($_POST['consentement'])) {
  http_response_code(400); echo 'Formulaire incomplet. <a href="contact.html">Retour</a>'; exit;
}
$nom = str_replace(["\r", "\n"], ' ', $nom); $sujet = str_replace(["\r", "\n"], ' ', $sujet);
$corps = "Message envoyé depuis le site www.sfx1.org\n\nNom : $nom\nEmail : $email\nSujet : $sujet\n\n$message\n";
$entetes = "From: Site SFX1 <$expediteur>\r\nReply-To: $email\r\nContent-Type: text/plain; charset=UTF-8\r\n";
$ok = mail($destinataire, '=?UTF-8?B?' . base64_encode('[Site] ' . $sujet) . '?=', $corps, $entetes);
header('Location: ' . ($ok ? 'merci.html' : 'contact.html?erreur=1')); exit;
