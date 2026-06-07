import {
  parseLibrary,
  filterSources,
  buildBibtexKey,
  buildShortCitation,
  buildDemoLibrary,
  isDone
} from "./library.js";

const STORAGE_KEY = "litzentrum-web-companion:last-library";

let library = null;
let activeProjectId = null;
let activeSourceId = null;

const importTrigger = document.getElementById("import-trigger");
const demoTrigger = document.getElementById("demo-trigger");
const copyBibtexTrigger = document.getElementById("copy-bibtex-trigger");
const fileInput = document.getElementById("file-input");
const dropZone = document.getElementById("drop-zone");
const searchInput = document.getElementById("search-input");
const summaryGrid = document.getElementById("summary-grid");
const projectList = document.getElementById("project-list");
const sourceList = document.getElementById("source-list");
const sourceCount = document.getElementById("source-count");
const detailEmpty = document.getElementById("detail-empty");
const detailView = document.getElementById("detail-view");
const statusBar = document.getElementById("status-bar");
const androidStatus = document.getElementById("android-status");
const iosStatus = document.getElementById("ios-status");
const offlineStatus = document.getElementById("offline-status");

importTrigger.addEventListener("click", () => fileInput.click());
demoTrigger.addEventListener("click", () => loadBundle(buildDemoLibrary(), { persist: false, label: "Demo geladen." }));
copyBibtexTrigger.addEventListener("click", () => {
  if (!library?.bibliography.bibtex) {
    setStatus("Kein BibTeX im aktuellen Export enthalten.", true);
    return;
  }
  copyText(library.bibliography.bibtex, "Bibliografie als BibTeX kopiert.");
});

fileInput.addEventListener("change", event => {
  const file = event.target.files?.[0];
  if (file) {
    readFile(file);
  }
  event.target.value = "";
});

searchInput.addEventListener("input", () => {
  renderSources();
  syncSelectionWithResults();
  renderDetail();
});

dropZone.addEventListener("dragover", event => {
  event.preventDefault();
  dropZone.classList.add("drag-over");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("drag-over");
});

dropZone.addEventListener("drop", event => {
  event.preventDefault();
  dropZone.classList.remove("drag-over");
  const file = event.dataTransfer?.files?.[0];
  if (file) {
    readFile(file);
  }
});

function readFile(file) {
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const payload = JSON.parse(reader.result);
      loadBundle(payload, { persist: true, label: `${file.name} geladen.` });
    } catch {
      setStatus("Ungültige JSON-Datei.", true);
    }
  };
  reader.readAsText(file, "utf-8");
}

function loadBundle(payload, { persist, label }) {
  try {
    library = payload.stats ? payload : parseLibrary(payload);
    activeProjectId = library.projects[0]?.id ?? null;
    activeSourceId = library.projects[0]?.sources[0]?.id ?? null;
    if (persist) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    }
    renderAll();
    setStatus(label || "Bibliothek geladen.");
  } catch (error) {
    setStatus(`Fehler beim Laden: ${error.message}`, true);
  }
}

function renderAll() {
  renderSummary();
  renderProjects();
  renderSources();
  syncSelectionWithResults();
  renderDetail();
}

function renderSummary() {
  if (!library) {
    summaryGrid.innerHTML = "";
    return;
  }

  const cards = [
    ["Projekte", library.stats.projectCount],
    ["Quellen", library.stats.sourceCount],
    ["Offene Aufgaben", library.stats.openTaskCount],
    ["Zitate", library.stats.quoteCount]
  ];

  summaryGrid.innerHTML = "";
  for (const [label, value] of cards) {
    const card = document.createElement("article");
    card.className = "summary-card";

    const number = document.createElement("strong");
    number.textContent = String(value);

    const text = document.createElement("span");
    text.textContent = label;

    card.append(number, text);
    summaryGrid.appendChild(card);
  }
}

function renderProjects() {
  if (!library) {
    projectList.innerHTML = "<p class='empty-list'>Noch kein Projekt geladen.</p>";
    return;
  }

  projectList.innerHTML = "";
  for (const project of library.projects) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "project-chip" + (project.id === activeProjectId ? " active" : "");
    button.addEventListener("click", () => {
      activeProjectId = project.id;
      activeSourceId = project.sources[0]?.id ?? null;
      renderProjects();
      renderSources();
      renderDetail();
    });

    const title = document.createElement("span");
    title.className = "project-chip-title";
    title.textContent = project.name;

    const meta = document.createElement("span");
    meta.className = "project-chip-meta";
    meta.textContent = [
      `${project.sources.length} Quellen`,
      `${project.projectNotes.length} Projekt-Notizen`,
      `${project.projectTasks.length} Projekt-Aufgaben`
    ].join(" · ");

    button.append(title, meta);
    projectList.appendChild(button);
  }
}

