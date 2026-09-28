// ==========================================================
// AEROLUX - TICKET & BOOKING MANAGEMENT
// ==========================================================

document.addEventListener('DOMContentLoaded', () => {
  // 1. Web Check-in Button Handler
  const checkinButtons = document.querySelectorAll('.btn-action-checkin');
  checkinButtons.forEach((btn) => {
    btn.addEventListener('click', async () => {
      const ref = btn.getAttribute('data-ref');
      btn.disabled = true;
      btn.innerText = 'Checking In...';

      try {
        const resp = await fetch(`/api/checkin/${ref}`, { method: 'POST' });
        const data = await resp.json();
        if (data.success) {
          showToast(data.message, 'success');
          // Update status badge
          const statusBadge = document.getElementById(`status-badge-${ref}`);
          if (statusBadge) {
            statusBadge.className = 'badge badge-success';
            statusBadge.innerText = 'Checked-In';
          }
          btn.remove();
        } else {
          showToast(data.message || 'Check-in failed.', 'danger');
          btn.disabled = false;
          btn.innerText = 'Online Check-In';
        }
      } catch (err) {
        showToast('Network error during check-in.', 'danger');
        btn.disabled = false;
        btn.innerText = 'Online Check-In';
      }
    });
  });

  // 2. Cancel Booking Button Handler
  const cancelButtons = document.querySelectorAll('.btn-action-cancel');
  cancelButtons.forEach((btn) => {
    btn.addEventListener('click', async () => {
      const ref = btn.getAttribute('data-ref');
      const fare = parseFloat(btn.getAttribute('data-fare') || '0');
      const refund = Math.round(fare * 0.9).toLocaleString('en-IN');

      const confirmed = confirm(
        `Are you sure you want to cancel booking ${ref}?\n\nA 90% refund (₹${refund}) will be credited to your original payment method, and your seats will be released.`
      );

      if (!confirmed) return;

      btn.disabled = true;
      btn.innerText = 'Cancelling...';

      try {
        const resp = await fetch(`/api/cancel-booking/${ref}`, { method: 'POST' });
        const data = await resp.json();
        if (data.success) {
          showToast(data.message, 'info');
          // Update status badge
          const statusBadge = document.getElementById(`status-badge-${ref}`);
          if (statusBadge) {
            statusBadge.className = 'badge badge-danger';
            statusBadge.innerText = 'Cancelled';
          }
          btn.parentElement.innerHTML = `<span class="badge badge-danger">Booking Cancelled</span>`;
        } else {
          showToast(data.message || 'Cancellation failed.', 'danger');
          btn.disabled = false;
          btn.innerText = 'Cancel Flight';
        }
      } catch (err) {
        showToast('Network error during cancellation.', 'danger');
        btn.disabled = false;
        btn.innerText = 'Cancel Flight';
      }
    });
  });

  // 3. Tab filter for My Bookings (Upcoming vs Past / Cancelled)
  const bookingTabs = document.querySelectorAll('.booking-filter-tab');
  const bookingCards = document.querySelectorAll('.booking-item-card');

  bookingTabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      bookingTabs.forEach((t) => t.classList.remove('active'));
      tab.classList.add('active');
      const filter = tab.getAttribute('data-filter');

      bookingCards.forEach((card) => {
        const isPast = card.getAttribute('data-past') === 'true';
        const isCancelled = card.getAttribute('data-status') === 'Cancelled';

        if (filter === 'upcoming') {
          card.style.display = (!isPast && !isCancelled) ? 'block' : 'none';
        } else if (filter === 'past') {
          card.style.display = (isPast || isCancelled) ? 'block' : 'none';
        } else {
          card.style.display = 'block';
        }
      });
    });
  });
});
