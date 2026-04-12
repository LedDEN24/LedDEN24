const highlights = [
  {
    icon: "🪴",
    title: "Комнатные растения",
    text: "Зеленые подарки для дома и офиса с доставкой в фирменной упаковке.",
    badge: "от 2 900 ₽",
  },
  {
    icon: "🍓",
    title: "Цветы + десерт",
    text: "Подарочные наборы с макаронс, клубникой в шоколаде и свечами.",
    badge: "хит вечера",
  },
  {
    icon: "💌",
    title: "Каллиграфия в подарок",
    text: "Напишем открытку от руки, чтобы заказ выглядел персонально и тепло.",
    badge: "бесплатно",
  },
  {
    icon: "🌙",
    title: "Сюрприз после 20:00",
    text: "Вечерние слоты для романтических доставок и неожиданных поздравлений.",
    badge: "слоты онлайн",
  },
];

const categories = [
  {
    id: "all",
    title: "Вся витрина",
    description: "Полный каталог букетов, композиций и подарочных сетов от локальных студий.",
    icon: "✨",
    themeClass: "theme-peach",
  },
  {
    id: "spring",
    title: "Весенние букеты",
    description: "Тюльпаны, пионы, ранункулюсы и свежие пастельные сочетания.",
    icon: "🌷",
    themeClass: "theme-pink",
  },
  {
    id: "gift",
    title: "Цветы + подарок",
    description: "Композиции с десертами, свечами, открытками и наборами для сюрприза.",
    icon: "🎁",
    themeClass: "theme-berry",
  },
  {
    id: "mono",
    title: "Монобукеты",
    description: "Лаконичные решения из одного сорта цветов для стильного жеста.",
    icon: "💐",
    themeClass: "theme-lilac",
  },
  {
    id: "roses",
    title: "Классика с розами",
    description: "Пионовидные, французские и садовые розы в современной подаче.",
    icon: "🌹",
    themeClass: "theme-cream",
  },
  {
    id: "wedding",
    title: "Для событий",
    description: "Композиции для свадеб, камерных праздников и фотосессий.",
    icon: "✨",
    themeClass: "theme-mint",
  },
];

const chipFilters = [
  { id: "all", label: "Все" },
  { id: "bestseller", label: "Бестселлеры" },
  { id: "premium", label: "Премиум" },
  { id: "pastel", label: "Пастельные" },
  { id: "gift-ready", label: "С подарком" },
  { id: "under-7000", label: "До 7 000 ₽" },
];