function renderSources() {
  if (!library) {
    sourceList.innerHTML = "<p class='empty-list'>Importiere zuerst eine Bibliothek.</p>";
    sourceCount.textContent = "";
    return;
  }

  const results = getVisibleSources();
  sourceCount.textContent = `${results.length} Treffer`;
  sourceList.innerHTML = "";

  if (results.length === 0) {
    sourceList.innerHTML = "<p class='empty-list'>Keine Quellen zur Suche gefunden.</p>";
    return;
  }

  for (const source of results) {
    const card = document.createElement("button");
    card.type = "button";
    card.className = "source-card" + (source.id === activeSourceId ? " active" : "") + (source.files.some(file => !file.exists) ? " missing" : "");
    card.addEventListener("click", () => {
      activeSourceId = source.id;
      renderSources();
      renderDetail();
    });

    const top = document.createElement("div");
    top.className = "source-card-top";

    const titleWrap = document.createElement("div");
    const title = document.createElement("span");
    title.className = "source-title";
    title.textContent = source.title;

    const meta = document.createElement("span");
    meta.className = "source-meta";
    meta.textContent = sourceMetadataLine(source);

    titleWrap.append(title, meta);

    const badge = document.createElement("span");
    badge.className = "pill" + (source.files.some(file => !file.exists) ? " warning" : "");
    badge.textContent = source.files.some(file => !file.exists) ? "Datei fehlt" : "Read-only";

    top.append(titleWrap, badge);
    card.appendChild(top);

    const counts = document.createElement("span");
    counts.className = "source-counts";
    counts.textContent = [
      `${source.notes.length} Notizen`,
      `${source.quotes.length} Zitate`,
      `${source.tasks.length} Aufgaben`,
      `${source.summaries.length} Zusammenfassungen`
    ].join(" · ");
    card.appendChild(counts);

    const tags = document.createElement("div");
    tags.className = "source-card-tags";
    for (const tag of (source.metadata.tags || []).slice(0, 4)) {
      tags.appendChild(buildTag(tag));
    }
    if (source.metadata.tags?.length > 4) {
      tags.appendChild(buildTag(`+${source.metadata.tags.length - 4}`));
    }
    if (tags.children.length > 0) {
      card.appendChild(tags);
    }

    sourceList.appendChild(card);
  }
}

function renderDetail() {
  const source = getActiveSource();
  if (!library || !source) {
    detailEmpty.classList.remove("hidden");
    detailView.classList.add("hidden");
    detailView.innerHTML = "";
    return;
  }

  detailEmpty.classList.add("hidden");
  detailView.classList.remove("hidden");
  detailView.innerHTML = "";

  const titleRow = document.createElement("div");
  titleRow.className = "detail-title";

  const titleWrap = document.createElement("div");
  const title = document.createElement("h2");
  title.textContent = source.title;

  const subtitle = document.createElement("p");
  subtitle.className = "detail-subtitle";
  subtitle.textContent = `${source.projectName} · ${buildShortCitation(source)}`;
  titleWrap.append(title, subtitle);

  const actions = document.createElement("div");
  actions.className = "detail-actions";
  actions.append(
    buildActionButton("BibTeX-Key kopieren", () => copyText(buildBibtexKey(source), "BibTeX-Key kopiert.")),
    buildActionButton("Kurzverweis kopieren", () => copyText(buildShortCitation(source), "Kurzverweis kopiert."))
  );

  if (source.metadata.url) {
    const link = document.createElement("a");
    link.className = "button text-button";
    link.href = source.metadata.url;
    link.target = "_blank";
    link.rel = "noreferrer";
    link.textContent = "Quelle öffnen";
    actions.appendChild(link);
  }

  titleRow.append(titleWrap, actions);
  detailView.appendChild(titleRow);

  const contentGrid = document.createElement("div");
  contentGrid.className = "content-grid";
  contentGrid.append(
    buildMetadataSection(source),
    buildFilesSection(source),
    buildProjectSection(source),
    buildTasksSection(source),
    buildNotesSection(source),
    buildQuotesSection(source),
    buildSummariesSection(source)
  );

  detailView.appendChild(contentGrid);
}

