const API = {
  tests: '/api/tests',
  summary: '/api/analytics/summary',
  funnel: '/api/analytics/funnel',
  profiles: '/api/analytics/profiles'
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

const initCharts = (funnelData, profileData) => {
  const funnelCtx = document.getElementById('funnelChart');
  const profileCtx = document.getElementById('profileChart');

  if (!funnelCtx || !profileCtx) {
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
    window.location.href = '/test-mixed';
  });
};

const getBlockSize = () => {
  const width = window.innerWidth;
  if (width < 720) return 1;
  if (width < 1024) return 2;
  return 3;
};

const renderPattern = (pattern, variant = 'option') => {
  const wrap = document.createElement('div');
  wrap.className = variant === 'question' ? 'visual-pattern question-visual' : 'visual-pattern';
  if (pattern && pattern.src) {
    const img = document.createElement('img');
    img.src = pattern.src;
    img.alt = pattern.alt || 'pattern';
    wrap.appendChild(img);
  } else {
    const pre = document.createElement('pre');
    pre.textContent = Array.isArray(pattern) ? pattern.join('\n') : String(pattern || '');
    wrap.appendChild(pre);
  }
  return wrap;
};

const renderQuestion = (item, state, onAnswer) => {
  const container = document.getElementById('test-block');
  const progressEl = document.getElementById('test-progress');
  const timerEl = document.getElementById('test-timer');
  if (!container || !progressEl || !timerEl) return;

  // limpiar estado previo
  if (state.activeTimer) clearInterval(state.activeTimer);
  container.innerHTML = '';
  state.currentAnswer = null;
  state.questionDone = false;

  const questionNumber = state.answered + 1;
  progressEl.textContent = `Pregunta ${questionNumber} / ${state.total}`;
  state.questionStart = performance.now();
  state.answerChanges = 0;

  const card = document.createElement('div');
  card.className = 'question-card';
  card.dataset.itemId = item.item_id;

  const meta = document.createElement('div');
  meta.className = 'question-meta';
  meta.innerHTML = `<span>Pregunta ${questionNumber}</span>`;

  const prompt = document.createElement('div');
  prompt.className = 'question-text';
  prompt.textContent = item.prompt;

  const options = document.createElement('div');
  options.className = 'question-options';
  item.options.forEach((opt) => {
    const value = typeof opt === 'string' ? opt : opt.value ?? opt.label ?? JSON.stringify(opt);
    const label = typeof opt === 'string' ? opt : opt.label ?? opt.value ?? '';
    const pattern = typeof opt === 'object' ? opt.pattern : null;
    const image = typeof opt === 'object' ? opt.image : null;

    const btn = document.createElement('button');
    btn.className = 'question-option';
    if (image) {
      btn.appendChild(renderPattern({ src: image, alt: label || 'option' }, 'option'));
    } else if (pattern) {
      btn.appendChild(renderPattern(pattern, 'option'));
    } else {
      btn.textContent = label;
    }
    btn.addEventListener('click', () => {
      if (state.questionDone) return;
      const elapsedMs = performance.now() - state.questionStart;
      const seconds = Math.max(0.1, Math.round(elapsedMs / 1000));
      state.currentAnswer = { item_id: item.item_id, answer: value, timed_out: false, seconds, changes: state.answerChanges };
      btn.classList.add('active');
      options.querySelectorAll('button').forEach((b) => (b.disabled = true));
      if (state.activeTimer) clearInterval(state.activeTimer);
      state.questionDone = true;
      onAnswer(state.currentAnswer);
    });
    options.appendChild(btn);
  });

  card.appendChild(meta);
  if (item.visual && item.visual.base) {
    card.appendChild(renderPattern(item.visual.base, 'question'));
  }
  card.appendChild(prompt);
  card.appendChild(options);
  container.appendChild(card);

  const perQuestionTimer = document.getElementById(`timer-${item.item_id}`);
  let remaining = item.time_limit;
  const updateTimerLabel = () => {
    if (perQuestionTimer) perQuestionTimer.textContent = `${remaining}s`;
    timerEl.textContent = `Tiempo restante: ${remaining}s`;
  };
  updateTimerLabel();

  state.activeTimer = setInterval(() => {
    remaining -= 1;
    updateTimerLabel();
      if (remaining <= 0) {
        clearInterval(state.activeTimer);
        if (state.questionDone) return;
        state.currentAnswer = {
          item_id: item.item_id,
          answer: null,
          timed_out: true,
          seconds: item.time_limit || 0,
          changes: state.answerChanges,
        };
        options.querySelectorAll('button').forEach((b) => (b.disabled = true));
        state.questionDone = true;
        onAnswer(state.currentAnswer);
      }
  }, 1000);
};