const products = [
  {
    id: "peony-cloud",
    title: "Peony Cloud",
    shop: "Peony Lab",
    description: "Воздушный букет из пионов, маттиолы и ранункулюсов в сливочно-розовой палитре.",
    composition: "пионы, маттиола, ранункулюс, эвкалипт",
    price: 8900,
    previousPrice: 9900,
    rating: 4.9,
    popularity: 98,
    sameDay: true,
    deliveryMinutes: 75,
    categories: ["spring", "gift"],
    tags: ["Хит дня", "Открытка бесплатно", "Пастель"],
    badge: "Хит недели",
    emoji: "🌸",
    themeClass: "theme-pink",
    palette: "pastel",
    featured: true,
  },
  {
    id: "rose-whisper",
    title: "Rose Whisper",
    shop: "Velvet Petals",
    description: "Пионовидные розы и французская упаковка для романтичного поздравления.",
    composition: "пионовидные розы, лента, упаковка premium",
    price: 5900,
    previousPrice: 6800,
    rating: 4.8,
    popularity: 93,
    sameDay: true,
    deliveryMinutes: 90,
    categories: ["roses", "mono"],
    tags: ["51 стебель", "Классика", "Лента"],
    badge: "Популярный",
    emoji: "🌹",
    themeClass: "theme-cream",
    palette: "classic",
    featured: false,
  },
  {
    id: "morning-sherbet",
    title: "Morning Sherbet",
    shop: "Satin Bloom",
    description: "Нежный микс тюльпанов и диантусов для легкого весеннего сюрприза.",
    composition: "тюльпаны, диантусы, кустовая роза",
    price: 4200,
    previousPrice: 4700,
    rating: 4.7,
    popularity: 88,
    sameDay: false,
    deliveryMinutes: 140,
    categories: ["spring", "mono"],
    tags: ["Легкий букет", "Весна", "Нежные оттенки"],
    badge: "Новая коллекция",
    emoji: "🌷",
    themeClass: "theme-peach",
    palette: "pastel",
    featured: false,
  },
  {
    id: "velvet-box",
    title: "Velvet Bloom Box",
    shop: "Atelier Fleur",
    description: "Шляпная коробка с пионовидными розами, свечой и открыткой ручной работы.",
    composition: "роза, эустома, свеча, открытка, коробка",
    price: 10900,
    previousPrice: 11900,
    rating: 5,
    popularity: 96,
    sameDay: true,
    deliveryMinutes: 80,
    categories: ["gift", "wedding"],
    tags: ["Премиум", "Подарочный сет", "Коробка"],
    badge: "Премиум выбор",
    emoji: "🎀",
    themeClass: "theme-berry",
    palette: "rich",
    featured: true,
  },
  {
    id: "ivory-vow",
    title: "Ivory Vow",
    shop: "Wedding Stem",
    description: "Сдержанный букет в бело-кремовой гамме для камерных церемоний и утренних сборов.",
    composition: "белая роза, эустома, маттиола, шелковая лента",
    price: 7600,
    previousPrice: 8200,
    rating: 4.9,
    popularity: 84,
    sameDay: false,
    deliveryMinutes: 180,
    categories: ["wedding", "mono"],
    tags: ["Свадьба", "Минимализм", "Кремовая палитра"],
    badge: "Для события",
    emoji: "🤍",
    themeClass: "theme-mint",
    palette: "pastel",
    featured: false,
  },
  {
    id: "berry-kiss-set",
    title: "Berry Kiss Set",
    shop: "Sweet Petal Studio",
    description: "Розы, клубника в шоколаде и ароматическая свеча для готового подарочного сценария.",
    composition: "розы, клубника в шоколаде, свеча, карточка",
    price: 6900,
    previousPrice: 7600,
    rating: 4.8,
    popularity: 91,
    sameDay: true,
    deliveryMinutes: 85,
    categories: ["gift", "roses"],
    tags: ["С подарком", "Десерт", "Романтика"],
    badge: "Подарочный сет",
    emoji: "🍓",
    themeClass: "theme-pink",
    palette: "rich",
    featured: false,
  },
  {
    id: "cloud-minimal",
    title: "Cloud Minimal",
    shop: "Mono Muse",
    description: "Стильный монобукет из белых тюльпанов в матовой упаковке.",
    composition: "белые тюльпаны, матовая пленка, лента",
    price: 3500,
    previousPrice: 3900,
    rating: 4.6,
    popularity: 77,
    sameDay: true,
    deliveryMinutes: 60,
    categories: ["mono", "spring"],
    tags: ["До 5 000 ₽", "Минимализм", "Срочно"],
    badge: "Быстрая доставка",
    emoji: "☁️",
    themeClass: "theme-lilac",
    palette: "pastel",
    featured: false,
  },
  {
    id: "garden-ceremony",
    title: "Garden Ceremony",
    shop: "Atelier Fleur",
    description: "Большая композиция для свадебного ужина или домашнего события с wow-эффектом.",
    composition: "гортензия, розы, дельфиниум, сезонная зелень",
    price: 14900,
    previousPrice: 15900,
    rating: 5,
    popularity: 89,
    sameDay: false,
    deliveryMinutes: 210,
    categories: ["wedding", "gift"],
    tags: ["Премиум", "Большой формат", "Для события"],
    badge: "Luxury",
    emoji: "🏛️",
    themeClass: "theme-peach",
    palette: "classic",
    featured: true,
  },
];

