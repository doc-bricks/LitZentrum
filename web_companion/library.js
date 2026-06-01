export const SCHEMA_NAME = "litzentrum-library";
export const SCHEMA_VERSION = "1.0";

export function parseLibrary(json) {
  if (json?.schema !== SCHEMA_NAME) {
    throw new Error(`Unbekanntes Schema: ${json?.schema ?? "leer"}`);
  }
  if (json?.schema_version !== SCHEMA_VERSION) {
    throw new Error(`Unbekannte Schema-Version: ${json?.schema_version ?? "leer"}`);
  }

  const projects = (json.projects || []).map(normalizeProject);
  const library = {
    app: {
      name: json.app?.name || "LitZentrum",
      version: json.app?.version || ""
    },
    exportedAt: json.exported_at || "",
    capabilities: {
      containsPdfFiles: Boolean(json.capabilities?.contains_pdf_files),
      containsPdfText: Boolean(json.capabilities?.contains_pdf_text),
      readOnlyCompanion: Boolean(json.capabilities?.read_only_companion)
    },
    bibliography: {
      bibtex: json.bibliography?.bibtex || "",
      styles: Array.isArray(json.bibliography?.styles) ? json.bibliography.styles : []
    },
    projects
  };
  library.stats = buildSummaryStats(library);
  return library;
}

export function filterSources(library, { projectId = null, query = "" } = {}) {
  const tokens = query
    .trim()
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean);

  const projects = projectId
    ? library.projects.filter(project => project.id === projectId)
    : library.projects;

  return projects.flatMap(project =>
    project.sources
      .filter(source => tokens.every(token => source.searchText.includes(token)))
      .map(source => ({
        ...source,
        projectId: project.id,
        projectName: project.name,
        projectNotes: project.projectNotes,
        projectTasks: project.projectTasks
      }))
  );
}

export function buildBibtexKey(source) {
  const metadata = source.metadata || {};
  const authorRaw = Array.isArray(metadata.authors) && metadata.authors.length
    ? String(metadata.authors[0]).split(",")[0]
    : "unknown";
  const year = metadata.year ? String(metadata.year) : "oJ";
  const firstWord = firstSignificantWord(metadata.title || source.title || "");
  const authorPart = toAscii(authorRaw).toLowerCase().replace(/[^a-z]/g, "") || "unknown";
  return `${authorPart}_${year}_${firstWord}`;
}

export function buildShortCitation(source) {
  const metadata = source.metadata || {};
  const authors = Array.isArray(metadata.authors) ? metadata.authors.filter(Boolean) : [];
  const firstAuthor = authors[0]?.split(",")[0]?.trim() || "Unbekannt";
  const suffix = authors.length > 1 ? " et al." : "";
  const year = metadata.year ? String(metadata.year) : "o. J.";
  const title = metadata.title || source.title || source.folderName;
  return `${firstAuthor}${suffix} (${year}): ${title}`;
}

export function buildSummaryStats(library) {
  const stats = {
    projectCount: library.projects.length,
    sourceCount: 0,
    noteCount: 0,
    quoteCount: 0,
    openTaskCount: 0,
    summaryCount: 0,
    missingFileCount: 0
  };

  for (const project of library.projects) {
    stats.noteCount += project.projectNotes.length;
    stats.openTaskCount += project.projectTasks.filter(task => !isDone(task.status)).length;
    for (const source of project.sources) {
      stats.sourceCount += 1;
      stats.noteCount += source.notes.length;
      stats.quoteCount += source.quotes.length;
      stats.summaryCount += source.summaries.length;
      stats.openTaskCount += source.tasks.filter(task => !isDone(task.status)).length;
      stats.missingFileCount += source.files.filter(file => !file.exists).length;
    }
  }

  return stats;
}