const startTestFlow = async () => {
  const screen = document.getElementById('test-screen');
  const complete = document.getElementById('test-complete');
  if (!screen || !complete) return;

  const blockSize = getBlockSize();
  const startData = await fetchJson(`${IQ_API.start}?block_size=${blockSize}`, {
    method: 'POST'
  });
  if (!startData || !startData.block) return;

  const state = {
    sessionId: startData.session_id,
    total: startData.config.n_items,
    answered: 0,
    currentBlock: startData.block,
    blockAnswers: [],
    currentIndex: 0,
    currentAnswer: null,
    activeTimer: null,
    questionDone: false,
    questionStart: performance.now(),
    answerChanges: 0
  };

  localStorage.setItem('iq_session_id', state.sessionId);

  const showCurrentQuestion = () => {
    const current = state.currentBlock[state.currentIndex];
    if (!current) return;
    renderQuestion(current, state, handleAnswer);
  };

  const sendBlockAndLoadNext = async () => {
    const payload = { session_id: state.sessionId, answers: state.blockAnswers };
    const resp = await fetchJson(IQ_API.answer, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!resp) return null;
    return resp;
  };

  const finalizeTest = async () => {
    const finish = await fetchJson(IQ_API.finish, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: state.sessionId })
    });
    saveLastResult(finish);
    screen.classList.add('hidden');
    complete.classList.remove('hidden');
  };

  const handleAnswer = async (answer) => {
    state.blockAnswers.push(answer);
    state.answered += 1;

    if (state.currentIndex < state.currentBlock.length - 1) {
      state.currentIndex += 1;
      showCurrentQuestion();
      return;
    }

    const resp = await sendBlockAndLoadNext();
    if (!resp) return;
    if (resp.done) {
      await finalizeTest();
      return;
    }

    state.currentBlock = resp.block || [];
    state.blockAnswers = [];
    state.currentIndex = 0;
    showCurrentQuestion();
  };

  if (!startData.block.length) return;
  showCurrentQuestion();
};

// Test combinado IQ + Stroop
const startMixedFlow = async () => {
  const screen = document.getElementById('mixed-screen');
  const complete = document.getElementById('mixed-complete');
  if (!screen || !complete) return;
  const startData = await fetchJson('/api/mixed/start', { method: 'POST' });
  if (!startData) return;
  const state = {
    sessionId: startData.session_id,
    current: startData.item,
    total: (startData.total || 16),
    answered: 0
  };
  renderMixedItem(state);
};

const renderMixedItem = (state) => {
  const container = document.getElementById('mixed-block');
  const progress = document.getElementById('mixed-progress');
  if (!container || !progress || !state.current) return;
  container.innerHTML = '';
  progress.textContent = `Item ${state.answered + 1}`;
  if (state.current.kind === 'iq') {
    const card = document.createElement('div');
    card.className = 'question-card';
    const prompt = document.createElement('div');
    prompt.className = 'question-text';
    prompt.textContent = state.current.payload.prompt;
    const opts = document.createElement('div');
    opts.className = 'question-options';
    state.current.payload.options.forEach((opt) => {
      const btn = document.createElement('button');
      btn.className = 'question-option';
      btn.textContent = opt;
      btn.onclick = () => answerMixed(state, opt);
      opts.appendChild(btn);
    });
    card.appendChild(prompt);
    card.appendChild(opts);
    container.appendChild(card);
  } else {
    const card = document.createElement('div');
    card.className = 'question-card';
    const stim = document.createElement('div');
    stim.className = 'stroop-stimulus';
    const inkColor = STROOP_COLOR_MAP[state.current.payload.ink] || state.current.payload.ink;
    stim.innerHTML = `
      <div class="stroop-shape" style="background:${inkColor};"></div>
      <div class="stroop-word" style="color:${inkColor};">${state.current.payload.word}</div>
    `;
    const opts = document.createElement('div');
    opts.className = 'question-options';
    STROOP_COLORS.forEach((c) => {
      const btn = document.createElement('button');
      btn.className = 'question-option';
      btn.style.color = STROOP_COLOR_MAP[c] || '#e2e8f0';
      btn.textContent = c.toUpperCase();
      btn.onclick = () => answerMixed(state, c);
      opts.appendChild(btn);
    });
    card.appendChild(stim);
    card.appendChild(opts);
    container.appendChild(card);
  }
};

const answerMixed = async (state, answer) => {
  state.answered += 1;
  const resp = await fetchJson('/api/mixed/answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: state.sessionId, answer })
  });
  if (!resp) return;
  if (resp.finished) {
    const finish = await fetchJson('/api/mixed/finish', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: state.sessionId })
    });
    if (!finish) return;
    document.getElementById('mixed-score').textContent = `Score combinado: ${finish.score} (IQ ${finish.iq_pct}%, Stroop ${finish.stroop_pct}%)`;
    document.getElementById('mixed-screen').classList.add('hidden');
    document.getElementById('mixed-complete').classList.remove('hidden');
    return;
  }
  if (resp.item) {
    state.current = resp.item;
    renderMixedItem(state);
  }
};

