(() => {
  document.documentElement.classList.add("js");

  const year = new Date().getFullYear();
  const footer = document.querySelector(".site-footer p");

  if (footer) {
    footer.textContent = `${footer.textContent} © ${year}`;
  }
})();
