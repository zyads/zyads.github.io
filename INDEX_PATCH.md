# INDEX_PATCH.md — changes index.html needs for the blog + SEO

The blog agent did not touch index.html (concurrent-edit rule). Apply these hunks
by exact string replacement. Anchors were re-taken from the CURRENT on-disk
index.html (the ~142KB version, section `05` = Writing) on 2026-08-02.
Delete this file after applying.

Things already true in index.html that this patch therefore does NOT touch:
- `<link rel="canonical">`, `og:site_name`, `og:image`, and Twitter card tags
  already exist in the head — do not duplicate them.
- The nav already links `#writing`, and the new section below keeps
  `id="writing"`, so the nav and the scrollspy array
  (`['about','experience','projects','education','writing','live','wall']`)
  keep working with zero JS changes.

Re-check after applying: nothing else. Hunk 2 only adds CSS; the existing
`.post`/`.post-body` rules become unused (the terminal may not need them either)
and can be pruned later — harmless to keep.

---

## Hunk 1 — head: Person JSON-LD (structured data for the home page)

**OLD** (the single line):

```html
<title>Zyad Shehadeh</title>
```

**NEW**:

```html
<title>Zyad Shehadeh</title>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "Zyad Shehadeh",
  "jobTitle": "Software Engineer",
  "url": "https://zyads.github.io/",
  "sameAs": [
    "https://github.com/zyads",
    "https://linkedin.com/in/zyads"
  ],
  "alumniOf": { "@type": "CollegeOrUniversity", "name": "University of Michigan" },
  "knowsAbout": [
    "Build systems", "Bazel", "CI/CD", "Artifact provenance",
    "Developer platforms", "Dependency graphs",
    "LLM agent tooling", "Model Context Protocol",
    "Distributed systems", "Observability",
    "Python", "C++", "Go", "Docker", "Kubernetes"
  ]
}
</script>
```

---

## Hunk 2 — CSS: add styles for the new writing-section link rows

**OLD** (last two lines of the `/* ---------- writing ---------- */` CSS block,
currently lines ~369–370):

```css
  .post-body .kw { color: var(--c3); }
  .post-body .cm { color: var(--faint); font-style: italic; }
```

**NEW**:

```css
  .post-body .kw { color: var(--c3); }
  .post-body .cm { color: var(--faint); font-style: italic; }
  .post-link {
    display: flex; align-items: baseline; gap: 1rem; flex-wrap: wrap;
    border: 1px solid var(--line); border-radius: 16px;
    background: var(--card);
    padding: 1.3rem 1.5rem;
    color: var(--text);
    transition: border-color 0.35s ease, box-shadow 0.35s ease;
  }
  .post-link:hover {
    text-decoration: none;
    border-color: rgba(56,224,255,0.35);
    box-shadow: 0 18px 50px -22px rgba(56,224,255,0.2);
  }
  .post-link h3 { font-size: 1.15rem; font-weight: 700; letter-spacing: -0.01em; }
  .post-link:hover h3 { color: var(--c1); }
  .post-link .when {
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 0.75rem; color: var(--faint); letter-spacing: 0.04em;
    margin-left: auto;
  }
  .post-link .teaser { flex-basis: 100%; color: var(--muted); font-size: 0.94rem; margin-top: 0.15rem; }
  .all-posts {
    margin-top: 1.5rem;
    display: inline-flex; align-items: center; gap: 0.4rem;
    min-height: 44px;
    font-weight: 600; font-size: 0.95rem;
  }
```

---

## Hunk 3 — replace the inline `#writing` section with a teaser of the blog

The inline `<details>` post moves to the standalone blog. The tree post now lives
at `/posts/storing-tree-relationships-in-a-table.html`.

The OLD block is large, so replace by boundaries instead of quoting all of it:
delete everything from this opening line (inclusive, currently line ~868):

```html
  <section id="writing" aria-labelledby="writing-h">
```

…through the FIRST `</section>` that follows it (inclusive, the one immediately
before `<section id="live"`). Sanity-check before deleting: that region should
contain exactly one `<details class="post reveal">` ("Storing Tree Relationships
in a Table") and the "ADD A POST" comment, and no other `<section` opens inside
it.

**NEW** (insert in its place):

```html
  <section id="writing" aria-labelledby="writing-h">
    <div class="wrap">
      <div class="sec-head reveal"><span class="idx">05</span><h2 id="writing-h">Writing</h2></div>

      <!-- Posts are standalone pages now. To add one: create posts/<slug>.html
           (copy an existing post — its head comment walks through every field),
           add it to blog.html and sitemap.xml, then add a row here (newest
           first, keep it to the latest three). -->

      <div class="posts">
        <a class="post-link reveal" href="posts/context-is-a-budget.html">
          <h3>Context Is a Budget, Not a Bucket</h3>
          <span class="when">Jun 2026</span>
          <p class="teaser">Designing tool interfaces for LLM agents &mdash; the cheapest token is the one never emitted.</p>
        </a>
        <a class="post-link reveal" style="--d:0.08s" href="posts/signing-without-hermeticity-is-theater.html">
          <h3>Signing Without Hermeticity Is Theater</h3>
          <span class="when">Mar 2026</span>
          <p class="teaser">What &ldquo;this artifact came from that commit&rdquo; actually requires, and why a signature alone proves almost nothing.</p>
        </a>
        <a class="post-link reveal" style="--d:0.16s" href="posts/dependency-graph-is-the-real-artifact.html">
          <h3>The Dependency Graph Is the Real Artifact</h3>
          <span class="when">Jan 2026</span>
          <p class="teaser">Blast radius, cycle ratchets, and critical paths &mdash; what a build graph tells you that the file tree never will.</p>
        </a>
      </div>

      <a class="all-posts reveal" href="blog.html">All posts <span aria-hidden="true">&rarr;</span></a>
    </div>
  </section>
```

Note: `05` in the `idx` span matches the section's current number in the on-disk
IA (about/experience/projects/education/**writing**/live/wall). If the other
agent renumbers sections again, match whatever number the deleted block had.

---

## Hunk 4 (small, recommended) — terminal easter egg points at the old inline post

The fake-filesystem `writing/tree-relationships.md` entry in the terminal JS ends
with a pointer to the now-replaced inline section.

**OLD** (single line, inside the `'writing':` object of the terminal FS, ~line 2000):

```js
          'update complexity you can stomach. full post: §05 Writing.'
```

**NEW**:

```js
          'update complexity you can stomach. full post: /posts/storing-tree-relationships-in-a-table.html'
```
