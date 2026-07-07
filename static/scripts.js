document.addEventListener("DOMContentLoaded", () => {
  const spinner = document.getElementById("spinner");
  if (spinner) setTimeout(() => spinner.classList.remove("show"), 1);
});

function checkPolicyStatus() {
  const select = document.getElementById("claimPolicySelect");
  const alertBox = document.getElementById("overdueAlert");
  const submitBtn = document.getElementById("submitClaimBtn");
  if (!select) return;
  const selected = select.options[select.selectedIndex];
  const isBlocked = selected && selected.getAttribute("data-blocked") === "1";
  if (isBlocked) {
    alertBox.classList.remove("d-none");
    submitBtn.disabled = true;
    submitBtn.classList.replace("btn-primary", "btn-secondary");
  } else {
    alertBox.classList.add("d-none");
    submitBtn.disabled = false;
    submitBtn.classList.replace("btn-secondary", "btn-primary");
  }
}

function updatePremiumPreview() {
  const select = document.getElementById("policytypeSelect");
  if (!select) return;
  const selected = select.options[select.selectedIndex];
  const base = parseFloat(selected.getAttribute("data-premium") || 0);
  const premiumInput = document.getElementById("annualPremiumVal");
  if (premiumInput) premiumInput.value = base.toFixed(2);
}

function generatePremiumPreview() {
  const annualPremium = parseFloat(document.getElementById("annualPremiumVal").value);
  const termYears = parseInt(document.getElementById("policyTerm").value);
  const startDateVal = document.getElementById("policyStartDate").value;
  if (!startDateVal) { alert("Please select a start date"); return; }
  const totalMonths = termYears * 12;
  const monthlyAmount = annualPremium / 12;
  let startDate = new Date(startDateVal);
  let html = `
    <div class="alert alert-info small mb-3">
      <strong>Schedule Details:</strong> ${totalMonths} installments of
      <strong>₹${monthlyAmount.toFixed(2)}</strong> each, starting from ${startDateVal}.
    </div>
    <table class="table table-sm table-striped small">
      <thead><tr><th>Inst #</th><th>Due Date</th><th>Amount</th><th>Status</th></tr></thead>
      <tbody>`;
  for (let i = 1; i <= totalMonths; i++) {
    let dueDate = new Date(startDate);
    dueDate.setMonth(startDate.getMonth() + i);
    html += `<tr>
      <td>${i}</td>
      <td>${dueDate.toISOString().split("T")[0]}</td>
      <td>₹${monthlyAmount.toFixed(2)}</td>
      <td><span class="badge bg-warning text-dark">pending</span></td>
    </tr>`;
  }
  html += `</tbody></table>`;
  document.getElementById("previewContainer").innerHTML = html;
}

function toggleReasonField() {
  const action = document.getElementById("adjudicateAction");
  if (!action) return;
  const approvedAmount = document.getElementById("approvedAmountInput");
  const notes = document.getElementById("adjudicationNotes");
  if (action.value === "approved") {
    notes.placeholder = "Detail payout transaction or notes...";
    if (approvedAmount) { approvedAmount.disabled = false; approvedAmount.required = true; }
  } else if (action.value === "rejected") {
    notes.placeholder = "Provide justification reason for rejection...";
    if (approvedAmount) { approvedAmount.disabled = true; approvedAmount.required = false; approvedAmount.value = ""; }
  } else {
    notes.placeholder = "Justify moving to review or outline document requests...";
    if (approvedAmount) { approvedAmount.disabled = true; approvedAmount.required = false; approvedAmount.value = ""; }
  }
}

function validateAmount(maxAmount) {
  const approvedInput = document.getElementById("approvedAmountInput");
  const warning = document.getElementById("amountWarning");
  const submitBtn = document.getElementById("saveAdjudicationBtn");
  if (!approvedInput) return;
  const approved = parseFloat(approvedInput.value) || 0;
  if (approved > maxAmount) {
    warning.classList.remove("d-none");
    if (submitBtn) { submitBtn.disabled = true; submitBtn.classList.replace("btn-primary", "btn-secondary"); }
  } else {
    warning.classList.add("d-none");
    if (submitBtn) { submitBtn.disabled = false; submitBtn.classList.replace("btn-secondary", "btn-primary"); }
  }
}
