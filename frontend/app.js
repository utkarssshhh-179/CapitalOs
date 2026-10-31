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

const formatCurrency = (value) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value ?? 0);

const setStatus = (text, variant = 'neutral') => {
  const statusNode = document.getElementById('status-message');
  statusNode.textContent = text;
  statusNode.className = `status-message ${variant}`;
};

const setConnectionState = (online) => {
  const badge = document.getElementById('connection-status');
  badge.textContent = online ? 'Backend online' : 'Backend offline';
  badge.className = `status-pill ${online ? 'online' : 'offline'}`;
};

const renderSummary = (data) => {
  document.getElementById('organizations').textContent = data.organizations ?? 0;
  document.getElementById('borrowers').textContent = data.borrowers ?? 0;
  document.getElementById('investors').textContent = data.investors ?? 0;
  document.getElementById('loans').textContent = data.loans ?? 0;
  document.getElementById('active-loans').textContent = data.active_loans ?? 0;
  document.getElementById('payments').textContent = data.payments ?? 0;
  document.getElementById('paid-payments').textContent = data.paid_payments ?? 0;
  document.getElementById('total-loan-value').textContent = formatCurrency(data.total_loan_value);
  document.getElementById('total-paid-value').textContent = formatCurrency(data.total_paid_value);
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

document.getElementById('refresh-button').addEventListener('click', refreshDashboard);

hydrateMeta();
loadDashboard();
