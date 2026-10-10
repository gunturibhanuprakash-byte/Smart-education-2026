/**
 * Offline & Low-Connectivity Manager
 */

function updateNetworkStatus() {
  const statusEl = document.getElementById('connectionStatus');
  const dotEl = statusEl ? statusEl.querySelector('.status-dot') : null;
  const textEl = document.getElementById('connectionText');

  if (navigator.onLine) {
    if (statusEl) statusEl.className = 'connection-status';
    if (textEl) textEl.textContent = 'ONLINE';
  } else {
    if (statusEl) statusEl.className = 'connection-status offline';
    if (textEl) textEl.textContent = 'OFFLINE MODE';
  }
}

// Prefetch and cache core syllabus data for offline viewing
function cacheOfflineData() {
  if ('localStorage' in window) {
    fetch('/api/offline-data')
      .then(res => res.json())
      .then(data => {
        localStorage.setItem('smart_edu_offline_data', JSON.stringify(data));
      })
      .catch(() => {});
  }
}

// Register Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/sw.js')
      .then(() => console.log('Smart Education Service Worker Registered'))
      .catch(err => console.log('SW registration failed: ', err));
  });
}

window.addEventListener('online', () => {
  updateNetworkStatus();
  cacheOfflineData();
});

window.addEventListener('offline', updateNetworkStatus);

document.addEventListener('DOMContentLoaded', () => {
  updateNetworkStatus();
  cacheOfflineData();
});
