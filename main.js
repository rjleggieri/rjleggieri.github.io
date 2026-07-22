const header = document.querySelector("[data-header]");
const menuButton = document.querySelector("[data-menu-button]");
const menuLabel = document.querySelector("[data-menu-label]");
const nav = document.querySelector("[data-nav]");
const navLinks = [...document.querySelectorAll('.site-nav a[href^="#"]')];
const navFocusables = [...nav.querySelectorAll("a")];
const revealItems = document.querySelectorAll(".reveal");

document.querySelector("[data-year]").textContent = new Date().getFullYear();

const toggleHeader = () => header.classList.toggle("scrolled", window.scrollY > 12);
toggleHeader();
window.addEventListener("scroll", toggleHeader, { passive: true });

const setMenu = (open, returnFocus = false) => {
  menuButton.setAttribute("aria-expanded", String(open));
  menuLabel.textContent = open ? "Close navigation" : "Open navigation";
  nav.classList.toggle("open", open);
  document.body.style.overflow = open ? "hidden" : "";

  if (open) navFocusables[0]?.focus();
  if (!open && returnFocus) menuButton.focus();
};

menuButton.addEventListener("click", () => {
  setMenu(menuButton.getAttribute("aria-expanded") !== "true");
});

navLinks.forEach((link) => link.addEventListener("click", () => setMenu(false)));

document.addEventListener("keydown", (event) => {
  if (menuButton.getAttribute("aria-expanded") !== "true") return;

  if (event.key === "Escape") {
    event.preventDefault();
    setMenu(false, true);
    return;
  }

  if (event.key !== "Tab") return;
  const first = navFocusables[0];
  const last = navFocusables[navFocusables.length - 1];
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
});

const revealObserver = new IntersectionObserver((entries, observer) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    entry.target.classList.add("is-visible");
    observer.unobserve(entry.target);
  });
}, { threshold: 0.1 });

revealItems.forEach((item) => revealObserver.observe(item));

const sectionObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    navLinks.forEach((link) => link.classList.toggle("active", link.getAttribute("href") === `#${entry.target.id}`));
  });
}, { rootMargin: "-30% 0px -60% 0px" });

document.querySelectorAll("main section[id]").forEach((section) => sectionObserver.observe(section));
