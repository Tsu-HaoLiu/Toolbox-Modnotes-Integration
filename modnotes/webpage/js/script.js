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


const fv = function formValidation() {
    console.log("Click Confirm");
    const formID = document.forms["form-detail"].getElementsByTagName('input');

    const filledForm = [];
    Array.from(formID).every(input => {
        
        if (input.value && // if exist AND
            input.value.length > 0 && // if value have one charecter at least
            input.value.trim().length > 0 &&
            input.id != "save-info") //remeber me button (optional)
        {
            filledForm.push(input.value);
        } else if (input.id == "mfa" && !input.value) {
            filledForm.push(null);
        } else if (input.id == "save-info") {
            filledForm.push(formID["save-info"].checked);
        } else {
            console.log("Missing info: " + input.id);
            printjs("Missing info: " + input.id );
            return false;
        }
        return true;
    });
    sendValidatedData(filledForm, formID);
}


// Auto fills form from ini
function fillForm(l) {
    for (let [i, k] of Array.from(document.forms["form-detail"].getElementsByTagName('input')).entries()) {
        k.value = l[i]
        if (k.id == "save-info") {
            k.checked = true;
        }
    }
}


// Switch buttons once authenticated
function btnSwitcher() {
    const subbtn = document.querySelector("#confirm-button");
    subbtn.removeEventListener("click", fv, true);
    subbtn.innerText = "Convert Notes";
    subbtn.addEventListener("click", () => pStartNoteProcess());
}


// Togglable password and client secret values with eye buttons
function eyeClickEvent(eyeOject) {
    const prevChild = eyeOject.previousElementSibling;

    // toggle the type attribute
    const type = prevChild.getAttribute("type") === "password" ? "text" : "password";
    prevChild.setAttribute("type", type);
    prevChild.focus();

    // toggle the icon
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
    document.getElementById('ex-csv').addEventListener("click", () => pRetrieveCSV());
    document.getElementById('ex-json').addEventListener("click", () => pRetrieveJSON());
}

// DOM load
window.addEventListener('DOMContentLoaded', () => scriptmain(), false);