const shops = [
  {
    id: "atelier-fleur",
    name: "Atelier Fleur",
    tagline: "Премиальные коробки и свадебные композиции",
    description: "Собирают сложные композиции в фирменной стилистике, добавляют свечи и десерты.",
    rating: 5,
    orders: "2 140 заказов",
    delivery: "от 80 минут",
    avatar: "AF",
    themeClass: "theme-berry",
  },
  {
    id: "peony-lab",
    name: "Peony Lab",
    tagline: "Пастельные букеты и пионовидные розы",
    description: "Специализируются на воздушных монобукетах, открытках от руки и нежной упаковке.",
    rating: 4.9,
    orders: "1 860 заказов",
    delivery: "от 75 минут",
    avatar: "PL",
    themeClass: "theme-pink",
  },
  {
    id: "mono-muse",
    name: "Mono Muse",
    tagline: "Минималистичные букеты на каждый день",
    description: "Лаконичная подача, быстрые слоты и моносоставы без визуального шума.",
    rating: 4.8,
    orders: "930 заказов",
    delivery: "от 60 минут",
    avatar: "MM",
    themeClass: "theme-lilac",
  },
];

const reviews = [
  {
    author: "Марина, Москва",
    title: "Букет оказался даже красивее фото",
    text: "Заказала сюрприз на вечер и получила фото перед отправкой. Очень удобно, что можно сразу добавить десерт и открытку.",
    avatar: "М",
  },
  {
    author: "Илья, Казань",
    title: "Собрали готовый подарок за пару минут",
    text: "Фильтры по категориям реально помогают. Выбрал набор с розами и клубникой, и все приехало аккуратно упакованным.",
    avatar: "И",
  },
  {
    author: "Екатерина, Санкт-Петербург",
    title: "Отличный сервис для маленькой свадьбы",
    text: "Нашли стильный букет и коробку для welcome-зоны в одном месте. Очень понравилась витрина локальных флористов.",
    avatar: "Е",
  },
];

const deliveryFees = {
  today: 490,
  morning: 690,
  surprise: 390,
};

const state = {
  selectedCategory: "all",
  activeChip: "all",
  sameDayOnly: false,
  sort: "popular",
  search: "",
  deliveryMode: "today",
  cart: new Map(),
  favorites: new Set(),
};

const elements = {
  heroSpotlight: document.querySelector("#heroSpotlight"),
  storyButtons: document.querySelector("#storyButtons"),
  categoryGrid: document.querySelector("#categoryGrid"),
  chipFilters: document.querySelector("#chipFilters"),
  productGrid: document.querySelector("#productGrid"),
  shopGrid: document.querySelector("#shopGrid"),
  reviewGrid: document.querySelector("#reviewGrid"),
  cartItems: document.querySelector("#cartItems"),
  catalogSummary: document.querySelector("#catalogSummary"),
  searchInput: document.querySelector("#searchInput"),
  sameDayToggle: document.querySelector("#sameDayToggle"),
  sortSelect: document.querySelector("#sortSelect"),
  cartCount: document.querySelector("#cartCount"),
  subtotalValue: document.querySelector("#subtotalValue"),
  deliveryValue: document.querySelector("#deliveryValue"),
  serviceValue: document.querySelector("#serviceValue"),
  totalValue: document.querySelector("#totalValue"),
  deliveryButtons: Array.from(document.querySelectorAll(".delivery-option")),
};

function formatPrice(value) {
  return `${new Intl.NumberFormat("ru-RU").format(value)} ₽`;
}

function pluralize(count, one, few, many) {
  const mod10 = count % 10;
  const mod100 = count % 100;

  if (mod10 === 1 && mod100 !== 11) {
    return one;
  }

  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) {
    return few;
  }

  return many;
}

function getProductById(id) {
  return products.find((product) => product.id === id);
}

function getSelectedCategoryTitle() {
  return categories.find((category) => category.id === state.selectedCategory)?.title || "Вся витрина";
}

function matchesChipFilter(product) {
  switch (state.activeChip) {
    case "bestseller":
      return product.popularity >= 90;
    case "premium":
      return product.price >= 8000;
    case "pastel":
      return product.palette === "pastel";
    case "gift-ready":
      return product.categories.includes("gift") || product.tags.some((tag) => tag.includes("подар"));
    case "under-7000":
      return product.price <= 7000;
    default:
      return true;
  }
}

