const root = document.documentElement;
const storedTheme = localStorage.getItem('theme');
if (storedTheme === 'dark' || (!storedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) root.classList.add('dark');
document.getElementById('theme-toggle')?.addEventListener('click', () => {
  root.classList.toggle('dark');
  localStorage.setItem('theme', root.classList.contains('dark') ? 'dark' : 'light');
});
function toast(message, type = 'info') {
  const el = document.createElement('div');
  el.className = `rounded-2xl px-4 py-3 text-sm text-white shadow-xl ${type === 'error' ? 'bg-red-600' : 'bg-slate-900'}`;
  el.textContent = message;
  document.getElementById('toast-root')?.appendChild(el);
  setTimeout(() => el.remove(), 4500);
}
const donationForm = document.getElementById('donation-form');
if (donationForm) {
  donationForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(donationForm).entries());
    if (!data.project) delete data.project;
    data.is_anonymous = data.is_anonymous === 'true';
    const response = await fetch('/api/donations/', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '' }, body: JSON.stringify(data) });
    const payload = await response.json();
    const result = document.getElementById('donation-result');
    if (response.ok) { result.textContent = `Donation created: ${payload.public_id}. Status: ${payload.status}`; toast('Donation submitted for verification'); donationForm.reset(); }
    else { result.textContent = JSON.stringify(payload); toast('Donation failed validation', 'error'); }
  });
}
const token = localStorage.getItem('accessToken');
if (token) {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const socket = new WebSocket(`${wsProtocol}://${window.location.host}/ws/notifications/?token=${token}`);
  socket.onmessage = (event) => { const data = JSON.parse(event.data); toast(data.title || 'New notification'); };
}
