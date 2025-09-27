(function(){
  try{
    const root = document.documentElement;
    const key = "epi_theme";
    const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    const saved = localStorage.getItem(key) || (prefersDark ? "dark" : "light");
    function apply(theme){
      root.setAttribute("data-theme", theme);
      localStorage.setItem(key, theme);
      setLabel(theme);
    }
    function setLabel(t){
      const btn = document.getElementById("themeToggle") || document.getElementById("btn-theme-toggle");
      if(!btn) return;
      btn.textContent = (t === "dark") ? "☀️" : "🌙";
      btn.setAttribute("aria-pressed", String(t === "dark"));
      btn.setAttribute("title", (t === "dark") ? "Usar tema claro" : "Usar tema escuro");
    }
    apply(saved);
    const b = document.getElementById("themeToggle") || document.getElementById("btn-theme-toggle");
    if(b){
      b.addEventListener("click", function(){
        const cur = root.getAttribute("data-theme") || "light";
        apply(cur === "dark" ? "light" : "dark");
      });
    }
  }catch(e){ /* no-op */ }
})();
