const API_BASE = 'http://localhost:8000/api/v1';

const fallbackData = {
  organizations: 12,
  borrowers: 146,
  investors: 38,
  loans: 84,
  active_loans: 59,
  payments: 318,
  paid_payments: 206,
  total_loan_value: 12450000,
  total_paid_value: 8540000,
};

const demoPortfolio = [38, 52, 45, 60, 63, 72];

const demoBorrowers = [
  { name: 'Ava Patel', segment: 'prime', risk: 'low', balance: 255000, status: 'active' },
  { name: 'Noah Chen', segment: 'professional', risk: 'medium', balance: 430000, status: 'watchlist' },
  { name: 'Mila Rodriguez', segment: 'consumer', risk: 'medium', balance: 190000, status: 'active' },
  { name: 'Leo Carter', segment: 'prime', risk: 'low', balance: 610000, status: 'active' },
  { name: 'Sofia Martin', segment: 'smaller', risk: 'high', balance: 280000, status: 'watchlist' },
];

const demoLoans = [
  { id: 'LN-1024', borrower: 'Ava Patel', amount: 350000, rate: 9.4, dueDate: '2026-11-18', status: 'active' },
  { id: 'LN-1048', borrower: 'Noah Chen', amount: 520000, rate: 11.6, dueDate: '2026-11-21', status: 'approved' },
  { id: 'LN-1088', borrower: 'Mila Rodriguez', amount: 210000, rate: 12.9, dueDate: '2026-11-26', status: 'delinquent' },
  { id: 'LN-0981', borrower: 'Leo Carter', amount: 720000, rate: 8.7, dueDate: '2026-12-02', status: 'active' },
  { id: 'LN-1163', borrower: 'Sofia Martin', amount: 260000, rate: 14.1, dueDate: '2026-12-09', status: 'approved' },
];

const demoCollections = [
  { name: 'Ariana Singh', amount: 48000, due: '3 days overdue', owner: 'Collections team A' },
  { name: 'Benjamin Lee', amount: 62000, due: '5 days overdue', owner: 'Collections team B' },
  { name: 'Emily Johnson', amount: 35000, due: '1 day overdue', owner: 'Collections team A' },
];

const demoReports = [
  { label: 'Portfolio yield', value: '12.4%', detail: 'vs 11.1% last quarter' },
  { label: 'NPL ratio', value: '2.3%', detail: 'Healthy underwriting mix' },
  { label: 'Collections recovery', value: '88%', detail: 'Recovered over 30 days' },
];

const state = {
  currentView: 'overview',
  borrowerFilter: 'all',
  loanFilter: 'all',
  demoMode: false,
  searchTerm: '',
  isAuthenticated: false,
};

const formatCurrency = (value) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value ?? 0);

const formatCompactCurrency = (value) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(value ?? 0);

const setStatus = (text, variant = 'neutral') => {
  const statusNode = document.getElementById('status-message');
  if (!statusNode) return;
  statusNode.textContent = text;
  statusNode.className = `status-message ${variant}`;
};

const setConnectionState = (online) => {
  const badge = document.getElementById('connection-status');
  if (!badge) return;
  badge.textContent = online ? 'Backend online' : 'Backend offline';
  badge.className = `status-pill ${online ? 'online' : 'offline'}`;
};

const renderSummary = (data) => {
  const summary = { ...fallbackData, ...(data || {}) };
  document.getElementById('organizations').textContent = summary.organizations ?? 0;
  document.getElementById('borrowers').textContent = summary.borrowers ?? 0;
  document.getElementById('investors').textContent = summary.investors ?? 0;
  document.getElementById('loans').textContent = summary.loans ?? 0;
  document.getElementById('active-loans').textContent = summary.active_loans ?? 0;
  document.getElementById('payments').textContent = summary.payments ?? 0;
  document.getElementById('paid-payments').textContent = summary.paid_payments ?? 0;
  document.getElementById('total-loan-value').textContent = formatCurrency(summary.total_loan_value);
  document.getElementById('total-paid-value').textContent = formatCurrency(summary.total_paid_value);
  document.getElementById('page-heading').textContent = state.currentView === 'overview' ? 'Portfolio overview' : 'Portfolio overview';
};

const renderBars = (values) => {
  const container = document.getElementById('portfolio-bars');
  if (!container) return;
  container.innerHTML = values
    .map((value, index) => {
      const month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'][index] || 'M';
      return `
        <div class="bar-box">
          <div class="bar" title="${month}: $${value}M" style="height:${value}%"></div>
        </div>
      `;
    })
    .join('');
};