const loadData = async () => {
  const [tests, summary, funnel, profiles] = await Promise.all([
    fetchJson(API.tests),
    fetchJson(API.summary),
    fetchJson(API.funnel),
    fetchJson(API.profiles)
  ]);

  const testsList = tests?.tests || [];
  updateSummary(summary);
  updateHero(testsList[0]);
  updateTestsTable(testsList);
  initCharts(funnel, profiles);
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
    applyCompactLayout();
    startTestFlow();
  }
  if (path === '/stroop') {
    startStroopFlow();
  }
  if (path === '/test-mixed') {
    startMixedFlow();
  }
  loadData();
});

const applyCompactLayout = () => {
  const toggle = () => {
    if (window.innerHeight < 900) {
      document.body.classList.add('test-compact');
    } else {
      document.body.classList.remove('test-compact');
    }
  };
  toggle();
  window.addEventListener('resize', toggle);
};

// Stroop/WCST híbrido
const STROOP_COLORS = ['rojo', 'verde', 'azul', 'amarillo'];
const STROOP_COLOR_MAP = {
  rojo: '#ef4444',
  verde: '#22c55e',
  azul: '#3b82f6',
  amarillo: '#eab308'
};

const startStroopFlow = async () => {
  const screen = document.getElementById('stroop-screen');
  const complete = document.getElementById('stroop-complete');
  if (!screen || !complete) return;
  const startResp = await fetchJson('/api/stroop/start', { method: 'POST' });
  if (!startResp) return;
  const state = {
    sessionId: startResp.session_id,
    currentTrial: startResp.trial,
    trialIndex: 0,
    feedbackEl: document.getElementById('stroop-feedback'),
    progressEl: document.getElementById('stroop-progress'),
    stimEl: document.getElementById('stroop-stimulus'),
    optionsEl: document.getElementById('stroop-options'),
    ruleHintEl: document.getElementById('stroop-rule-hint'),
  };
  renderStroopTrial(state);
  const finishBtn = document.getElementById('stroop-finish');
  finishBtn?.addEventListener('click', () => finishStroop(state, screen, complete));
};

const renderStroopTrial = (state) => {
  if (!state.currentTrial) return;
  state.trialIndex += 1;
  state.progressEl.textContent = `Trial ${state.trialIndex}`;
  state.ruleHintEl.textContent = 'Elegí el color correcto según la regla activa.';
  state.feedbackEl.textContent = 'En curso';
  const { word, ink } = state.currentTrial;
  const inkColor = STROOP_COLOR_MAP[ink] || ink;
  state.stimEl.innerHTML = `
    <div class="stroop-shape" style="background:${inkColor};"></div>
    <div class="stroop-word" style="color:${inkColor};">${word}</div>
  `;
  state.optionsEl.innerHTML = '';
  state.trialStart = performance.now();
  STROOP_COLORS.forEach((color) => {
    const btn = document.createElement('button');
    btn.className = 'btn btn-outline-light stroop-btn';
    btn.textContent = color.toUpperCase();
    btn.style.borderColor = STROOP_COLOR_MAP[color] || '#64748b';
    btn.style.color = STROOP_COLOR_MAP[color] || '#e2e8f0';
    btn.addEventListener('click', () => handleStroopAnswer(state, color));
    state.optionsEl.appendChild(btn);
  });
};

const handleStroopAnswer = async (state, color) => {
  const rt_ms = Math.max(1, Math.round(performance.now() - state.trialStart));
  const payload = { session_id: state.sessionId, answer: color, rt_ms };
  const resp = await fetchJson('/api/stroop/answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!resp) return;
  state.feedbackEl.textContent = resp.correct ? '✅ Correcto' : '❌ Incorrecto';
  if (resp.finished) {
    return finishStroop(state, document.getElementById('stroop-screen'), document.getElementById('stroop-complete'));
  }
  if (resp.next_trial) {
    state.currentTrial = resp.next_trial;
    setTimeout(() => renderStroopTrial(state), 500);
  }
};

const finishStroop = async (state, screen, complete) => {
  const resp = await fetchJson('/api/stroop/finish', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: state.sessionId })
  });
  if (!resp) return;
  screen.classList.add('hidden');
  complete.classList.remove('hidden');
  document.getElementById('stroop-score').textContent = `Score: ${resp.score}`;
  document.getElementById('stroop-profile').textContent = resp.profile;
};
