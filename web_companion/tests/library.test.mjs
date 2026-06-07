import { test } from "node:test";
import assert from "node:assert/strict";
import {
  SCHEMA_NAME,
  SCHEMA_VERSION,
  parseLibrary,
  filterSources,
  buildBibtexKey,
  buildShortCitation,
  buildSummaryStats,
  buildDemoLibrary,
  isDone
} from "../library.js";

const SAMPLE = {
  schema: SCHEMA_NAME,
  schema_version: SCHEMA_VERSION,
  app: { name: "LitZentrum", version: "1.0.0" },
  exported_at: "2026-06-01T10:00:00Z",
  capabilities: {
    contains_pdf_files: false,
    contains_pdf_text: false,
    read_only_companion: true
  },
  projects: [
    {
      id: "masterarbeit",
      name: "Masterarbeit",
      citation_style: "apa",
      language: "de",
      sources_folder: "Quellen",
      project_notes: [
        {
          id: "pn1",
          content: "Übergreifende Notiz",
          page: null,
          tags: ["planung"],
          created_at: "2026-06-01T09:00:00Z",
          updated_at: null
        }
      ],
      project_tasks: [
        {
          id: "pt1",
          title: "Projektweit prüfen",
          description: null,
          status: "open",
          priority: "medium",
          due_date: null,
          page: null,
          tags: [],
          created_at: "2026-06-01T09:10:00Z",
          completed_at: null
        }
      ],
      sources: [
        {
          id: "src1",
          folder_name: "Müller2024_AI",
          metadata: {
            title: "Über KI im Lesen",
            authors: ["Müller, Jörg"],
            year: 2024,
            tags: ["lesen", "ki"],
            abstract: "Fokus auf ruhige Oberflächen"
          },
          notes: [
            {
              id: "n1",
              content: "Wichtig für Kapitel 2",
              page: 5,
              tags: ["kapitel-2"],
              created_at: "2026-06-01T09:20:00Z",
              updated_at: null
            }
          ],
          quotes: [
            {
              id: "q1",
              type: "direct",
              text: "Lesefluss entsteht im ruhigen Interface.",
              page: 11,
              page_end: 11,
              comment: "Schlüsselzitat",
              tags: ["kernzitat"],
              used_in: ["Kapitel 2"],
              created_at: "2026-06-01T09:30:00Z"
            }
          ],
          tasks: [
            {
              id: "t1",
              title: "Zitat einbauen",
              description: "Mit Gegenposition abgleichen",
              status: "open",
              priority: "high",
              due_date: "2026-06-03",
              page: 11,
              tags: ["schreiben"],
              created_at: "2026-06-01T09:40:00Z",
              completed_at: null
            }
          ],
          summaries: [
            {
              id: "s1",
              title: "Kurzüberblick",
              content: "Verbindet Lesetiefe und Interface-Ruhe.",
              type: "manual",
              source: "user",
              ai_model: null,
              pages: "1-5",
              tags: ["überblick"],
              created_at: "2026-06-01T09:50:00Z",
              updated_at: null
            }
          ],
          files: [
            {
              role: "source_pdf",
              name: "source.pdf",
              relative_path: "Quellen/Müller2024_AI/source.pdf",
              sha256: null,
              included: false,
              exists: true
            }
          ]
        }
      ]
    }
  ],
  bibliography: {
    bibtex: "@article{mueller_2024_ki,\n  title={Über KI im Lesen}\n}",
    styles: ["apa", "mla"]
  }
};

test("parseLibrary normalisiert Projekte und Quellen", () => {
  const library = parseLibrary(SAMPLE);
  assert.equal(library.projects.length, 1);
  assert.equal(library.projects[0].sources.length, 1);
  assert.equal(library.projects[0].sources[0].title, "Über KI im Lesen");
  assert.equal(library.stats.openTaskCount, 2);
});

test("parseLibrary lehnt falsches Schema ab", () => {
  assert.throws(
    () => parseLibrary({ ...SAMPLE, schema: "andere-bibliothek" }),
    /Unbekanntes Schema/
  );
});

test("filterSources sucht über Notizen, Zitate und Aufgaben", () => {
  const library = parseLibrary(SAMPLE);
  assert.equal(filterSources(library, { query: "kapitel" }).length, 1);
  assert.equal(filterSources(library, { query: "ruhigen interface" }).length, 1);
  assert.equal(filterSources(library, { query: "nichtvorhanden" }).length, 0);
});

test("buildBibtexKey transliteriert Umlaute", () => {
  const library = parseLibrary(SAMPLE);
  const key = buildBibtexKey(library.projects[0].sources[0]);
  assert.equal(key, "mueller_2024_ki");
});

test("buildShortCitation baut Autor-Jahr-Titel", () => {
  const library = parseLibrary(SAMPLE);
  const text = buildShortCitation(library.projects[0].sources[0]);
  assert.equal(text, "Müller (2024): Über KI im Lesen");
});

test("buildSummaryStats zählt fehlende Dateien und Inhalte", () => {
  const library = parseLibrary(SAMPLE);
  const stats = buildSummaryStats(library);
  assert.equal(stats.projectCount, 1);
  assert.equal(stats.sourceCount, 1);
  assert.equal(stats.noteCount, 2);
  assert.equal(stats.quoteCount, 1);
  assert.equal(stats.summaryCount, 1);
  assert.equal(stats.missingFileCount, 0);
});

test("buildDemoLibrary liefert eine parsebare Demo", () => {
  const library = buildDemoLibrary();
  assert.ok(library.projects.length >= 1);
  assert.ok(library.projects[0].sources.length >= 1);
  assert.ok(library.stats.quoteCount >= 1);
});

test("isDone erkennt alle erledigten Status-Varianten", () => {
  for (const done of ["done", "completed", "closed", "erledigt", "DONE", "Completed"]) {
    assert.ok(isDone(done), `isDone("${done}") muss true sein`);
  }
  for (const open of ["open", "in-progress", "", null, undefined]) {
    assert.ok(!isDone(open), `isDone(${JSON.stringify(open)}) muss false sein`);
  }
});

test("parseLibrary normalisiert authors-String zu Array", () => {
  const raw = {
    ...SAMPLE,
    projects: [
      {
        ...SAMPLE.projects[0],
        sources: [
          {
            ...SAMPLE.projects[0].sources[0],
            metadata: {
              ...SAMPLE.projects[0].sources[0].metadata,
              authors: "Müller, Jörg"
            }
          }
        ]
      }
    ]
  };
  const library = parseLibrary(raw);
  const src = library.projects[0].sources[0];
  assert.ok(Array.isArray(src.metadata.authors), "authors muss ein Array sein");
  assert.equal(src.metadata.authors.length, 1);
  assert.equal(src.metadata.authors[0], "Müller, Jörg");
});
