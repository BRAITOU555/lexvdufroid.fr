"use strict";
const eligibilityForm = document.querySelector("#eligibility-form");
const result = document.querySelector("#eligibility-result");
eligibilityForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (!eligibilityForm.reportValidity()) return;
  const data = new FormData(eligibilityForm);
  const postcode = String(data.get("postcode"));
  const inRegion = ["75", "77", "78", "91", "92", "93", "94", "95"].includes(postcode.slice(0, 2));
  const notes = [inRegion ? "Votre projet est situé dans notre zone d’intervention en Île-de-France. Une étude technique peut être demandée." : "Votre code postal est hors de notre zone habituelle en Île-de-France. Contactez-nous pour vérifier si votre projet peut être pris en charge."];
  if (data.get("occupancy") === "tenant") notes.push("En tant que locataire, l’autorisation du propriétaire devra être vérifiée avant les travaux.");
  if (data.get("building") === "Appartement") notes.push("Pour un appartement, les règles de copropriété et les autorisations éventuelles doivent aussi être examinées.");
  notes.push("Ce résultat ne confirme ni la faisabilité de l’installation ni l’acceptation d’un financement.");
  result.replaceChildren();
  const paragraph = document.createElement("p");
  paragraph.textContent = notes.join(" ");
  const link = document.createElement("a");
  link.href = "#etude"; link.textContent = "Continuer vers la demande d’étude";
  result.append(paragraph, link); result.hidden = false;
  document.querySelector("#study-postcode").value = postcode;
  document.querySelector("#study-occupancy").value = data.get("occupancy");
  document.querySelector("#study-building").value = data.get("building");
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
