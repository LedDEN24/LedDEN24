(function () {
  const root = document.querySelector('[data-search]');
  if (!root) return;

  const input = root.querySelector('.mp-search__input');
  const dropdown = root.querySelector('.mp-search__dropdown');

  let timer = null;
  let last = '';

  function hide() {
    dropdown.hidden = true;
    dropdown.innerHTML = '';
  }

  function show() {
    dropdown.hidden = false;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) => (
      {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
      }[c]
    ));
  }

  async function run(q) {
    const url = `/api/search/?q=${encodeURIComponent(q)}&limit=8`;
    const r = await fetch(url, { headers: { 'X-Requested-With': 'fetch' } });
    const data = await r.json();

    // если пользователь успел изменить ввод — не перерисовываем
    if ((data.q || '').trim() !== input.value.trim()) return;

    const items = data.items || [];
    if (!items.length) {
      hide();
      return;
    }

    dropdown.innerHTML = items.map((p) => {
      const badges = [
        p.is_hit ? '<span class="mp-badge">🔥 Хит</span>' : '',
        p.is_new ? '<span class="mp-badge">🆕 Новый</span>' : '',
      ].join('');

      const img = p.img ? `<img class="mp-item__img" src="${p.img}" alt="">` : '<div class="mp-item__img mp-item__img--empty"></div>';

      const sub = `${escapeHtml(p.category || '')}${p.category ? ' • ' : ''}${p.price} ₽${p.in_stock ? '' : ' • нет в наличии'}`;

      return `
        <a class="mp-item" href="${p.url}">
          ${img}
          <div class="mp-item__meta">
            <div class="mp-item__title">${escapeHtml(p.title)}</div>
            <div class="mp-item__sub">${sub}</div>
          </div>
          <div class="mp-badges">${badges}</div>
        </a>
      `;
    }).join('');

    show();
  }

  input.addEventListener('input', () => {
    const q = input.value.trim();
    if (q === last) return;
    last = q;

    clearTimeout(timer);
    if (q.length < 2) {
      hide();
      return;
    }
    timer = setTimeout(() => run(q), 180);
  });

  document.addEventListener('click', (e) => {
    if (!root.contains(e.target)) hide();
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const q = input.value.trim();
      if (q.length >= 2) {
        window.location.href = `/search/?q=${encodeURIComponent(q)}`;
      }
    }
  });
})();
