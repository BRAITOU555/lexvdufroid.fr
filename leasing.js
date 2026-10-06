"use strict";
const eligibilityForm = document.querySelector("#eligibility-form");
const result = document.querySelector("#eligibility-result");
eligibilityForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (!eligibilityForm.reportValidity()) return;
  const data = new FormData(eligibilityForm);
  const postcode = String(data.get("postcode"));
  const inRegion = ["75", "77", "78", "91", "92", "93", "94", "95"].includes(postcode.slice(0, 2));
  const owner = data.get("occupancy") === "owner";
  const house = data.get("building") === "Maison";
  const fossil = ["Gaz", "Fioul", "Charbon"].includes(data.get("heating"));
  const notes = [];
  if (owner && house && fossil) notes.push("Votre situation correspond aux premiers critères de statut, de logement et de chauffage de l’offre intégrée. Les ressources du foyer, un éventuel dossier Anah déjà déposé et la faisabilité technique restent à vérifier.");
  else {
    notes.push("Votre projet nécessite une orientation spécifique avant d’envisager l’offre intégrée.");
    if (!owner) notes.push("Le dispositif est réservé aux propriétaires occupants.");
    if (!house) notes.push("Il concerne uniquement les maisons individuelles.");
    if (!fossil) notes.push("Il vise le remplacement d’une chauffage fossile (gaz, fioul ou charbon).");
    notes.push("D’autres solutions de pompe à chaleur peuvent exister : demandez une étude.");
  }
  notes.push(inRegion ? "Votre projet est situé dans notre zone d’intervention en Île-de-France." : "Votre code postal est hors de notre zone habituelle : contactez-nous pour vérifier.");
  notes.push("Résultat indicatif : il ne confirme ni la faisabilité technique ni l’acceptation d’un financement.");
  result.replaceChildren();
  const paragraph = document.createElement("p");
  paragraph.textContent = notes.join(" ");
  const link = document.createElement("a");
  link.href = "#etude"; link.textContent = "Continuer vers la demande d’étude";
  result.append(paragraph, link); result.hidden = false;
  document.querySelector("#study-postcode").value = postcode;
  document.querySelector("#study-occupancy").value = data.get("occupancy");
  document.querySelector("#study-building").value = data.get("building");
  document.querySelector("#study-heating").value = data.get("heating") === "Autre" ? "Autre / à préciser" : data.get("heating");
});
const studyForm = document.querySelector("#study-form");
studyForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const success = document.querySelector("#study-success");
  const error = document.querySelector("#study-error");
  const button = document.querySelector("#study-submit");
  success.hidden = true; error.hidden = true;
  if (!studyForm.reportValidity()) return;
  const data = new FormData(studyForm);
  if (data.get("_honey")) return;
  // Libellé lisible dans l’email plutôt que les valeurs internes du sélecteur.
  data.set("Statut", document.querySelector("#study-occupancy").selectedOptions[0].textContent);
  button.disabled = true; button.textContent = "Envoi en cours…";
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 20000);
  try {
    const response = await fetch(studyForm.action.replace("formsubmit.co/", "formsubmit.co/ajax/"), {method: "POST", body: data, headers: {Accept: "application/json"}, signal: controller.signal});
    const payload = await response.json();
    if (!response.ok || !(payload.success === true || payload.success === "true")) throw new Error("Envoi non confirmé");
    studyForm.reset(); success.hidden = false;
  } catch {error.hidden = false;}
  finally {clearTimeout(timeout); button.disabled = false; button.textContent = "Envoyer ma demande d’étude";}
});
