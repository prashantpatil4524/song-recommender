// recommend.js

let genreChart = null;

async function recommend() {
  const btn = document.querySelector('.btn-primary');
  btn.textContent = '⏳ Finding genres…';
  btn.disabled = true;

  const payload = {
    Gener:              document.getElementById('Gener').value,
    User_age:           +document.getElementById('User_age').value,
    User_Gender:        +document.getElementById('User_Gender').value,
    Spotify_Popularity: +document.getElementById('Spotify_Popularity').value,
    Explicit_Track:     +document.getElementById('Explicit_Track').value,
    Spotify_Streams:    500000,
    Release_Days:       365,
  };

  try {
    const res  = await fetch('/api/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (data.error) { alert('Error: ' + data.error); return; }

    // predicted genre
    document.getElementById('recResults').style.display = 'block';
    document.getElementById('predGenre').textContent = data.predicted_favourite_genre;

    // genre chips
    const grid = document.getElementById('recGrid');
    grid.innerHTML = '';
    data.recommended_genres.forEach(g => {
      const widthPct = Math.min(100, Math.round((g.popularity / 100) * 100));
      grid.innerHTML += `
        <div class="rec-chip">
          <div class="rc-name">${g.genres}</div>
          <div class="rc-pop">⭐ ${g.popularity}</div>
          <div class="rc-bar" style="width:${widthPct}%"></div>
        </div>`;
    });

    // chart
    renderChart(data.top_popular_genres);

  } catch (e) {
    alert('Request failed: ' + e.message);
  } finally {
    btn.textContent = '🎵 Find My Genres';
    btn.disabled = false;
  }
}

function renderChart(topGenres) {
  const labels = topGenres.map(g => g.genre);
  const values = topGenres.map(g => g.avg_popularity);

  if (genreChart) genreChart.destroy();

  const ctx = document.getElementById('genreChart').getContext('2d');
  genreChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Avg Popularity',
        data: values,
        backgroundColor: 'rgba(124,106,247,0.7)',
        borderColor: '#7c6af7',
        borderWidth: 1,
        borderRadius: 6,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
      },
      scales: {
        x: { ticks: { color: '#94a3b8' }, grid: { color: '#1e2535' } },
        y: { ticks: { color: '#94a3b8' }, grid: { color: '#1e2535' }, beginAtZero: true },
      },
    },
  });
}

// load top genres chart on page load
async function loadTopGenres() {
  try {
    const res  = await fetch('/api/top-genres');
    const data = await res.json();
    renderChart(data.map(d => ({ genre: d.genre, avg_popularity: d.popularity })));
  } catch (e) {
    console.warn('Could not load top genres chart');
  }
}

loadTopGenres();
