// dashboard.js

const CHART_DEFAULTS = {
  responsive: true,
  plugins: { legend: { labels: { color: '#94a3b8', font: { size: 12 } } } },
  scales: {
    x: { ticks: { color: '#94a3b8' }, grid: { color: '#1e2535' } },
    y: { ticks: { color: '#94a3b8' }, grid: { color: '#1e2535' }, beginAtZero: true },
  },
};

function makeBar(ctx, labels, values, color = '#7c6af7') {
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: color + 'b3',
        borderColor: color,
        borderWidth: 1,
        borderRadius: 6,
      }],
    },
    options: { ...CHART_DEFAULTS, plugins: { legend: { display: false } } },
  });
}

function makeDoughnut(ctx, labels, values) {
  return new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: ['#7c6af7b3', '#06b6d4b3', '#f59e0bb3', '#10b981b3',
                          '#f43f5eb3', '#8b5cf6b3', '#3b82f6b3', '#ec4899b3'],
        borderColor: '#1a1d2e',
        borderWidth: 2,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', padding: 12 } } },
    },
  });
}

async function loadDashboard() {
  try {
    const res  = await fetch('/api/stats');
    const data = await res.json();

    if (data.error) { console.error(data.error); return; }

    // stat cards
    document.getElementById('sc-total').textContent  = data.total_records.toLocaleString();
    document.getElementById('sc-pop').textContent    = data.avg_popularity;
    document.getElementById('sc-age').textContent    = data.avg_user_age;
    document.getElementById('sc-genres').textContent = data.total_genres;

    // fav genre doughnut
    makeDoughnut(
      document.getElementById('favGenreChart').getContext('2d'),
      Object.keys(data.fav_genre_dist),
      Object.values(data.fav_genre_dist),
    );

    // gender doughnut
    makeDoughnut(
      document.getElementById('genderChart').getContext('2d'),
      Object.keys(data.gender_split),
      Object.values(data.gender_split),
    );

    // age bar
    makeBar(
      document.getElementById('ageChart').getContext('2d'),
      Object.keys(data.age_distribution),
      Object.values(data.age_distribution),
      '#06b6d4',
    );

    // popularity by genre bar
    makeBar(
      document.getElementById('popGenreChart').getContext('2d'),
      Object.keys(data.popularity_by_genre),
      Object.values(data.popularity_by_genre),
      '#a78bfa',
    );

  } catch (e) {
    console.error('Dashboard load failed:', e);
  }
}

loadDashboard();
