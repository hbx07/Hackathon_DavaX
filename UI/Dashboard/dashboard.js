// dashboard.js
// Loads bills, handles font size and contrast

// Bill data (static for now, can be loaded from server or CSV)
const bills = [
  { provider: 'Electrica', amount: '150 RON', due: '10 mai', status: 'warning' },
  { provider: 'Digi', amount: '65 RON', due: '20 mai', status: 'close' },
  { provider: 'E.ON', amount: '—', due: '—', status: 'success' }
];

function getStatusIcon(status) {
  switch (status) {
    case 'success':
      return '<img src="../Images/success.svg" alt="Success" class="bill-status" height="24" width="24">';
    case 'warning':
      return '<img src="../Images/warning.svg" alt="Warning" class="bill-status" height="24" width="24">';
    case 'close':
      return '<img src="../Images/close.svg" alt="Close" class="bill-status" height="24" width="24">';
    default:
      return '';
  }
}

function renderBills(filterStatus = null) {
  const row = document.getElementById('billsRow');
  row.innerHTML = '';
  bills.filter(bill => !filterStatus || bill.status === filterStatus)
    .forEach(bill => {
      const el = document.createElement('article');
      el.className = 'bill';
      el.setAttribute('role', 'listitem');
      el.setAttribute('aria-label', bill.provider);
      el.innerHTML = `
        <div style="display:flex;align-items:center;gap:10px;">
          ${getStatusIcon(bill.status)}
          <h2>${bill.provider}</h2>
        </div>
        <div class="meta">
          <div>Sumă: <b>${bill.amount}</b></div>
          <div>Scadență: <b>${bill.due}</b></div>
        </div>
        <div class="actions">
          <button class="btn primary" aria-label="Plătește factura ${bill.provider}">Plătește</button>
          <button class="btn" aria-label="Șterge ${bill.provider}">Șterge</button>
        </div>
      `;
      row.appendChild(el);
    });
}

document.addEventListener('DOMContentLoaded', function () {
  renderBills();

  // Status filter logic
  document.querySelectorAll('.status-filter').forEach(btn => {
    btn.addEventListener('click', function() {
      // Remove active from all
      document.querySelectorAll('.status-filter').forEach(b => b.classList.remove('active'));
      // Add active to clicked
      btn.classList.add('active');
      // Filter bills
      renderBills(btn.getAttribute('data-status'));
    });
  });

  // Font size controls
  const html = document.documentElement;
  const dec = document.getElementById('dec');
  const inc = document.getElementById('inc');
  let scale = 1.125; // rem base
  function apply(){ html.style.fontSize = (16*scale)+'px'; }
  dec.addEventListener('click', ()=>{ scale = Math.max(1.0, +(scale - 0.1).toFixed(2)); apply(); });
  inc.addEventListener('click', ()=>{ scale = Math.min(1.8, +(scale + 0.1).toFixed(2)); apply(); });

  // Dyslexic font toggle
  const dysBtn = document.getElementById('dyslexic');
  if (dysBtn) {
    dysBtn.addEventListener('click', () => {
      document.body.classList.toggle('dyslexic');
      const enabled = document.body.classList.contains('dyslexic');
      dysBtn.setAttribute('aria-pressed', enabled ? 'true' : 'false');
    });
  }

  // High contrast toggle
  const contrastBtn = document.getElementById('contrast');
  contrastBtn.addEventListener('click', ()=>{
    const on = document.documentElement.classList.toggle('hc');
    contrastBtn.setAttribute('aria-pressed', on ? 'true' : 'false');
  });
});
