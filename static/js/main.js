// === STATE ===
let patrolInterval = null;
let patrolSeconds = 0;
let intruderCount = 0;
let cameraStream = null;
let isPatrolRunning = false;
let isCameraRunning = false;

// === DOM ELEMENTS ===
const video = document.getElementById('camera');
const infoBox = document.getElementById('infoBox');
const cameraBtn = document.getElementById('cameraToggleBtn');
const patrolBtn = document.getElementById('patrolToggleBtn');
const detectBtn = document.getElementById('detectFaceBtn');
const recognizeBtn = document.getElementById('recognizeBtn');
const intruderField = document.getElementById('intruderCount');
const patrolDurationField = document.getElementById('patrolDuration');
const addFaceBtn = document.getElementById('addFaceBtn');
const addNameInput = document.getElementById('addName');
const faceList = document.getElementById('faceList');

// === UI HELPERS ===
function showMessage(message, duration = 5000) {
    infoBox.textContent = message;
    infoBox.style.display = 'block';
    setTimeout(() => {
        infoBox.style.display = 'none';
    }, duration);
}

function toggleCameraButtons(visible) {
    detectBtn.classList.toggle('hidden', !visible);
    recognizeBtn.classList.toggle('hidden', !visible);
}

// === CAMERA HANDLING ===
async function startCamera() {
    if (isCameraRunning) return;

    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = cameraStream;
        video.play();

        isCameraRunning = true;
        cameraBtn.textContent = '⛔ Stopper la caméra';
        cameraBtn.style.backgroundColor = '#dc3545';
        toggleCameraButtons(true);

        showMessage('Caméra démarrée !');
    } catch (err) {
        showMessage('❌ Erreur caméra : ' + err.message);
    }
}

function stopCamera() {
    if (!isCameraRunning) return;

    cameraStream.getTracks().forEach((track) => track.stop());
    video.srcObject = null;
    cameraStream = null;
    isCameraRunning = false;

    cameraBtn.textContent = '🎥 Démarrer la caméra';
    cameraBtn.style.backgroundColor = '#0d6efd';
    toggleCameraButtons(false);

    showMessage('Caméra arrêtée.');
}

// === PATROL HANDLING ===
function startPatrolTimer() {
    patrolSeconds = 0;
    patrolDurationField.value = '0';
    clearInterval(patrolInterval);
    patrolInterval = setInterval(() => {
        patrolSeconds++;
        patrolDurationField.value = patrolSeconds;
    }, 1000);
}

function stopPatrolTimer() {
    clearInterval(patrolInterval);
    patrolSeconds = 0;
    patrolDurationField.value = '0';
}

// === FACE IMAGE ===
function captureImage() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    return canvas.toDataURL('image/jpeg');
}

async function sendToServer(endpoint, payload) {
    const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    return res.json();
}

// === FACE LIST ===
async function refreshFaceList() {
    const res = await fetch('/list-faces');
    const names = await res.json();
    faceList.innerHTML = '';

    if (!names.length) {
        const li = document.createElement('li');
        li.textContent = 'Aucun visage enregistré';
        li.style.fontStyle = 'italic';
        faceList.appendChild(li);
        return;
    }

    names.forEach((name) => {
        const li = document.createElement('li');

        const span = document.createElement('span');
        span.textContent = name;

        const delBtn = document.createElement('button');
        delBtn.textContent = 'Supprimer';
        delBtn.className = 'face-delete-btn';
        delBtn.addEventListener('click', () => handleDeleteFace(name));

        li.appendChild(span);
        li.appendChild(delBtn);
        faceList.appendChild(li);
    });
}

async function handleDeleteFace(name) {
    if (!confirm(`Supprimer le visage de ${name} ?`)) return;

    const res = await fetch('/delete-face', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
    });

    const result = await res.json();
    if (res.ok) {
        showMessage(`❌ Visage supprimé : ${result.name}`);
        refreshFaceList();
    } else {
        showMessage('Erreur suppression : ' + (result.error || 'inconnue'));
    }
}

// === EVENTS ===
cameraBtn.addEventListener('click', async () => {
    isCameraRunning ? stopCamera() : await startCamera();
});

patrolBtn.addEventListener('click', async () => {
    if (!isPatrolRunning) {
        await startCamera();

        const res = await fetch('/send-command', {
            method: 'POST',
            body: new URLSearchParams({ command: 'start-patrol' }),
        });

        showMessage(await res.text());
        patrolBtn.textContent = '🛑 Arrêter la patrouille';
        patrolBtn.style.backgroundColor = '#dc3545';
        isPatrolRunning = true;

        startPatrolTimer();
    } else {
        const res = await fetch('/send-command', {
            method: 'POST',
            body: new URLSearchParams({ command: 'stop-patrol' }),
        });

        showMessage(await res.text());
        patrolBtn.textContent = '🚓 Lancer la patrouille';
        patrolBtn.style.backgroundColor = '#198754';
        isPatrolRunning = false;

        stopPatrolTimer();
    }
});

detectBtn.addEventListener('click', async () => {
    const image = captureImage();
    const res = await sendToServer('/detect-face', { image });

    if (res.someone_present) {
        showMessage(`👤 Présence détectée (${res.faces_detected} visage(s))`);
    } else {
        showMessage('✅ Aucun visage détecté');
    }
});

recognizeBtn.addEventListener('click', async () => {
    const image = captureImage();
    const res = await sendToServer('/recognize', { image });

    if (res.status === 'authorized') {
        showMessage(`✅ Visage reconnu : ${res.person}`);
    } else if (res.status === 'intruder') {
        showMessage('❌ Intrus détecté !');
        intruderCount++;
        intruderField.value = intruderCount;
    } else {
        showMessage('⚠️ Aucun visage détecté');
    }
});

addFaceBtn.addEventListener('click', async () => {
    const name = addNameInput.value.trim();
    if (!name) return showMessage('⚠️ Veuillez entrer un nom.');

    const image = captureImage();
    const res = await sendToServer('/add-face', { name, image });

    if (res.status === 'saved') {
        showMessage(`✅ Visage de ${res.name} enregistré`);
        refreshFaceList();
    } else {
        showMessage('❌ Erreur : ' + (res.error || 'Inconnue'));
    }

    addNameInput.value = '';
});

// === BACKGROUND TASK ===
setInterval(() => {
    if (Math.random() < 0.2) {
        intruderCount++;
        intruderField.value = intruderCount;
    }
}, 10000);

// === INIT ===
refreshFaceList();
