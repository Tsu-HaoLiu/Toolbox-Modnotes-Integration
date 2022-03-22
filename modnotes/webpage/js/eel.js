// This js specificity communicates with the exposed python backend.

function eelTotalNotes(t) {totalNotes(t);}

function eelActionedNotes(t) {actionedNotes(t);}

function eelCoinsLeft(c) {coinsleft(c);}

function eelFillForm(l) {fillForm(l);}

function eelupdateBtn() {btnSwitcher();}

function pStartNoteProcess() {eel.startNotes();}

function pRetrieveCSV() {eel.downloadCSV();}

function pRetrieveJSON() {eel.downloadJSON();}


// print to textarea
function printjs(txt) {
    const text = txt.toString();
    var textarea = frames['output-display'];
    textarea.innerHTML += text
    if (!text.endsWith('\n')) {
        textarea.innerHTML += '\n'; // If there was no new line, add one
    }
    textarea.scrollBy(0, textarea.scrollHeight);
}


// send validated data to python for authentication
function sendValidatedData(filledForm, formID) {
    if (filledForm.length == formID.length) {
        eel.authentication(filledForm);
    }
}

// expose functions for python
function eelmain() {
    eel.expose(printjs);
    eel.expose(eelupdateBtn);
    eel.expose(eelCoinsLeft);
    eel.expose(eelTotalNotes);
    eel.expose(eelActionedNotes);
    eelFillForm(eel.browser__init());
}

// DOM load
window.addEventListener('DOMContentLoaded', () => eelmain(), false);
