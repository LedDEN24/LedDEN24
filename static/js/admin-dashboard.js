async function loadAdminStats() {
  const response = await fetch('/platform/api/admin/stats/');
  if (!response.ok) return;
  const stats = await response.json();
  const cards = [
    ['Collected', stats.total_collected], ['Pending', stats.pending_count], ['Donors', stats.donors_count], ['Completed projects', stats.completed_projects]
  ];
  document.getElementById('admin-stat-cards').innerHTML = cards.map(([label, value]) => `<div class="rounded-3xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"><p class="text-sm text-slate-500">${label}</p><p class="mt-2 text-3xl font-black">${value}</p></div>`).join('');
  const ctx = document.getElementById('method-chart');
  if (ctx && window.Chart) new Chart(ctx, { type: 'doughnut', data: { labels: stats.by_method.map(i => i.method), datasets: [{ data: stats.by_method.map(i => i.count), backgroundColor: ['#0f766e', '#1d4ed8', '#f59e0b', '#dc2626', '#7c3aed'] }] } });
}
loadAdminStats();
document.querySelectorAll('[data-approve]').forEach(btn => btn.addEventListener('click', async () => { await fetch(`/api/donations/${btn.dataset.approve}/approve/`, { method: 'POST', headers: { 'X-CSRFToken': document.cookie.split('csrftoken=')[1]?.split(';')[0] || '' } }); location.reload(); }));
document.querySelectorAll('[data-reject]').forEach(btn => btn.addEventListener('click', async () => { await fetch(`/api/donations/${btn.dataset.reject}/reject/`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': document.cookie.split('csrftoken=')[1]?.split(';')[0] || '' }, body: JSON.stringify({ reason: 'Rejected from dashboard' }) }); location.reload(); }));
