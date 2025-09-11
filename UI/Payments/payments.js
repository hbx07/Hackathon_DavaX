// payments.js

document.addEventListener('DOMContentLoaded', function () {
  const API_BASE = ""; // ugyanazon az originon fut a backend
  const DASHBOARD_PAGE = "/ui/Dashboard/dashboard.html";

  // --- Chat tab and window logic (meghagyva) ---
  const chatTab = document.getElementById('chat-tab');
  const chatWindow = document.getElementById('chat-window');
  const chatClose = document.getElementById('chat-close');
  const chatForm = document.getElementById('chatForm');
  const chatInput = document.getElementById('chatInput');
  const chatMessages = document.getElementById('chatMessages');

  if (chatTab && chatWindow) {
    chatTab.addEventListener('click', function () {
      chatWindow.classList.toggle('open');
      document.body.classList.toggle('chat-open', chatWindow.classList.contains('open'));
      if (chatWindow.classList.contains('open')) {
        if (!chatMessages.hasChildNodes()) {
          const welcome = document.createElement('div');
          welcome.textContent = '👋 Salut! Sunt asistentul AI. Întreabă-mă orice despre completarea formularului de plată.';
          welcome.style.color = '#2b66c3';
          welcome.style.marginBottom = '12px';
          chatMessages.appendChild(welcome);
        }
      }
    });
  }
  if (chatClose && chatWindow) {
    chatClose.addEventListener('click', function () {
      chatWindow.classList.remove('open');
      document.body.classList.remove('chat-open');
    });
  }

  // --- Token + bill id ---
  const token = localStorage.getItem("payments_token");
  if (!token) {
    window.location.href = "/ui/Login/login.html";
    return;
  }
  const billId = sessionStorage.getItem("current_bill_id") ||
                 new URLSearchParams(location.search).get("bill_id");

  const err = document.getElementById('err') || (() => {
    const e = document.createElement('div');
    e.id = 'err';
    e.className = 'err';
    document.body.appendChild(e);
    return e;
  })();

  if (!billId) {
    err.textContent = "Nu a fost selectată nicio factură.";
    return;
  }

  // --- Form refs ---
  const form = document.getElementById('paymentForm');
  const receiverInput = document.getElementById('receiver');
  const amountInput = document.getElementById('amount');
  const cardInput = document.getElementById('card');
  const expInput = document.getElementById('exp');
  const cvvInput = document.getElementById('cvv');

  // --- Számla részletek betöltése ---
  (async () => {
    try {
      const res = await fetch(`${API_BASE}/bills/${billId}`, {
        headers: { "Authorization": `Bearer ${token}` }
      });
      if (!res.ok) {
        err.textContent = "Nu am găsit factura.";
        return;
      }
      const bill = await res.json();

      // CSAK EZ A KÉT MEZŐ TÖLTŐDJÖN:
      receiverInput.value = bill.company || "";

      const n = Number(bill.amount);
      amountInput.value = Number.isFinite(n)
        ? (Number.isInteger(n) ? String(n) : n.toFixed(2))
        : "";

      // a többi mező (card/exp/cvv) üresen marad
    } catch {
      err.textContent = "Eroare de rețea.";
    }
  })();

  // --- Kártyaszám formázás ---
  if (cardInput) {
    cardInput.addEventListener('input', function () {
      let value = cardInput.value.replace(/\D/g, '');
      value = value.substring(0, 16);
      let formatted = value.replace(/(.{4})/g, '$1 ').trim();
      cardInput.value = formatted;
    });
  }
  function formatCardNumber(num) {
    return num.replace(/\D/g, '').replace(/(.{4})/g, '$1 ').trim();
  }

  // --- Chat logic (meghagyva; külön AI szolgáltatás) ---
  if (chatForm && chatInput && chatMessages) {
    chatForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const msg = chatInput.value.trim();
      if (!msg) return;
      const formData = {
        receiver: receiverInput.value,
        amount: amountInput.value,
        card: cardInput.value,
        exp: expInput.value,
        cvv: cvvInput.value
      };
      const userMsg = document.createElement('div');
      userMsg.textContent = 'Tu: ' + msg;
      userMsg.style.marginBottom = '8px';
      chatMessages.appendChild(userMsg);
      chatInput.value = '';
      chatMessages.scrollTop = chatMessages.scrollHeight;

      fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, form: formData })
      })
        .then(res => res.json())
        .then(data => {
            const aiMsg = document.createElement('div');
            aiMsg.textContent = 'AI: ' + (data.reply || 'Eroare răspuns AI');
            aiMsg.style.color = '#2b66c3';
            chatMessages.appendChild(aiMsg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            // Play TTS for AI reply
            if (data.reply) {
                fetch('http://localhost:5000/tts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: data.reply })
                })
                .then(resp => resp.ok ? resp.blob() : null)
                .then(blob => {
                    if (blob) {
                        const url = URL.createObjectURL(blob);
                        const audio = new Audio(url);
                        audio.play();
                    }
                });
            }
            // Autofill form fields if slots are present
            if (data.slots) {
                if (data.slots.receiver) form.receiver.value = data.slots.receiver;
                if (data.slots.amount) form.amount.value = data.slots.amount;
                if (data.slots.card) form.card.value = formatCardNumber(data.slots.card);
                if (data.slots.exp) form.exp.value = data.slots.exp;
                if (data.slots.cvv) form.cvv.value = data.slots.cvv;
            }
          const aiMsg = document.createElement('div');
          aiMsg.textContent = 'AI: ' + (data.reply || 'Eroare răspuns AI');
          aiMsg.style.color = '#2b66c3';
          chatMessages.appendChild(aiMsg);
          chatMessages.scrollTop = chatMessages.scrollHeight;
          // Play TTS for AI reply
          if (data.reply) {
              fetch('http://localhost:5000/tts', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ text: data.reply })
              })
              .then(resp => resp.ok ? resp.blob() : null)
              .then(blob => {
                  if (blob) {
                      const url = URL.createObjectURL(blob);
                      const audio = new Audio(url);
                      audio.play();
                  }
              });
            }
          if (data.slots) {
            if (data.slots.receiver) receiverInput.value = data.slots.receiver;
            if (data.slots.amount) amountInput.value = data.slots.amount;
            if (data.slots.card) cardInput.value = formatCardNumber(data.slots.card);
            if (data.slots.exp) expInput.value = data.slots.exp;
            if (data.slots.cvv) cvvInput.value = data.slots.cvv;
          }
        })
        .catch(() => {
          const aiMsg = document.createElement('div');
          aiMsg.textContent = 'AI: Eroare de conectare la server.';
          aiMsg.style.color = 'red';
          chatMessages.appendChild(aiMsg);
          chatMessages.scrollTop = chatMessages.scrollHeight;
        });
    });

    // Microphone (meghagyva)
