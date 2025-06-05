let patrolInterval = null;
let patrolSeconds = 0;
let intruderCount = 0;
let cameraStream = null;
let isPatrolRunning = false;
let isCameraRunning = false;
let dogIsAwake = false;

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
const cameraBtn = document.getElementById("cameraToggleBtn");
const awakeBtn = document.getElementById("awakeDog");

awakeBtn.addEventListener("click", async() => {
    const command = dogIsAwake ? 'sleep-dog' : 'awake-dog';
    const res = await fetch("/awake", {
            method: "POST",
            body: new URLSearchParams({ command: command}),
        });
    showMessage(await res.text());
    awakeBtn.textContent = dogIsAwake ? "Arrêter PiDog" : "Éveiller PiDog";
    awakeBtn.style.backgroundColor = dogIsAwake ? "#dc3545" :  "#198754";
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

cameraBtn.addEventListener("click", async () => {
    if (!isCameraRunning) {
    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = cameraStream;
        video.play();
        showMessage("Caméra démarrée !");
        cameraBtn.textContent = "⛔ Stopper la caméra";
        cameraBtn.style.backgroundColor = "#dc3545";
        isCameraRunning = true;
    } catch (err) {
        showMessage("❌ Erreur caméra : " + err.message, 6000);
    }
    } else {
    cameraStream.getTracks().forEach(track => track.stop());
    video.srcObject = null;
    cameraStream = null;
    showMessage("Caméra arrêtée.");
    cameraBtn.textContent = "🎥 Démarrer la caméra";
    cameraBtn.style.backgroundColor = "#0d6efd";
    isCameraRunning = false;
    }
});


document.getElementById("detectFaceBtn").addEventListener("click", async () => {
    const image = captureImage();
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
    const image = captureImage();
    const res = await sendToServer("/add-face", { name, image });
    if (res.status === "saved") {
    showMessage(`✅ Visage de ${res.name} enregistré`);
    } else {
    showMessage("❌ Erreur : " + (res.error || "Inconnue"), 5000);
    }
    document.getElementById("addName").value = "";
});

document.getElementById("recognizeBtn").addEventListener("click", async () => {
    const image = captureImage();
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