(function () {
  const btn = document.querySelector(".nav-toggle");
  const mainNav = document.querySelector(".main-nav");

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
})();