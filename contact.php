<?php
declare(strict_types=1);

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: contact.html', true, 303);
    exit;
}

function field(string $name): string
{
    $value = $_POST[$name] ?? '';
    if (is_array($value)) {
        $value = implode(', ', $value);
    }

    return trim(strip_tags((string) $value));
}

function clean_email(string $email): string
{
    $email = trim($email);
    return filter_var($email, FILTER_VALIDATE_EMAIL) ? $email : '';
}

function has_header_injection(string $value): bool
{
    return preg_match('/[\r\n]/', $value) === 1;
}

$honeypot = field('site_web');
if ($honeypot !== '') {
    header('Location: merci.html', true, 303);
    exit;
}

$name = field('Nom et prénom');
$phone = field('Téléphone');
$email = clean_email(field('email'));
$city = field('Ville');
$requestType = field('Type de demande');
$propertyType = field('Type de bien');
$timing = field('Délai souhaité');
$units = field('Nombre d’unités');
$message = field('Message');

$required = [$name, $phone, $email, $city, $requestType, $propertyType, $timing, $message];
foreach ($required as $value) {
    if ($value === '' || has_header_injection($value)) {
        header('Location: contact.html?erreur=1', true, 303);
        exit;
    }
}

if (has_header_injection($email)) {
    header('Location: contact.html?erreur=1', true, 303);
    exit;
}

$to = 'contact@lexvdufroid.fr';
$from = 'contact@lexvdufroid.fr';
$subject = 'Nouvelle demande';

$leadBody = implode("\n", [
    'Nouvelle demande depuis le site Le XV du Froid',
    '',
    'Nom et prénom : ' . $name,
    'Téléphone : ' . $phone,
    'Email : ' . $email,
    'Ville : ' . $city,
    'Type de demande : ' . $requestType,
    'Type de bien : ' . $propertyType,
    'Délai souhaité : ' . $timing,
    'Nombre d’unités : ' . ($units !== '' ? $units : 'Non renseigné'),
    '',
    'Message :',
    $message,
    '',
    'Répondre au client : ' . $email,
]);

$headers = [
    'From: Le XV du Froid <' . $from . '>',
    'Reply-To: ' . $email,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'X-Mailer: PHP/' . phpversion(),
];

$clientSubject = 'Votre demande a bien été reçue';
$clientBody = implode("\n", [
    'Bonjour ' . $name . ',',
    '',
    'Nous avons bien reçu votre demande pour Le XV du Froid.',
    'Nous allons reprendre les informations envoyées et vous recontacter par téléphone ou par email.',
    '',
    'Récapitulatif de votre demande :',
    'Ville : ' . $city,
    'Type de demande : ' . $requestType,
    'Type de bien : ' . $propertyType,
    'Délai souhaité : ' . $timing,
    '',
    'Votre message :',
    $message,
    '',
    'À bientôt,',
    'Le XV du Froid',
    '07 57 83 26 26',
]);

$clientHeaders = [
    'From: Le XV du Froid <' . $from . '>',
    'Reply-To: Le XV du Froid <' . $from . '>',
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'X-Mailer: PHP/' . phpversion(),
];

$senderParam = '-f ' . $from;
$sentToOwner = mail($to, $subject, $leadBody, implode("\r\n", $headers), $senderParam);
$sentToClient = mail($email, $clientSubject, $clientBody, implode("\r\n", $clientHeaders), $senderParam);

if (!$sentToOwner || !$sentToClient) {
    header('Location: contact.html?erreur=mail', true, 303);
    exit;
}

header('Location: merci.html', true, 303);
exit;
