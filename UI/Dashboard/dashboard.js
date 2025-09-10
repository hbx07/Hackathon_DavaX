// dashboard.js
// Loads bills from backend, renders list, handles UI toggles & navigation to Payments

// ---- CONFIG ----
const API_BASE = ""; // ugyanarról az originről szolgáljuk ki az API-t is
const PAYMENTS_PAGE = "/ui/Payments/payments.html"; // ide navigálunk fizetéskor

// ---- STATE ----
let serverBills = []; // a backendről jövő eredeti tömb
let currentFilter = null; // "DUE" | "PAID" | null

// ---- Helpers ----
function getStatusIconFromBillStatus(status) {
  // Backenden: DUE | PAID
  switch (status) {
    case "PAID":
      return '<img src="../Images/success.svg" alt="Plătită" class="bill-status" height="24" width="24">';
    case "DUE":
    default:
      return '<img src="../Images/warning.svg" alt="În așteptare" class="bill-status" height="24" width="24">';
  }
}

function formatAmount(n) {
  const x = Number(n);
  if (!Number.isFinite(x)) return "—";
  return Number.isInteger(x) ? `${x} RON` : `${x.toFixed(2)} RON`;
}

function renderBills(filterStatus = null) {
  const row = document.getElementById("billsRow");
  row.innerHTML = "";

  const list = serverBills.filter(b => !filterStatus || b.status === filterStatus);

  if (list.length === 0) {
    const empty = document.createElement("div");
    empty.style.padding = "12px 8px";
    empty.style.color = "#6b7280";
    empty.textContent = "Nu există facturi pentru filtrul selectat.";
    row.appendChild(empty);
    return;
  }

  list.forEach(bill => {
    const el = document.createElement("article");
    el.className = "bill";
    el.setAttribute("role", "listitem");
    el.setAttribute("aria-label", bill.company);

    const due = bill.due_date ? bill.due_date : "—";

    el.innerHTML = `
      <div style="display:flex;align-items:center;gap:10px;">
        ${getStatusIconFromBillStatus(bill.status)}
        <h2>${bill.company}</h2>
      </div>
      <div class="meta">
        <div>Sumă: <b>${formatAmount(bill.amount)}</b></div>
        <div>Scadență: <b>${due}</b></div>
      </div>
      <div class="actions">
        <button class="btn primary pay-btn" data-bill-id="${bill.id}" aria-label="Plătește factura ${bill.company}">Plătește</button>
        <button class="btn delete-btn" data-bill-id="${bill.id}" aria-label="Șterge ${bill.company}">Șterge</button>
      </div>
    `;
    row.appendChild(el);
  });

  // Kattintás kezelők (render után!)
  row.querySelectorAll(".pay-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const billId = btn.dataset.billId;
      sessionStorage.setItem("current_bill_id", billId);
      window.location.href = PAYMENTS_PAGE;
    });
  });

  // (opcionális) törlés – itt csak UI-ban tüntetjük el
  row.querySelectorAll(".delete-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = btn.dataset.billId;
      serverBills = serverBills.filter(b => b.id !== id);
      renderBills(currentFilter);
    });
  });
}

// ---- Load from backend ----
async function loadBills() {
  const token = localStorage.getItem("payments_token");
  if (!token) {
    // nincs bejelentkezve
    window.location.href = "/ui/Login/login.html";
    return;
  }
  try {
    const res = await fetch(`${API_BASE}/bills`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      console.error("Failed to load bills", await res.text());
      serverBills = [];
    } else {
      serverBills = await res.json();
    }
  } catch (e) {
    console.error("Network error while loading bills", e);
    serverBills = [];
  }
}

// ---- UI bootstrapping ----
document.addEventListener("DOMContentLoaded", async function () {
  await loadBills();
  renderBills();

  // Status filter logic
  document.querySelectorAll(".status-filter").forEach(btn => {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".status-filter").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const status = btn.getAttribute("data-status"); // "DUE" | "PAID" | ""
      currentFilter = status ? status : null;
      renderBills(currentFilter);
    });
  });

  // Font size controls
  const html = document.documentElement;
  const dec = document.getElementById("dec");
  const inc = document.getElementById("inc");
  let scale = 1.125; // rem base
  function apply() { html.style.fontSize = (16 * scale) + "px"; }
  if (dec) dec.addEventListener("click", () => { scale = Math.max(1.0, +(scale - 0.1).toFixed(2)); apply(); });
  if (inc) inc.addEventListener("click", () => { scale = Math.min(1.8, +(scale + 0.1).toFixed(2)); apply(); });

  // Dyslexic font toggle
  const dysBtn = document.getElementById("dyslexic");
  if (dysBtn) {
    dysBtn.addEventListener("click", () => {
      document.body.classList.toggle("dyslexic");
      const enabled = document.body.classList.contains("dyslexic");
      dysBtn.setAttribute("aria-pressed", enabled ? "true" : "false");
    });
  }

  // High contrast toggle
  const contrastBtn = document.getElementById("contrast");
  if (contrastBtn) {
    contrastBtn.addEventListener("click", () => {
      const on = document.documentElement.classList.toggle("hc");
      contrastBtn.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }
});