export function buildDemoLibrary() {
  return parseLibrary({
    schema: SCHEMA_NAME,
    schema_version: SCHEMA_VERSION,
    app: {
      name: "LitZentrum",
      version: "demo"
    },
    exported_at: "2026-06-01T10:30:00+02:00",
    capabilities: {
      contains_pdf_files: false,
      contains_pdf_text: false,
      read_only_companion: true
    },
    projects: [
      {
        id: "masterarbeit",
        name: "Masterarbeit Bildung",
        description: "Forschungsstand zu Lesestrategien und KI-Unterstützung",
        citation_style: "apa",
        language: "de",
        sources_folder: "Quellen",
        project_notes: [
          {
            id: "project-note-1",
            content: "Kapitel 3 braucht stärkere Einordnung der methodischen Grenzen.",
            page: null,
            tags: ["planung"],
            created_at: "2026-05-30T09:00:00+02:00",
            updated_at: "2026-05-30T09:00:00+02:00"
          }
        ],
        project_tasks: [
          {
            id: "project-task-1",
            title: "Zitierstil gegen Prüfordnung prüfen",
            description: "APA 7 mit Betreuer abstimmen",
            status: "open",
            priority: "medium",
            due_date: "2026-06-05",
            page: null,
            tags: ["orga"],
            created_at: "2026-05-30T09:10:00+02:00",
            completed_at: null
          }
        ],
        sources: [
          {
            id: "quelle-1",
            folder_name: "Müller2024_Lesefluss",
            metadata: {
              title: "Über Lesefluss in digitalen Lernräumen",
              authors: ["Müller, Jörg", "Schäfer, Alina"],
              year: 2024,
              journal: "Zeitschrift für Bildungsforschung",
              pages: "41-63",
              tags: ["lesen", "digital"],
              source_file: "source.pdf",
              source_type: "article",
              verified: true,
              url: "https://example.org/lesefluss"
            },
            notes: [
              {
                id: "note-1",
                content: "Zentrale These: ruhige Oberflächen erhöhen die Verweildauer.",
                page: 12,
                tags: ["theorie"],
                created_at: "2026-05-30T10:00:00+02:00",
                updated_at: "2026-05-30T10:20:00+02:00"
              }
            ],
            quotes: [
              {
                id: "quote-1",
                type: "direct",
                text: "Lesefluss entsteht dort, wo kognitive Reibung gezielt sinkt.",
                page: 18,
                page_end: 18,
                comment: "Passt gut in Kapitel 2.",
                tags: ["kernzitat"],
                used_in: ["Kapitel 2"],
                created_at: "2026-05-30T10:05:00+02:00"
              }
            ],
            tasks: [
              {
                id: "task-1",
                title: "Zitat in Kapitel 2 einbauen",
                description: "Mit eigenem Gegenargument spiegeln",
                status: "open",
                priority: "high",
                due_date: null,
                page: 18,
                tags: ["kapitel-2"],
                created_at: "2026-05-30T10:10:00+02:00",
                completed_at: null
              }
            ],
            summaries: [
              {
                id: "summary-1",
                title: "Kurzüberblick",
                content: "Der Artikel verknüpft Interface-Ruhe, Orientierung und Lesetiefe.",
                type: "manual",
                source: "user",
                ai_model: null,
                pages: "1-6",
                tags: ["intro"],
                created_at: "2026-05-30T10:15:00+02:00",
                updated_at: "2026-05-30T10:15:00+02:00"
              }
            ],
            files: [
              {
                role: "source_pdf",
                name: "source.pdf",
                relative_path: "Quellen/Müller2024_Lesefluss/source.pdf",
                sha256: null,
                included: false,
                exists: true
              }
            ]
          },
          {
            id: "quelle-2",
            folder_name: "Öztürk2023_Notizen",
            metadata: {
              title: "Ästhetik des Nachschlagens",
              authors: ["Öztürk, Derya"],
              year: 2023,
              publisher: "Wissensverlag",
              tags: ["design", "zitat"],
              source_file: "essay.pdf",
              source_type: "book",
              verified: false,
              url: null
            },
            notes: [],
            quotes: [],
            tasks: [
              {
                id: "task-2",
                title: "Kapitel 4 querlesen",
                description: null,
                status: "done",
                priority: "low",
                due_date: null,
                page: null,
                tags: [],
                created_at: "2026-05-29T17:00:00+02:00",
                completed_at: "2026-05-30T08:00:00+02:00"
              }
            ],
            summaries: [],
            files: [
              {
                role: "source_pdf",
                name: "essay.pdf",
                relative_path: "Quellen/Öztürk2023_Notizen/essay.pdf",
                sha256: null,
                included: false,
                exists: false
              }
            ]
          }
        ]
      }
    ],
    bibliography: {
      bibtex: "@article{mueller_2024_lesefluss,\n  title={Über Lesefluss in digitalen Lernräumen},\n  author={Müller, Jörg and Schäfer, Alina},\n  year={2024}\n}",
      styles: ["apa", "mla", "chicago", "din", "harvard"]
    }
  });
}

function normalizeProject(project) {
  const projectNotes = (project.project_notes || []).map(normalizeNote);
  const projectTasks = (project.project_tasks || []).map(normalizeTask);
  const sources = (project.sources || []).map(normalizeSource);
  return {
    id: project.id || slugify(project.name || "projekt"),
    name: project.name || "Unbenanntes Projekt",
    description: project.description || "",
    citationStyle: project.citation_style || "",
    language: project.language || "",
    sourcesFolder: project.sources_folder || "",
    projectNotes,
    projectTasks,
    sources
  };
}

