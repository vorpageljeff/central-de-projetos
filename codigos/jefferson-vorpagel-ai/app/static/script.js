const header = document.querySelector("[data-header]");
const menuButton = document.querySelector("[data-menu-button]");
const nav = document.querySelector("[data-nav]");

if (menuButton && nav && header) {
  menuButton.addEventListener("click", () => {
    const isOpen = nav.classList.toggle("is-open");
    document.body.classList.toggle("menu-open", isOpen);
    header.classList.toggle("is-open", isOpen);
    menuButton.setAttribute("aria-label", isOpen ? "Fechar menu" : "Abrir menu");
  });

  nav.addEventListener("click", (event) => {
    if (!(event.target instanceof HTMLAnchorElement)) {
      return;
    }

    nav.classList.remove("is-open");
    document.body.classList.remove("menu-open");
    header.classList.remove("is-open");
    menuButton.setAttribute("aria-label", "Abrir menu");
  });
}

document.querySelectorAll("[data-event]").forEach((element) => {
  element.addEventListener("click", () => {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({
      event: element.dataset.event,
      ad_position: element.dataset.adPosition || null,
      href: element.getAttribute("href") || null,
    });
  });
});

document.querySelectorAll("ins.adsbygoogle").forEach(() => {
  try {
    (window.adsbygoogle = window.adsbygoogle || []).push({});
  } catch (error) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event: "adsense_render_error" });
  }
});
