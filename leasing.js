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
  const fossil = ["Gaz", "Fioul"].includes(data.get("heating"));
  const notes = [];
  if (owner && house && fossil) notes.push("Votre situation correspond aux conditions de statut, de logement et de chauffage du leasing social. Reste à vérifier vos revenus avec le barème de l’Anah (ménages modestes ou très modestes).");
  else {
    notes.push("Votre situation ne correspond pas à toutes les conditions du leasing social (propriétaire occupant d’une maison chauffée au gaz ou au fioul, revenus modestes).");
    if (!owner) notes.push("Le dispositif est réservé aux propriétaires occupants.");
    if (!house) notes.push("Il concerne uniquement les maisons individuelles.");
    if (!fossil) notes.push("Il vise le remplacement d’une chaudière gaz ou fioul.");
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
