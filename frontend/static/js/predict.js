// predict.js

async function predict() {
  const btn = document.querySelector('.btn-primary');
  btn.textContent = '⏳ Predicting…';
  btn.disabled = true;

  const payload = {
    Gener:               document.getElementById('Gener').value,
    Spotify_Popularity:  +document.getElementById('Spotify_Popularity').value,
    Spotify_Streams:     +document.getElementById('Spotify_Streams').value,
    Explicit_Track:      +document.getElementById('Explicit_Track').value,
    Release_Days:        +document.getElementById('Release_Days').value,
    User_age:            +document.getElementById('User_age').value,
    User_Gender:         +document.getElementById('User_Gender').value,
  };

  try {
    const res  = await fetch('/api/predict', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
    const data = await res.json();

    if (data.error) { alert('Error: ' + data.error); return; }

    document.getElementById('resultCard').style.display = 'block';
    document.getElementById('resultGenre').textContent  = data.predicted_genre;
    document.getElementById('confFill').style.width     = data.confidence + '%';
    document.getElementById('confPct').textContent      = data.confidence + '%';
    document.getElementById('modelBadge').textContent   = '✅ ' + data.best_model + '  |  Acc: ' + data.model_accuracy + '%';

    // prob list
    const list = document.getElementById('probList');
    list.innerHTML = '';
    const sorted = Object.entries(data.all_probabilities).sort((a,b) => b[1]-a[1]);
    sorted.forEach(([genre, pct]) => {
      list.innerHTML += `
        <div class="prob-item">
          <span class="prob-name">${genre}</span>
          <div class="prob-bar-wrap"><div class="prob-bar" style="width:${pct}%"></div></div>
          <span class="prob-val">${pct}%</span>
        </div>`;
    });

  } catch(e) {
    alert('Request failed: ' + e.message);
  } finally {
    btn.textContent = '🔮 Predict Genre Preference';
    btn.disabled = false;
  }
}

// load model leaderboard on page load
async function loadModelInfo() {
  try {
    const res  = await fetch('/api/model-info');
    const data = await res.json();
    const div  = document.getElementById('modelTable');

    let html = `<table class="model-table">
      <thead><tr><th>Model</th><th>Accuracy</th><th>CV Acc</th><th></th></tr></thead><tbody>`;

    data.models.forEach(m => {
      html += `<tr class="${m.is_best ? 'best-row' : ''}">
        <td>${m.name}</td>
        <td>${m.accuracy}%</td>
        <td>${m.cv_accuracy}%</td>
        <td>${m.is_best ? '<span class="badge-best">Best</span>' : ''}</td>
      </tr>`;
    });

    html += '</tbody></table>';
    div.innerHTML = html;
    document.querySelector('#modelCard .muted').style.display = 'none';
  } catch(e) {
    document.querySelector('#modelCard .muted').textContent = 'Train model first: python backend/train_model.py';
  }
}

loadModelInfo();