function getVisibleProducts() {
  const query = state.search.trim().toLowerCase();

  return products
    .filter((product) => {
      const matchesCategory =
        state.selectedCategory === "all" || product.categories.includes(state.selectedCategory);
      const matchesSearch =
        !query ||
        [product.title, product.shop, product.description, product.composition, ...product.tags]
          .join(" ")
          .toLowerCase()
          .includes(query);
      const matchesSameDay = !state.sameDayOnly || product.sameDay;

      return matchesCategory && matchesSearch && matchesSameDay && matchesChipFilter(product);
    })
    .sort((left, right) => {
      switch (state.sort) {
        case "priceAsc":
          return left.price - right.price;
        case "priceDesc":
          return right.price - left.price;
        case "rating":
          return right.rating - left.rating || right.popularity - left.popularity;
        default:
          return right.popularity - left.popularity;
      }
    });
}

function renderHeroSpotlight() {
  elements.heroSpotlight.innerHTML = highlights
    .map(
      (item) => `
        <article class="hero-mini-card">
          <div class="hero-mini-card__top">
            <div class="hero-mini-card__icon">${item.icon}</div>
            <span class="product-card__badge">${item.badge}</span>
          </div>
          <div>
            <h3>${item.title}</h3>
            <p>${item.text}</p>
          </div>
        </article>
      `
    )
    .join("");
}

function renderCategories() {
  elements.categoryGrid.innerHTML = categories
    .map(
      (category) => `
        <button
          class="category-card ${category.id === state.selectedCategory ? "is-active" : ""}"
          data-category="${category.id}"
          type="button"
          aria-pressed="${String(category.id === state.selectedCategory)}"
        >
          <div class="category-card__icon ${category.themeClass}">${category.icon}</div>
          <h3>${category.title}</h3>
          <p>${category.description}</p>
        </button>
      `
    )
    .join("");

  Array.from(elements.storyButtons.querySelectorAll(".story-card")).forEach((button) => {
    button.classList.toggle("is-active", button.dataset.category === state.selectedCategory);
    button.setAttribute("aria-pressed", String(button.dataset.category === state.selectedCategory));
  });
}

function renderChipFilters() {
  elements.chipFilters.innerHTML = chipFilters
    .map(
      (chip) => `
        <button
          class="chip ${chip.id === state.activeChip ? "is-active" : ""}"
          data-chip="${chip.id}"
          type="button"
          aria-pressed="${String(chip.id === state.activeChip)}"
        >
          ${chip.label}
        </button>
      `
    )
    .join("");
}

