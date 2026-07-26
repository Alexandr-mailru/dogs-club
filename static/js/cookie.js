(function () {
  var KEY = "dogs-club-cookie-v1";
  var box = document.querySelector("[data-cookie]");
  var ok = document.querySelector("[data-cookie-ok]");
  if (!box || !ok) return;

  function accepted() {
    try {
      return localStorage.getItem(KEY) === "1";
    } catch (e) {
      return false;
    }
  }

  function accept() {
    try {
      localStorage.setItem(KEY, "1");
    } catch (e) {}
    box.hidden = true;
    box.classList.remove("is-open");
    document.body.classList.remove("cookie-open");
  }

  if (!accepted()) {
    box.hidden = false;
    box.classList.add("is-open");
    document.body.classList.add("cookie-open");
  }

  ok.addEventListener("click", function (e) {
    e.preventDefault();
    accept();
  });
})();