const renderBorrowers = () => {
  const tbody = document.getElementById('borrowers-table-body');
  if (!tbody) return;

  const filtered = demoBorrowers.filter((borrower) => {
    const matchesStatus = state.borrowerFilter === 'all' || borrower.status === state.borrowerFilter;
    const query = state.searchTerm.trim().toLowerCase();
    const matchesSearch =
      !query ||
      borrower.name.toLowerCase().includes(query) ||
      borrower.segment.toLowerCase().includes(query) ||
      borrower.status.toLowerCase().includes(query);

    return matchesStatus && matchesSearch;
  });

  tbody.innerHTML = filtered
    .map(
      (borrower) => `
        <tr>
          <td><strong>${borrower.name}</strong></td>
          <td><span class="segment-badge ${borrower.segment}">${borrower.segment}</span></td>
          <td><span class="risk-badge ${borrower.risk}">${borrower.risk}</span></td>
          <td>${formatCompactCurrency(borrower.balance)}</td>
          <td><span class="status-badge ${borrower.status}">${borrower.status}</span></td>
        </tr>
      `
    )
    .join('');
};

const renderLoans = () => {
  const tbody = document.getElementById('loans-table-body');
  if (!tbody) return;

  const filtered = demoLoans.filter((loan) => {
    const matchesStatus = state.loanFilter === 'all' || loan.status === state.loanFilter;
    const query = state.searchTerm.trim().toLowerCase();
    const matchesSearch =
      !query ||
      loan.id.toLowerCase().includes(query) ||
      loan.borrower.toLowerCase().includes(query) ||
      loan.status.toLowerCase().includes(query);

    return matchesStatus && matchesSearch;
  });

  tbody.innerHTML = filtered
    .map(
      (loan) => `
        <tr>
          <td><strong>${loan.id}</strong></td>
          <td>${loan.borrower}</td>
          <td>${formatCurrency(loan.amount)}</td>
          <td>${loan.rate}%</td>
          <td>${loan.dueDate}</td>
          <td><span class="status-badge ${loan.status}">${loan.status}</span></td>
        </tr>
      `
    )
    .join('');
};

const renderCollections = () => {
  const list = document.getElementById('collections-list');
  const focus = document.getElementById('collections-focus');
  if (!list || !focus) return;

  list.innerHTML = demoCollections
    .map(
      (item) => `
        <div class="collection-item">
          <strong>${item.name}</strong>
          <span>${item.due}</span>
          <span>${formatCurrency(item.amount)}</span>
          <small>${item.owner}</small>
        </div>
      `
    )
    .join('');

  focus.innerHTML = [
    { label: 'High priority', value: '12 cases' },
    { label: 'Recovery rate', value: '88%' },
    { label: 'Escalations', value: '5 today' },
  ]
    .map(
      (item) => `
        <div class="focus-item">
          <span>${item.label}</span>
          <strong>${item.value}</strong>
        </div>
      `
    )
    .join('');
};

const renderReports = () => {
  const grid = document.getElementById('reports-grid');
  if (!grid) return;

  grid.innerHTML = demoReports
    .map(
      (report) => `
        <article class="report-card">
          <span>${report.label}</span>
          <strong>${report.value}</strong>
          <small>${report.detail}</small>
        </article>
      `
    )
    .join('');
};

const showView = (viewName) => {
  state.currentView = viewName;
  document.querySelectorAll('.nav-item').forEach((button) => {
    button.classList.toggle('active', button.dataset.view === viewName);
  });

  document.querySelectorAll('.view').forEach((section) => {
    const isVisible = section.id === `${viewName}-view` || (viewName === 'overview' && section.id === 'overview-view-details');
    section.classList.toggle('visible', isVisible);
  });

  const headings = {
    overview: 'Portfolio overview',
    borrowers: 'Borrower pipeline',
    loans: 'Loan operations',
    collections: 'Collections center',
    reports: 'Executive reports',
    settings: 'Platform settings',
  };

  document.getElementById('page-heading').textContent = headings[viewName] || 'Portfolio overview';
};

const loadDashboard = async () => {
  try {
    const response = await fetch(`${API_BASE}/dashboard`);
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    const data = await response.json();
    renderSummary(data);
    setConnectionState(true);
    setStatus(
      `CapitalOS is connected to the backend. Current portfolio snapshot: ${data.active_loans ?? 0} active loans across ${data.organizations ?? 0} organizations.`,
      'success'
    );
  } catch (error) {
    console.error(error);
    renderSummary(fallbackData);
    setConnectionState(false);
    setStatus(
      'Backend unavailable. Showing demo values until the API is running on http://localhost:8000.',
      'error'
    );
  }
};

const checkApiHealth = async () => {
  try {
    const response = await fetch(`${API_BASE}/health/live`);
    if (response.ok) {
      const payload = await response.json();
      return payload.version || 'unknown';
    }
  } catch (error) {
    console.error('Health check failed', error);
  }

  return 'offline';
};

