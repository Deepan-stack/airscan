// ==========================================================
// AEROLUX - INTERACTIVE SEAT SELECTION & CHECKOUT ENGINE
// ==========================================================

document.addEventListener('DOMContentLoaded', () => {
  const seatButtons = document.querySelectorAll('.seat-btn:not(.occupied)');
  const maxSeats = window.BOOKING_CONFIG ? window.BOOKING_CONFIG.passengersCount : 1;
  const basePricePerPerson = window.BOOKING_CONFIG ? window.BOOKING_CONFIG.baseFare : 300;
  const flightId = window.BOOKING_CONFIG ? window.BOOKING_CONFIG.flightId : null;
  const cabinClass = window.BOOKING_CONFIG ? window.BOOKING_CONFIG.cabinClass : 'Economy';

  let selectedSeats = []; // Array of { id, number, seatClass, modifier }
  let appliedPromoDiscount = 0;
  let activePromoCode = '';

  // 1. Seat selection click
  seatButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const seatId = btn.getAttribute('data-seat-id');
      const seatNum = btn.getAttribute('data-seat-num');
      const seatClass = btn.getAttribute('data-seat-class');
      const modifier = parseFloat(btn.getAttribute('data-modifier') || '0');

      // Check if already selected
      const existingIdx = selectedSeats.findIndex((s) => s.id === seatId);

      if (existingIdx !== -1) {
        // Deselect
        selectedSeats.splice(existingIdx, 1);
        btn.classList.remove('selected');
      } else {
        // Enforce max seats
        if (selectedSeats.length >= maxSeats) {
          // If only 1 seat allowed, replace it
          if (maxSeats === 1) {
            const prevSeat = selectedSeats[0];
            const prevBtn = document.querySelector(`.seat-btn[data-seat-id="${prevSeat.id}"]`);
            if (prevBtn) prevBtn.classList.remove('selected');
            selectedSeats = [{ id: seatId, number: seatNum, seatClass, modifier }];
            btn.classList.add('selected');
          } else {
            showToast(`You have already selected ${maxSeats} seats for your passengers.`, 'warning');
            return;
          }
        } else {
          selectedSeats.push({ id: seatId, number: seatNum, seatClass, modifier });
          btn.classList.add('selected');
        }
      }

      updateSeatAssignmentsAndPricing();
    });
  });

  // 2. Update passenger form badges & recalculate pricing
  function updateSeatAssignmentsAndPricing() {
    // Update passenger forms with selected seats
    for (let i = 0; i < maxSeats; i++) {
      const seatBadge = document.getElementById(`passenger-seat-badge-${i}`);
      const seatInput = document.getElementById(`passenger-seat-id-${i}`);
      const seatNumInput = document.getElementById(`passenger-seat-num-${i}`);

      if (selectedSeats[i]) {
        if (seatBadge) {
          seatBadge.innerHTML = `<span class="badge badge-gold">Seat ${selectedSeats[i].number} (${selectedSeats[i].seatClass})</span>`;
        }
        if (seatInput) seatInput.value = selectedSeats[i].id;
        if (seatNumInput) seatNumInput.value = selectedSeats[i].number;
      } else {
        if (seatBadge) {
          seatBadge.innerHTML = `<span class="badge badge-warning">Select a seat on map</span>`;
        }
        if (seatInput) seatInput.value = '';
        if (seatNumInput) seatNumInput.value = '';
      }
    }

    // Pricing calculation
    let baseFareTotal = basePricePerPerson * maxSeats;
    let seatAddonTotal = selectedSeats.reduce((sum, s) => sum + s.modifier, 0);

    // Baggage fees (₹1,200 for priority 32kg)
    let baggageTotal = 0;
    const baggageSelects = document.querySelectorAll('.passenger-baggage-select');
    baggageSelects.forEach((sel) => {
      const kg = parseInt(sel.value || '0', 10);
      if (kg > 23) baggageTotal += 1200.00;
    });

    let subtotal = baseFareTotal + seatAddonTotal + baggageTotal;

    // Apply promo
    let discountVal = 0;
    if (activePromoCode === 'AIRSCAN20' || activePromoCode === 'FLYLUX20') {
      discountVal = subtotal * 0.20;
    } else if (activePromoCode === 'AIRSCAN500' || activePromoCode === 'FIRSTFLY') {
      discountVal = Math.min(subtotal, 500.00);
    }

    let discountedSubtotal = Math.max(0, subtotal - discountVal);
    let tax = discountedSubtotal * 0.12;
    let grandTotal = discountedSubtotal + tax;

    const fmtInr = (n) => '₹' + Math.round(n).toLocaleString('en-IN');

    // Update UI summary elements
    setText('summary-seat-count', `${selectedSeats.length} / ${maxSeats} Selected`);
    setText('summary-base-fare', fmtInr(baseFareTotal));
    setText('summary-seat-addons', fmtInr(seatAddonTotal));
    setText('summary-baggage-fees', fmtInr(baggageTotal));
    setText('summary-discount', discountVal > 0 ? `-${fmtInr(discountVal)}` : '₹0');
    setText('summary-taxes', fmtInr(tax));
    setText('summary-grand-total', fmtInr(grandTotal));

    const checkoutBtn = document.getElementById('btn-confirm-checkout');
    if (checkoutBtn) {
      if (selectedSeats.length === maxSeats) {
        checkoutBtn.disabled = false;
        checkoutBtn.innerHTML = `<span>Complete Reservation • ${fmtInr(grandTotal)}</span>`;
      } else {
        checkoutBtn.disabled = true;
        checkoutBtn.innerHTML = `<span>Select ${maxSeats - selectedSeats.length} more seat(s)</span>`;
      }
    }
  }

  function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.innerText = text;
  }

  // Baggage change listeners
  const baggageSelects = document.querySelectorAll('.passenger-baggage-select');
  baggageSelects.forEach((sel) => {
    sel.addEventListener('change', updateSeatAssignmentsAndPricing);
  });

  // Promo code button
  const promoBtn = document.getElementById('btn-apply-promo');
  const promoInput = document.getElementById('promo-code-input');
  if (promoBtn && promoInput) {
    promoBtn.addEventListener('click', () => {
      const code = promoInput.value.trim().toUpperCase();
      if (code === 'AIRSCAN20' || code === 'FLYLUX20') {
        activePromoCode = code;
        showToast('Promo code applied: 20% Discount unlocked!', 'success');
      } else if (code === 'AIRSCAN500' || code === 'FIRSTFLY') {
        activePromoCode = code;
        showToast('Promo code applied: ₹500 First Flight Credit applied!', 'success');
      } else {
        activePromoCode = '';
        showToast('Invalid promo code. Try AIRSCAN20 or AIRSCAN500', 'warning');
      }
      updateSeatAssignmentsAndPricing();
    });
  }

  // 3. Checkout Form Submission
  const checkoutBtn = document.getElementById('btn-confirm-checkout');
  if (checkoutBtn) {
    checkoutBtn.addEventListener('click', async (e) => {
      e.preventDefault();

      if (selectedSeats.length < maxSeats) {
        showToast(`Please choose all ${maxSeats} seats before proceeding.`, 'warning');
        return;
      }

      // Collect passenger data
      let passengers = [];
      let missingFields = false;

      for (let i = 0; i < maxSeats; i++) {
        const nameInput = document.getElementById(`passenger-name-${i}`);
        const passportInput = document.getElementById(`passenger-passport-${i}`);
        const dobInput = document.getElementById(`passenger-dob-${i}`);
        const mealInput = document.getElementById(`passenger-meal-${i}`);
        const baggageInput = document.getElementById(`passenger-baggage-${i}`);

        const fullName = nameInput ? nameInput.value.trim() : '';
        const passport = passportInput ? passportInput.value.trim().toUpperCase() : '';

        if (!fullName || !passport) {
          missingFields = true;
          break;
        }

        passengers.push({
          seat_id: selectedSeats[i].id,
          seat_number: selectedSeats[i].number,
          full_name: fullName,
          passport: passport,
          dob: dobInput ? dobInput.value : '1995-01-01',
          meal: mealInput ? mealInput.value : 'Standard Gourmet',
          baggage: baggageInput ? parseInt(baggageInput.value, 10) : 0
        });
      }

      if (missingFields) {
        showToast('Please provide full name and passport number for all passengers.', 'danger');
        return;
      }

      checkoutBtn.disabled = true;
      checkoutBtn.innerHTML = `<span>Securing Seats & Issuing Tickets...</span>`;

      try {
        const response = await fetch('/api/book', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            flight_id: flightId,
            cabin_class: cabinClass,
            passengers: passengers,
            promo_code: activePromoCode
          })
        });

        const result = await response.json();
        if (result.success) {
          showToast('Reservation confirmed! Redirecting to boarding pass...', 'success');
          setTimeout(() => {
            window.location.href = result.redirect_url;
          }, 800);
        } else {
          showToast(result.message || 'Booking failed.', 'danger');
          checkoutBtn.disabled = false;
          updateSeatAssignmentsAndPricing();
        }
      } catch (err) {
        showToast('Network error during checkout.', 'danger');
        checkoutBtn.disabled = false;
        updateSeatAssignmentsAndPricing();
      }
    });
  }

  // Pre-select first available seats if none selected yet for convenience
  updateSeatAssignmentsAndPricing();
});
