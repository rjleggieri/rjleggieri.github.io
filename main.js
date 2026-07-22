const header = document.querySelector("[data-header]");
const menuButton = document.querySelector("[data-menu-button]");
const nav = document.querySelector("[data-nav]");
const navLinks = [...document.querySelectorAll('.site-nav a[href^="#"]')];
const revealItems = document.querySelectorAll(".reveal");

document.querySelector("[data-year]").textContent = new Date().getFullYear();

const toggleHeader = () => header.classList.toggle("scrolled", window.scrollY > 12);
toggleHeader();
window.addEventListener("scroll", toggleHeader, { passive: true });

menuButton.addEventListener("click", () => {
  const isOpen = menuButton.getAttribute("aria-expanded") === "true";
  menuButton.setAttribute("aria-expanded", String(!isOpen));
  nav.classList.toggle("open", !isOpen);
  document.body.style.overflow = isOpen ? "" : "hidden";
});

navLinks.forEach((link) => link.addEventListener("click", () => {
  menuButton.setAttribute("aria-expanded", "false");
  nav.classList.remove("open");
  document.body.style.overflow = "";
}));

const revealObserver = new IntersectionObserver((entries, observer) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    entry.target.classList.add("is-visible");
    observer.unobserve(entry.target);
  });
}, { threshold: 0.12 });

revealItems.forEach((item) => revealObserver.observe(item));

const sectionObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    navLinks.forEach((link) => link.classList.toggle("active", link.getAttribute("href") === `#${entry.target.id}`));
  });
}, { rootMargin: "-30% 0px -60% 0px" });

document.querySelectorAll("main section[id]").forEach((section) => sectionObserver.observe(section));
