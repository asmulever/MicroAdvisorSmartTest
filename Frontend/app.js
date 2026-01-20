const API = {
  tests: '/api/tests',
  summary: '/api/analytics/summary',
  funnel: '/api/analytics/funnel',
  profiles: '/api/analytics/profiles',
  dropoff: '/api/analytics/dropoff'
};

const IQ_API = {
  start: '/api/iq/start',
  answer: '/api/iq/answer',
  finish: '/api/iq/finish'
};

const formatTime = (seconds) => {
  if (!seconds) return '--';
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const fetchJson = async (url, options = {}) => {
  try {
    const res = await fetch(url, options);
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.info('fetch_error', url, err);
    return null;
  }
};

const updateSummary = (summary) => {
  const testsEl = document.getElementById('metric-tests');
  const finishEl = document.getElementById('metric-finish');
  const timeEl = document.getElementById('metric-time');

  if (!testsEl || !finishEl || !timeEl) {
    return;
  }

  if (!summary) {
    testsEl.textContent = '--';
    finishEl.textContent = '--';
    timeEl.textContent = '--';
    return;
  }

  testsEl.textContent = summary.active_tests ?? '--';
  finishEl.textContent = `${summary.finish_rate ?? 0}%`;
  timeEl.textContent = formatTime(summary.avg_time_sec ?? 0);
};

const updateHero = (test) => {
  const titleEl = document.getElementById('hero-test-title');
  const versionEl = document.getElementById('hero-test-version');
  if (!titleEl || !versionEl) {
    return;
  }

  if (!test) {
    titleEl.textContent = 'Test de IQ General';
    versionEl.textContent = 'Listo para iniciar';
    return;
  }

  titleEl.textContent = test.title;
  versionEl.textContent = `Version ${test.published_version ?? '--'}`;
};

const updateTestsTable = (tests) => {
  const body = document.getElementById('tests-table-body');
  if (!body) {
    return;
  }
  body.innerHTML = '';

  if (!tests || tests.length === 0) {
    const row = document.createElement('tr');
    row.innerHTML = '<td colspan="5" class="text-muted">Sin tests disponibles.</td>';
    body.appendChild(row);
    return;
  }

  tests.forEach((test) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${test.slug}</td>
      <td>${test.title}</td>
      <td>${(test.lang || 'ES').toUpperCase()}</td>
      <td>${test.published_version ?? '--'}</td>
      <td><span class="pill${test.is_active ? '' : ' ghost'}">${test.is_active ? 'publicado' : 'inactivo'}</span></td>
    `;
    body.appendChild(row);
  });
};

const initReveal = () => {
  const revealItems = document.querySelectorAll('.reveal');
  revealItems.forEach((el) => {
    el.style.animationDelay = el.style.getPropertyValue('--delay');
    el.classList.add('is-visible');
  });
};

const setActiveNav = () => {
  const current = window.location.pathname || '/';
  document.querySelectorAll('.nav-link').forEach((link) => {
    const href = link.getAttribute('href');
    if (href === current) {
      link.classList.add('active');
    }
  });
};

const initCharts = (funnelData, profileData, dropData) => {
  const funnelCtx = document.getElementById('funnelChart');
  const profileCtx = document.getElementById('profileChart');
  const dropCtx = document.getElementById('dropChart');

  if (!funnelCtx || !profileCtx || !dropCtx) {
    return;
  }

  const funnelLabels = funnelData?.labels?.length ? funnelData.labels : ['Start', 'Finish'];
  const funnelValues = funnelData?.values?.length ? funnelData.values : [0, 0];

  new Chart(funnelCtx, {
    type: 'bar',
    data: {
      labels: funnelLabels,
      datasets: [{
        label: 'Usuarios',
        data: funnelValues,
        backgroundColor: ['#6ee7ff', '#5bd1f2', '#4ab2e0', '#3a8ec7'],
        borderRadius: 12
      }]
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        y: { grid: { color: 'rgba(255,255,255,0.08)' }, ticks: { color: '#d5e4ff' } },
        x: { grid: { display: false }, ticks: { color: '#d5e4ff' } }
      }
    }
  });

  const profileLabels = profileData?.labels?.length ? profileData.labels : ['Sin datos'];
  const profileValues = profileData?.values?.length ? profileData.values : [0];

  new Chart(profileCtx, {
    type: 'doughnut',
    data: {
      labels: profileLabels,
      datasets: [{
        data: profileValues,
        backgroundColor: ['#f9b27a', '#6c7bff', '#22d3a6', '#6ee7ff']
      }]
    },
    options: {
      plugins: {
        legend: { position: 'bottom', labels: { color: '#d5e4ff' } }
      }
    }
  });

  const dropLabels = dropData?.labels?.length ? dropData.labels : ['Q1'];
  const dropValues = dropData?.values?.length ? dropData.values : [0];

  new Chart(dropCtx, {
    type: 'line',
    data: {
      labels: dropLabels,
      datasets: [{
        label: 'Abandono',
        data: dropValues,
        borderColor: '#ff8aa1',
        backgroundColor: 'rgba(255,138,161,0.2)',
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      plugins: { legend: { labels: { color: '#d5e4ff' } } },
      scales: {
        y: { grid: { color: 'rgba(255,255,255,0.08)' }, ticks: { color: '#d5e4ff' } },
        x: { grid: { display: false }, ticks: { color: '#d5e4ff' } }
      }
    }
  });
};

const saveLastResult = (result) => {
  if (!result) return;
  localStorage.setItem('iq_last_result', JSON.stringify(result));
};

const loadLastResult = () => {
  const raw = localStorage.getItem('iq_last_result');
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch (err) {
    console.info('result_parse_error', err);
    return null;
  }
};

const updateResultView = (result) => {
  const iqEl = document.getElementById('result-iq');
  const labelEl = document.getElementById('result-label');
  const scoreEl = document.getElementById('result-score');
  const markerEl = document.getElementById('result-marker');
  if (!iqEl || !labelEl || !scoreEl || !markerEl) return;

  if (!result) {
    iqEl.textContent = 'IQ estimado: --';
    labelEl.textContent = 'Completa el test para ver tu resultado.';
    scoreEl.textContent = 'Score: --';
    markerEl.style.left = '0%';
    return;
  }

  iqEl.textContent = `IQ estimado: ${result.iq}`;
  labelEl.textContent = result.label;
  scoreEl.textContent = `Score: ${result.score}`;
  const pct = Math.min(100, Math.max(0, ((result.iq - 80) / 70) * 100));
  markerEl.style.left = `${pct}%`;
};

const updateLastAnalytics = (result) => {
  const iqEl = document.getElementById('last-iq');
  const labelEl = document.getElementById('last-label');
  const scoreEl = document.getElementById('last-score');
  if (!iqEl || !labelEl || !scoreEl) return;

  if (!result) {
    iqEl.textContent = 'IQ estimado: --';
    labelEl.textContent = 'Completa el test para ver tu resultado.';
    scoreEl.textContent = 'Score: --';
    return;
  }

  iqEl.textContent = `IQ estimado: ${result.iq}`;
  labelEl.textContent = result.label;
  scoreEl.textContent = `Score: ${result.score}`;
};

const bindStartButton = () => {
  const btn = document.getElementById('start-test-btn');
  if (!btn) return;
  btn.addEventListener('click', () => {
    window.location.href = '/test';
  });
};

const getBlockSize = () => {
  const width = window.innerWidth;
  if (width < 720) return 1;
  if (width < 1024) return 2;
  return 3;
};

const renderBlock = (block, state) => {
  const container = document.getElementById('test-block');
  const nextBtn = document.getElementById('test-next');
  if (!container || !nextBtn) return;

  container.innerHTML = '';
  state.answers = {};
  state.timeouts = {};
  let resolved = 0;

  const updateNext = () => {
    nextBtn.disabled = resolved < block.length;
  };

  block.forEach((item, idx) => {
    const card = document.createElement('div');
    card.className = 'question-card';
    card.dataset.itemId = item.item_id;

    const meta = document.createElement('div');
    meta.className = 'question-meta';
    meta.innerHTML = `<span>Pregunta ${state.answerCount + idx + 1}</span><span>Tiempo: <strong id=\"timer-${item.item_id}\"></strong></span>`;

    const prompt = document.createElement('div');
    prompt.className = 'question-text';
    prompt.textContent = item.prompt;

    const options = document.createElement('div');
    options.className = 'question-options';
    item.options.forEach((opt) => {
      const btn = document.createElement('button');
      btn.className = 'question-option';
      btn.textContent = opt;
      btn.addEventListener('click', () => {
        if (state.answers[item.item_id]) return;
        state.answers[item.item_id] = { answer: opt, timed_out: false };
        btn.classList.add('active');
        options.querySelectorAll('button').forEach((b) => (b.disabled = true));
        clearInterval(state.timeouts[item.item_id]);
        resolved += 1;
        updateNext();
      });
      options.appendChild(btn);
    });

    card.appendChild(meta);
    card.appendChild(prompt);
    card.appendChild(options);
    container.appendChild(card);

    const timerEl = document.getElementById(`timer-${item.item_id}`);
    let remaining = item.time_limit;
    if (timerEl) timerEl.textContent = `${remaining}s`;

    state.timeouts[item.item_id] = setInterval(() => {
      remaining -= 1;
      if (timerEl) timerEl.textContent = `${remaining}s`;
      if (remaining <= 0) {
        clearInterval(state.timeouts[item.item_id]);
        if (!state.answers[item.item_id]) {
          state.answers[item.item_id] = { answer: null, timed_out: true };
          options.querySelectorAll('button').forEach((b) => (b.disabled = true));
          resolved += 1;
          updateNext();
        }
      }
    }, 1000);
  });

  updateNext();
};

