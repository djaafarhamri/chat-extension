(function() {
  let chatExists = false;

  function createChatUI() {
    if (chatExists) return;

    // Create toggle button
    const toggleButton = document.createElement("button");
    toggleButton.id = "chat-toggle-button";
    toggleButton.textContent = "Chat";
    document.body.appendChild(toggleButton);

    // Create chat popup
    const chatPopup = document.createElement("div");
    chatPopup.id = "chat-popup";
    chatPopup.innerHTML = `
      <div id="chat-header">Chat <span id="chat-close">&times;</span></div>
      <div id="chat-body"></div>
      <div id="chat-input-container">
        <input id="chat-input" type="text" placeholder="Type a message...">
        <button id="chat-send">Send</button>
      </div>
    `;
    document.body.appendChild(chatPopup);

    chatPopup.style.display = "none";

    // Toggle chat display
    toggleButton.addEventListener("click", () => {
      chatPopup.style.display = chatPopup.style.display === "none" ? "flex" : "none";
    });

    // Close chat
    document.getElementById("chat-close").addEventListener("click", () => {
      chatPopup.style.display = "none";
    });

    // Send message
    document.getElementById("chat-send").addEventListener("click", () => {
      const chatInput = document.getElementById("chat-input");
      const message = chatInput.value.trim();
      if (message) {
        const messageDiv = document.createElement("div");
        messageDiv.className = "chat-message";
        messageDiv.textContent = message;
        document.getElementById("chat-body").appendChild(messageDiv);
        chatInput.value = "";
      }
    });

    chatExists = true;
  }

  function removeChatUI() {
    const toggleButton = document.getElementById("chat-toggle-button");
    const chatPopup = document.getElementById("chat-popup");
    if (toggleButton) toggleButton.remove();
    if (chatPopup) chatPopup.remove();
    chatExists = false;
  }

  // Listen for messages from popup.js
  chrome.runtime.onMessage.addListener((message) => {
    if (message.action === "toggleChat") {
      if (message.enabled) {
        createChatUI();
      } else {
        removeChatUI();
      }
    }
  });

  // Load chat state on page load
  chrome.storage.sync.get(["chatEnabled"], (data) => {
    if (data.chatEnabled) createChatUI();
  });
})();
