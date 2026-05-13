const root = document.documentElement;
const storedTheme = localStorage.getItem("theme");
if (storedTheme === "dark" || (!storedTheme && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
  root.classList.add("dark");
}

document.getElementById("theme-toggle")?.addEventListener("click", () => {
  root.classList.toggle("dark");
  localStorage.setItem("theme", root.classList.contains("dark") ? "dark" : "light");
});

const chartCanvas = document.getElementById("donationChart");
if (chartCanvas && window.Chart) {
  const stats = JSON.parse(chartCanvas.dataset.stats || "[]");
  new Chart(chartCanvas, {
    type: "doughnut",
    data: {
      labels: stats.map((item) => item.status),
      datasets: [{ data: stats.map((item) => item.count), backgroundColor: ["#0f766e", "#f59e0b", "#ef4444", "#6366f1"] }],
    },
    options: { plugins: { legend: { position: "bottom" } } },
  });
}

if (window.location.protocol.startsWith("http") && "WebSocket" in window) {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const socket = new WebSocket(`${protocol}://${window.location.host}/ws/notifications/`);
  socket.onmessage = (event) => {
    const payload = JSON.parse(event.data);
    const node = document.createElement("div");
    node.className = "toast fixed right-4 bottom-4 z-50 rounded-2xl bg-slate-950 px-5 py-4 text-white shadow-xl";
    node.innerHTML = `<strong>${payload.title}</strong><p class="text-sm opacity-80">${payload.message}</p>`;
    document.body.appendChild(node);
    setTimeout(() => node.remove(), 6000);
  };
}