const hydrateMeta = async () => {
  const version = await checkApiHealth();
  if (version !== 'offline') {
    setStatus(`CapitalOS backend is online. API version ${version}.`, 'success');
  }
};

const refreshDashboard = async () => {
  await hydrateMeta();
  await loadDashboard();
};

const bindNav = () => {
  document.querySelectorAll('.nav-item').forEach((button) => {
    button.addEventListener('click', () => showView(button.dataset.view));
  });
};

const bindFilterButtons = () => {
  document.querySelectorAll('[data-borrower-filter]').forEach((button) => {
    button.addEventListener('click', () => {
      state.borrowerFilter = button.dataset.borrowerFilter;
      document.querySelectorAll('[data-borrower-filter]').forEach((el) => el.classList.toggle('active', el === button));
      renderBorrowers();
    });
  });

  document.querySelectorAll('[data-loan-filter]').forEach((button) => {
    button.addEventListener('click', () => {
      state.loanFilter = button.dataset.loanFilter;
      document.querySelectorAll('[data-loan-filter]').forEach((el) => el.classList.toggle('active', el === button));
      renderLoans();
    });
  });
};

const bindSearch = () => {
  const input = document.getElementById('global-search');
  input.addEventListener('input', (event) => {
    state.searchTerm = event.target.value;
    renderBorrowers();
    renderLoans();
  });
};

const showToast = (message) => {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('show');
  clearTimeout(showToast.timeoutId);
  showToast.timeoutId = setTimeout(() => toast.classList.remove('show'), 2200);
};

const bindModal = () => {
  const modal = document.getElementById('loan-modal');
  const openBtn = document.getElementById('create-loan-btn');
  const closeBtn = document.getElementById('close-modal-btn');
  const form = document.getElementById('loan-form');

  const toggleModal = (isOpen) => {
    modal.classList.toggle('open', isOpen);
    modal.setAttribute('aria-hidden', String(!isOpen));
  };

  openBtn.addEventListener('click', () => toggleModal(true));
  closeBtn.addEventListener('click', () => toggleModal(false));
  modal.addEventListener('click', (event) => {
    if (event.target === modal) toggleModal(false);
  });

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const borrower = formData.get('borrower');
    const amount = Number(formData.get('amount'));
    const rate = Number(formData.get('rate'));
    const dueDate = formData.get('dueDate');

    demoLoans.unshift({
      id: `LN-${Math.floor(Math.random() * 9000 + 1000)}`,
      borrower: String(borrower),
      amount,
      rate,
      dueDate: String(dueDate),
      status: 'approved',
    });

    toggleModal(false);
    form.reset();
    renderLoans();
    setStatus(`New loan request for ${borrower} created and routed for approval.`, 'success');
    showToast('Loan request created');
  });
};

const bindAuthFlow = () => {
  const authShell = document.getElementById('auth-shell');
  const appShell = document.getElementById('app-shell');
  const loginForm = document.getElementById('login-form');
  const logoutButton = document.getElementById('logout-button');

  const revealApp = () => {
    state.isAuthenticated = true;
    authShell.classList.add('hidden');
    appShell.classList.remove('hidden');
    showToast('Welcome back to CapitalOS');
  };

  const hideApp = () => {
    state.isAuthenticated = false;
    appShell.classList.add('hidden');
    authShell.classList.remove('hidden');
    showToast('Logged out');
  };

  loginForm.addEventListener('submit', (event) => {
    event.preventDefault();
    revealApp();
  });

  logoutButton.addEventListener('click', hideApp);
  if (!state.isAuthenticated) {
    appShell.classList.add('hidden');
    authShell.classList.remove('hidden');
  }
};

const bindDemoToggle = () => {
  const button = document.getElementById('demo-mode-toggle');
  button.addEventListener('click', () => {
    state.demoMode = !state.demoMode;
    button.textContent = state.demoMode ? 'Live mode' : 'Demo mode';
    renderSummary(state.demoMode ? fallbackData : fallbackData);
    setStatus(
      state.demoMode
        ? 'Demo mode is active; using curated portfolio values.'
        : 'Live mode is active; attempting to fetch backend data.',
      state.demoMode ? 'neutral' : 'success'
    );
  });
};

document.getElementById('refresh-button')?.addEventListener('click', refreshDashboard);

bindNav();
bindFilterButtons();
bindSearch();
bindModal();
bindAuthFlow();
bindDemoToggle();
renderBars(demoPortfolio);
renderBorrowers();
renderLoans();
renderCollections();
renderReports();
showView('overview');
hydrateMeta();
loadDashboard();
