/* RailMind AI — Predictive Railway Crowd Intelligence
   Pure HTML + CSS + Vanilla JS + Chart.js. No frameworks. */
(function () {
  "use strict";

  /* ------------------------------------------------------------------ CONFIG */
  var API_BASE = "http://127.0.0.1:8000";
  var EP = {
    upload: "/api/video/upload",
    analyze: "/api/video/analyze",
    master: "/api/demo/analyze",
    health: "/api/health"
  };

  var STATIONS = [
    { code: "PUNE", name: "PUNE JUNCTION", platforms: 5, gates: ["GATE A", "GATE B", "GATE C"] },
    { code: "BCT", name: "MUMBAI CENTRAL", platforms: 6, gates: ["GATE A", "GATE B", "GATE C", "GATE D"] },
    { code: "CSMT", name: "CHHATRAPATI SHIVAJI MAHARAJ TERMINUS", platforms: 7, gates: ["NORTH GATE", "SOUTH GATE", "GATE C"] },
    { code: "NDLS", name: "NEW DELHI", platforms: 8, gates: ["AJMERI GATE", "PAHARGANJ GATE", "GATE C"] },
    { code: "HWH", name: "HOWRAH", platforms: 8, gates: ["GATE A", "GATE B", "GATE C"] },
    { code: "SBC", name: "BENGALURU (KSR)", platforms: 6, gates: ["GATE A", "GATE B"] },
    { code: "ADI", name: "AHMEDABAD", platforms: 5, gates: ["GATE A", "GATE B"] },
    { code: "NGP", name: "NAGPUR", platforms: 5, gates: ["EAST GATE", "WEST GATE"] }
  ];

  var NAV = [
    ["dashboard", "Dashboard", "▦"],
    ["live-monitoring", "Live Monitoring", "◉"],
    ["crowd-analytics", "Crowd Analytics", "▤"],
    ["surge-forecast", "Surge Forecast", "◤"],
    ["train-intelligence", "Train Intelligence", "🚆"],
    ["bottlenecks", "Bottlenecks", "⧗"],
    ["gate-control", "Gate Control", "⛩"],
    ["platform-allocation", "Platform Allocation", "▥"],
    ["announcements", "Announcements", "🔊"],
    ["alerts", "Alerts & Notifications", "⚠", 4],
    ["emergency-access", "Emergency Access", "✚"],
    ["intervention-simulator", "Intervention Simulator", "⚙"],
    ["post-event-analytics", "Post Event Analytics", "◷"],
    ["ai-model-performance", "AI Model Performance", "◈"],
    ["system-status", "System Status", "✦"],
    ["reports", "Reports", "🗎"],
    ["settings", "Settings", "⚑"]
  ];

  /* ------------------------------------------------------------------ STATE */
  var STATE = {
    station: STATIONS[0],
    mode: "demo",              // "live" | "demo" | "offline"
    master: null,
    loading: false,
    error: null,
    route: "dashboard",
    filters: { analyticsWindow: "30 MIN", forecastWindow: "5 MIN", camRisk: "ALL", timeline: "NOW", lang: "ENGLISH" },
    video: { file: null, id: null, uploadStatus: "IDLE", analysisStatus: "IDLE" },
    lastSim: null,
    settings: load("rm.settings", {
      warnThreshold: 40, highThreshold: 60, critThreshold: 75,
      forecastHorizon: 5, autoRefresh: false, language: "ENGLISH", density: "COMFORTABLE", sound: true, sms: true, whatsapp: true, pa: true
    })
  };

  function load(k, d) { try { var v = JSON.parse(localStorage.getItem(k)); return v ? Object.assign({}, d, v) : d; } catch (e) { return d; } }
  function save(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }

  /* ============================================================== GLOBAL STATE
     ONE global application state shared by every page: language, voice,
     station, theme and thresholds. Persisted in localStorage. */
  var LS = {
    lang: "railmind.language", vOn: "railmind.voice.enabled", vVol: "railmind.voice.volume",
    vRate: "railmind.voice.rate", vPitch: "railmind.voice.pitch", theme: "railmind.theme"
  };
  function lsGet(k, d) { try { var v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } }
  function lsSet(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }

  var LANGS = [
    { key: "english", label: "ENGLISH", voice: "en-IN", keys: ["english", "ENGLISH", "En", "en", "EN"] },
    { key: "hindi", label: "हिंदी", voice: "hi-IN", keys: ["hindi", "HINDI", "हिंदी", "hi", "HI"] },
    { key: "marathi", label: "मराठी", voice: "mr-IN", keys: ["marathi", "MARATHI", "मराठी", "mr", "MR"] }
  ];
  var voiceLanguageMap = { english: "en-IN", hindi: "hi-IN", marathi: "mr-IN" };
  var TEST_PHRASE = {
    english: "RailMind AI voice system is ready.",
    hindi: "रेलमाइंड एआई वॉइस सिस्टम तैयार है।",
    marathi: "रेलमाइंड एआय व्हॉइस सिस्टम तयार आहे."
  };
  function langDef(key) { for (var i = 0; i < LANGS.length; i++) if (LANGS[i].key === key) return LANGS[i]; return LANGS[0]; }
  function langLabel(key) { return langDef(key).label; }
  function langFromLabel(label) { for (var i = 0; i < LANGS.length; i++) if (LANGS[i].label === label) return LANGS[i].key; return "english"; }

  // Pick a value from a backend object using whichever language key the backend uses.
  function pickLang(obj, key) {
    if (!obj) return "";
    var d = langDef(key), i;
    for (i = 0; i < d.keys.length; i++) if (obj[d.keys[i]] != null) return obj[d.keys[i]];
    var en = langDef("english");
    for (i = 0; i < en.keys.length; i++) if (obj[en.keys[i]] != null) return obj[en.keys[i]];
    return "";
  }

  var RailMindState = {
    selectedStation: null,
    currentLanguage: lsGet(LS.lang, "english"),
    voiceEnabled: lsGet(LS.vOn, true),
    voiceVolume: lsGet(LS.vVol, 1),
    voiceRate: lsGet(LS.vRate, 1),
    voicePitch: lsGet(LS.vPitch, 1),
    theme: lsGet(LS.theme, "black-red"),
    notificationPreference: null,
    riskThreshold: null,
    forecastSettings: null,
    backendStatus: "unknown",
    lastSpokenKey: null
  };
  window.RailMindState = RailMindState;
  if (!/^(english|hindi|marathi)$/.test(RailMindState.currentLanguage)) RailMindState.currentLanguage = "english";

  function persistVoice() {
    lsSet(LS.lang, RailMindState.currentLanguage); lsSet(LS.vOn, RailMindState.voiceEnabled);
    lsSet(LS.vVol, RailMindState.voiceVolume); lsSet(LS.vRate, RailMindState.voiceRate);
    lsSet(LS.vPitch, RailMindState.voicePitch); lsSet(LS.theme, RailMindState.theme);
  }

  /* ------------------------------------------------------------ SPEECH ENGINE */
  function stopSpeech() { try { if ("speechSynthesis" in window) window.speechSynthesis.cancel(); } catch (e) {} }
  var VOICES = [];
  function refreshVoices() { try { VOICES = window.speechSynthesis.getVoices() || []; } catch (e) { VOICES = []; } }
  if ("speechSynthesis" in window) {
    refreshVoices();
    try { window.speechSynthesis.onvoiceschanged = refreshVoices; } catch (e) {}
  }
  function pickVoice(langTag) {
    if (!VOICES.length) refreshVoices();
    var base = langTag.split("-")[0], i, v;
    for (i = 0; i < VOICES.length; i++) if ((VOICES[i].lang || "").replace("_", "-").toLowerCase() === langTag.toLowerCase()) return VOICES[i];
    for (i = 0; i < VOICES.length; i++) { v = (VOICES[i].lang || "").replace("_", "-").toLowerCase(); if (v.indexOf(base + "-") === 0 || v === base) return VOICES[i]; }
    if (base !== "en") for (i = 0; i < VOICES.length; i++) if ((VOICES[i].lang || "").toLowerCase().indexOf("-in") > -1) return VOICES[i];
    return null;
  }
  /* Speaks text in the CURRENT language. Always cancels previous speech first,
     so two voices can never overlap. */
  function speak(text, opts) {
    opts = opts || {};
    if (!text) return;
    if (!("speechSynthesis" in window)) { toast("Speech synthesis unavailable in this browser.", "err"); return; }
    if (opts.auto && !RailMindState.voiceEnabled) return;
    stopSpeech();
    var lang = opts.language || RailMindState.currentLanguage;
    var tag = voiceLanguageMap[lang] || "en-IN";
    var u = new SpeechSynthesisUtterance(String(text));
    u.lang = tag;
    var v = pickVoice(tag); if (v) u.voice = v;
    u.volume = clamp01(RailMindState.voiceVolume);
    u.rate = Math.min(2, Math.max(0.5, +RailMindState.voiceRate || 1));
    u.pitch = Math.min(2, Math.max(0, +RailMindState.voicePitch || 1));
    try { window.speechSynthesis.speak(u); } catch (e) { toast("Voice playback failed.", "err"); }
  }
  function clamp01(v) { v = +v; if (isNaN(v)) return 1; return Math.min(1, Math.max(0, v)); }
  function hash(str) { var h = 0, i; str = String(str); for (i = 0; i < str.length; i++) h = ((h << 5) - h + str.charCodeAt(i)) | 0; return h; }
  /* Duplicate prevention: only speak when the message, alert id or language changed. */
  function speakOnce(id, text, opts) {
    var key = RailMindState.currentLanguage + "|" + id + "|" + hash(text);
    if (RailMindState.lastSpokenKey === key) return;
    RailMindState.lastSpokenKey = key;
    speak(text, opts);
  }

  /* Global language switch — stops old speech, updates every language-dependent
     surface, then speaks the new-language announcement when voice mode is ON. */
  function setLanguage(key, opts) {
    key = /^(english|hindi|marathi)$/.test(key) ? key : "english";
    var changed = key !== RailMindState.currentLanguage;
    stopSpeech();
    RailMindState.currentLanguage = key;
    STATE.filters.lang = langLabel(key);
    STATE.settings.language = langLabel(key);
    persistVoice(); save("rm.settings", STATE.settings);
    render();
    if (changed) {
      RailMindState.lastSpokenKey = null;
      if (RailMindState.voiceEnabled && !(opts && opts.silent)) {
        speak(currentAnnouncement(D()), { auto: true });
      }
    }
  }
  function currentAnnouncement(d) { return pickLang(d && d.announcements, RailMindState.currentLanguage); }
  function currentPassengerAlert(d) {
    if (!d) return "";
    var pa = d.passenger_alerts;
    if (Array.isArray(pa)) {
      var lbl = langLabel(RailMindState.currentLanguage), i;
      for (i = 0; i < pa.length; i++) {
        var l = String(pa[i].lang || pa[i].language || "");
        if (l === lbl || l.toLowerCase() === RailMindState.currentLanguage) return pa[i].text || pa[i].message || "";
      }
      return pa.length ? (pa[0].text || "") : "";
    }
    return pickLang(pa, RailMindState.currentLanguage);
  }

  /* ------------------------------------------------- DETERMINISTIC DEMO DATA */
  function seedOf(str) { var h = 0, i; for (i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) % 100000; return h; }
  function seq(seed, n, min, max) {
    var out = [], s = seed, i;
    for (i = 0; i < n; i++) { s = (s * 1103515245 + 12345) % 2147483648; out.push(min + Math.round((s / 2147483648) * (max - min))); }
    return out;
  }
  var TRAIN_POOL = [
    ["16506", "SBC-GIMB GANDHIDHAM EXP", "EXPRESS"], ["12127", "INTERCITY EXPRESS", "EXPRESS"],
    ["11007", "DECCAN EXPRESS", "MAIL"], ["12126", "PRAGATI EXPRESS", "SUPERFAST"],
    ["17031", "HYDERABAD EXPRESS", "EXPRESS"], ["11077", "JHELUM EXPRESS", "MAIL"],
    ["22943", "INDORE EXPRESS", "SUPERFAST"], ["51027", "PUNE-MUMBAI PASSENGER", "PASSENGER"],
    ["12124", "DECCAN QUEEN", "SUPERFAST"], ["19311", "SUPERFAST EXPRESS", "SUPERFAST"],
    ["01234", "SPECIAL UNRESERVED", "SPECIAL"], ["12115", "SIDDHESHWAR EXPRESS", "SUPERFAST"]
  ];

  // Demo master JSON, shaped exactly like the backend contract.
  function demoMaster(st) {
    var s = seedOf(st.code), P = st.platforms;
    var lvl = ["LOW", "MEDIUM", "HIGH", "LOW", "CRITICAL", "MEDIUM", "HIGH", "LOW"];
    var dens = seq(s + 7, P, 22, 94);
    var platforms = [];
    for (var i = 0; i < P; i++) {
      var d = st.code === "PUNE" ? [28, 52, 76, 31, 91][i] : dens[i];
      platforms.push({
        id: i + 1, name: "PLATFORM " + (i + 1), density: d,
        level: d > 85 ? "CRITICAL" : d > 65 ? "HIGH" : d > 45 ? "MEDIUM" : "LOW",
        crowd: Math.round(d * 4.2), capacity: 420,
        next_train: TRAIN_POOL[(i + s) % TRAIN_POOL.length][0],
        arrival: pad(18, 40 + i * 7), allocation: "PLATFORM " + (i + 1),
        recommended: d > 85 ? "DIVERT TO PLATFORM 1" : d > 65 ? "HOLD BOARDING 3 MIN" : "MAINTAIN"
      });
    }
    var trains = TRAIN_POOL.map(function (t, i) {
      var delay = [0, 0, 12, 5, 0, 25, 0, 8, 0, 3, 40, 0][i];
      var pressure = seq(s + i * 13, 1, 18, 96)[0];
      return {
        number: t[0], name: t[1], type: t[2],
        arrival: pad(18, 35 + i * 6), departure: pad(18, 40 + i * 6),
        platform: (i % P) + 1, delay: delay,
        coach_position: ["FRONT", "MIDDLE", "REAR"][i % 3],
        coaches: t[2] === "PASSENGER" ? 18 : 22,
        unreserved: t[2] === "PASSENGER" || t[2] === "SPECIAL",
        load: pressure * 12, pressure: pressure,
        crowd_impact: Math.round(pressure * 1.6),
        risk: pressure > 80 ? "CRITICAL" : pressure > 60 ? "HIGH" : pressure > 40 ? "MEDIUM" : "LOW"
      };
    });
    var zones = ["PLATFORM", "FOOTBRIDGE", "CONCOURSE", "GATE A", "GATE B", "EXIT"];
    return {
      _demo: true,
      station: { code: st.code, name: st.name, platform_count: P, gates: st.gates },
      video: { video_id: null, status: "NOT UPLOADED" },
      crowd: {
        current: st.code === "PUNE" ? 0 : seq(s + 3, 1, 40, 260)[0],
        peak: seq(s + 5, 1, 180, 460)[0], average: seq(s + 9, 1, 60, 200)[0],
        growth_rate: 0.2, acceleration: 0.2, trend: "STABLE",
        density: dens[0], flow_rate: seq(s + 11, 1, 20, 90)[0],
        history: seq(s + 21, 24, 20, 220),
        entry: seq(s + 31, 12, 10, 70), exit: seq(s + 41, 12, 8, 60),
        zones: zones.map(function (z, i) { return { zone: z, density: seq(s + i * 5 + 2, 1, 20, 95)[0] }; })
      },
      forecast: {
        window: "5 MIN", predicted: 10.61, increase: 10.61, confidence: 82,
        series: seq(s + 61, 12, 30, 200), predicted_series: seq(s + 71, 12, 40, 240),
        factors: ["TRAIN ARRIVAL", "MULTIPLE TRAIN ARRIVALS", "UNRESERVED COACH", "FOOTBRIDGE CONGESTION", "HIGH ENTRY FLOW"],
        surge_score: 71, surge_location: "FOOTBRIDGE / PLATFORM 5", surge_eta: "18:44"
      },
      risk: { level: "CRITICAL", score: 75, activity: "VERY HIGH" },
      schedule: {
        trains: trains,
        pressure: { "5": 11, "10": 22, "15": 22, "30": 26 },
        simultaneous: 7,
        next_event: { time: "18:40", type: "ARRIVAL", train: "16506", name: "SBC-GIMB GAN" }
      },
      intervention: {
        recommended: "GATE CONTROL + PLATFORM GUIDANCE",
        before: 10.61, after: 6.90, reduction: 3.71, reduction_pct: 35,
        projected_risk: "MEDIUM", flow_improvement: 28, emergency_effect: "CORRIDOR RESTORED TO CLEAR"
      },
      operator_alert: {
        level: "CRITICAL",
        message: "Crowd surge predicted at FOOTBRIDGE within 5 minutes.",
        reason: "Simultaneous arrivals (7) with unreserved coach concentration.",
        action: "REGULATE GATE A · OPEN GATE B · GUIDE PASSENGERS TO PLATFORM 1"
      },
      platforms: {
        list: platforms,
        recommended_platform: "PLATFORM 1",
        recommended_gate: "REGULATE GATE A",
        bottlenecks: [
          { location: "FOOTBRIDGE NORTH", density: 92, capacity: 300, flow: 41, status: "CRITICAL", cause: "Simultaneous arrivals converging", action: "Open alternate footbridge · restrict Gate A" },
          { location: "PLATFORM 5 MID", density: 88, capacity: 420, flow: 33, status: "CRITICAL", cause: "Unreserved coach boarding", action: "Deploy staff · stagger boarding" },
          { location: "GATE A ENTRY", density: 71, capacity: 260, flow: 58, status: "AT RISK", cause: "High entry flow", action: "Regulate entry to 60%" },
          { location: "CONCOURSE CENTRE", density: 54, capacity: 600, flow: 74, status: "AT RISK", cause: "Waiting passengers", action: "Announce platform guidance" },
          { location: "EXIT CORRIDOR", density: 31, capacity: 240, flow: 80, status: "CLEAR", cause: "Normal flow", action: "Monitor" },
          { location: "PLATFORM 1", density: 28, capacity: 420, flow: 88, status: "CLEAR", cause: "Normal flow", action: "Use as diversion platform" }
        ],
        emergency_corridor: [
          { name: "EMERGENCY EXIT EAST", status: "CLEAR", access_risk: "LOW", action: "Monitor" },
          { name: "EMERGENCY EXIT WEST", status: "AT RISK", access_risk: "MEDIUM", action: "Clear vendor obstruction" },
          { name: "FOOTBRIDGE NORTH ROUTE", status: "BLOCKED", access_risk: "HIGH", action: "Divert crowd · restrict Gate A" },
          { name: "PLATFORM 1 RAMP", status: "CLEAR", access_risk: "LOW", action: "Keep clear" },
          { name: "AMBULANCE BAY ACCESS", status: "CLEAR", access_risk: "LOW", action: "Keep clear" }
        ]
      },
      gates: st.gates.map(function (g, i) {
        var f = seq(s + i * 17 + 4, 1, 20, 95)[0];
        return {
          name: g, flow: f, queue: Math.round(f * 1.8), capacity: 180, density: Math.min(99, f + 8),
          risk: f > 80 ? "CRITICAL" : f > 60 ? "HIGH" : f > 40 ? "MEDIUM" : "LOW",
          recommended: f > 80 ? "RESTRICT" : f > 60 ? "REDIRECT" : "OPEN", state: "OPEN"
        };
      }),
      cameras: buildCameras(st, s),
      passenger_alerts: [
        { text: "Passengers for train 16506 please use PLATFORM 1 via South footbridge.", lang: "ENGLISH" },
        { text: "कृपया दक्षिण पादचारी पुल का उपयोग करें। भीड़भाड़ से बचें।", lang: "हिंदी" },
        { text: "कृपया दक्षिण पादचारी पुलाचा वापर करा. गर्दी टाळा.", lang: "मराठी" }
      ],
      announcements: {
        ENGLISH: "Attention passengers. Due to heavy crowding on the north footbridge, please use the south footbridge. Train 16506 will arrive on Platform 1.",
        "हिंदी": "यात्रीगण ध्यान दें। उत्तर पादचारी पुल पर भीड़ के कारण कृपया दक्षिण पुल का प्रयोग करें। गाड़ी 16506 प्लेटफ़ॉर्म 1 पर आएगी।",
        "मराठी": "प्रवाशांनी लक्ष द्यावे. उत्तर पादचारी पुलावर गर्दी असल्याने कृपया दक्षिण पुलाचा वापर करा. गाडी 16506 फलाट 1 वर येईल."
      },
      delivery_channels: [
        { channel: "STATION PA", status: "NOT CONNECTED" },
        { channel: "STATION DISPLAY", status: "NOT CONNECTED" },
        { channel: "MOBILE APP PUSH", status: "NOT CONNECTED" },
        { channel: "SMS", status: "NOT CONNECTED" },
        { channel: "WHATSAPP", status: "NOT CONNECTED" }
      ],
      post_event: {
        peak_crowd: 214, peak_risk: 88, surge_duration: "11 MIN", intervention_time: "18:42",
        crowd_reduction: 35, risk_reduction: 42, response_time: "96 s", corridor_status: "RESTORED",
        before: seq(s + 81, 10, 90, 220), after: seq(s + 91, 10, 50, 140),
        worked: ["Gate A regulation reduced entry flow within 90 seconds", "Platform 1 diversion absorbed 35% of footbridge load", "Multilingual announcement reached the concourse before peak"],
        failed: ["Emergency exit west remained partially obstructed for 4 minutes", "Gate B opening was delayed by 70 seconds"],
        improve: ["Pre-position staff 3 minutes before simultaneous arrivals", "Automate Gate B opening trigger at surge score > 70"]
      },
      model: {
        status: "NOT CONNECTED", version: null, accuracy: null, precision: null, recall: null,
        f1: null, confidence: null, fps: null, latency: null,
        engines: [
          { name: "YOLO DETECTION", status: "NOT CONNECTED" },
          { name: "FORECAST ENGINE", status: "NOT CONNECTED" },
          { name: "RISK ENGINE", status: "NOT CONNECTED" },
          { name: "RECOMMENDATION ENGINE", status: "NOT CONNECTED" }
        ]
      },
      system: [
        { service: "CCTV FEED", status: "OFFLINE", latency: null, requests: 0, errors: 0 },
        { service: "FORECAST ENGINE", status: "OFFLINE", latency: null, requests: 0, errors: 0 },
        { service: "TRAIN DATA", status: "OFFLINE", latency: null, requests: 0, errors: 0 },
        { service: "RISK ENGINE", status: "OFFLINE", latency: null, requests: 0, errors: 0 },
        { service: "RECOMMENDATION ENGINE", status: "OFFLINE", latency: null, requests: 0, errors: 0 },
        { service: "PASSENGER FLOW", status: "OFFLINE", latency: null, requests: 0, errors: 0 },
        { service: "ANNOUNCEMENT SYSTEM", status: "OFFLINE", latency: null, requests: 0, errors: 0 },
        { service: "API", status: "OFFLINE", latency: null, requests: 0, errors: 0 },
        { service: "DATABASE", status: "OFFLINE", latency: null, requests: 0, errors: 0 }
      ],
      alerts: buildAlerts(st)
    };
  }

  function pad(h, m) { var hh = h + Math.floor(m / 60), mm = m % 60; return (hh % 24 < 10 ? "0" : "") + (hh % 24) + ":" + (mm < 10 ? "0" : "") + mm; }

  function buildCameras(st, s) {
    var locs = [], i;
    for (i = 1; i <= st.platforms; i++) locs.push("PLATFORM " + i);
    locs = locs.concat(["FOOTBRIDGE", st.gates[0], st.gates[1] || "GATE B", "CONCOURSE", "ENTRY", "EXIT"]);
    return locs.map(function (l, i) {
      var d = seq(s + i * 23 + 1, 1, 15, 96)[0];
      return {
        id: "CAM-" + (101 + i), location: l, count: Math.round(d * 3.4), density: d,
        risk: d > 85 ? "CRITICAL" : d > 65 ? "HIGH" : d > 45 ? "MEDIUM" : "LOW",
        fps: 24, updated: "—", live: false
      };
    });
  }

  function buildAlerts(st) {
    return [
      { id: "A-1", time: "18:39", station: st.code, location: "FOOTBRIDGE NORTH", risk: "CRITICAL", message: "Crowd surge predicted in 5 minutes", reason: "7 simultaneous arrivals", action: "Restrict Gate A, open Gate B", status: "OPEN" },
      { id: "A-2", time: "18:36", station: st.code, location: "PLATFORM 5", risk: "CRITICAL", message: "Density above safe threshold (91%)", reason: "Unreserved coach boarding", action: "Stagger boarding, deploy staff", status: "OPEN" },
      { id: "A-3", time: "18:31", station: st.code, location: "GATE A", risk: "HIGH", message: "Entry flow exceeding gate capacity", reason: "High entry flow", action: "Regulate entry to 60%", status: "OPEN" },
      { id: "A-4", time: "18:24", station: st.code, location: "EMERGENCY EXIT WEST", risk: "HIGH", message: "Emergency corridor partially obstructed", reason: "Vendor obstruction", action: "Clear corridor immediately", status: "OPEN" },
      { id: "A-5", time: "18:18", station: st.code, location: "CONCOURSE", risk: "MEDIUM", message: "Waiting crowd build-up", reason: "Train 11077 delayed 25 min", action: "Announce platform guidance", status: "ACKNOWLEDGED" },
      { id: "A-6", time: "17:58", station: st.code, location: "PLATFORM 2", risk: "MEDIUM", message: "Density trending up", reason: "Train arrival", action: "Monitor", status: "RESOLVED" }
    ];
  }

  /* ------------------------------------------------------------------ DOM */
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var view = $("#view"), banner = $("#banner");
  var charts = {};

  function esc(v) { return String(v === null || v === undefined ? "" : v).replace(/[&<>"]/g, function (c) { return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]; }); }
  function lvlClass(l) {
    l = String(l || "").toUpperCase();
    if (l === "CRITICAL" || l === "BLOCKED") return "crit";
    if (l === "HIGH" || l === "AT RISK") return "high";
    if (l === "MEDIUM" || l === "WARNING" || l === "DEGRADED") return "warn";
    if (l === "LOW" || l === "CLEAR" || l === "SAFE" || l === "ONLINE") return "safe";
    return "info";
  }
  function badge(l) { return '<span class="badge badge-' + lvlClass(l) + '">' + esc(l || "N/A") + "</span>"; }
  function na(v, suffix) { return (v === null || v === undefined) ? '<span class="mono">NOT CONNECTED</span>' : esc(v) + (suffix || ""); }
  function toast(msg, kind) {
    var t = document.createElement("div");
    t.className = "toast " + (kind || "");
    t.textContent = msg;
    $("#toasts").appendChild(t);
    setTimeout(function () { t.remove(); }, 4200);
  }

  /* ------------------------------------------------------------------ CHART */
  var C = { blue: "#2563EB", cyan: "#38BDF8", blue2: "#0053DB", blue3: "#003EA8", green: "#22C55E", amber: "#F59E0B", orange: "#F59E0B", red: "#EF4444", grid: "rgba(148,178,255,0.10)", text: "#AFC0DC" };
  function mkChart(id, cfg) {
    var el = document.getElementById(id);
    if (!el || typeof Chart === "undefined") return;
    if (charts[id]) { charts[id].destroy(); delete charts[id]; }
    cfg.options = Object.assign({
      responsive: true, maintainAspectRatio: false, animation: { duration: 400 },
      interaction: { intersect: false, mode: "index" },
      plugins: {
        legend: { labels: { color: C.text, boxWidth: 12, font: { size: 11 } } },
        tooltip: { backgroundColor: "#11131B", borderColor: "#1E2A44", borderWidth: 1, titleColor: "#FFFFFF", bodyColor: "#AFC0DC" }
      },
      scales: cfg.type === "doughnut" || cfg.type === "polarArea" || cfg.type === "radar" ? undefined : {
        x: { ticks: { color: C.text, font: { size: 10 } }, grid: { color: C.grid } },
        y: { ticks: { color: C.text, font: { size: 10 } }, grid: { color: C.grid }, beginAtZero: true }
      }
    }, cfg.options || {});
    charts[id] = new Chart(el.getContext("2d"), cfg);
  }
  function destroyCharts() { Object.keys(charts).forEach(function (k) { charts[k].destroy(); delete charts[k]; }); }
  function ds(label, data, color, fill) {
    return { label: label, data: data, borderColor: color, backgroundColor: fill ? color + "33" : color, fill: !!fill, tension: .35, pointRadius: 2, borderWidth: 2 };
  }
  function timeLabels(n, stepMin) {
    var out = [], now = new Date(), i;
    for (i = n - 1; i >= 0; i--) { var d = new Date(now.getTime() - i * stepMin * 60000); out.push(two(d.getHours()) + ":" + two(d.getMinutes())); }
    return out;
  }
  function two(n) { return (n < 10 ? "0" : "") + n; }

  /* ------------------------------------------------------------------ API */
  function api(path, opts, timeout) {
    return new Promise(function (resolve, reject) {
      var ctl = new AbortController();
      var t = setTimeout(function () { ctl.abort(); }, timeout || 4000);
      fetch(API_BASE + path, Object.assign({ signal: ctl.signal }, opts || {}))
        .then(function (r) { clearTimeout(t); if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
        .then(resolve).catch(function (e) { clearTimeout(t); reject(e); });
    });
  }

  function loadMaster(videoId) {
    STATE.loading = true; STATE.error = null; render();
    return api(EP.master, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ video_id: videoId || STATE.video.id, station: STATE.station.code })
    }).then(function (json) {
      STATE.master = json; STATE.mode = "live"; RailMindState.backendStatus = "online"; STATE.loading = false; render();
      toast("Railway Intelligence Engine connected — live master JSON loaded.");
    }).catch(function (e) {
      STATE.master = demoMaster(STATE.station);
      STATE.mode = "demo"; STATE.loading = false; STATE.error = e.message; RailMindState.backendStatus = "offline"; render();
    });
  }

  function D() { return STATE.master || demoMaster(STATE.station); }

  /* ------------------------------------------------------------------ SHELL */
  function buildNav() {
    $("#nav").innerHTML = NAV.map(function (n, i) {
      return '<a href="#/' + n[0] + '" data-route="' + n[0] + '"><span class="ic" aria-hidden="true">' + n[2] + "</span><span>" + n[1] + "</span>" +
        (n[3] ? '<span class="nb">' + n[3] + "</span>" : "") + "</a>";
    }).join("");
  }
  function buildStations() {
    $("#stationSelect").innerHTML = STATIONS.map(function (s) { return '<option value="' + s.code + '">' + s.name + "</option>"; }).join("");
    $("#stationSelect").value = STATE.station.code;
  }
  function tickClock() {
    var d = new Date();
    $("#clockTime").textContent = two(d.getHours()) + ":" + two(d.getMinutes());
    $("#clockDate").textContent = d.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }).toUpperCase();
  }
  function updateBanner() {
    var b = banner;
    if (STATE.loading) { b.className = "banner"; b.innerHTML = "LOADING RAILWAY INTELLIGENCE…"; return; }
    if (STATE.mode === "live") {
      b.className = "banner ok";
      b.innerHTML = "<span>● LIVE DATA — RAILWAY INTELLIGENCE ENGINE CONNECTED (" + esc(API_BASE) + ")</span>";
    } else {
      b.className = "banner";
      b.innerHTML = "<span>DEMO DATA — BACKEND NOT CONNECTED. All values below are demo/simulated, not live railway data.</span>" +
        '<button class="btn small" id="retryBtn">RETRY CONNECTION</button>';
    }
    $("#sysStatus").className = "status-pill" + (STATE.mode === "live" ? "" : " off");
    $("#sysStatus").textContent = STATE.mode === "live" ? "● SYSTEM ONLINE" : "● BACKEND OFFLINE";
  }

  function head(title, desc) {
    return '<div class="page-head"><div><h1>' + esc(title) + "</h1><p>" + esc(desc) + "</p></div>" +
      '<div class="row"><span class="route-tag">ROUTE /' + STATE.route + "</span>" + badge(STATE.mode === "live" ? "LIVE" : "DEMO") +
      '<span class="badge badge-info">' + esc(STATE.station.name) + "</span></div></div>";
  }
  function kpi(label, value, level, sub) {
    return '<div class="card kpi ' + (level ? lvlClass(level) : "") + '"><div class="lbl">' + esc(label) + '</div><div class="val">' + value + "</div>" +
      '<div class="sub">' + esc(sub || "") + "</div></div>";
  }
  function card(title, body, sub) {
    return '<div class="card"><h3>' + esc(title) + "</h3>" + (sub ? '<div class="sub">' + esc(sub) + "</div>" : "") + "<div style=\"margin-top:10px\">" + body + "</div></div>";
  }
  function chartCard(title, id, note, tall) {
    return '<div class="card"><h3>' + esc(title) + '</h3><div class="chart-box' + (tall ? " tall" : "") + '"><canvas id="' + id + '"></canvas></div>' +
      (note ? '<div class="legend-note">' + esc(note) + "</div>" : "") + "</div>";
  }
  function table(cols, rows, attrs) {
    return '<div class="table-wrap"><table><thead><tr>' + cols.map(function (c) { return "<th>" + esc(c) + "</th>"; }).join("") + "</tr></thead><tbody>" +
      rows.map(function (r, i) { return "<tr " + (attrs ? attrs(i) : "") + ">" + r.map(function (c) { return "<td>" + c + "</td>"; }).join("") + "</tr>"; }).join("") +
      "</tbody></table></div>";
  }
  function seg(name, options, active) {
    return '<div class="seg" data-seg="' + name + '">' + options.map(function (o) {
      return '<button data-val="' + esc(o) + '" class="' + (o === active ? "active" : "") + '">' + esc(o) + "</button>";
    }).join("") + "</div>";
  }

  /* ------------------------------------------------------------------ PAGES */
  var PAGES = {};

  PAGES["dashboard"] = function (d) {
    var f = d.forecast, r = d.risk, sc = d.schedule, iv = d.intervention;
    var html = head("Railway Intelligence Command Center", "What is happening, where the risk is, when the surge will form, why, what to do and what happens after the action.");
    html += '<div class="grid g6">' +
      kpi("Current Crowd", esc(d.crowd.current) + " <small>people</small>", "info", "Growth " + d.crowd.growth_rate + "/min · " + d.crowd.trend) +
      kpi("5-Min Forecast", esc(f.predicted) + " <small>people</small>", "warn", "Predicted increase " + f.increase) +
      kpi("Risk Score", esc(r.score) + " / 100", r.level, "Level " + r.level) +
      kpi("Railway Activity", esc(r.activity), "high", "Simultaneous pressure " + sc.simultaneous) +
      kpi("Train Pressure", esc(sc.pressure["5"]) + " → " + esc(sc.pressure["30"]), "high", "5 / 10 / 15 / 30 min window") +
      kpi("Next Event", esc(sc.next_event.time), "info", sc.next_event.type + " " + sc.next_event.train + " " + sc.next_event.name) +
      "</div>";

    html += '<div class="section-title">Detection → Analysis → Forecast</div><div class="grid g3">';
    html += card("CCTV Upload & Analysis",
      '<input type="file" id="videoFile" accept="video/*" aria-label="CCTV video file" />' +
      '<div class="row" style="margin-top:10px"><button class="btn btn-primary" id="uploadBtn">UPLOAD VIDEO</button>' +
      '<button class="btn" id="analyzeBtn">ANALYZE VIDEO</button><button class="btn" id="masterBtn">FETCH MASTER JSON</button></div>' +
      '<dl class="kv" style="margin-top:12px"><dt>File name</dt><dd id="vFile">—</dd><dt>Video ID</dt><dd id="vId">' + (STATE.video.id || "—") +
      "</dd><dt>Upload status</dt><dd id=\"vUp\">" + STATE.video.uploadStatus + "</dd><dt>Analysis status</dt><dd id=\"vAn\">" + STATE.video.analysisStatus + "</dd></dl>" +
      '<div class="legend-note">POST ' + EP.upload + " → " + EP.analyze + " → " + EP.master + "</div>",
      "YOLO people detection pipeline");
    html += chartCard("Crowd Forecast (actual vs predicted)", "dashForecast", "People per minute · demo series when backend offline");
    html += chartCard("Train Movement Pressure", "dashPressure", "Pressure index by forecast window");
    html += "</div>";

    html += '<div class="section-title">Risk → Recommendation → Action</div><div class="grid g3">';
    html += card("Operator Alert",
      badge(d.operator_alert.level) + "<p style=\"margin:8px 0 4px\">" + esc(d.operator_alert.message) + "</p>" +
      '<div class="mono">WHY: ' + esc(d.operator_alert.reason) + '</div><div class="mono" style="margin-top:4px">ACTION: ' + esc(d.operator_alert.action) + "</div>" +
      '<div class="row" style="margin-top:10px"><button class="btn btn-primary" data-go="alerts">OPEN ALERTS</button><button class="btn" data-go="intervention-simulator">SIMULATE</button></div>');
    html += card("Recommended Intervention",
      "<h4 style=\"margin:0 0 8px\">" + esc(iv.recommended) + "</h4>" +
      '<dl class="kv"><dt>Before</dt><dd>' + iv.before + " people</dd><dt>After (SIMULATED)</dt><dd>" + iv.after + " people</dd>" +
      "<dt>Crowd reduction</dt><dd>" + iv.reduction + " (" + iv.reduction_pct + "%)</dd><dt>Projected risk</dt><dd>" + badge(iv.projected_risk) + "</dd>" +
      "<dt>Emergency access</dt><dd>" + esc(iv.emergency_effect) + "</dd></dl>" +
      '<span class="badge badge-sim" style="margin-top:8px;display:inline-block">SIMULATED — NO PHYSICAL RAILWAY ACTION PERFORMED</span>');
    html += card("Platform Intelligence",
      d.platforms.list.map(function (p) {
        return '<div style="margin-bottom:8px"><div class="row" style="justify-content:space-between"><span>' + esc(p.name) + " " + badge(p.level) +
          '</span><span class="mono">' + p.density + '%</span></div><div class="bar"><i style="width:' + p.density + "%;background:" + colorFor(p.level) + '"></i></div></div>';
      }).join("") +
      '<div class="mono" style="margin-top:8px">RECOMMENDED PLATFORM: ' + esc(d.platforms.recommended_platform) + " · " + esc(d.platforms.recommended_gate) + "</div>");
    html += "</div>";

    html += '<div class="section-title">Communication · Safety · Status</div><div class="grid g4">';
    html += card("Passenger Alerts", '<div class="list">' + d.passenger_alerts.map(function (a) {
      var isCur = String(a.lang) === langLabel(RailMindState.currentLanguage);
      return '<div class="item"' + (isCur ? ' style="border-color:var(--red)"' : '') + '><div class="mono">' + esc(a.lang) + (isCur ? " · SELECTED" : "") + "</div><div>" + esc(a.text) + "</div></div>";
    }).join("") + "</div>");
    html += card("Bottlenecks", '<div class="list">' + d.platforms.bottlenecks.slice(0, 4).map(function (b) {
      return '<div class="item"><div class="row" style="justify-content:space-between"><b>' + esc(b.location) + "</b>" + badge(b.status) + "</div>" +
        '<div class="m">' + esc(b.cause) + "</div></div>";
    }).join("") + '</div><button class="btn small" style="margin-top:8px" data-go="bottlenecks">VIEW ALL</button>');
    html += card("Emergency Corridor", '<div class="list">' + d.platforms.emergency_corridor.slice(0, 4).map(function (c) {
      return '<div class="item"><div class="row" style="justify-content:space-between"><b>' + esc(c.name) + "</b>" + badge(c.status) + "</div></div>";
    }).join("") + '</div><button class="btn small" style="margin-top:8px" data-go="emergency-access">EMERGENCY ACCESS</button>');
    html += card("Announcement Center & Delivery Channels",
      '<p style="margin:0 0 8px">' + esc(currentAnnouncement(d)) + "</p>" +
      '<div class="row"><button class="btn btn-primary" id="dashPlay">PLAY</button><button class="btn" data-go="announcements">OPEN CENTER</button></div>' +
      '<div style="margin-top:10px">' + d.delivery_channels.map(function (c) {
        return '<div class="switch"><span>' + esc(c.channel) + "</span>" + badge(c.status) + "</div>";
      }).join("") + "</div>");
    html += "</div>";
    return html;
  };
  function colorFor(l) {
    l = String(l).toUpperCase();
    return l === "CRITICAL" || l === "BLOCKED" ? C.red : l === "HIGH" || l === "AT RISK" ? C.orange : l === "MEDIUM" ? C.amber : C.green;
  }

  PAGES["dashboard"].after = function (d) {
    mkChart("dashForecast", {
      type: "line",
      data: { labels: timeLabels(12, 5), datasets: [ds("Actual crowd (people)", d.forecast.series, C.blue, true), ds("Predicted crowd (people)", d.forecast.predicted_series, C.cyan)] }
    });
    mkChart("dashPressure", {
      type: "bar",
      data: { labels: ["5 MIN", "10 MIN", "15 MIN", "30 MIN"], datasets: [{ label: "Pressure index", data: [d.schedule.pressure["5"], d.schedule.pressure["10"], d.schedule.pressure["15"], d.schedule.pressure["30"]], backgroundColor: [C.green, C.amber, C.orange, C.red] }] }
    });
    var fi = $("#videoFile");
    if (fi) fi.addEventListener("change", function () {
      STATE.video.file = fi.files[0] || null;
      $("#vFile").textContent = STATE.video.file ? STATE.video.file.name : "—";
    });
    on("#uploadBtn", "click", doUpload);
    on("#analyzeBtn", "click", doAnalyze);
    on("#masterBtn", "click", function () { loadMaster(); });
    on("#dashPlay", "click", function () { speak(currentAnnouncement(d)); });
  };

  function doUpload() {
    if (!STATE.video.file) { toast("Select a CCTV video file first.", "warn"); return; }
    STATE.video.uploadStatus = "UPLOADING…"; $("#vUp").textContent = STATE.video.uploadStatus;
    var fd = new FormData(); fd.append("file", STATE.video.file);
    api(EP.upload, { method: "POST", body: fd }, 20000).then(function (j) {
      STATE.video.id = j.video_id || j.id; STATE.video.uploadStatus = "SUCCESS";
      $("#vId").textContent = STATE.video.id; $("#vUp").textContent = "SUCCESS";
      toast("Upload complete. video_id " + STATE.video.id);
    }).catch(function () {
      STATE.video.uploadStatus = "BACKEND OFFLINE — UPLOAD NOT PERFORMED";
      $("#vUp").textContent = STATE.video.uploadStatus;
      toast("Backend offline — video was NOT uploaded.", "err");
    });
  }
  function doAnalyze() {
    if (!STATE.video.id) { toast("No video_id yet — upload a video first (backend required).", "warn"); return; }
    STATE.video.analysisStatus = "ANALYZING…"; $("#vAn").textContent = STATE.video.analysisStatus;
    api(EP.analyze, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ video_id: STATE.video.id }) }, 60000)
      .then(function () { STATE.video.analysisStatus = "SUCCESS"; $("#vAn").textContent = "SUCCESS"; return loadMaster(STATE.video.id); })
      .catch(function () { STATE.video.analysisStatus = "BACKEND OFFLINE — NOT ANALYZED"; $("#vAn").textContent = STATE.video.analysisStatus; toast("Backend offline — analysis not performed.", "err"); });
  }

  /* ---------------------------------------------------------- LIVE MONITORING */
  PAGES["live-monitoring"] = function (d) {
    var cams = d.cameras.filter(function (c) { return STATE.filters.camRisk === "ALL" || c.risk === STATE.filters.camRisk; });
    var crit = d.cameras.filter(function (c) { return c.risk === "CRITICAL"; }).length;
    var avg = Math.round(d.cameras.reduce(function (a, c) { return a + c.density; }, 0) / d.cameras.length);
    var worst = d.cameras.slice().sort(function (a, b) { return b.density - a.density; })[0];
    var h = head("Live Monitoring", "CCTV command center for " + STATE.station.name + ". Feeds are placeholders until the CCTV backend is connected.");
    h += '<div class="grid g6">' +
      kpi("Active Cameras", d.cameras.length, "info", "Feeds registered") +
      kpi("Critical Cameras", crit, crit ? "CRITICAL" : "LOW", "Above critical density") +
      kpi("Current Crowd", d.crowd.current, "info", "People detected") +
      kpi("Average Density", avg + "%", avg > 70 ? "HIGH" : "MEDIUM", "Across all zones") +
      kpi("Highest Risk Zone", esc(worst.location), worst.risk, worst.density + "% density") +
      kpi("Stream Status", "NOT CONNECTED", "MEDIUM", "CCTV backend offline") + "</div>";
    h += '<div class="toolbar" style="margin-top:14px">' + seg("camRisk", ["ALL", "LOW", "MEDIUM", "HIGH", "CRITICAL"], STATE.filters.camRisk) +
      '<button class="btn" id="playAll">▶ PLAY</button><button class="btn" id="pauseAll">⏸ PAUSE</button>' +
      '<button class="btn" id="gridToggle">GRID VIEW</button></div>';
    h += '<div class="grid g4" id="camGrid">' + cams.map(function (c) {
      return '<div class="cam" data-cam="' + c.id + '" tabindex="0" role="button" aria-label="Camera ' + c.id + '"><div class="live">' + (c.live ? "LIVE" : "NO SIGNAL") + '</div>' +
        '<div class="feed">FEED NOT CONNECTED</div><div class="meta"><div class="row" style="justify-content:space-between"><b>' + esc(c.location) + "</b>" + badge(c.risk) + "</div>" +
        '<div class="r"><span>' + c.id + "</span><span>FPS <b>" + c.fps + "</b></span></div>" +
        '<div class="r"><span>Passengers <b>' + c.count + "</b></span><span>Density <b>" + c.density + "%</b></span></div>" +
        '<div class="r"><span>Updated</span><span>' + esc(c.updated) + "</span></div>" +
        '<div class="bar"><i style="width:' + c.density + "%;background:" + colorFor(c.risk) + '"></i></div></div></div>';
    }).join("") + "</div>";
    h += '<div class="section-title">Live Crowd Heatmap</div><div class="card"><div class="heat">' +
      d.cameras.map(function (c) { return '<i title="' + esc(c.location) + " " + c.density + '%" style="background:' + colorFor(c.risk) + ';opacity:' + (0.35 + c.density / 160) + '"></i>'; }).join("") +
      '</div><div class="legend-note">GREEN = SAFE · AMBER = WARNING · ORANGE = HIGH · RED = CRITICAL</div></div>';
    h += '<div class="grid g2" style="margin-top:12px">' + chartCard("Zone Density (all cameras)", "camDensity", "Density % by camera location") +
      chartCard("Risk Distribution", "camRisk", "Cameras per risk band") + "</div>";
    return h;
  };
  PAGES["live-monitoring"].after = function (d) {
    mkChart("camDensity", { type: "bar", data: { labels: d.cameras.map(function (c) { return c.location; }), datasets: [{ label: "Density %", data: d.cameras.map(function (c) { return c.density; }), backgroundColor: d.cameras.map(function (c) { return colorFor(c.risk); }) }] } });
    var bands = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
    mkChart("camRisk", { type: "doughnut", data: { labels: bands, datasets: [{ label: "Cameras", data: bands.map(function (b) { return d.cameras.filter(function (c) { return c.risk === b; }).length; }), backgroundColor: [C.green, C.amber, C.orange, C.red] }] } });
    on("#playAll", "click", function () { toast("Stream playback requires the CCTV backend — DEMO only.", "warn"); });
    on("#pauseAll", "click", function () { toast("Streams paused (SIMULATED).", "warn"); });
    on("#gridToggle", "click", function () {
      var g = $("#camGrid"); g.classList.toggle("g4"); g.classList.toggle("g2"); toast("Grid layout switched.");
    });
    Array.prototype.forEach.call(document.querySelectorAll("[data-cam]"), function (el) {
      el.addEventListener("click", function () {
        var c = d.cameras.filter(function (x) { return x.id === el.getAttribute("data-cam"); })[0];
        openDrawer("CAMERA " + c.id, '<dl class="kv"><dt>Location</dt><dd>' + esc(c.location) + "</dd><dt>Passengers</dt><dd>" + c.count +
          "</dd><dt>Density</dt><dd>" + c.density + "%</dd><dt>Risk</dt><dd>" + badge(c.risk) + "</dd><dt>FPS</dt><dd>" + c.fps +
          "</dd><dt>Feed</dt><dd>NOT CONNECTED</dd></dl>");
      });
    });
  };

  /* ---------------------------------------------------------- CROWD ANALYTICS */
  var WINDOWS = { "15 MIN": [15, 1], "30 MIN": [15, 2], "1 HOUR": [12, 5], "3 HOURS": [18, 10], "TODAY": [24, 60] };
  PAGES["crowd-analytics"] = function (d) {
    var c = d.crowd;
    var h = head("Crowd Analytics", "Density, flow and zone analytics for " + STATE.station.name + ". Time filters update every chart on this page.");
    h += '<div class="grid g6">' +
      kpi("Current Crowd", c.current, "info") + kpi("Peak Crowd", c.peak, "HIGH") + kpi("Average Crowd", c.average, "MEDIUM") +
      kpi("Growth Rate", c.growth_rate + " /min", "MEDIUM", "Trend " + c.trend) + kpi("Acceleration", c.acceleration + " /min²", "MEDIUM") +
      kpi("Flow Rate", c.flow_rate + " p/min", "info", "Density " + c.density + "%") + "</div>";
    h += '<div class="toolbar" style="margin-top:14px">' + seg("analyticsWindow", Object.keys(WINDOWS), STATE.filters.analyticsWindow) + '<span class="mono">WINDOW APPLIES TO ALL CHARTS</span></div>';
    h += '<div class="grid g2">' + chartCard("Crowd Density Over Time", "caDensity", "People detected per interval") +
      chartCard("Passenger Flow Rate", "caFlow", "People per minute") +
      chartCard("Zone Density", "caZone", "Density % per station zone") +
      chartCard("Entry vs Exit Flow", "caEntry", "People per minute") + "</div>";
    h += '<div class="grid g2" style="margin-top:12px">' + chartCard("Platform Comparison", "caPlatform", "Density % per platform") +
      card("Zone Breakdown", table(["Zone", "Density", "Status"], c.zones.map(function (z) {
        return [esc(z.zone), z.density + "%", badge(z.density > 85 ? "CRITICAL" : z.density > 65 ? "HIGH" : z.density > 45 ? "MEDIUM" : "LOW")];
      }))) + "</div>";
    return h;
  };
  PAGES["crowd-analytics"].after = function (d) {
    var w = WINDOWS[STATE.filters.analyticsWindow], n = w[0], step = w[1];
    var hist = d.crowd.history.slice(-n);
    if (!hist.length) { toast("NO HISTORICAL DATA AVAILABLE", "warn"); return; }
    mkChart("caDensity", { type: "line", data: { labels: timeLabels(hist.length, step), datasets: [ds("Crowd (people)", hist, C.blue, true)] } });
    mkChart("caFlow", { type: "line", data: { labels: timeLabels(hist.length, step), datasets: [ds("Flow (people/min)", hist.map(function (v) { return Math.round(v / 3); }), C.cyan, true)] } });
    mkChart("caZone", { type: "bar", data: { labels: d.crowd.zones.map(function (z) { return z.zone; }), datasets: [{ label: "Density %", data: d.crowd.zones.map(function (z) { return z.density; }), backgroundColor: d.crowd.zones.map(function (z) { return colorFor(z.density > 85 ? "CRITICAL" : z.density > 65 ? "HIGH" : z.density > 45 ? "MEDIUM" : "LOW"); }) }] } });
    mkChart("caEntry", { type: "line", data: { labels: timeLabels(d.crowd.entry.length, step), datasets: [ds("Entry (p/min)", d.crowd.entry, C.green), ds("Exit (p/min)", d.crowd.exit, C.orange)] } });
    mkChart("caPlatform", { type: "bar", data: { labels: d.platforms.list.map(function (p) { return p.name; }), datasets: [{ label: "Density %", data: d.platforms.list.map(function (p) { return p.density; }), backgroundColor: d.platforms.list.map(function (p) { return colorFor(p.level); }) }] }, });
  };

  /* ----------------------------------------------------------- SURGE FORECAST */
  PAGES["surge-forecast"] = function (d) {
    var f = d.forecast;
    var h = head("Surge Forecast", "Short-term predictive intelligence: where the surge will form, when it will form, and why.");
    h += '<div class="grid g6">' +
      kpi("Current Crowd", d.crowd.current, "info") +
      kpi("Predicted Crowd", f.predicted, "HIGH", "Window " + STATE.filters.forecastWindow) +
      kpi("Surge Score", f.surge_score + " / 100", f.surge_score > 70 ? "CRITICAL" : "HIGH") +
      kpi("Forecast Window", STATE.filters.forecastWindow, "info") +
      kpi("Confidence", f.confidence + "%", "MEDIUM") +
      kpi("Risk", d.risk.level, d.risk.level, "Score " + d.risk.score) + "</div>";
    h += '<div class="toolbar" style="margin-top:14px">' + seg("forecastWindow", ["5 MIN", "10 MIN", "15 MIN", "30 MIN"], STATE.filters.forecastWindow) + "</div>";
    h += '<div class="grid g2">' + chartCard("Actual vs Predicted with Confidence Range", "sfMain", "Shaded band = confidence range", true) +
      card("Surge Formation", '<dl class="kv"><dt>WHERE</dt><dd>' + esc(f.surge_location) + "</dd><dt>WHEN</dt><dd>" + esc(f.surge_eta) +
        "</dd><dt>WHY</dt><dd>" + esc(f.factors[0]) + "</dd></dl>" +
        '<div class="section-title">Contributing Factors</div><div class="list">' + f.factors.map(function (x) {
          return '<div class="item"><b>' + esc(x) + '</b><div class="m">Contributing to predicted surge at ' + esc(f.surge_eta) + "</div></div>";
        }).join("") + "</div>") + "</div>";
    h += '<div class="grid g2" style="margin-top:12px">' + chartCard("Surge Score by Window", "sfScore", "Predicted surge score per forecast window") +
      chartCard("Factor Contribution", "sfFactors", "Relative contribution to predicted surge") + "</div>";
    return h;
  };
  PAGES["surge-forecast"].after = function (d) {
    var f = d.forecast, n = { "5 MIN": 8, "10 MIN": 10, "15 MIN": 12, "30 MIN": 16 }[STATE.filters.forecastWindow];
    var actual = f.series.slice(0, n), pred = f.predicted_series.slice(0, n);
    mkChart("sfMain", {
      type: "line", data: {
        labels: timeLabels(n, 5), datasets: [
          ds("Actual crowd", actual, C.blue),
          ds("Predicted crowd", pred, C.cyan),
          { label: "Confidence upper", data: pred.map(function (v) { return Math.round(v * 1.15); }), borderColor: "#38bdf866", backgroundColor: "#38bdf81f", fill: "+1", pointRadius: 0, borderWidth: 1 },
          { label: "Confidence lower", data: pred.map(function (v) { return Math.round(v * 0.85); }), borderColor: "#38bdf866", pointRadius: 0, borderWidth: 1 }
        ]
      }
    });
    mkChart("sfScore", { type: "bar", data: { labels: ["5 MIN", "10 MIN", "15 MIN", "30 MIN"], datasets: [{ label: "Surge score", data: [f.surge_score, f.surge_score + 6, f.surge_score + 4, f.surge_score - 8], backgroundColor: [C.orange, C.red, C.red, C.amber] }] } });
    mkChart("sfFactors", { type: "doughnut", data: { labels: f.factors, datasets: [{ data: f.factors.map(function (_, i) { return 30 - i * 4; }), backgroundColor: [C.red, C.orange, C.amber, C.blue, C.cyan] }] } });
  };

  /* -------------------------------------------------------- TRAIN INTELLIGENCE */
  PAGES["train-intelligence"] = function (d) {
    var t = d.schedule.trains;
    var delayed = t.filter(function (x) { return x.delay > 0; }).length;
    var hp = t.filter(function (x) { return x.pressure > 70; }).length;
    var h = head("Train Intelligence", "Train operations, coach position awareness and passenger-pressure analysis feeding crowd risk.");
    h += '<div class="grid g6">' +
      kpi("Active Trains", t.length, "info") + kpi("Arrivals +15 min", Math.min(4, t.length), "MEDIUM") +
      kpi("Departures +15 min", Math.min(3, t.length), "MEDIUM") + kpi("Delayed Trains", delayed, delayed > 2 ? "HIGH" : "MEDIUM") +
      kpi("High Pressure Trains", hp, hp ? "CRITICAL" : "LOW") + kpi("Simultaneous Arrivals", d.schedule.simultaneous, "CRITICAL") + "</div>";
    h += '<div class="toolbar" style="margin-top:14px">' + seg("timeline", ["NOW", "+5 MIN", "+10 MIN", "+15 MIN", "+30 MIN"], STATE.filters.timeline) +
      '<span class="mono">CLICK ANY TRAIN ROW FOR THE DETAIL PANEL</span></div>';
    h += card("Train Board", table(
      ["Train", "Name", "Type", "Arr", "Dep", "PF", "Delay", "Coach Pos", "Pressure", "Crowd Impact", "Risk"],
      t.map(function (x) {
        return ["<b>" + esc(x.number) + "</b>", esc(x.name), esc(x.type), esc(x.arrival), esc(x.departure), esc(x.platform),
          x.delay ? '<span style="color:#F59E0B">+' + x.delay + " min</span>" : "ON TIME", esc(x.coach_position),
          x.pressure, x.crowd_impact + " people", badge(x.risk)];
      }), function (i) { return 'data-train="' + t[i].number + '"'; }));
    h += '<div class="grid g2" style="margin-top:12px">' + chartCard("Train Movement Pressure", "tiPressure", "Pressure index per train") +
      chartCard("Arrival vs Departure Timeline", "tiTimeline", "Trains per time bucket") +
      chartCard("Platform Occupancy Pressure", "tiOcc", "Aggregated pressure per platform") +
      chartCard("Train Crowd Impact", "tiImpact", "Estimated people added to station crowd") + "</div>";
    h += '<div class="card" style="margin-top:12px"><h3>Impact Chain</h3><div class="flow"><b>TRAIN</b><span class="ar">→</span><b>PLATFORM</b><span class="ar">→</span><b>PASSENGER FLOW</b><span class="ar">→</span><b>CROWD IMPACT</b><span class="ar">→</span><b>RISK</b></div></div>';
    return h;
  };
  PAGES["train-intelligence"].after = function (d) {
    var t = d.schedule.trains;
    mkChart("tiPressure", { type: "bar", data: { labels: t.map(function (x) { return x.number; }), datasets: [{ label: "Pressure index", data: t.map(function (x) { return x.pressure; }), backgroundColor: t.map(function (x) { return colorFor(x.risk); }) }] } });
    mkChart("tiTimeline", { type: "line", data: { labels: ["NOW", "+5", "+10", "+15", "+30"], datasets: [ds("Arrivals", [1, 2, 3, 3, 4], C.cyan), ds("Departures", [1, 1, 2, 3, 3], C.orange)] } });
    var pf = {}; t.forEach(function (x) { pf[x.platform] = (pf[x.platform] || 0) + x.pressure; });
    mkChart("tiOcc", { type: "bar", data: { labels: Object.keys(pf).map(function (k) { return "PF " + k; }), datasets: [{ label: "Occupancy pressure", data: Object.keys(pf).map(function (k) { return pf[k]; }), backgroundColor: C.blue }] } });
    mkChart("tiImpact", { type: "line", data: { labels: t.map(function (x) { return x.number; }), datasets: [ds("Crowd impact (people)", t.map(function (x) { return x.crowd_impact; }), C.red, true)] } });
    Array.prototype.forEach.call(document.querySelectorAll("[data-train]"), function (row) {
      row.addEventListener("click", function () {
        var x = t.filter(function (y) { return y.number === row.getAttribute("data-train"); })[0];
        openDrawer("TRAIN " + x.number, '<dl class="kv">' +
          "<dt>Name</dt><dd>" + esc(x.name) + "</dd><dt>Type</dt><dd>" + esc(x.type) + "</dd><dt>Arrival</dt><dd>" + x.arrival +
          "</dd><dt>Departure</dt><dd>" + x.departure + "</dd><dt>Platform</dt><dd>" + x.platform + "</dd><dt>Delay</dt><dd>" + (x.delay ? "+" + x.delay + " min" : "ON TIME") +
          "</dd><dt>Coach composition</dt><dd>" + x.coaches + " coaches</dd><dt>Coach position</dt><dd>" + x.coach_position +
          "</dd><dt>Estimated load</dt><dd>" + x.load + " passengers</dd><dt>Unreserved coach</dt><dd>" + (x.unreserved ? badge("CRITICAL") + " YES" : "NO") +
          "</dd><dt>Expected crowd contribution</dt><dd>" + x.crowd_impact + " people</dd><dt>Risk impact</dt><dd>" + badge(x.risk) + "</dd></dl>" +
          '<div class="flow" style="margin-top:12px"><b>' + esc(x.number) + '</b><span class="ar">→</span><b>PF ' + x.platform + '</b><span class="ar">→</span><b>' + x.load +
          ' pax</b><span class="ar">→</span><b>+' + x.crowd_impact + ' crowd</b><span class="ar">→</span>' + badge(x.risk) + "</div>");
      });
    });
  };

  /* ---------------------------------------------------------------- BOTTLENECKS */
  PAGES["bottlenecks"] = function (d) {
    var b = d.platforms.bottlenecks;
    var cnt = function (s) { return b.filter(function (x) { return x.status === s; }).length; };
    var h = head("Bottlenecks", "Flow constraint detection across platforms, footbridges, gates, corridors and concourse.");
    h += '<div class="grid g4">' + kpi("Total Bottlenecks", b.length, "info") + kpi("Critical", cnt("CRITICAL"), "CRITICAL") +
      kpi("At Risk", cnt("AT RISK"), "HIGH") + kpi("Clear", cnt("CLEAR"), "LOW") + "</div>";
    h += '<div class="section-title">Station Flow Visualization</div><div class="card"><div class="grid g6">' +
      b.map(function (x) {
        return '<div class="item"><div class="row" style="justify-content:space-between"><b>' + esc(x.location) + "</b>" + badge(x.status) + "</div>" +
          '<div class="bar" style="margin:6px 0"><i style="width:' + x.density + "%;background:" + colorFor(x.status) + '"></i></div>' +
          '<div class="m">' + x.density + "% of " + x.capacity + " cap · flow " + x.flow + " p/min</div></div>";
      }).join("") + '</div><div class="legend-note">ENTRY → GATES → CONCOURSE → FOOTBRIDGE → PLATFORMS → EXIT</div></div>';
    h += '<div class="grid g2" style="margin-top:12px">' + card("Bottleneck Detail", table(["Location", "Density", "Capacity", "Flow", "Status", "Cause", "Recommended action"],
      b.map(function (x) { return [esc(x.location), x.density + "%", x.capacity, x.flow + " p/min", badge(x.status), esc(x.cause), esc(x.action)]; }))) +
      chartCard("Bottleneck Ranking", "bnRank", "Density % — highest risk first") + "</div>";
    h += '<div class="grid g2" style="margin-top:12px">' + chartCard("Bottleneck Timeline", "bnTime", "Density trend for top 3 locations") +
      card("Top Risk Locations", '<div class="list">' + b.slice().sort(function (x, y) { return y.density - x.density; }).slice(0, 3).map(function (x, i) {
        return '<div class="item"><b>#' + (i + 1) + " " + esc(x.location) + "</b> " + badge(x.status) + '<div class="m">' + esc(x.action) + "</div>" +
          '<button class="btn small" style="margin-top:6px" data-go="intervention-simulator">SIMULATE FIX</button></div>';
      }).join("") + "</div>") + "</div>";
    return h;
  };
  PAGES["bottlenecks"].after = function (d) {
    var b = d.platforms.bottlenecks.slice().sort(function (x, y) { return y.density - x.density; });
    mkChart("bnRank", { type: "bar", options: { indexAxis: "y" }, data: { labels: b.map(function (x) { return x.location; }), datasets: [{ label: "Density %", data: b.map(function (x) { return x.density; }), backgroundColor: b.map(function (x) { return colorFor(x.status); }) }] } });
    mkChart("bnTime", {
      type: "line", data: {
        labels: timeLabels(10, 3), datasets: b.slice(0, 3).map(function (x, i) {
          return ds(x.location, seq(seedOf(x.location), 10, Math.max(10, x.density - 35), x.density), [C.red, C.orange, C.amber][i]);
        })
      }
    });
  };

  /* --------------------------------------------------------------- GATE CONTROL */
  PAGES["gate-control"] = function (d) {
    var g = d.gates;
    var h = head("Gate Control", "Gate flow management. All control actions are SIMULATED — no physical railway hardware is connected.");
    h += '<div class="grid g4">' + kpi("Gates Monitored", g.length, "info") +
      kpi("Highest Gate Flow", Math.max.apply(null, g.map(function (x) { return x.flow; })) + " p/min", "HIGH") +
      kpi("Total Queue", g.reduce(function (a, x) { return a + x.queue; }, 0), "MEDIUM") +
      kpi("Recommended Gate Action", esc(d.platforms.recommended_gate), "HIGH") + "</div>";
    h += '<div class="grid g3" style="margin-top:12px">' + g.map(function (x, i) {
      return '<div class="card"><div class="row" style="justify-content:space-between"><h3>' + esc(x.name) + "</h3>" + badge(x.risk) + "</div>" +
        '<dl class="kv" style="margin-top:8px"><dt>Current flow</dt><dd>' + x.flow + " p/min</dd><dt>Queue</dt><dd>" + x.queue +
        "</dd><dt>Capacity</dt><dd>" + x.capacity + "</dd><dt>Density</dt><dd>" + x.density + "%</dd><dt>Current state</dt><dd>" + esc(x.state) +
        "</dd><dt>Recommended</dt><dd>" + badge(x.recommended) + "</dd></dl>" +
        '<div class="bar" style="margin:8px 0"><i style="width:' + x.density + "%;background:" + colorFor(x.risk) + '"></i></div>' +
        '<div class="row">' + ["OPEN", "RESTRICT", "REDIRECT", "CLOSE"].map(function (a) {
          return '<button class="btn small' + (a === "CLOSE" ? " btn-danger" : "") + '" data-gate="' + i + '" data-action="' + a + '">' + a + "</button>";
        }).join("") + "</div></div>";
    }).join("") + "</div>";
    h += '<div class="grid g2" style="margin-top:12px">' + chartCard("Gate Flow vs Capacity", "gcFlow", "People per minute against gate capacity") +
      chartCard("Queue Length by Gate", "gcQueue", "Passengers waiting") + "</div>";
    return h;
  };
  PAGES["gate-control"].after = function (d) {
    var g = d.gates;
    mkChart("gcFlow", { type: "bar", data: { labels: g.map(function (x) { return x.name; }), datasets: [{ label: "Flow p/min", data: g.map(function (x) { return x.flow; }), backgroundColor: C.blue }, { label: "Capacity index", data: g.map(function (x) { return Math.round(x.capacity / 2); }), backgroundColor: "#003EA8" }] } });
    mkChart("gcQueue", { type: "line", data: { labels: g.map(function (x) { return x.name; }), datasets: [ds("Queue", g.map(function (x) { return x.queue; }), C.orange, true)] } });
    Array.prototype.forEach.call(document.querySelectorAll("[data-gate]"), function (btn) {
      btn.addEventListener("click", function () {
        var gate = g[+btn.getAttribute("data-gate")], action = btn.getAttribute("data-action");
        openModal("CONFIRM GATE ACTION — SIMULATED",
          "<p>Apply <b>" + action + "</b> to <b>" + esc(gate.name) + "</b>?</p>" +
          '<p class="mono">NO PHYSICAL GATE WILL BE OPERATED. RAILWAY HARDWARE NOT CONNECTED.</p>',
          [{ label: "CANCEL", cls: "btn" }, {
            label: "SIMULATE ACTION", cls: "btn btn-primary", fn: function () {
              var factor = action === "OPEN" ? 1.2 : action === "RESTRICT" ? 0.6 : action === "REDIRECT" ? 0.75 : 0.15;
              var after = Math.round(gate.flow * factor), risk = after > 80 ? "CRITICAL" : after > 60 ? "HIGH" : after > 40 ? "MEDIUM" : "LOW";
              openModal("SIMULATION RESULT — " + gate.name,
                '<span class="badge badge-sim">SIMULATED</span><dl class="kv" style="margin-top:10px">' +
                "<dt>Action</dt><dd>" + action + "</dd><dt>Flow before</dt><dd>" + gate.flow + " p/min</dd><dt>Flow after</dt><dd>" + after +
                " p/min</dd><dt>Projected crowd change</dt><dd>" + (after - gate.flow) * 3 + " people</dd><dt>Risk before</dt><dd>" + badge(gate.risk) +
                "</dd><dt>Projected risk</dt><dd>" + badge(risk) + "</dd><dt>Emergency access effect</dt><dd>" +
                (action === "CLOSE" ? "CORRIDOR LOAD INCREASES — REVIEW" : "CORRIDOR PRESSURE REDUCED") + "</dd></dl>",
                [{ label: "CLOSE", cls: "btn" }]);
              toast("Gate action simulated — no physical action performed.", "warn");
            }
          }]);
      });
    });
  };

  /* --------------------------------------------------------- PLATFORM ALLOCATION */
  PAGES["platform-allocation"] = function (d) {
    var p = d.platforms.list;
    var h = head("Platform Allocation", "Current allocation versus AI-recommended allocation, with the reasons behind each recommendation.");
    h += '<div class="grid g4">' + kpi("Platforms", p.length, "info") +
      kpi("Critical Platforms", p.filter(function (x) { return x.level === "CRITICAL"; }).length, "CRITICAL") +
      kpi("Recommended Platform", esc(d.platforms.recommended_platform), "LOW") +
      kpi("Recommended Gate", esc(d.platforms.recommended_gate), "HIGH") + "</div>";
    h += '<div class="card" style="margin-top:12px"><h3>Platform Board</h3>' + table(
      ["Platform", "Crowd", "Capacity", "Density", "Next train", "Arrival", "Risk", "Current allocation", "Recommended action"],
      p.map(function (x) { return [esc(x.name), x.crowd, x.capacity, x.density + "%", esc(x.next_train), esc(x.arrival), badge(x.level), esc(x.allocation), esc(x.recommended)]; }),
      function (i) { return 'data-pf="' + i + '"'; }) + "</div>";
    h += '<div class="grid g2" style="margin-top:12px">' +
      card("Current vs Recommended Allocation", table(["Train", "Current", "Recommended", "Reason"],
        d.schedule.trains.slice(0, 6).map(function (t) {
          var cur = "PLATFORM " + t.platform, rec = t.pressure > 70 ? d.platforms.recommended_platform : cur;
          return [esc(t.number), cur, rec === cur ? cur + " (no change)" : "<b>" + rec + "</b>",
            t.pressure > 70 ? "High passenger pressure + platform density" : "Within capacity"];
        }))) +
      chartCard("Platform Comparison", "paCompare", "Crowd vs capacity per platform") + "</div>";
    h += '<div class="card" style="margin-top:12px"><h3>Recommendation Reasons</h3><div class="grid g3" style="margin-top:8px">' +
      ["Crowd", "Train Schedule", "Passenger Flow", "Capacity", "Emergency Access"].map(function (r) {
        return '<div class="item"><b>' + r + "</b><div class=\"m\">Factored into the recommendation engine output for " + esc(STATE.station.name) + ".</div></div>";
      }).join("") + "</div></div>";
    return h;
  };
  PAGES["platform-allocation"].after = function (d) {
    var p = d.platforms.list;
    mkChart("paCompare", { type: "bar", data: { labels: p.map(function (x) { return x.name; }), datasets: [{ label: "Crowd (people)", data: p.map(function (x) { return x.crowd; }), backgroundColor: p.map(function (x) { return colorFor(x.level); }) }, { label: "Capacity", data: p.map(function (x) { return x.capacity; }), backgroundColor: "#003EA8" }] } });
    Array.prototype.forEach.call(document.querySelectorAll("[data-pf]"), function (row) {
      row.addEventListener("click", function () {
        var x = p[+row.getAttribute("data-pf")];
        openDrawer(x.name, '<dl class="kv"><dt>Crowd</dt><dd>' + x.crowd + "</dd><dt>Capacity</dt><dd>" + x.capacity + "</dd><dt>Density</dt><dd>" + x.density +
          "%</dd><dt>Risk</dt><dd>" + badge(x.level) + "</dd><dt>Next train</dt><dd>" + x.next_train + " @ " + x.arrival +
          "</dd><dt>Recommended</dt><dd>" + esc(x.recommended) + "</dd></dl>");
      });
    });
  };

  /* -------------------------------------------------------------- ANNOUNCEMENTS */
  PAGES["announcements"] = function (d) {
    var lang = RailMindState.currentLanguage, text = currentAnnouncement(d), alertText = currentPassengerAlert(d);
    var h = head("Announcements", "Multilingual passenger guidance. Text, voice text and voice language always follow the selected language. Broadcast requires a connected railway PA backend — previews only.");
    h += '<div class="toolbar">' + seg("lang", ["ENGLISH", "हिंदी", "मराठी"], langLabel(lang)) +
      '<button class="btn btn-primary" id="playAnn" aria-label="Play announcement in selected language">▶ PLAY</button>' +
      '<button class="btn" id="testVoice" aria-label="Test voice in selected language">TEST VOICE</button>' +
      '<button class="btn" id="broadcastAnn">BROADCAST (DEMO)</button>' +
      '<button class="btn" id="annVoiceToggle" aria-label="Toggle voice mode">VOICE ' + (RailMindState.voiceEnabled ? "ON" : "OFF") + '</button>' +
      '<span class="chip mono">VOICE LANG ' + voiceLanguageMap[lang] + '</span></div>';
    h += '<div class="grid g2">' + card("Announcement Preview", '<textarea id="annText" rows="5" style="width:100%" aria-label="Announcement text">' + esc(text) + "</textarea>" +
      '<div class="legend-note">Text comes from the master JSON for ' + esc(langLabel(lang)) + '. PLAY speaks it with ' + voiceLanguageMap[lang] + ' speech synthesis.</div>') +
      card("Passenger Alert", '<div class="item">' + esc(alertText) + "</div>" +
        '<div class="row" style="margin-top:8px"><button class="btn small" id="playAlert">▶ PLAY ALERT</button></div>') +
      card("Station Display Preview", '<div class="item" style="font-size:16px;letter-spacing:.04em"><div class="mono">' + esc(STATE.station.name) +
        ' · DISPLAY BOARD</div><div style="margin-top:8px">' + esc(text) + "</div></div>" + '<span class="badge badge-warn" style="margin-top:8px;display:inline-block">DISPLAY BACKEND NOT CONNECTED</span>') +
      card("Mobile Alert Preview", '<div class="item"><b>RailMind AI</b><div class="m">' + esc(text) + "</div></div>" + badge("NOT CONNECTED")) +
      card("SMS Preview", '<div class="item mono" style="color:#FFFFFF">' + esc(String(text).slice(0, 160)) + "</div>" + badge("NOT CONNECTED")) +
      card("WhatsApp Preview", '<div class="item"><b>RailMind AI Station Bot</b><div class="m">' + esc(text) + "</div></div>" + badge("NOT CONNECTED")) +
      card("Delivery Channels", d.delivery_channels.map(function (c) { return '<div class="switch"><span>' + esc(c.channel) + "</span>" + badge(c.status) + "</div>"; }).join("")) +
      "</div>";
    return h;
  };
  PAGES["announcements"].after = function (d) {
    on("#playAnn", "click", function () { speak($("#annText").value); toast("Playing announcement (" + voiceLanguageMap[RailMindState.currentLanguage] + ")."); });
    on("#playAlert", "click", function () { speak(currentPassengerAlert(d)); });
    on("#testVoice", "click", function () { speak(TEST_PHRASE[RailMindState.currentLanguage]); });
    on("#annVoiceToggle", "click", function () {
      RailMindState.voiceEnabled = !RailMindState.voiceEnabled; persistVoice();
      if (!RailMindState.voiceEnabled) stopSpeech();
      toast("Voice mode " + (RailMindState.voiceEnabled ? "ON" : "OFF") + "."); render();
    });
    on("#broadcastAnn", "click", function () {
      openModal("BROADCAST — DEMO", "<p>Broadcast to station PA, displays, SMS and WhatsApp?</p><p class=\"mono\">NO MESSAGE WILL ACTUALLY BE SENT. ANNOUNCEMENT BACKEND NOT CONNECTED.</p>",
        [{ label: "CANCEL", cls: "btn" }, { label: "SIMULATE BROADCAST", cls: "btn btn-primary", fn: function () { toast("Announcement broadcast initiated — DEMO, nothing was actually sent.", "warn"); } }]);
    });
  };

  /* --------------------------------------------------------------------- ALERTS */
  var alertFilter = { risk: "ALL", status: "ALL" };
  PAGES["alerts"] = function (d) {
    var a = d.alerts.filter(function (x) {
      return (alertFilter.risk === "ALL" || x.risk === alertFilter.risk) && (alertFilter.status === "ALL" || x.status === alertFilter.status);
    });
    var h = head("Alerts & Notifications", "Operator alert queue with acknowledge / resolve workflow and full alert detail.");
    h += '<div class="grid g4">' +
      kpi("Critical", d.alerts.filter(function (x) { return x.risk === "CRITICAL" && x.status !== "RESOLVED"; }).length, "CRITICAL") +
      kpi("High", d.alerts.filter(function (x) { return x.risk === "HIGH" && x.status !== "RESOLVED"; }).length, "HIGH") +
      kpi("Medium", d.alerts.filter(function (x) { return x.risk === "MEDIUM" && x.status !== "RESOLVED"; }).length, "MEDIUM") +
      kpi("Resolved", d.alerts.filter(function (x) { return x.status === "RESOLVED"; }).length, "LOW") + "</div>";
    h += '<div class="toolbar" style="margin-top:14px">' + seg("alertRisk", ["ALL", "CRITICAL", "HIGH", "MEDIUM"], alertFilter.risk) +
      seg("alertStatus", ["ALL", "OPEN", "ACKNOWLEDGED", "RESOLVED"], alertFilter.status) +
      '<span class="chip mono">STATION ' + esc(STATE.station.code) + "</span></div>";
    h += a.length ? '<div class="list">' + a.map(function (x) {
      return '<div class="item"><div class="row" style="justify-content:space-between"><div><b>' + esc(x.time) + " · " + esc(x.location) + "</b> " + badge(x.risk) + " " + badge(x.status) +
        '<div class="m">' + esc(x.message) + '</div><div class="mono">WHY: ' + esc(x.reason) + " · ACTION: " + esc(x.action) + "</div></div>" +
        '<div class="row"><button class="btn small" data-ack="' + x.id + '">ACKNOWLEDGE</button><button class="btn small" data-res="' + x.id +
        '">RESOLVE</button><button class="btn small btn-primary" data-det="' + x.id + '">VIEW DETAILS</button></div></div></div>';
    }).join("") + "</div>" : '<div class="empty">NO DATA AVAILABLE FOR THE SELECTED FILTERS</div>';
    h += '<div class="grid g2" style="margin-top:12px">' + chartCard("Alerts by Risk", "alRisk", "Current alert queue") + chartCard("Alerts Over Time", "alTime", "Alerts raised per 10-minute bucket") + "</div>";
    return h;
  };
  PAGES["alerts"].after = function (d) {
    var bands = ["CRITICAL", "HIGH", "MEDIUM"];
    mkChart("alRisk", { type: "doughnut", data: { labels: bands, datasets: [{ data: bands.map(function (b) { return d.alerts.filter(function (x) { return x.risk === b; }).length; }), backgroundColor: [C.red, C.orange, C.amber] }] } });
    mkChart("alTime", { type: "bar", data: { labels: ["17:50", "18:00", "18:10", "18:20", "18:30", "18:40"], datasets: [{ label: "Alerts", data: [1, 0, 1, 1, 2, 1], backgroundColor: C.blue }] } });
    function find(id) { return d.alerts.filter(function (x) { return x.id === id; })[0]; }
    bind("[data-ack]", "data-ack", function (x) { x.status = "ACKNOWLEDGED"; toast("Alert " + x.id + " acknowledged."); render(); });
    bind("[data-res]", "data-res", function (x) { x.status = "RESOLVED"; toast("Alert " + x.id + " resolved."); render(); });
    bind("[data-det]", "data-det", function (x) {
      openDrawer("ALERT " + x.id, '<dl class="kv"><dt>Time</dt><dd>' + x.time + "</dd><dt>Station</dt><dd>" + x.station + "</dd><dt>Location</dt><dd>" + esc(x.location) +
        "</dd><dt>Risk</dt><dd>" + badge(x.risk) + "</dd><dt>Status</dt><dd>" + badge(x.status) + "</dd></dl><p>" + esc(x.message) + "</p>" +
        '<div class="mono">REASON: ' + esc(x.reason) + '</div><div class="mono" style="margin-top:4px">RECOMMENDED ACTION: ' + esc(x.action) + "</div>" +
        '<button class="btn btn-primary" style="margin-top:12px" data-go="intervention-simulator">SIMULATE INTERVENTION</button>');
    });
    function bind(sel, attr, fn) {
      Array.prototype.forEach.call(document.querySelectorAll(sel), function (b) {
        b.addEventListener("click", function () { fn(find(b.getAttribute(attr))); });
      });
    }
  };

  /* ----------------------------------------------------------- EMERGENCY ACCESS */
  PAGES["emergency-access"] = function (d) {
    var e = d.platforms.emergency_corridor;
    var cnt = function (s) { return e.filter(function (x) { return x.status === s; }).length; };
    var h = head("Emergency Access", "Emergency corridor, exit route and critical access monitoring. Always evaluated inside intervention logic.");
    h += '<div class="grid g4">' + kpi("Clear Corridors", cnt("CLEAR"), "LOW") + kpi("At-Risk Corridors", cnt("AT RISK"), "HIGH") +
      kpi("Blocked Corridors", cnt("BLOCKED"), "CRITICAL") + kpi("Emergency Access Risk", cnt("BLOCKED") ? "HIGH" : cnt("AT RISK") ? "MEDIUM" : "LOW", cnt("BLOCKED") ? "HIGH" : "MEDIUM") + "</div>";
    h += '<div class="card" style="margin-top:12px"><h3>Emergency Corridor Map</h3><div class="grid g4" style="margin-top:8px">' +
      e.map(function (x) {
        return '<div class="item" style="border-color:' + colorFor(x.status) + '"><div class="row" style="justify-content:space-between"><b>' + esc(x.name) + "</b>" + badge(x.status) +
          '</div><div class="m">Access risk: ' + esc(x.access_risk) + "</div><div class=\"mono\">ACTION: " + esc(x.action) + "</div></div>";
      }).join("") + '</div><div class="legend-note">CLEAR · AT RISK · BLOCKED — corridor status drives intervention scoring.</div></div>';
    h += '<div class="grid g2" style="margin-top:12px">' + chartCard("Corridor Status Distribution", "eaStatus", "Corridors per status") +
      card("Exit Routes & Critical Areas", table(["Route", "Status", "Access risk", "Recommended action"],
        e.map(function (x) { return [esc(x.name), badge(x.status), esc(x.access_risk), esc(x.action)]; }))) + "</div>";
    return h;
  };
  PAGES["emergency-access"].after = function (d) {
    var e = d.platforms.emergency_corridor, st = ["CLEAR", "AT RISK", "BLOCKED"];
    mkChart("eaStatus", { type: "doughnut", data: { labels: st, datasets: [{ data: st.map(function (s) { return e.filter(function (x) { return x.status === s; }).length; }), backgroundColor: [C.green, C.orange, C.red] }] } });
  };

  /* ------------------------------------------------------ INTERVENTION SIMULATOR */
  var SIM_ACTIONS = ["Open Gate B", "Restrict Gate A", "Redirect Platform", "Platform Guidance", "Passenger Announcement", "Change Passenger Route"];
  var simSel = { "Restrict Gate A": true, "Platform Guidance": true };
  PAGES["intervention-simulator"] = function (d) {
    var iv = d.intervention, res = STATE.lastSim;
    var h = head("Intervention Simulator", "Model the effect of operator actions before committing. All projections are SIMULATED.");
    h += '<div class="grid g4">' + kpi("Current Crowd", d.crowd.current, "info", "BEFORE ACTION") +
      kpi("Forecast Crowd", d.forecast.predicted, "HIGH", "BEFORE ACTION") + kpi("Risk", d.risk.level, d.risk.level, "Score " + d.risk.score) +
      kpi("Train Pressure", d.schedule.pressure["15"], "HIGH", "15-minute window") + "</div>";
    h += '<div class="grid g2" style="margin-top:12px">' + card("Select Interventions",
      SIM_ACTIONS.map(function (a) {
        return '<label class="switch"><span>' + a + '</span><input type="checkbox" data-act="' + a + '"' + (simSel[a] ? " checked" : "") + "></label>";
      }).join("") + '<button class="btn btn-primary" id="simBtn" style="margin-top:12px">SIMULATE INTERVENTION</button>' +
      '<div class="legend-note">Recommended by engine: ' + esc(iv.recommended) + "</div>") +
      card("After Action (SIMULATED)", res ? '<span class="badge badge-sim">SIMULATED</span><dl class="kv" style="margin-top:10px">' +
        "<dt>Projected crowd</dt><dd>" + res.after + " people</dd><dt>Crowd reduction</dt><dd>" + res.reduction + " (" + res.pct + "%)</dd>" +
        "<dt>Projected risk</dt><dd>" + badge(res.risk) + "</dd><dt>Flow improvement</dt><dd>" + res.flow + "%</dd>" +
        "<dt>Emergency access effect</dt><dd>" + esc(res.emergency) + "</dd></dl>" :
        '<div class="empty">SELECT ACTIONS AND RUN A SIMULATION</div>') + "</div>";
    h += '<div style="margin-top:12px">' + chartCard("Current vs Forecast vs After Intervention", "ivChart", "People — after-intervention series is SIMULATED", true) + "</div>";
    return h;
  };
  PAGES["intervention-simulator"].after = function (d) {
    Array.prototype.forEach.call(document.querySelectorAll("[data-act]"), function (cb) {
      cb.addEventListener("change", function () { simSel[cb.getAttribute("data-act")] = cb.checked; });
    });
    on("#simBtn", "click", function () {
      var chosen = Object.keys(simSel).filter(function (k) { return simSel[k]; });
      if (!chosen.length) { toast("Select at least one intervention.", "warn"); return; }
      var base = d.forecast.predicted, factor = Math.max(0.4, 1 - chosen.length * 0.12);
      var after = Math.round(base * factor * 100) / 100;
      STATE.lastSim = {
        after: after, reduction: Math.round((base - after) * 100) / 100, pct: Math.round((1 - factor) * 100),
        risk: factor > 0.8 ? "HIGH" : factor > 0.6 ? "MEDIUM" : "LOW", flow: chosen.length * 9,
        emergency: chosen.indexOf("Restrict Gate A") > -1 ? "CORRIDOR PRESSURE REDUCED" : "CORRIDOR UNCHANGED — REVIEW"
      };
      toast("Intervention simulated — no physical railway action performed.", "warn");
      render();
    });
    var res = STATE.lastSim;
    mkChart("ivChart", {
      type: "line", data: {
        labels: timeLabels(10, 3), datasets: [
          ds("Current", d.forecast.series.slice(0, 10), C.blue),
          ds("Forecast", d.forecast.predicted_series.slice(0, 10), C.orange),
          ds("After intervention (SIMULATED)", d.forecast.predicted_series.slice(0, 10).map(function (v) { return Math.round(v * (res ? (1 - res.pct / 100) : 0.65)); }), C.green, true)
        ]
      }
    });
  };

  /* ------------------------------------------------------- POST EVENT ANALYTICS */
  PAGES["post-event-analytics"] = function (d) {
    var p = d.post_event;
    var h = head("Post Event Analytics", "Did the intervention actually reduce crowd and risk? Evaluation of the last surge event.");
    h += '<div class="grid g4">' + kpi("Peak Crowd", p.peak_crowd, "HIGH") + kpi("Peak Risk", p.peak_risk + " / 100", "CRITICAL") +
      kpi("Surge Duration", esc(p.surge_duration), "MEDIUM") + kpi("Intervention Time", esc(p.intervention_time), "info") +
      kpi("Crowd Reduction", p.crowd_reduction + "%", "LOW") + kpi("Risk Reduction", p.risk_reduction + "%", "LOW") +
      kpi("Response Time", esc(p.response_time), "MEDIUM") + kpi("Emergency Corridor", esc(p.corridor_status), "LOW") + "</div>";
    h += '<div class="grid g2" style="margin-top:12px">' + chartCard("Crowd Before vs After", "peCrowd", "People per interval") +
      chartCard("Risk Before vs After", "peRisk", "Risk score 0-100") +
      chartCard("Flow Recovery", "peFlow", "Flow rate recovery after intervention") +
      chartCard("Intervention Effectiveness", "peEff", "Percentage improvement per action") + "</div>";
    h += '<div class="grid g3" style="margin-top:12px">' +
      card("What Worked?", '<div class="list">' + p.worked.map(function (x) { return '<div class="item">' + esc(x) + "</div>"; }).join("") + "</div>") +
      card("What Failed?", '<div class="list">' + p.failed.map(function (x) { return '<div class="item">' + esc(x) + "</div>"; }).join("") + "</div>") +
      card("What Should Be Improved?", '<div class="list">' + p.improve.map(function (x) { return '<div class="item">' + esc(x) + "</div>"; }).join("") + "</div>") + "</div>";
    return h;
  };
  PAGES["post-event-analytics"].after = function (d) {
    var p = d.post_event, l = timeLabels(10, 2);
    mkChart("peCrowd", { type: "line", data: { labels: l, datasets: [ds("Before", p.before, C.red), ds("After", p.after, C.green, true)] } });
    mkChart("peRisk", { type: "bar", data: { labels: ["BEFORE", "AFTER"], datasets: [{ label: "Risk score", data: [p.peak_risk, Math.round(p.peak_risk * (1 - p.risk_reduction / 100))], backgroundColor: [C.red, C.green] }] } });
    mkChart("peFlow", { type: "line", data: { labels: l, datasets: [ds("Flow (p/min)", p.after.map(function (v) { return Math.round(v / 2 + 20); }), C.cyan, true)] } });
    mkChart("peEff", { type: "bar", options: { indexAxis: "y" }, data: { labels: ["Gate regulation", "Platform diversion", "Announcement", "Staff deployment"], datasets: [{ label: "Improvement %", data: [34, 28, 17, 12], backgroundColor: C.blue }] } });
  };

  /* -------------------------------------------------------- AI MODEL PERFORMANCE */
  PAGES["ai-model-performance"] = function (d) {
    var m = d.model, connected = m.accuracy !== null && m.accuracy !== undefined;
    var h = head("AI Model Performance", "Detection, forecast and risk model metrics. Metrics are only shown when the backend reports them.");
    h += '<div class="grid g4">' + kpi("Model Status", na(m.status === "NOT CONNECTED" ? null : m.status), "MEDIUM") +
      kpi("Model Version", na(m.version), "info") + kpi("Prediction Accuracy", na(m.accuracy, "%"), "info") +
      kpi("Forecast Confidence", na(m.confidence, "%"), "info") + kpi("Precision", na(m.precision, "%"), "info") +
      kpi("Recall", na(m.recall, "%"), "info") + kpi("F1 Score", na(m.f1), "info") + kpi("Detection FPS", na(m.fps), "info") + "</div>";
    h += '<div class="card" style="margin-top:12px"><h3>Engine Status</h3><div class="grid g4" style="margin-top:8px">' +
      m.engines.map(function (e) { return '<div class="item"><b>' + esc(e.name) + "</b><div>" + badge(e.status) + "</div></div>"; }).join("") + "</div></div>";
    h += connected ? '<div class="grid g2" style="margin-top:12px">' + chartCard("Accuracy Trend", "mpAcc") + chartCard("Prediction Error", "mpErr") +
      chartCard("Latency", "mpLat") + chartCard("Confidence Distribution", "mpConf") + "</div>"
      : '<div class="empty" style="margin-top:12px">METRICS NOT CONNECTED — Accuracy, precision, recall, F1, latency and confidence charts will populate once the ML backend reports real values. No metrics are fabricated.</div>';
    return h;
  };
  PAGES["ai-model-performance"].after = function (d) {
    var m = d.model; if (m.accuracy === null || m.accuracy === undefined) return;
    mkChart("mpAcc", { type: "line", data: { labels: timeLabels(10, 30), datasets: [ds("Accuracy %", m.accuracy_trend || [], C.green)] } });
    mkChart("mpErr", { type: "bar", data: { labels: timeLabels(10, 30), datasets: [{ label: "Error", data: m.error_trend || [], backgroundColor: C.orange }] } });
    mkChart("mpLat", { type: "line", data: { labels: timeLabels(10, 30), datasets: [ds("Latency ms", m.latency_trend || [], C.cyan)] } });
    mkChart("mpConf", { type: "doughnut", data: { labels: ["High", "Medium", "Low"], datasets: [{ data: m.confidence_dist || [], backgroundColor: [C.green, C.amber, C.red] }] } });
  };

  /* ---------------------------------------------------------------- SYSTEM STATUS */
  PAGES["system-status"] = function (d) {
    var s = d.system;
    var cnt = function (v) { return s.filter(function (x) { return x.status === v; }).length; };
    var h = head("System Status", "Technical health of the RailMind AI pipeline services. Values come from backend health where available.");
    h += '<div class="grid g4">' + kpi("Services", s.length, "info") + kpi("Online", cnt("ONLINE"), "LOW") +
      kpi("Degraded", cnt("DEGRADED"), "MEDIUM") + kpi("Offline", cnt("OFFLINE"), "CRITICAL") + "</div>";
    h += '<div class="card" style="margin-top:12px"><h3>Service Health</h3>' + table(["Service", "Status", "Latency", "Last updated", "Requests", "Errors"],
      s.map(function (x) { return [esc(x.service), badge(x.status), na(x.latency, " ms"), x.status === "OFFLINE" ? '<span class="mono">—</span>' : "just now", x.requests, x.errors]; })) +
      '<div class="row" style="margin-top:10px"><button class="btn btn-primary" id="pingBtn">RUN HEALTH CHECK</button><span class="mono">GET ' + API_BASE + EP.health + "</span></div></div>";
    h += '<div class="grid g2" style="margin-top:12px">' + chartCard("Service Availability", "ssAvail", "Services per status") +
      card("Pipeline", '<div class="flow"><b>CCTV</b><span class="ar">→</span><b>FASTAPI</b><span class="ar">→</span><b>YOLO / CV</b><span class="ar">→</span><b>CROWD ANALYSIS</b><span class="ar">→</span><b>FORECASTING</b><span class="ar">→</span><b>RISK ENGINE</b><span class="ar">→</span><b>RECOMMENDATION</b><span class="ar">→</span><b>MASTER JSON</b><span class="ar">→</span><b>DASHBOARD</b></div>') + "</div>";
    return h;
  };
  PAGES["system-status"].after = function (d) {
    var st = ["ONLINE", "DEGRADED", "OFFLINE"];
    mkChart("ssAvail", { type: "doughnut", data: { labels: st, datasets: [{ data: st.map(function (v) { return d.system.filter(function (x) { return x.status === v; }).length; }), backgroundColor: [C.green, C.amber, C.red] }] } });
    on("#pingBtn", "click", function () {
      toast("Checking Railway Intelligence Engine…");
      api(EP.health, {}, 3000).then(function () { toast("Backend reachable."); loadMaster(); })
        .catch(function () { toast("BACKEND OFFLINE — unable to connect to Railway Intelligence Engine.", "err"); });
    });
  };

  /* --------------------------------------------------------------------- REPORTS */
  var REPORTS = ["Daily Crowd Report", "Surge Event Report", "Train Pressure Report", "Intervention Report", "Station Safety Report", "Post Event Report"];
  PAGES["reports"] = function (d) {
    var h = head("Reports", "Operational reporting. Report generation requires the backend — nothing is claimed as generated when it is not.");
    h += '<div class="card"><h3>Filters</h3><div class="row" style="margin-top:8px">' +
      '<input type="date" id="rpDate" aria-label="Report date" />' +
      '<select id="rpStation">' + STATIONS.map(function (s) { return '<option' + (s.code === STATE.station.code ? " selected" : "") + ">" + s.name + "</option>"; }).join("") + "</select>" +
      '<select id="rpPlatform"><option>ALL PLATFORMS</option>' + d.platforms.list.map(function (p) { return "<option>" + p.name + "</option>"; }).join("") + "</select>" +
      '<select id="rpTrain"><option>ALL TRAINS</option>' + d.schedule.trains.map(function (t) { return "<option>" + t.number + " " + esc(t.name) + "</option>"; }).join("") + "</select>" +
      '<select id="rpType"><option>ALL EVENT TYPES</option><option>SURGE</option><option>INTERVENTION</option><option>BOTTLENECK</option></select></div></div>';
    h += '<div class="grid g3" style="margin-top:12px">' + REPORTS.map(function (r) {
      return '<div class="card"><h3>' + r + '</h3><div class="sub">Scope: ' + esc(STATE.station.name) + '</div><div class="row" style="margin-top:10px">' +
        '<button class="btn" data-report="VIEW" data-name="' + r + '">VIEW</button>' +
        '<button class="btn btn-primary" data-report="GENERATE" data-name="' + r + '">GENERATE</button>' +
        '<button class="btn" data-report="DOWNLOAD" data-name="' + r + '">DOWNLOAD</button></div></div>';
    }).join("") + "</div>";
    h += '<div style="margin-top:12px">' + chartCard("Report Coverage (events per day)", "rpChart", "Recorded events available for reporting") + "</div>";
    return h;
  };
  PAGES["reports"].after = function (d) {
    mkChart("rpChart", { type: "bar", data: { labels: ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"], datasets: [{ label: "Surge events", data: seq(seedOf(STATE.station.code), 7, 1, 9), backgroundColor: C.blue }] } });
    Array.prototype.forEach.call(document.querySelectorAll("[data-report]"), function (b) {
      b.addEventListener("click", function () {
        var kind = b.getAttribute("data-report"), name = b.getAttribute("data-name");
        if (STATE.mode !== "live") {
          openModal(name, '<p class="mono">REPORT GENERATION NOT CONNECTED</p><p>The reporting backend is offline, so this report was <b>not</b> generated or downloaded. ' +
            "Below is a preview of the demo data currently loaded for " + esc(STATE.station.name) + ".</p>" +
            '<dl class="kv"><dt>Peak crowd</dt><dd>' + d.crowd.peak + "</dd><dt>Risk score</dt><dd>" + d.risk.score +
            "</dd><dt>Surge score</dt><dd>" + d.forecast.surge_score + "</dd><dt>Bottlenecks</dt><dd>" + d.platforms.bottlenecks.length + "</dd></dl>",
            [{ label: "CLOSE", cls: "btn" }]);
          return;
        }
        toast(kind + " requested from backend for " + name + ".");
      });
    });
  };

  /* -------------------------------------------------------------------- SETTINGS */
  PAGES["settings"] = function (d) {
    var s = STATE.settings;
    var h = head("Settings", "Station configuration, thresholds, forecast behaviour and display preferences. Saved locally in this browser.");
    h += '<div class="grid g2">';
    h += card("Station Configuration", '<div class="switch"><span>Default station</span><select id="setStation">' +
      STATIONS.map(function (x) { return '<option' + (x.code === STATE.station.code ? " selected" : "") + ">" + x.name + "</option>"; }).join("") + "</select></div>" +
      '<div class="switch"><span>Station code</span><span class="chip mono">' + esc(STATE.station.code) + "</span></div>" +
      '<div class="switch"><span>Platforms</span><span>' + STATE.station.platforms + "</span></div>" +
      '<div class="switch"><span>Backend base URL</span><span class="mono">' + esc(API_BASE) + "</span></div>");
    h += card("Alert & Risk Thresholds",
      thr("warnThreshold", "Warning threshold", s.warnThreshold) + thr("highThreshold", "High threshold", s.highThreshold) + thr("critThreshold", "Critical threshold", s.critThreshold));
    h += card("Forecast Settings", '<div class="switch"><span>Forecast horizon (minutes)</span><select id="setHorizon">' +
      [5, 10, 15, 30].map(function (v) { return '<option' + (v === s.forecastHorizon ? " selected" : "") + ">" + v + "</option>"; }).join("") + "</select></div>" +
      '<div class="switch"><span>Auto refresh master JSON (30 s)</span><input type="checkbox" id="setAuto"' + (s.autoRefresh ? " checked" : "") + "></div>");
    h += card("Language & Notifications", '<div class="switch"><span>Announcement language</span><select id="setLang">' +
      ["ENGLISH", "हिंदी", "मराठी"].map(function (v) { return '<option' + (v === s.language ? " selected" : "") + ">" + v + "</option>"; }).join("") + "</select></div>" +
      '<div class="switch"><span>Sound alerts</span><input type="checkbox" id="setSound"' + (s.sound ? " checked" : "") + "></div>" +
      '<div class="switch"><span>SMS notifications</span><input type="checkbox" id="setSms"' + (s.sms ? " checked" : "") + "></div>" +
      '<div class="switch"><span>WhatsApp notifications</span><input type="checkbox" id="setWa"' + (s.whatsapp ? " checked" : "") + "></div>" +
      '<div class="switch"><span>Station PA</span><input type="checkbox" id="setPa"' + (s.pa ? " checked" : "") + "></div>");
    h += card("Voice & Speech",
      '<div class="switch"><span>Voice mode</span><input type="checkbox" id="setVoiceOn" aria-label="Enable voice mode"' + (RailMindState.voiceEnabled ? " checked" : "") + "></div>" +
      '<div class="switch"><span>Voice / announcement language</span><select id="setVoiceLang" aria-label="Select language">' +
      LANGS.map(function (L) { return '<option value="' + L.key + '"' + (L.key === RailMindState.currentLanguage ? " selected" : "") + ">" + L.label + " (" + L.voice + ")</option>"; }).join("") + "</select></div>" +
      '<div class="switch"><span>Volume</span><span class="row"><input type="range" min="0" max="1" step="0.05" id="setVol" value="' + RailMindState.voiceVolume + '" aria-label="Voice volume"><b id="setVolV">' + RailMindState.voiceVolume + "</b></span></div>" +
      '<div class="switch"><span>Speech rate</span><span class="row"><input type="range" min="0.5" max="2" step="0.05" id="setRate" value="' + RailMindState.voiceRate + '" aria-label="Speech rate"><b id="setRateV">' + RailMindState.voiceRate + "</b></span></div>" +
      '<div class="switch"><span>Pitch</span><span class="row"><input type="range" min="0" max="2" step="0.05" id="setPitch" value="' + RailMindState.voicePitch + '" aria-label="Voice pitch"><b id="setPitchV">' + RailMindState.voicePitch + "</b></span></div>" +
      '<div class="row" style="margin-top:8px"><button class="btn btn-primary" id="setVoiceTest" aria-label="Test voice">VOICE TEST</button><button class="btn" id="setVoiceStop">STOP VOICE</button></div>');
    h += card("Theme", '<div class="switch"><span>Interface theme</span><span class="chip mono">BLACK + RED</span></div>' +
      '<div class="switch"><span>Accent</span><span class="badge badge-info">#2563EB</span></div>');
    h += card("Display Preferences", '<div class="switch"><span>Information density</span><select id="setDensity">' +
      ["COMFORTABLE", "COMPACT"].map(function (v) { return '<option' + (v === s.density ? " selected" : "") + ">" + v + "</option>"; }).join("") + "</select></div>" +
      '<div class="row" style="margin-top:10px"><button class="btn btn-primary" id="saveSettings">SAVE SETTINGS</button><button class="btn" id="resetSettings">RESET</button></div>');
    h += "</div>";
    return h;
  };
  function thr(id, label, val) {
    return '<div class="switch"><span>' + label + '</span><span class="row"><input type="range" min="0" max="100" value="' + val + '" id="' + id + '"><b id="' + id + 'V">' + val + "</b></span></div>";
  }
  PAGES["settings"].after = function () {
    ["warnThreshold", "highThreshold", "critThreshold"].forEach(function (id) {
      on("#" + id, "input", function (e) { $("#" + id + "V").textContent = e.target.value; STATE.settings[id] = +e.target.value; });
    });
    on("#setStation", "change", function (e) { setStation(STATIONS.filter(function (s) { return s.name === e.target.value; })[0].code); });
    on("#setHorizon", "change", function (e) { STATE.settings.forecastHorizon = +e.target.value; });
    on("#setLang", "change", function (e) { setLanguage(langFromLabel(e.target.value)); });
    on("#setVoiceOn", "change", function (e) { RailMindState.voiceEnabled = e.target.checked; persistVoice(); if (!e.target.checked) stopSpeech(); });
    on("#setVoiceLang", "change", function (e) { setLanguage(e.target.value); });
    [["setVol", "voiceVolume"], ["setRate", "voiceRate"], ["setPitch", "voicePitch"]].forEach(function (p) {
      on("#" + p[0], "input", function (e) { RailMindState[p[1]] = +e.target.value; $("#" + p[0] + "V").textContent = e.target.value; persistVoice(); });
    });
    on("#setVoiceTest", "click", function () { speak(TEST_PHRASE[RailMindState.currentLanguage]); });
    on("#setVoiceStop", "click", stopSpeech);
    ["setAuto:autoRefresh", "setSound:sound", "setSms:sms", "setWa:whatsapp", "setPa:pa"].forEach(function (p) {
      var a = p.split(":"); on("#" + a[0], "change", function (e) { STATE.settings[a[1]] = e.target.checked; if (a[1] === "autoRefresh") setupAuto(); });
    });
    on("#setDensity", "change", function (e) { STATE.settings.density = e.target.value; document.body.style.fontSize = e.target.value === "COMPACT" ? "13px" : "14px"; });
    on("#saveSettings", "click", function () { save("rm.settings", STATE.settings); toast("Settings saved to this browser."); });
    on("#resetSettings", "click", function () { localStorage.removeItem("rm.settings"); toast("Settings reset. Reloading…"); setTimeout(function () { location.reload(); }, 600); });
  };

  /* ------------------------------------------------------------------ HELPERS */
  function on(sel, ev, fn) { var el = $(sel); if (el) el.addEventListener(ev, fn); }
  function openModal(title, body, actions) {
    $("#modalTitle").textContent = title; $("#modalBody").innerHTML = body;
    $("#modalFoot").innerHTML = "";
    (actions || [{ label: "CLOSE", cls: "btn" }]).forEach(function (a) {
      var b = document.createElement("button"); b.className = a.cls; b.textContent = a.label;
      b.addEventListener("click", function () { closeModal(); if (a.fn) a.fn(); });
      $("#modalFoot").appendChild(b);
    });
    $("#modal").hidden = false;
  }
  function closeModal() { $("#modal").hidden = true; }
  function openDrawer(title, body) { $("#drawerTitle").textContent = title; $("#drawerBody").innerHTML = body; $("#drawer").hidden = false; }
  function closeDrawer() { $("#drawer").hidden = true; }

  /* ------------------------------------------------------------------- ROUTER */
  function currentRoute() {
    var raw = (location.hash || "").replace(/^#\/?/, "").split("?")[0];
    if (!raw && location.pathname) {
      var seg = location.pathname.split("/").filter(Boolean).pop() || "";
      if (PAGES[seg]) raw = seg;
    }
    return PAGES[raw] ? raw : "dashboard";
  }
  function go(route) { location.hash = "#/" + route; }
  function setStation(code) {
    var s = STATIONS.filter(function (x) { return x.code === code; })[0];
    if (!s) return;
    STATE.station = s; STATE.master = STATE.mode === "live" ? STATE.master : null; STATE.lastSim = null;
    $("#stationSelect").value = code; $("#stationCode").textContent = code;
    save("rm.station", { code: code });
    toast("Station context switched to " + s.name + ".");
    RailMindState.selectedStation = code;
    if (STATE.mode === "live") loadMaster(); else render();
  }

  function render() {
    STATE.route = currentRoute();
    destroyCharts();
    updateBanner();
    Array.prototype.forEach.call(document.querySelectorAll("#nav a"), function (a) {
      a.classList.toggle("active", a.getAttribute("data-route") === STATE.route);
      if (a.getAttribute("data-route") === STATE.route) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
    document.title = "RailMind AI — " + STATE.route.replace(/-/g, " ").toUpperCase();
    $("#stationCode").textContent = STATE.station.code;

    if (STATE.loading) {
      view.innerHTML = '<div class="empty">LOADING RAILWAY INTELLIGENCE…</div>';
      return;
    }
    var d = D();
    var page = PAGES[STATE.route];
    try {
      view.innerHTML = page(d);
      if (page.after) page.after(d);
    } catch (e) {
      view.innerHTML = '<div class="empty">ERROR RENDERING PAGE — ' + esc(e.message) + '<br><button class="btn" style="margin-top:10px" onclick="location.reload()">RETRY</button></div>';
    }
    maybeSpeakCritical(d);
    // shared handlers
    Array.prototype.forEach.call(document.querySelectorAll("[data-go]"), function (b) {
      b.addEventListener("click", function () { closeDrawer(); go(b.getAttribute("data-go")); });
    });
    Array.prototype.forEach.call(document.querySelectorAll("[data-seg]"), function (s) {
      s.addEventListener("click", function (e) {
        var b = e.target.closest("button[data-val]"); if (!b) return;
        var key = s.getAttribute("data-seg"), val = b.getAttribute("data-val");
        if (key === "lang") { setLanguage(langFromLabel(val)); return; }
        if (key === "alertRisk") alertFilter.risk = val;
        else if (key === "alertStatus") alertFilter.status = val;
        else STATE.filters[key] = val;
        render();
      });
    });
  }

  /* Critical alerts speak once, in the selected language, only when voice is ON.
     Message text always comes from the backend master JSON. */
  function maybeSpeakCritical(d) {
    if (!RailMindState.voiceEnabled || !d) return;
    var lvl = (d.risk && d.risk.level) || (d.operator_alert && d.operator_alert.level);
    if (String(lvl).toUpperCase() !== "CRITICAL") return;
    var msg = currentPassengerAlert(d) || currentAnnouncement(d) || (d.operator_alert && d.operator_alert.message);
    if (!msg) return;
    var id = (d.operator_alert && (d.operator_alert.id || d.operator_alert.message)) || "critical";
    speakOnce(id, msg, { auto: true });
  }

  /* --------------------------------------------------------------------- BOOT */
  var autoTimer = null;
  function setupAuto() {
    if (autoTimer) { clearInterval(autoTimer); autoTimer = null; }
    if (STATE.settings.autoRefresh) autoTimer = setInterval(function () { loadMaster(); }, 30000);
  }

  function boot() {
    buildNav(); buildStations();
    var saved = load("rm.station", null);
    if (saved && saved.code) { var s = STATIONS.filter(function (x) { return x.code === saved.code; })[0]; if (s) STATE.station = s; }
    STATE.filters.lang = langLabel(RailMindState.currentLanguage);
    STATE.settings.language = STATE.filters.lang;
    RailMindState.selectedStation = STATE.station.code;
    document.documentElement.setAttribute("data-theme", RailMindState.theme);
    $("#stationSelect").value = STATE.station.code;
    tickClock(); setInterval(tickClock, 10000);
    window.addEventListener("hashchange", function () { closeDrawer(); render(); view.focus(); });
    $("#stationSelect").addEventListener("change", function (e) {
      setStation(STATIONS.filter(function (x) { return x.name === e.target.options[e.target.selectedIndex].text; })[0].code);
    });
    $("#modalClose").addEventListener("click", closeModal);
    $("#drawerClose").addEventListener("click", closeDrawer);
    $("#modal").addEventListener("click", function (e) { if (e.target.id === "modal") closeModal(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") { closeModal(); closeDrawer(); } });
    $("#bellBtn").addEventListener("click", function () { go("alerts"); });
    banner.addEventListener("click", function (e) { if (e.target.id === "retryBtn") loadMaster(); });
    if (!location.hash) location.replace("#/dashboard");
    setupAuto();
    render();
    // Attempt a live connection once at startup; falls back to clearly-labelled demo data.
    loadMaster();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
