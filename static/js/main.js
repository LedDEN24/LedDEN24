(function () {
  const btn = document.querySelector(".nav-toggle");
  const mainNav = document.querySelector(".main-nav");
  const cartCounters = Array.from(document.querySelectorAll("[data-cart-count]"));
  const cartToast = document.querySelector("[data-cart-toast]");
  let toastTimer = null;

  if (btn) {
    btn.addEventListener("click", () => {
      document.body.classList.toggle("nav-open");
      btn.classList.toggle("is-active");
    });
  }

  if (mainNav) {
    mainNav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        document.body.classList.remove("nav-open");
        if (btn) btn.classList.remove("is-active");
      });
    });
  }

  document.querySelectorAll("[data-scroll-top]").forEach((el) => {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  });

  document.querySelectorAll("[data-scroll-link]").forEach((el) => {
    el.addEventListener("click", (e) => {
      const selector = el.getAttribute("data-scroll-link");
      if (!selector) return;
      const target = document.querySelector(selector);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  const showcaseTrack = document.querySelector("[data-showcase-slider]");
  if (showcaseTrack) {
    const cards = Array.from(showcaseTrack.querySelectorAll(".hero-mini-card"));
    const prev = document.querySelector("[data-showcase-prev]");
    const next = document.querySelector("[data-showcase-next]");
    const gap = 16;

    function scrollByCard(direction) {
      const firstCard = cards[0];
      if (!firstCard) return;
      const cardWidth = firstCard.getBoundingClientRect().width;
      showcaseTrack.scrollBy({
        left: direction * (cardWidth + gap),
        behavior: "smooth",
      });
    }

    if (prev) {
      prev.addEventListener("click", () => scrollByCard(-1));
    }

    if (next) {
      next.addEventListener("click", () => scrollByCard(1));
    }
  }

  function getCsrfToken(form) {
    if (!form) return "";
    const input = form.querySelector('input[name="csrfmiddlewaretoken"]');
    return input ? input.value : "";
  }

  function updateCartCounters(count) {
    cartCounters.forEach((el) => {
      el.textContent = String(count);
      const parent = el.closest(".mobile-bottom-nav__item--cart");
      if (parent) {
        parent.classList.toggle("has-items", Number(count) > 0);
      }
    });
  }

  function showCartToast(message, count) {
    if (!cartToast) return;
    const messageEl = cartToast.querySelector("[data-cart-toast-message]");
    const countEl = cartToast.querySelector("[data-cart-toast-count]");
    if (messageEl) messageEl.textContent = message || "Товар добавлен в корзину";
    if (countEl) countEl.textContent = String(count ?? 0);
    cartToast.hidden = false;
    cartToast.classList.add("is-visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      cartToast.classList.remove("is-visible");
      setTimeout(() => {
        cartToast.hidden = true;
      }, 220);
    }, 2200);
  }

  async function submitCartForm(form) {
    const action = form.getAttribute("action");
    if (!action) return;

    const formData = new FormData(form);
    formData.append("ajax", "1");

    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
      submitButton.disabled = true;
      submitButton.classList.add("is-loading");
    }

    try {
      const response = await fetch(action, {
        method: "POST",
        headers: {
          "X-Requested-With": "fetch",
          "X-CSRFToken": getCsrfToken(form),
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error("cart request failed");
      }

      const payload = await response.json();
      updateCartCounters(payload.cart_count ?? 0);
      showCartToast(payload.message || "Товар добавлен в корзину", payload.cart_count ?? 0);
    } catch (_err) {
      form.submit();
      return;
    } finally {
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.classList.remove("is-loading");
      }
    }
  }

  document.querySelectorAll("form[data-cart-add-form]").forEach((form) => {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      submitCartForm(form);
    });
  });
})();