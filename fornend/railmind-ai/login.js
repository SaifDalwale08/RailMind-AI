/* RailMind AI — login page script */
  (function () {
    var form = document.getElementById("login-form");
    var err = document.getElementById("login-error");
    var pw = document.getElementById("password");
    var toggle = document.getElementById("toggle-password");
    var slash = document.getElementById("eye-slash");

    toggle.addEventListener("click", function () {
      var show = pw.type === "password";
      pw.type = show ? "text" : "password";
      toggle.setAttribute("aria-label", show ? "Hide password" : "Show password");
      slash.style.display = show ? "none" : "";
    });

    function fail(msg) { err.textContent = msg; err.classList.remove("hidden"); }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      err.classList.add("hidden");
      var res = RailMindAuth.login(document.getElementById("email").value, pw.value);
      if (!res.ok) { fail(res.error); return; }
      RailMindAuth.go("dashboard/index.html");
    });

    document.getElementById("google-btn").addEventListener("click", function () {
      fail("Google sign-in is not available yet. Please sign in with your email address.");
    });
  })();
