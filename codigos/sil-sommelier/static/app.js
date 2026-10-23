const WHATSAPP_NUMBER = "5545991059550";

const form = document.querySelector("#interest-form");
const interestSelect = form?.elements.interest;
const selectionSummary = document.querySelector("#selection-summary");
const statusMessage = document.querySelector("#form-status");

let selectedDetail = "";
let selectedDate = "";

function updateSelection(detail, date = "") {
    selectedDetail = detail;
    selectedDate = date;

    if (!selectionSummary) {
        return;
    }

    const dateText = date ? `, dia ${date}` : "";
    selectionSummary.textContent = `Interesse selecionado: ${detail}${dateText}`;
    selectionSummary.hidden = false;
}

document.querySelectorAll("[data-interest]").forEach((cta) => {
    cta.addEventListener("click", () => {
        const interest = cta.dataset.interest;
        const detail = cta.dataset.detail || interest;
        const date = cta.dataset.date || "";

        if (interestSelect) {
            interestSelect.value = interest;
        }

        updateSelection(detail, date);
    });
});

interestSelect?.addEventListener("change", () => {
    updateSelection(interestSelect.value);
});

form?.addEventListener("submit", (event) => {
    event.preventDefault();

    if (!form.reportValidity()) {
        return;
    }

    const data = new FormData(form);
    const name = data.get("name").trim();
    const interest = data.get("interest");
    const detail = selectedDetail || interest;
    const dateText = selectedDate ? `, dia ${selectedDate}` : "";
    const message = `Oi Sil! Vim pelo site. Meu nome é ${name} e quero saber mais sobre ${detail}${dateText}.`;

    const whatsappUrl = WHATSAPP_NUMBER
        ? `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(message)}`
        : `https://wa.me/?text=${encodeURIComponent(message)}`;

    if (!WHATSAPP_NUMBER) {
        statusMessage.textContent = "O número oficial ainda precisa ser configurado. Ao abrir o WhatsApp, escolha o contato da Sil.";
    }

    window.open(whatsappUrl, "_blank", "noopener,noreferrer");
});
