document.addEventListener("DOMContentLoaded", () => {
    const loginContainer = document.getElementById("login-container");
    const chatContainer = document.getElementById("chat-container");
    const loginBtn = document.getElementById("login-btn");
    const logoutBtn = document.getElementById("logout-btn");
    const toggleChatBtn = document.getElementById("toggleChat");

    const API_URL = "http://localhost:8000";

    function checkAuth() {
        chrome.storage.sync.get(["token"], (data) => {
            if (data.token) {
                chatContainer.style.display = "block";
                loginContainer.style.display = "none";
            } else {
                chatContainer.style.display = "none";
                loginContainer.style.display = "block";
            }
        });
    }

    loginBtn.addEventListener("click", () => {
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        fetch(`${API_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        })
        .then(res => res.json())
        .then(data => {
            if (data.access_token) {
                chrome.storage.sync.set({ token: data.access_token });
                checkAuth();
            } else {
                alert("Invalid credentials");
            }
        });
    });

    logoutBtn.addEventListener("click", () => {
        chrome.storage.sync.remove("token", checkAuth);
    });

    toggleChatBtn.addEventListener("click", () => {
        chrome.storage.sync.get(["token"], (data) => {
            if (!data.token) {
                alert("Please log in first.");
                return;
            }
            chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                chrome.tabs.sendMessage(tabs[0].id, { action: "toggleChat" });
            });
        });
    });

    checkAuth();
});
