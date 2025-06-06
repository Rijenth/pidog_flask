let patrolInterval = null;
let patrolSeconds = 0;
let intruderCount = 0;
let cameraStream = null;
let isPatrolRunning = false;
let isCameraRunning = false;
let dogIsAwake = false;
const faceList = document.getElementById('faceList');

const video = document.getElementById('camera');
const infoBox = document.getElementById("infoBox");

function showMessage(message, duration = 4000) {
    infoBox.textContent = message;
    infoBox.style.display = "block";
    setTimeout(() => {
    infoBox.textContent = "";
    infoBox.style.display = "none";
    }, duration);
}

async function captureImage() {
    const res = await fetch('/capture-image');
    const data = await res.json();
    return data.image;
}

async function sendToServer(endpoint, payload) {
    const res = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
    });
    return res.json();
}

const patrolBtn = document.getElementById("patrolToggleBtn");
const awakeBtn = document.getElementById("awakeDog");

awakeBtn.addEventListener("click", async() => {
    const command = dogIsAwake ? 'sleep-dog' : 'awake-dog';
    const res = await fetch("/send-command", {
            method: "POST",
            body: new URLSearchParams({ command: command}),
        });
    const message = await res.text();
    showMessage(message);
    awakeBtn.textContent = message === 'awake-dog' ? "Arrêter PiDog" : "Éveiller PiDog";
    awakeBtn.style.backgroundColor = message === 'awake-dog' ? "#dc3545" : "#198754";
    dogIsAwake = !dogIsAwake;
})

patrolBtn.addEventListener("click", async () => {
    if (!isPatrolRunning) {
    const res = await fetch("/send-command", {
        method: "POST",
        body: new URLSearchParams({ command: "start-patrol" }),
    });
    showMessage(await res.text());
    patrolBtn.textContent = "🛑 Arrêter la patrouille";
    patrolBtn.style.backgroundColor = "#dc3545";
    isPatrolRunning = true;

    patrolSeconds = 0;
    document.getElementById("patrolDuration").value = 0;
    clearInterval(patrolInterval);
    patrolInterval = setInterval(() => {
        patrolSeconds++;
        document.getElementById("patrolDuration").value = patrolSeconds;
    }, 1000);
    } else {
    const res = await fetch("/send-command", {
        method: "POST",
        body: new URLSearchParams({ command: "stop-patrol" }),
    });
    showMessage(await res.text());
    clearInterval(patrolInterval);
    patrolSeconds = 0;
    document.getElementById("patrolDuration").value = 0;

    patrolBtn.textContent = "🚓 Lancer la patrouille";
    patrolBtn.style.backgroundColor = "#198754";
    isPatrolRunning = false;
    }
});

document.getElementById("detectFaceBtn").addEventListener("click", async () => {
    const image = await captureImage();
    console.log("image: " , image)
    const res = await sendToServer("/detect-face", { image });
    if (res.someone_present) {
    showMessage(`👤 Présence détectée (${res.faces_detected} visage(s))`);
    } else {
    showMessage("✅ Aucun visage détecté");
    }
});

document.getElementById("addFaceBtn").addEventListener("click", async () => {
    const name = document.getElementById("addName").value.trim();
    if (!name) return showMessage("⚠️ Veuillez entrer un nom.");
    const image = await captureImage();
    const res = await sendToServer("/add-face", { name, image });
    if (res.status === "saved") {
    showMessage(`✅ Visage de ${res.name} enregistré`);
    refreshFaceList();
    } else {
    showMessage("❌ Erreur : " + (res.error || "Inconnue"), 5000);
    }
    document.getElementById("addName").value = "";
});

document.getElementById("recognizeBtn").addEventListener("click", async () => {
    const image = await captureImage();
    const res = await sendToServer("/recognize", { image });
    if (res.status === "authorized") {
    showMessage(`✅ Visage reconnu : ${res.person}`);
    } else if (res.status === "intruder") {
    showMessage("❌ Intrus détecté !");
    intruderCount++;
    document.getElementById("intruderCount").value = intruderCount;
    } else {
    showMessage("⚠️ Aucun visage détecté");
    }
});

// Détection simulée toutes les 10s
setInterval(() => {
    intruderCount += Math.random() < 0.2 ? 1 : 0;
    document.getElementById("intruderCount").value = intruderCount;
}, 10000);

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

refreshFaceList();