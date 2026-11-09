(() => {
  const body = document.body;
  const sidebar = document.getElementById("application-sidebar");
  const toggle = document.querySelector("[data-sidebar-toggle]");
  const closeControls = document.querySelectorAll("[data-sidebar-close]");

  if (!sidebar || !toggle) {
    return;
  }

  const setSidebarOpen = (isOpen) => {
    body.classList.toggle("chord-sidebar-open", isOpen);
    toggle.setAttribute("aria-expanded", String(isOpen));
    if (isOpen) {
      sidebar.querySelector("a, button")?.focus();
    } else {
      toggle.focus();
    }
  };

  toggle.addEventListener("click", () => {
    setSidebarOpen(!body.classList.contains("chord-sidebar-open"));
  });

  closeControls.forEach((control) => {
    control.addEventListener("click", () => setSidebarOpen(false));
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && body.classList.contains("chord-sidebar-open")) {
      setSidebarOpen(false);
    }
  });

  const desktopQuery = window.matchMedia("(min-width: 992px)");
  desktopQuery.addEventListener("change", (event) => {
    if (event.matches) {
      body.classList.remove("chord-sidebar-open");
      toggle.setAttribute("aria-expanded", "false");
    }
  });
})();
