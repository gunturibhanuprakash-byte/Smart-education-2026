

document.addEventListener('DOMContentLoaded', () => {
  const chatMessages = document.getElementById('chatMessages');
  const chatInput = document.getElementById('chatInput');
  const sendBtn = document.getElementById('btnSendChat');
  const topicFilter = document.getElementById('topicFilter');
  const levelToggle = document.getElementById('levelToggle');

  if (!chatMessages || !chatInput || !sendBtn) return;

  function appendMessage(text, role) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${role}`;
    
    // Parse basic markdown formatting (bold, code blocks)
    let formatted = text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
      .replace(/\n/g, '<br>');

    bubble.innerHTML = formatted;
    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function sendMessage(customText) {
    const text = customText || chatInput.value.trim();
    if (!text) return;

    appendMessage(text, 'user');
    if (!customText) chatInput.value = '';

    // Show typing indicator
    const typingBubble = document.createElement('div');
    typingBubble.className = 'chat-bubble ai typing';
    typingBubble.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Smart AI Tutor is thinking...';
    chatMessages.appendChild(typingBubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    const topic = topicFilter ? topicFilter.value : '';
    const level = levelToggle ? levelToggle.value : 'beginner';

    fetch('/api/ai/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: text,
        topic_hint: topic,
        level: level
      })
    })
    .then(res => res.json())
    .then(data => {
      typingBubble.remove();
      appendMessage(data.reply || "I am here to help! Could you please clarify your question?", 'ai');
    })
    .catch(err => {
      typingBubble.remove();
      appendMessage("⚠️ Smart AI Tutor is temporarily running in offline mode. Let's study using the learning materials!", 'ai');
    });
  }

  sendBtn.addEventListener('click', () => sendMessage());

  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Suggested prompt chips
  document.querySelectorAll('.prompt-chip').forEach(chip => {
    chip.addEventListener('click', function() {
      const promptText = this.getAttribute('data-prompt') || this.textContent;
      sendMessage(promptText);
    });
  });
});