function buildMetadataSection(source) {
  const metadata = source.metadata || {};
  const section = buildSection("Metadaten");
  const grid = document.createElement("dl");
  grid.className = "meta-grid";

  const rows = [
    ["Autor:innen", (metadata.authors || []).join(", ") || "—"],
    ["Jahr", metadata.year ?? "—"],
    ["Typ", metadata.source_type || "—"],
    ["Journal / Verlag", metadata.journal || metadata.publisher || "—"],
    ["Seiten", metadata.pages || "—"],
    ["DOI / ISBN", metadata.doi || metadata.isbn || "—"],
    ["Sprache", metadata.language || "—"],
    ["Verifiziert", metadata.verified ? "Ja" : "Nein"]
  ];

  for (const [label, value] of rows) {
    const wrapper = document.createElement("div");
    wrapper.className = "meta-row";
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    dd.textContent = String(value);
    wrapper.append(dt, dd);
    grid.appendChild(wrapper);
  }

  section.appendChild(grid);

  if (metadata.abstract) {
    const abstract = document.createElement("p");
    abstract.textContent = metadata.abstract;
    section.appendChild(abstract);
  }

  if (metadata.tags?.length) {
    const tags = document.createElement("div");
    tags.className = "tag-list";
    for (const tag of metadata.tags) {
      tags.appendChild(buildTag(tag));
    }
    section.appendChild(tags);
  }

  return section;
}

function buildFilesSection(source) {
  const section = buildSection("Dateihinweise");
  if (!source.files.length) {
    section.appendChild(buildEmptyText("Keine Dateihinweise im Export."));
    return section;
  }

  const list = document.createElement("div");
  list.className = "item-list";
  for (const file of source.files) {
    const card = document.createElement("div");
    card.className = "item-card";
    const top = document.createElement("div");
    top.className = "item-card-top";

    const name = document.createElement("strong");
    name.textContent = file.name;

    const badge = document.createElement("span");
    badge.className = "pill" + (file.exists ? "" : " warning");
    badge.textContent = file.exists ? "Lokal vorhanden" : "Nicht mit exportiert";

    top.append(name, badge);

    const path = document.createElement("p");
    path.innerHTML = `<code>${escapeHtml(file.relativePath)}</code>`;

    card.append(top, path);
    list.appendChild(card);
  }

  section.appendChild(list);
  return section;
}

function buildProjectSection(source) {
  const section = buildSection("Projektweit");
  section.classList.add("section-wide");
  const noteText = source.projectNotes.length
    ? source.projectNotes.map(note => note.content).join(" · ")
    : "Keine Projekt-Notizen im Export.";
  const taskText = source.projectTasks.length
    ? source.projectTasks.map(task => `${task.title} (${task.status || "offen"})`).join(" · ")
    : "Keine Projekt-Aufgaben im Export.";

  const notes = document.createElement("p");
  notes.textContent = noteText;

  const tasks = document.createElement("p");
  tasks.textContent = taskText;

  section.append(notes, tasks);
  return section;
}

function buildTasksSection(source) {
  const section = buildSection("Aufgaben");
  if (!source.tasks.length) {
    section.appendChild(buildEmptyText("Keine quellenbezogenen Aufgaben."));
    return section;
  }

  const list = document.createElement("div");
  list.className = "item-list";
  for (const task of source.tasks) {
    const card = document.createElement("div");
    card.className = "item-card";
    const top = document.createElement("div");
    top.className = "item-card-top";

    const title = document.createElement("strong");
    title.textContent = task.title;

    const badge = document.createElement("span");
    badge.className = "pill" + (isDone(task.status) ? "" : " warning");
    badge.textContent = task.status || "offen";

    top.append(title, badge);
    card.appendChild(top);

    if (task.description) {
      const text = document.createElement("p");
      text.textContent = task.description;
      card.appendChild(text);
    }

    const meta = document.createElement("span");
    meta.className = "inline-list";
    meta.textContent = [
      task.priority ? `Priorität: ${task.priority}` : null,
      task.dueDate ? `Fällig: ${formatDate(task.dueDate)}` : null,
      task.page !== null ? `Seite ${task.page}` : null
    ].filter(Boolean).join(" · ") || "Keine Zusatzdetails";
    card.appendChild(meta);

    if (task.tags.length) {
      const tags = document.createElement("div");
      tags.className = "tag-list";
      for (const tag of task.tags) {
        tags.appendChild(buildTag(tag));
      }
      card.appendChild(tags);
    }

    list.appendChild(card);
  }

  section.appendChild(list);
  return section;
}

