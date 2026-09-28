// ==========================================================
// AEROLUX AIRWAYS - CORE SCRIPTS
// ==========================================================

document.addEventListener('DOMContentLoaded', () => {
  // 1. Auto-dismiss flash alerts after 5 seconds
  const flashMessages = document.querySelectorAll('.flash-message');
  flashMessages.forEach((msg) => {
    setTimeout(() => {
      msg.style.opacity = '0';
      msg.style.transform = 'translateY(-10px)';
      setTimeout(() => msg.remove(), 400);
    }, 5500);
  });

  // 2. Set min date for date inputs to today
  const dateInputs = document.querySelectorAll('input[type="date"]');
  const today = new Date().toISOString().split('T')[0];
  dateInputs.forEach((input) => {
    if (!input.getAttribute('min')) {
      input.setAttribute('min', today);
    }
  });

  // 3. OTP 6-Digit input auto-focus and auto-tabbing
  const otpInputs = document.querySelectorAll('.otp-digit');
  if (otpInputs.length > 0) {
    otpInputs[0].focus();

    otpInputs.forEach((input, index) => {
      input.addEventListener('input', (e) => {
        const val = e.target.value;
        if (val.length === 1 && index < otpInputs.length - 1) {
          otpInputs[index + 1].focus();
        }
      });

      input.addEventListener('keydown', (e) => {
        if (e.key === 'Backspace' && !input.value && index > 0) {
          otpInputs[index - 1].focus();
        }
      });

      // Handle paste of 6 digits
      input.addEventListener('paste', (e) => {
        e.preventDefault();
        const pasted = (e.clipboardData || window.clipboardData).getData('text').trim();
        if (pasted.length === 6 && /^\d+$/.test(pasted)) {
          otpInputs.forEach((inp, idx) => {
            inp.value = pasted[idx] || '';
          });
          otpInputs[5].focus();
        }
      });
    });
  }

  // 4. Verification Resend Code API & Timer
  const resendBtn = document.getElementById('btn-resend-code');
  if (resendBtn) {
    resendBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      resendBtn.disabled = true;
      resendBtn.innerText = 'Sending...';

      try {
        const resp = await fetch('/api/resend-code', { method: 'POST' });
        const data = await resp.json();
        if (data.success) {
          showToast(data.message, 'success');
          // If simulation preview box exists, update it
          const previewElem = document.getElementById('simulated-code-display');
          if (previewElem && data.simulated_code) {
            previewElem.innerText = data.simulated_code;
          }
          startResendCountdown(resendBtn, 60);
        } else {
          showToast(data.message || 'Failed to resend code', 'danger');
          resendBtn.disabled = false;
          resendBtn.innerText = 'Resend Code';
        }
      } catch (err) {
        showToast('Network error while requesting code.', 'danger');
        resendBtn.disabled = false;
        resendBtn.innerText = 'Resend Code';
      }
    });
  }

  // 5. Trip Type Tab Selector on Search Widgets
  const tripTabs = document.querySelectorAll('.trip-type-btn');
  const returnDateField = document.getElementById('return-date-field');
  const tripTypeInput = document.getElementById('trip-type-input');

  tripTabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      tripTabs.forEach((t) => t.classList.remove('active'));
      tab.classList.add('active');
      const trip = tab.getAttribute('data-trip');
      if (tripTypeInput) tripTypeInput.value = trip;

      if (returnDateField) {
        if (trip === 'round-trip') {
          returnDateField.style.display = 'flex';
          const depInput = document.getElementById('dep-date-input');
          const retInput = document.getElementById('ret-date-input');
          if (depInput && retInput && depInput.value) {
            retInput.min = depInput.value;
          }
        } else {
          returnDateField.style.display = 'none';
        }
      }
    });
  });

  // 6. Mobile Navigation Drawer Toggle
  const navToggle = document.getElementById('nav-toggle');
  const navMenu = document.querySelector('.nav-menu');
  const navActions = document.querySelector('.nav-actions');

  if (navToggle && navMenu) {
    navToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      navToggle.classList.toggle('active');
      navMenu.classList.toggle('open');
      if (navActions) navActions.classList.toggle('open');
    });

    // Close menu when clicking outside or clicking any nav link
    document.addEventListener('click', (e) => {
      if (!navToggle.contains(e.target) && !navMenu.contains(e.target) && (!navActions || !navActions.contains(e.target))) {
        navToggle.classList.remove('active');
        navMenu.classList.remove('open');
        if (navActions) navActions.classList.remove('open');
      }
    });

    navMenu.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        navToggle.classList.remove('active');
        navMenu.classList.remove('open');
        if (navActions) navActions.classList.remove('open');
      });
    });
  }
});

function startResendCountdown(btn, seconds) {
  let remaining = seconds;
  const interval = setInterval(() => {
    remaining--;
    if (remaining <= 0) {
      clearInterval(interval);
      btn.disabled = false;
      btn.innerText = 'Resend Code';
    } else {
      btn.innerText = `Resend in ${remaining}s`;
    }
  }, 1000);
}

// Global Toast utility
function showToast(message, type = 'info') {
  let container = document.querySelector('.flash-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'flash-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `flash-message flash-${type}`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-10px)';
    setTimeout(() => toast.remove(), 400);
  }, 5000);
}

// Quick helper to fill simulated verification code
function autoFillCode(code) {
  const inputs = document.querySelectorAll('.otp-digit');
  if (inputs.length === 6 && code && code.length === 6) {
    for (let i = 0; i < 6; i++) {
      inputs[i].value = code[i];
    }
    inputs[5].focus();
    showToast('Verification code auto-filled!', 'info');
  }
}
