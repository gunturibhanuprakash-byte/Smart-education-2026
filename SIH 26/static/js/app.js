/**
 * Global App UI Helpers
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Sidebar Toggle
  const sidebar = document.querySelector('.app-sidebar');
  const toggleBtn = document.querySelector('.sidebar-toggle');
  
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });

    // Close when clicking outside on mobile
    document.addEventListener('click', (e) => {
      if (window.innerWidth <= 768 && 
          !sidebar.contains(e.target) && 
          !toggleBtn.contains(e.target) && 
          sidebar.classList.contains('open')) {
        sidebar.classList.remove('open');
      }
    });
  }

  // 2. Alert Dismissals
  document.querySelectorAll('.alert-close').forEach(btn => {
    btn.addEventListener('click', () => {
      const alert = btn.closest('.alert');
      if (alert) alert.remove();
    });
  });

  // 3. Modal Open/Close Controls
  window.openModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add('active');
  };

  window.closeModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove('active');
  };

  // Close modals on backdrop click
  document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) {
        backdrop.classList.remove('active');
      }
    });
  });

  // 4. Quick Demo Login Presets
  window.fillDemo = function(role) {
    const userInput = document.querySelector('input[name="username"]');
    const passInput = document.querySelector('input[name="password"]');
    if (userInput && passInput) {
      if (role === 'student') {
        userInput.value = 'student1';
        passInput.value = 'student123';
      } else if (role === 'teacher') {
        userInput.value = 'teacher1';
        passInput.value = 'teacher123';
      }
    }
  };
});