function buildNotesSection(source) {
  const section = buildSection("Notizen");
  section.classList.add("section-wide");
  if (!source.notes.length) {
    section.appendChild(buildEmptyText("Keine Notizen im Export."));
    return section;
  }

  const list = document.createElement("div");
  list.className = "item-list";
  for (const note of source.notes) {
    const card = document.createElement("div");
    card.className = "item-card";
    const top = document.createElement("div");
    top.className = "item-card-top";

    const title = document.createElement("strong");
    title.textContent = note.page !== null ? `Seite ${note.page}` : "Freie Notiz";

    const badge = document.createElement("span");
    badge.className = "pill";
    badge.textContent = formatDate(note.updatedAt || note.createdAt);

    const text = document.createElement("p");
    text.textContent = note.content;

    top.append(title, badge);
    card.append(top, text);

    if (note.tags.length) {
      const tags = document.createElement("div");
      tags.className = "tag-list";
      for (const tag of note.tags) {
        tags.appendChild(buildTag(tag));
      }
      card.appendChild(tags);
    }

    list.appendChild(card);
  }

  section.appendChild(list);
  return section;
}

function buildQuotesSection(source) {
  const section = buildSection("Zitate");
  section.classList.add("section-wide");
  if (!source.quotes.length) {
    section.appendChild(buildEmptyText("Keine Zitate im Export."));
    return section;
  }

  const list = document.createElement("div");
  list.className = "item-list";
  for (const quote of source.quotes) {
    const card = document.createElement("div");
    card.className = "item-card";
    const top = document.createElement("div");
    top.className = "item-card-top";

    const title = document.createElement("strong");
    const pagePart = quote.pageEnd && quote.pageEnd !== quote.page
      ? `${quote.page}-${quote.pageEnd}`
      : `${quote.page ?? "?"}`;
    title.textContent = `Zitat · Seite ${pagePart}`;

    const copy = buildActionButton("Zitat kopieren", () => copyText(quote.text, "Zitat kopiert."));
    top.append(title, copy);
    card.appendChild(top);

    const text = document.createElement("p");
    text.className = "quote-text";
    text.textContent = quote.text;
    card.appendChild(text);

    if (quote.comment) {
      const comment = document.createElement("p");
      comment.textContent = quote.comment;
      card.appendChild(comment);
    }

    if (quote.tags.length || quote.usedIn.length) {
      const tags = document.createElement("div");
      tags.className = "tag-list";
      for (const tag of quote.tags) {
        tags.appendChild(buildTag(tag));
      }
      for (const use of quote.usedIn) {
        tags.appendChild(buildTag(`Verwendet in ${use}`));
      }
      card.appendChild(tags);
    }

    list.appendChild(card);
  }

  section.appendChild(list);
  return section;
}

function buildSummariesSection(source) {
  const section = buildSection("Zusammenfassungen");
  section.classList.add("section-wide");
  if (!source.summaries.length) {
    section.appendChild(buildEmptyText("Keine Zusammenfassungen im Export."));
    return section;
  }

  const list = document.createElement("div");
  list.className = "item-list";
  for (const summary of source.summaries) {
    const card = document.createElement("div");
    card.className = "item-card";

    const top = document.createElement("div");
    top.className = "item-card-top";

    const title = document.createElement("strong");
    title.textContent = summary.title;

    const badge = document.createElement("span");
    badge.className = "pill";
    badge.textContent = summary.type || "summary";

    top.append(title, badge);
    card.appendChild(top);

    const text = document.createElement("p");
    text.textContent = summary.content;
    card.appendChild(text);

    const meta = document.createElement("span");
    meta.className = "inline-list";
    meta.textContent = [
      summary.pages ? `Seiten: ${summary.pages}` : null,
      summary.aiModel ? `Modell: ${summary.aiModel}` : null,
      summary.updatedAt || summary.createdAt ? `Stand: ${formatDate(summary.updatedAt || summary.createdAt)}` : null
    ].filter(Boolean).join(" · ") || "Keine Zusatzdetails";
    card.appendChild(meta);

    if (summary.tags.length) {
      const tags = document.createElement("div");
      tags.className = "tag-list";
      for (const tag of summary.tags) {
        tags.appendChild(buildTag(tag));
      }
      card.appendChild(tags);
    }

    list.appendChild(card);
  }

  section.appendChild(list);
  return section;
}

