// login.js

const API_BASE = "";   // ha más a port/host, itt módosítsd
const DASHBOARD_PAGE = "/UI/Dashboard/dashboard.html";    // ha máshol van, állítsd át

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  const btn = document.getElementById("loginBtn");
  const errorBox = document.getElementById("loginError");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorBox.textContent = "";
    btn.disabled = true;
    btn.classList.add("is-loading");

    const cnp = document.getElementById("cnp").value.trim();
    const lastName = document.getElementById("nume").value.trim();
    const firstName = document.getElementById("prenume").value.trim();

    // minimális kliens oldali ellenőrzés
    if (!cnp || !lastName || !firstName) {
      showError("Te rugăm să completezi toate câmpurile!");
      resetBtn();
      return;
    }
    if (!/^\d{13}$/.test(cnp)) {
      showError("CNP trebuie să aibă exact 13 cifre.");
      resetBtn();
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify({
          cnp: cnp,
          last_name: lastName,   // a backend last_name / first_name kulcsokat vár
          first_name: firstName
        })
      });

      if (res.ok) {
        const data = await res.json();
        // token + user mentése – a dashboard ezt használja majd
        localStorage.setItem("payments_token", data.token);
        localStorage.setItem("payments_user", JSON.stringify(data.user));
        window.location.href = "/ui/Dashboard/dashboard.html";
      } else {
        // 401 vagy 422 stb. – maradunk a loginon, üzenet
        const err = await safeJson(res);
        const msg = err?.detail || "Utilizatorul nu există sau datele nu corespund.";
        showError(msg);
      }
    } catch (err) {
      showError("Eroare de rețea. Verifică dacă backend-ul rulează.");
    } finally {
      resetBtn();
    }
  });

  function showError(message) {
    errorBox.textContent = message;
    errorBox.style.display = "block";
  }
  function resetBtn() {
    btn.disabled = false;
    btn.classList.remove("is-loading");
  }
  async function safeJson(res) {
    try { return await res.json(); } catch { return null; }
  }
});
