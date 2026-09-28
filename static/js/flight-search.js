// ==========================================================
// AIRSCAN - FLIGHT SEARCH DYNAMIC FILTERING & SORTING (INR)
// ==========================================================

document.addEventListener('DOMContentLoaded', () => {
  const flightCards = document.querySelectorAll('.flight-card');
  const countDisplay = document.getElementById('flights-count');
  const priceSlider = document.getElementById('price-range-slider');
  const priceDisplay = document.getElementById('price-display');
  const directOnlyCheck = document.getElementById('filter-direct-only');
  const airlineSelect = document.getElementById('filter-airline');
  const aircraftSelect = document.getElementById('filter-aircraft');
  const sortSelect = document.getElementById('sort-by-select');
  const cabinSelector = document.getElementById('results-cabin-select');

  if (!flightCards.length) return;

  const fmtInr = (n) => '₹' + Math.round(n).toLocaleString('en-IN');

  function filterAndSortFlights() {
    const maxPrice = priceSlider ? parseFloat(priceSlider.value) : Infinity;
    const directOnly = directOnlyCheck ? directOnlyCheck.checked : false;
    const selectedAirline = airlineSelect ? airlineSelect.value : 'all';
    const selectedAircraft = aircraftSelect ? aircraftSelect.value : 'all';
    const selectedCabin = cabinSelector ? cabinSelector.value : 'Economy';
    const sortBy = sortSelect ? sortSelect.value : 'price-asc';

    let visibleCards = [];

    flightCards.forEach((card) => {
      // Get price based on chosen cabin
      let price = parseFloat(card.getAttribute(`data-price-${selectedCabin.toLowerCase()}`) || card.getAttribute('data-price-economy'));
      const duration = parseInt(card.getAttribute('data-duration') || '0', 10);
      const airline = card.getAttribute('data-airline') || '';
      const aircraft = card.getAttribute('data-aircraft') || '';
      const stops = parseInt(card.getAttribute('data-stops') || '0', 10);

      // Update displayed price on card in INR
      const cardPriceVal = card.querySelector('.price-val');
      if (cardPriceVal) {
        cardPriceVal.innerText = fmtInr(price);
      }

      // Update book link cabin query param
      const bookBtn = card.querySelector('.btn-book-flight');
      if (bookBtn) {
        const url = new URL(bookBtn.href, window.location.origin);
        url.searchParams.set('cabin_class', selectedCabin);
        bookBtn.href = url.pathname + url.search;
      }

      let matches = true;

      // Price filter
      if (price > maxPrice) matches = false;

      // Airline filter
      if (selectedAirline !== 'all' && airline.toLowerCase() !== selectedAirline.toLowerCase()) {
        matches = false;
      }

      // Direct flights filter
      if (directOnly && stops > 0) matches = false;

      // Aircraft filter
      if (selectedAircraft !== 'all' && !aircraft.toLowerCase().includes(selectedAircraft.toLowerCase())) {
        matches = false;
      }

      if (matches) {
        card.style.display = 'grid';
        visibleCards.push({ card, price, duration });
      } else {
        card.style.display = 'none';
      }
    });

    // Update count display
    if (countDisplay) {
      countDisplay.innerText = `${visibleCards.length} ${visibleCards.length === 1 ? 'Flight' : 'Flights'} Available`;
    }

    // Sort visible cards
    const container = document.getElementById('flights-list-container');
    if (container && visibleCards.length > 0) {
      visibleCards.sort((a, b) => {
        if (sortBy === 'price-asc') return a.price - b.price;
        if (sortBy === 'price-desc') return b.price - a.price;
        if (sortBy === 'duration-asc') return a.duration - b.duration;
        return 0;
      });

      visibleCards.forEach((item) => {
        container.appendChild(item.card);
      });
    }
  }

  // Event Listeners
  if (priceSlider) {
    priceSlider.addEventListener('input', (e) => {
      if (priceDisplay) priceDisplay.innerText = fmtInr(parseFloat(e.target.value));
      filterAndSortFlights();
    });
  }

  if (directOnlyCheck) directOnlyCheck.addEventListener('change', filterAndSortFlights);
  if (airlineSelect) airlineSelect.addEventListener('change', filterAndSortFlights);
  if (aircraftSelect) aircraftSelect.addEventListener('change', filterAndSortFlights);
  if (sortSelect) sortSelect.addEventListener('change', filterAndSortFlights);
  if (cabinSelector) cabinSelector.addEventListener('change', filterAndSortFlights);

  // Initial run
  filterAndSortFlights();
});
