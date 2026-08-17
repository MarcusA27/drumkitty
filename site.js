const menu = document.querySelector("#site-menu");
const menuToggle = document.querySelector(".menu-toggle");

if (menu && menuToggle) {
  const setMenuOpen = (open) => {
    menu.classList.toggle("is-open", open);
    menu.setAttribute("aria-hidden", String(!open));
    menuToggle.setAttribute("aria-expanded", String(open));
    menu.inert = !open;
    document.body.classList.toggle("menu-is-open", open);

    if (open) {
      menu.querySelector(".site-menu__close").focus();
    } else {
      menuToggle.focus();
    }
  };

  menuToggle.addEventListener("click", () => setMenuOpen(true));

  menu.querySelectorAll("[data-menu-close], .site-menu__nav a").forEach((item) => {
    item.addEventListener("click", () => setMenuOpen(false));
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menu.classList.contains("is-open")) {
      setMenuOpen(false);
    }
  });
}