function getVisibleSources() {
  return library
    ? filterSources(library, {
      projectId: activeProjectId,
      query: searchInput.value
    })
    : [];
}

function syncSelectionWithResults() {
  const results = getVisibleSources();
  if (!results.length) {
    activeSourceId = null;
    return;
  }
  if (!results.some(source => source.id === activeSourceId)) {
    activeSourceId = results[0].id;
  }
}

function getActiveSource() {
  return getVisibleSources().find(source => source.id === activeSourceId) || null;
}

function sourceMetadataLine(source) {
  const authors = source.metadata.authors?.length ? source.metadata.authors.join(", ") : "Unbekannt";
  const year = source.metadata.year ?? "o. J.";
  return `${authors} · ${year}`;
}

function buildSection(titleText) {
  const section = document.createElement("section");
  section.className = "section";
  const title = document.createElement("h3");
  title.textContent = titleText;
  section.appendChild(title);
  return section;
}

function buildActionButton(label, onClick) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "text-button";
  button.textContent = label;
  button.addEventListener("click", onClick);
  return button;
}

function buildTag(text) {
  const tag = document.createElement("span");
  tag.className = "tag";
  tag.textContent = text;
  return tag;
}

function buildEmptyText(text) {
  const empty = document.createElement("p");
  empty.className = "empty-list";
  empty.textContent = text;
  return empty;
}

async function copyText(text, successMessage) {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
    } else {
      const field = document.createElement("textarea");
      field.value = text;
      document.body.appendChild(field);
      field.select();
      document.execCommand("copy");
      field.remove();
    }
    setStatus(successMessage);
  } catch {
    setStatus("Kopieren wurde vom Browser blockiert.", true);
  }
}

function setStatus(text, isError = false) {
  statusBar.textContent = text;
  statusBar.className = "status-bar" + (isError ? " error" : "");
}

function setMobileStatus(element, text, state = "neutral") {
  element.textContent = text;
  element.dataset.state = state;
}

function updateMobilePwaStatus() {
  const userAgent = navigator.userAgent.toLowerCase();
  const isAndroid = userAgent.includes("android");
  const isIos = /iphone|ipad|ipod/.test(userAgent);
  const isStandalone = window.matchMedia?.("(display-mode: standalone)").matches || navigator.standalone === true;

  setMobileStatus(
    androidStatus,
    isAndroid ? (isStandalone ? "Installiert" : "PWA bereit") : "Chrome/Edge PWA",
    isAndroid ? "active" : "neutral"
  );
  setMobileStatus(
    iosStatus,
    isIos ? (isStandalone ? "Installiert" : "Safari PWA bereit") : "Safari PWA",
    isIos ? "active" : "neutral"
  );
  setMobileStatus(offlineStatus, "Offline-Cache wird vorbereitet.", "neutral");
}

function formatDate(value) {
  if (!value) {
    return "—";
  }
  try {
    return new Date(value).toLocaleDateString("de-DE");
  } catch {
    return value;
  }
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

updateMobilePwaStatus();

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("./sw.js")
    .then(() => setMobileStatus(offlineStatus, "Offline-Cache bereit.", "active"))
    .catch(() => setMobileStatus(offlineStatus, "Offline-Cache blockiert.", "warning"));
} else {
  setMobileStatus(offlineStatus, "Kein Service Worker verfügbar.", "warning");
}

const params = new URLSearchParams(window.location.search);
if (params.get("demo") === "1") {
  loadBundle(buildDemoLibrary(), { persist: false, label: "Demo geladen." });
} else {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved) {
    try {
      loadBundle(JSON.parse(saved), { persist: false, label: "Zuletzt geladene Bibliothek wiederhergestellt." });
    } catch {
      localStorage.removeItem(STORAGE_KEY);
      setStatus("Gespeicherte Bibliothek war ungültig und wurde verworfen.", true);
    }
  }
}