function normalizeSource(source) {
  const metadata = source.metadata || {};
  const notes = (source.notes || []).map(normalizeNote);
  const quotes = (source.quotes || []).map(normalizeQuote);
  const tasks = (source.tasks || []).map(normalizeTask);
  const summaries = (source.summaries || []).map(normalizeSummary);
  const files = (source.files || []).map(file => ({
    role: file.role || "",
    name: file.name || "",
    relativePath: file.relative_path || "",
    sha256: file.sha256 || null,
    included: Boolean(file.included),
    exists: Boolean(file.exists)
  }));
  const title = metadata.title || source.folder_name || "Unbenannte Quelle";

  return {
    id: source.id || slugify(title),
    folderName: source.folder_name || "",
    title,
    metadata,
    notes,
    quotes,
    tasks,
    summaries,
    files,
    searchText: buildSearchText({ title, metadata, notes, quotes, tasks, summaries })
  };
}

function normalizeNote(note) {
  return {
    id: note.id || cryptoFallbackId("note"),
    content: note.content || "",
    page: note.page ?? null,
    tags: Array.isArray(note.tags) ? note.tags : [],
    createdAt: note.created_at || "",
    updatedAt: note.updated_at || null
  };
}

function normalizeQuote(quote) {
  return {
    id: quote.id || cryptoFallbackId("quote"),
    type: quote.type || "",
    text: quote.text || "",
    page: quote.page ?? null,
    pageEnd: quote.page_end ?? null,
    comment: quote.comment || "",
    tags: Array.isArray(quote.tags) ? quote.tags : [],
    usedIn: Array.isArray(quote.used_in) ? quote.used_in : [],
    createdAt: quote.created_at || ""
  };
}

function normalizeTask(task) {
  return {
    id: task.id || cryptoFallbackId("task"),
    title: task.title || "",
    description: task.description || "",
    status: task.status || "",
    priority: task.priority || "",
    dueDate: task.due_date || null,
    page: task.page ?? null,
    tags: Array.isArray(task.tags) ? task.tags : [],
    createdAt: task.created_at || "",
    completedAt: task.completed_at || null
  };
}

function normalizeSummary(summary) {
  return {
    id: summary.id || cryptoFallbackId("summary"),
    title: summary.title || "",
    content: summary.content || "",
    type: summary.type || "",
    source: summary.source || "",
    aiModel: summary.ai_model || null,
    pages: summary.pages || null,
    tags: Array.isArray(summary.tags) ? summary.tags : [],
    createdAt: summary.created_at || "",
    updatedAt: summary.updated_at || null
  };
}

function buildSearchText({ title, metadata, notes, quotes, tasks, summaries }) {
  const parts = [
    title,
    metadata.abstract,
    metadata.journal,
    metadata.publisher,
    metadata.url,
    ...(metadata.authors || []),
    ...(metadata.tags || []),
    ...notes.map(note => `${note.content} ${note.tags.join(" ")}`),
    ...quotes.map(quote => `${quote.text} ${quote.comment} ${quote.tags.join(" ")} ${quote.usedIn.join(" ")}`),
    ...tasks.map(task => `${task.title} ${task.description} ${task.tags.join(" ")} ${task.status}`),
    ...summaries.map(summary => `${summary.title} ${summary.content} ${summary.tags.join(" ")}`)
  ];

  return parts
    .filter(Boolean)
    .join(" ")
    .toLowerCase();
}

function firstSignificantWord(title) {
  const stopwords = new Set([
    "der", "die", "das", "ein", "eine", "the", "a", "an",
    "und", "or", "and", "in", "im", "on", "of", "zu", "zur",
    "zum", "fuer", "für", "for", "von", "with", "mit", "ueber", "über"
  ]);
  const words = toAscii(title)
    .toLowerCase()
    .match(/[a-z]+/g) || [];
  return words.find(word => !stopwords.has(word)) || "untitled";
}

function toAscii(text) {
  return String(text)
    .replace(/ä/g, "ae")
    .replace(/ö/g, "oe")
    .replace(/ü/g, "ue")
    .replace(/ß/g, "ss")
    .replace(/Ä/g, "Ae")
    .replace(/Ö/g, "Oe")
    .replace(/Ü/g, "Ue")
    .normalize("NFKD")
    .replace(/[^\x00-\x7F]/g, "");
}

function isDone(status) {
  return ["done", "completed", "closed", "erledigt"].includes(String(status || "").toLowerCase());
}

function slugify(value) {
  return String(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "") || "eintrag";
}

function cryptoFallbackId(prefix) {
  return `${prefix}-${Math.random().toString(36).slice(2, 10)}`;
}