const micBtn = document.createElement('button');
    micBtn.type = 'button';
    micBtn.id = 'micBtn';
    micBtn.innerHTML = '🎤';
    micBtn.title = 'Vorbește';
    micBtn.style.fontSize = '1.3rem';
    micBtn.style.background = 'none';
    micBtn.style.border = 'none';
    micBtn.style.cursor = 'pointer';
    micBtn.style.marginRight = '4px';
    chatForm.insertBefore(micBtn, chatInput);

    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let stream;
    micBtn.addEventListener('click', async function () {
      if (!navigator.mediaDevices || !window.MediaRecorder) {
        alert('Microfonul nu este suportat în acest browser.');
        return;
      }
      micBtn.disabled = true;
      micBtn.innerHTML = '🎤...';
      audioChunks = [];
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.start();
      mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('audio', audioBlob, 'speech.webm');
        try {
          const res = await fetch('http://localhost:5000/speech', { method: 'POST', body: formData });
          const data = await res.json();
          chatInput.value = data.transcript || '';
        } finally {
          micBtn.disabled = false;
          micBtn.innerHTML = '🎤';
          if (chatInput.value.trim()) chatForm.dispatchEvent(new Event('submit'));
        }
      };
      setTimeout(() => {
        mediaRecorder.stop();
        stream.getTracks().forEach(track => track.stop());
      }, 5000);
        if (!navigator.mediaDevices || !window.MediaRecorder) {
            alert('Microfonul nu este suportat în acest browser.');
            return;
        }
        if (!isRecording) {
            micBtn.disabled = true;
            micBtn.innerHTML = '<span class="mic-anim"></span> Înregistrare...';
            micBtn.classList.add('recording');
            audioChunks = [];
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();
            isRecording = true;
            micBtn.disabled = false;
            mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
            mediaRecorder.onstop = async () => {
                micBtn.classList.remove('recording');
                micBtn.innerHTML = '🎤';
                micBtn.disabled = false;
                isRecording = false;
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const formData = new FormData();
                formData.append('audio', audioBlob, 'speech.webm');
                const res = await fetch('http://localhost:5000/speech', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                chatInput.value = data.transcript || '';
                // Automatically send the transcribed text as a chat message
                if (chatInput.value.trim()) {
                    chatForm.dispatchEvent(new Event('submit'));
                }
            };
        } else {
            mediaRecorder.stop();
            stream.getTracks().forEach(track => track.stop());
        }
    });

    // Add camera tab below chat tab
    const cameraTab = document.createElement('div');
    cameraTab.id = 'camera-tab';
    cameraTab.className = 'camera-tab';
    cameraTab.innerHTML = '📷';
    cameraTab.title = 'Deschide camera';
    chatTab.insertAdjacentElement('afterend', cameraTab);

    // Add camera window
    const cameraWindow = document.createElement('div');
    cameraWindow.id = 'camera-window';
    cameraWindow.className = 'camera-window';
    cameraWindow.innerHTML = '<div class="camera-header">Camera <button id="camera-close" class="camera-close" aria-label="Închide camera">&times;</button></div><div class="camera-content"><video id="cameraVideo" autoplay playsinline></video><button id="takePhotoBtn" class="take-photo-btn">📸 Fă poză cardului</button><canvas id="photoCanvas" style="display:none;"></canvas></div>';
    document.body.appendChild(cameraWindow);

    // Add modal for photo confirmation
    const photoModal = document.createElement('div');
    photoModal.id = 'photoModal';
    photoModal.className = 'photo-modal';
    photoModal.style.display = 'none';
    photoModal.innerHTML = `
      <div class="photo-modal-content">
        <img id="photoPreview" src="" alt="Preview" />
        <div class="photo-modal-question">Este totul vizibil?</div>
        <div class="photo-modal-actions">
          <button id="photoOkBtn" class="btn">OK</button>
          <button id="photoCancelBtn" class="btn">Anulează</button>
        </div>
      </div>
    `;
    document.body.appendChild(photoModal);

    // Camera tab click logic
    cameraTab.addEventListener('click', function () {
        cameraWindow.classList.add('open');
        document.body.classList.add('camera-open');
        // Start camera
        const video = document.getElementById('cameraVideo');
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => {
                video.srcObject = stream;
                video.dataset.active = 'true';
            })
            .catch(() => {
                video.dataset.active = 'false';
                video.poster = '';
            });
    });
    // Camera close logic
    document.getElementById('camera-close').addEventListener('click', function () {
        cameraWindow.classList.remove('open');
        document.body.classList.remove('camera-open');
        // Stop camera
        const video = document.getElementById('cameraVideo');
        if (video.srcObject) {
            video.srcObject.getTracks().forEach(track => track.stop());
            video.srcObject = null;
        }
    });
    // Take photo button logic
    const takePhotoBtn = document.getElementById('takePhotoBtn');
    takePhotoBtn.addEventListener('click', function () {
        const video = document.getElementById('cameraVideo');
        const canvas = document.getElementById('photoCanvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        // Show modal with photo
        const photoUrl = canvas.toDataURL('image/png');
        document.getElementById('photoPreview').src = photoUrl;
        photoModal.style.display = 'flex';
        // Optionally, pause video
        video.pause();
    });
    // Modal button logic
    document.getElementById('photoOkBtn').addEventListener('click', function () {
        photoModal.style.display = 'none';
        document.getElementById('cameraVideo').play();
        document.getElementById('photoCanvas').style.display = 'none';
    });
    document.getElementById('photoCancelBtn').addEventListener('click', function () {
        photoModal.style.display = 'none';
        document.getElementById('cameraVideo').play();
        document.getElementById('photoCanvas').style.display = 'none';
    });
  }
  // --- Fizetés (POST /bills/{id}/pay) ---
  const payForm = document.getElementById('paymentForm');
  if (payForm) {
    payForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      err.textContent = "";
      try {
        const res = await fetch(`${API_BASE}/bills/${billId}/pay`, {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Accept": "application/json"
          }
        });
        if (res.ok) {
          // vissza a dashboardra
          window.location.href = DASHBOARD_PAGE;
        } else {
          const body = await res.json().catch(() => ({}));
          err.textContent = body.detail || "Plata a eșuat.";
        }
      } catch {
        err.textContent = "Eroare de rețea.";
      }
    });
  }
});