const startTestFlow = async () => {
  const screen = document.getElementById('test-screen');
  const complete = document.getElementById('test-complete');
  const progressEl = document.getElementById('test-progress');
  const timerEl = document.getElementById('test-timer');
  const nextBtn = document.getElementById('test-next');
  if (!screen || !complete || !nextBtn) return;

  const blockSize = getBlockSize();
  const startData = await fetchJson(`${IQ_API.start}?block_size=${blockSize}`, {
    method: 'POST'
  });
  if (!startData) return;

  const state = {
    sessionId: startData.session_id,
    total: startData.config.n_items,
    answerCount: 0,
    answers: {},
    timeouts: {}
  };

  localStorage.setItem('iq_session_id', state.sessionId);
  timerEl.textContent = `Bloques de ${blockSize}`;

  const updateProgress = () => {
    progressEl.textContent = `${state.answerCount} de ${state.total}`;
  };

  const handleNext = async () => {
    nextBtn.disabled = true;
    const answers = Object.keys(state.answers).map((itemId) => ({
      item_id: itemId,
      answer: state.answers[itemId].answer,
      timed_out: state.answers[itemId].timed_out
    }));
    state.answerCount += answers.length;
    updateProgress();
    const payload = { session_id: state.sessionId, answers };
    const resp = await fetchJson(IQ_API.answer, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!resp) return;
    if (resp.done) {
      const finish = await fetchJson(IQ_API.finish, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: state.sessionId })
      });
      saveLastResult(finish);
      screen.classList.add('hidden');
      complete.classList.remove('hidden');
      return;
    }
    renderBlock(resp.block, state);
  };

  nextBtn.addEventListener('click', handleNext);
  updateProgress();
  if (!startData.block || startData.block.length === 0) {
    return;
  }
  renderBlock(startData.block, state);
};

const loadData = async () => {
  const [tests, summary, funnel, profiles, dropoff] = await Promise.all([
    fetchJson(API.tests),
    fetchJson(API.summary),
    fetchJson(API.funnel),
    fetchJson(API.profiles),
    fetchJson(API.dropoff)
  ]);

  const testsList = tests?.tests || [];
  updateSummary(summary);
  updateHero(testsList[0]);
  updateTestsTable(testsList);
  initCharts(funnel, profiles, dropoff);
};

document.addEventListener('DOMContentLoaded', () => {
  initReveal();
  setActiveNav();
  bindStartButton();
  const path = window.location.pathname || '/';
  if (path === '/resultado') {
    updateResultView(loadLastResult());
  }
  if (path === '/analitica') {
    updateLastAnalytics(loadLastResult());
  }
  if (path === '/test') {
    startTestFlow();
  }
  loadData();
});