function renderProducts() {
  const visibleProducts = getVisibleProducts();
  const sameDayCount = visibleProducts.filter((product) => product.sameDay).length;
  const categoryTitle = getSelectedCategoryTitle();

  elements.catalogSummary.textContent = `${visibleProducts.length} ${pluralize(
    visibleProducts.length,
    "вариант",
    "варианта",
    "вариантов"
  )} в категории "${categoryTitle}". ${sameDayCount} доступны для доставки сегодня.`;

  if (!visibleProducts.length) {
    elements.productGrid.innerHTML = `
      <div class="empty-state">
        <strong>Ничего не найдено.</strong>
        <p>Попробуйте очистить поиск или переключиться на другую категорию.</p>
      </div>
    `;
    return;
  }

  elements.productGrid.innerHTML = visibleProducts
    .map((product) => {
      const inCartQuantity = state.cart.get(product.id) || 0;
      const isFavorite = state.favorites.has(product.id);
      const deliveryLabel = product.sameDay
        ? `Доставка ${product.deliveryMinutes} мин`
        : `Под заказ ${product.deliveryMinutes} мин`;

      return `
        <article class="product-card">
          <div class="product-card__visual ${product.themeClass}">
            <span class="product-card__badge">${product.badge}</span>
            <button
              class="wishlist-button ${isFavorite ? "is-active" : ""}"
              data-favorite-product="${product.id}"
              type="button"
              aria-label="${isFavorite ? "Убрать из избранного" : "Добавить в избранное"}"
            >
              ♥
            </button>
            <div class="product-card__emoji">${product.emoji}</div>
          </div>
          <div class="product-card__content">
            <div class="product-card__header">
              <div>
                <h3>${product.title}</h3>
                <p class="product-card__vendor">${product.shop}</p>
              </div>
              <span class="product-card__rating">★ ${product.rating.toFixed(1)}</span>
            </div>
            <p class="product-card__meta">${product.description}</p>
            <div class="product-card__tags">
              ${product.tags.map((tag) => `<span class="product-card__tag">${tag}</span>`).join("")}
              <span class="product-card__tag">${deliveryLabel}</span>
            </div>
            <div class="product-card__footer">
              <div class="product-card__price">
                <strong>${formatPrice(product.price)}</strong>
                <span>${formatPrice(product.previousPrice)}</span>
              </div>
              <button class="product-card__button" data-add-product="${product.id}" type="button">
                ${inCartQuantity ? `Добавить еще (${inCartQuantity})` : "В корзину"}
              </button>
            </div>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderShops() {
  elements.shopGrid.innerHTML = shops
    .map(
      (shop) => `
        <article class="shop-card">
          <div class="shop-card__header">
            <div class="shop-card__topline">
              <div class="shop-card__avatar ${shop.themeClass}">${shop.avatar}</div>
              <div>
                <h3>${shop.name}</h3>
                <p>${shop.tagline}</p>
              </div>
            </div>
            <span class="product-card__rating">★ ${shop.rating.toFixed(1)}</span>
          </div>
          <p>${shop.description}</p>
          <div class="shop-card__metrics">
            <span class="shop-card__metric">${shop.orders}</span>
            <span class="shop-card__metric">${shop.delivery}</span>
          </div>
          <button class="shop-card__button" data-shop-name="${shop.name}" type="button">
            Смотреть витрину магазина
          </button>
        </article>
      `
    )
    .join("");
}

function renderReviews() {
  elements.reviewGrid.innerHTML = reviews
    .map(
      (review) => `
        <article class="review-card">
          <div class="review-card__header">
            <div class="review-card__author">
              <div class="review-card__avatar">${review.avatar}</div>
              <div>
                <h3>${review.title}</h3>
                <p>${review.author}</p>
              </div>
            </div>
            <span class="product-card__rating">5.0</span>
          </div>
          <blockquote>${review.text}</blockquote>
        </article>
      `
    )
    .join("");
}

function getCartEntries() {
  return Array.from(state.cart.entries())
    .map(([productId, quantity]) => {
      const product = getProductById(productId);
      return product ? { product, quantity } : null;
    })
    .filter(Boolean);
}

function renderCart() {
  const entries = getCartEntries();
  const itemCount = entries.reduce((sum, entry) => sum + entry.quantity, 0);
  const subtotal = entries.reduce((sum, entry) => sum + entry.product.price * entry.quantity, 0);
  const delivery = itemCount ? deliveryFees[state.deliveryMode] : 0;
  const service = itemCount ? 190 : 0;
  const total = subtotal + delivery + service;

  elements.cartCount.textContent = `${itemCount} ${pluralize(itemCount, "позиция", "позиции", "позиций")}`;
  elements.subtotalValue.textContent = formatPrice(subtotal);
  elements.deliveryValue.textContent = formatPrice(delivery);
  elements.serviceValue.textContent = formatPrice(service);
  elements.totalValue.textContent = formatPrice(total);

  if (!entries.length) {
    elements.cartItems.innerHTML = `
      <div class="empty-state">
        <strong>Корзина пока пустая.</strong>
        <p>Добавьте букет или подарочный набор, чтобы увидеть итог заказа.</p>
      </div>
    `;
    return;
  }

  elements.cartItems.innerHTML = entries
    .map(
      ({ product, quantity }) => `
        <article class="cart-item">
          <div class="cart-item__top">
            <div>
              <h3 class="cart-item__name">${product.title}</h3>
              <p class="cart-item__meta">${product.shop} · ${product.sameDay ? "доставка сегодня" : "под заказ"}</p>
            </div>
            <strong>${formatPrice(product.price * quantity)}</strong>
          </div>
          <div class="cart-item__controls">
            <div class="cart-item__counter">
              <button class="cart-item__step" data-cart-action="decrease" data-id="${product.id}" type="button">−</button>
              <strong>${quantity}</strong>
              <button class="cart-item__step" data-cart-action="increase" data-id="${product.id}" type="button">+</button>
            </div>
            <button class="cart-item__action" data-cart-action="remove" data-id="${product.id}" type="button">
              Удалить
            </button>
          </div>
        </article>
      `
    )
    .join("");
}

function renderAll() {
  renderCategories();
  renderChipFilters();
  renderProducts();
  renderCart();
}

function setCategory(categoryId) {
  state.selectedCategory = categoryId;
  renderAll();
}

function toggleFavorite(productId) {
  if (state.favorites.has(productId)) {
    state.favorites.delete(productId);
  } else {
    state.favorites.add(productId);
  }

  renderProducts();
}

function addToCart(productId) {
  const currentQuantity = state.cart.get(productId) || 0;
  state.cart.set(productId, currentQuantity + 1);
  renderProducts();
  renderCart();
}

function updateCartQuantity(productId, change) {
  const currentQuantity = state.cart.get(productId) || 0;
  const nextQuantity = currentQuantity + change;

  if (nextQuantity <= 0) {
    state.cart.delete(productId);
  } else {
    state.cart.set(productId, nextQuantity);
  }

  renderProducts();
  renderCart();
}

function setDeliveryMode(mode) {
  state.deliveryMode = mode;
  elements.deliveryButtons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.delivery === mode);
  });
  renderCart();
}

function bindEvents() {
  elements.storyButtons.addEventListener("click", (event) => {
    const button = event.target.closest("[data-category]");
    if (!button) {
      return;
    }

    setCategory(button.dataset.category);
    document.querySelector("#catalog").scrollIntoView({ behavior: "smooth", block: "start" });
  });

  elements.categoryGrid.addEventListener("click", (event) => {
    const button = event.target.closest("[data-category]");
    if (!button) {
      return;
    }

    setCategory(button.dataset.category);
  });

  elements.chipFilters.addEventListener("click", (event) => {
    const button = event.target.closest("[data-chip]");
    if (!button) {
      return;
    }

    state.activeChip = button.dataset.chip;
    renderAll();
  });

  elements.productGrid.addEventListener("click", (event) => {
    const favoriteButton = event.target.closest("[data-favorite-product]");
    if (favoriteButton) {
      toggleFavorite(favoriteButton.dataset.favoriteProduct);
      return;
    }

    const addButton = event.target.closest("[data-add-product]");
    if (addButton) {
      addToCart(addButton.dataset.addProduct);
    }
  });

  elements.shopGrid.addEventListener("click", (event) => {
    const button = event.target.closest("[data-shop-name]");
    if (!button) {
      return;
    }

    state.search = button.dataset.shopName;
    elements.searchInput.value = button.dataset.shopName;
    renderAll();
    document.querySelector("#catalog").scrollIntoView({ behavior: "smooth", block: "start" });
  });

  elements.cartItems.addEventListener("click", (event) => {
    const actionButton = event.target.closest("[data-cart-action]");
    if (!actionButton) {
      return;
    }

    const { id, cartAction } = actionButton.dataset;

    if (cartAction === "remove") {
      state.cart.delete(id);
    } else if (cartAction === "increase") {
      updateCartQuantity(id, 1);
      return;
    } else if (cartAction === "decrease") {
      updateCartQuantity(id, -1);
      return;
    }

    renderProducts();
    renderCart();
  });

  elements.searchInput.addEventListener("input", (event) => {
    state.search = event.target.value;
    renderProducts();
  });

  elements.sameDayToggle.addEventListener("click", () => {
    state.sameDayOnly = !state.sameDayOnly;
    elements.sameDayToggle.classList.toggle("is-active", state.sameDayOnly);
    elements.sameDayToggle.setAttribute("aria-pressed", String(state.sameDayOnly));
    renderProducts();
  });

  elements.sortSelect.addEventListener("change", (event) => {
    state.sort = event.target.value;
    renderProducts();
  });

  elements.deliveryButtons.forEach((button) => {
    button.addEventListener("click", () => {
      setDeliveryMode(button.dataset.delivery);
    });
  });
}

function init() {
  renderHeroSpotlight();
  renderShops();
  renderReviews();
  renderAll();
  bindEvents();
  setDeliveryMode(state.deliveryMode);
}

init();
