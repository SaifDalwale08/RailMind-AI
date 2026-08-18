/* RailMind AI — shared frontend authentication/session layer (vanilla JS, localStorage).
   NOTE: This is a lightweight frontend session mechanism, not production-grade
   authentication. Replace login()/register()/resetPassword() with real backend
   API calls when an authentication service is available. */
(function (global) {
  "use strict";

  var AUTH_KEY = "railmind_authenticated";
  var USER_KEY = "railmind_user";
  var USERS_KEY = "railmind_users";
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  /* Base path so the site works both at /app/ and at the root of a static host. */
  var BASE = (function () {
    var p = global.location.pathname;
    var i = p.indexOf("/app/");
    if (i >= 0) return p.slice(0, i + 5);
    var d = p.slice(0, p.lastIndexOf("/") + 1);
    if (/\/dashboard\/$/.test(d)) d = d.replace(/dashboard\/$/, "");
    return d || "/";
  })();

  function readUsers() {
    try { return JSON.parse(localStorage.getItem(USERS_KEY) || "[]"); } catch (e) { return []; }
  }
  function saveUser(user) {
    var users = readUsers().filter(function (u) { return u.email !== user.email; });
    users.push(user);
    localStorage.setItem(USERS_KEY, JSON.stringify(users));
  }
  function nameFromEmail(email) {
    var local = String(email).split("@")[0].replace(/[._-]+/g, " ").trim();
    return local.replace(/\b\w/g, function (c) { return c.toUpperCase(); }) || "Operator";
  }

  var Auth = {
    url: function (path) { return BASE + path; },
    go: function (path) { global.location.href = BASE + path; },

    isAuthenticated: function () {
      return localStorage.getItem(AUTH_KEY) === "true";
    },
    user: function () {
      try { return JSON.parse(localStorage.getItem(USER_KEY) || "null"); } catch (e) { return null; }
    },

    /* Accepts any valid email address with any non-empty password. */
    login: function (email, password) {
      var e = String(email || "").trim().toLowerCase();
      var p = String(password || "");
      if (!e) return { ok: false, error: "Please enter your email address." };
      if (!EMAIL_RE.test(e)) return { ok: false, error: "Please enter a valid email address." };
      if (!p) return { ok: false, error: "Please enter your password." };

      var stored = readUsers().filter(function (u) { return u.email === e; })[0];
      var session = stored
        ? { email: e, name: stored.fullName || nameFromEmail(e), organization: stored.organization, role: stored.role }
        : { email: e, name: nameFromEmail(e) };

      localStorage.setItem(AUTH_KEY, "true");
      localStorage.setItem(USER_KEY, JSON.stringify(session));
      return { ok: true, user: session };
    },

    register: function (data) {
      data = data || {};
      var email = String(data.email || "").trim().toLowerCase();
      if (!data.fullName) return { ok: false, error: "Please enter your full name." };
      if (!EMAIL_RE.test(email)) return { ok: false, error: "Please enter a valid email address." };
      if (!data.organization) return { ok: false, error: "Please enter your organization." };
      if (!data.role) return { ok: false, error: "Please select your role." };
      if (!data.password) return { ok: false, error: "Please enter a password." };
      if (data.password !== data.confirmPassword) return { ok: false, error: "Passwords do not match." };
      saveUser({
        fullName: data.fullName,
        email: email,
        organization: data.organization,
        role: data.role
      });
      return { ok: true };
    },

    resetPassword: function (email) {
      var e = String(email || "").trim().toLowerCase();
      if (!e) return { ok: false, error: "Please enter your email address." };
      if (!EMAIL_RE.test(e)) return { ok: false, error: "Please enter a valid email address." };
      return { ok: true };
    },

    logout: function () {
      localStorage.removeItem(AUTH_KEY);
      localStorage.removeItem(USER_KEY);
      Auth.go("login.html");
    },

    requireAuth: function (prefix) {
      if (!Auth.isAuthenticated()) {
        global.location.replace((prefix || "") + BASE + "login.html");
        return false;
      }
      return true;
    }
  };

  global.RailMindAuth = Auth;
})(window);
