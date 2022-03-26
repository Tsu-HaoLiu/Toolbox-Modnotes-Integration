// This js interacts with the main document

function totalNotes(t) {
    document.getElementById('total-notes').innerHTML = t.toString();
}

function actionedNotes(t) {
    document.getElementById('actioned-notes').innerHTML = t.toString();
}

function coinsleft(c) {
    document.getElementById('remaining-ratelimit').innerHTML = c.toString();
}


// Function to validate the forms before sending to python backend
const fv = function formValidation() {
    console.log("Clicked Confirm");
    const formID = document.forms["form-detail"].getElementsByTagName('input');

    const filledForm = [];
    Array.from(formID).every(input => {
        
        if (input.value &&                   // If exist AND
            input.value.trim().length > 0 && // If value have one charecter at least AND 
            input.id != "save-info") {       // Not a checkbox
            
            filledForm.push(input.value);    // Add string to filledForm array

        } else if (input.id == "mfa" && !input.value) { // If 2fa input and if empty push null
            filledForm.push(null);

        } else if (input.id == "save-info") { // If input checkbox push boolean
            filledForm.push(formID["save-info"].checked);

        } else {  // Stop loop (Return false) and invalid console log.
            printjs("Missing info: " + input.id );
            return false;
        }
        // .every requires a truthy value for every array element to continue
        return true;
    });

    // Once validated send data to python backend
    sendValidatedData(filledForm, formID);
}


// Auto fills form from ini
function fillForm(l) {

    // Check if array (or python list) is actually sent
    if (!Array.isArray(l) || !l.length) return;

    // Loop through all forms with input tag, and sort them accordingly
    for (let [i, k] of Array.from(document.forms["form-detail"].getElementsByTagName('input')).entries()) {
        
        if (k.id == "mfa") continue; // Ignore mfa input box as 2fa will have expired long before.
        
        if (k.id == "save-info") {   // Auto check "remember me", incase of user error and incidentally delete ini file
            k.checked = true; 
            continue;
        }

        // Add values from ini to input box
        k.value = l[i];
    }
}


// Switch buttons once authenticated
function btnSwitcher() {
    const subbtn = document.querySelector("#confirm-button");
    subbtn.removeEventListener("click", fv, true);
    subbtn.innerText = "Convert Notes";
    subbtn.addEventListener("click", () => pStartNoteProcess());

    const pcsv = document.getElementById('ex-csv');
    pcsv.addEventListener("click", () => pRetrieveCSV());
    pcsv.style.removeProperty('background-image');

    const pjson = document.getElementById('ex-json');
    pjson.addEventListener("click", () => pRetrieveJSON());
    pjson.style.removeProperty('background-image');
}


// Togglable password and client secret values with eye buttons
function eyeClickEvent(eyeOject) {
    const prevChild = eyeOject.previousElementSibling;

    // Toggle the type attribute
    const type = prevChild.getAttribute("type") === "password" ? "text" : "password";
    prevChild.setAttribute("type", type);
    prevChild.focus();

    // Toggle the icon
    if (type == "text") {
        eyeOject.classList += "-slash";
    } else {
        eyeOject.classList.replace("fa-eye-slash", "fa-eye");
    }
}

// main init function to add eventListeners to buttons
function scriptmain() {
    document.querySelector("#confirm-button").addEventListener("click", fv, true);
    document.querySelectorAll(".hidden-eye").forEach(item => item.addEventListener("click", () => eyeClickEvent(item)));
}

// DOM load
window.addEventListener('DOMContentLoaded', () => scriptmain(), false);
