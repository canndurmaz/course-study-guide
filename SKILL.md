---
name: course-study-guide
description: Build an extensive LaTeX study-guide PDF for a university course from a folder of lecture notes, instructor's (possibly handwritten/scanned) notes and exercise sets, including detailed verified exercise solutions. Use when the user asks to turn course materials / lecture notes into a learning PDF, study guide, or textbook-style document.
---

# Course Study Guide Builder

Turns a course folder (typed lecture PDFs, scanned/handwritten instructor notes,
exercise sets) into one compiled LaTeX book. Each chapter covers a topic. Every
exercise gets a detailed solution checked in SymPy. A formula sheet goes at the end.
First used for ME521 (METU); that repo's `StudyGuide/` folder is a complete worked example.

**Inputs (ask only if they're not obvious):** the folder of source PDFs, the course
code, and the deadline if there is one. Default output is `<repo>/StudyGuide/`, holding
the `.tex` sources, `compile.sh` and `<COURSE>_StudyGuide.pdf`.

Templates are in `~/.claude/skills/course-study-guide/templates/`:
`preamble.tex`, `compile.sh` and `lfs_fetch.py`.

---

## Phase 1: Survey the sources (do this yourself, ~10 min)

1. **Count pages and words for each PDF.** Run `pdfinfo` + `pdftotext -q f - | wc -w`.
   - A file of about **132 bytes** is a **Git LFS pointer** (`version https://git-lfs...`).
     Run `git lfs pull` first. If git-lfs is missing, use
     `python3 -I templates/lfs_fetch.py <owner/repo> <outdir> <pointer files...>`,
     which uses SSH `git-lfs-authenticate` and the LFS batch API and checks SHA-256.
   - **0 words** means a scanned or handwritten PDF. It has to be read as images.
   - Producer `Microsoft Word` means typed notes. The text layer exists, but
     **the math is garbled**, so render pages to PNG and read them as images whenever the equations matter.
2. **Find duplicates.** Lecture files from different weeks are often the same document
   re-issued (`diff` the pdftotext output). If so, the handwritten notes for each week
   are what tell you how far the class got that week.
3. **Find blank scanned pages.** Notes PDFs are often padded with empty pages. Measure ink density:
   ```bash
   pdftoppm -q -r 15 -gray notes.pdf ink/p
   for f in ink/p-*.pgm; do convert $f -threshold 80% -format "%[fx:int(1000*(1-mean))] " info:; done
   ```
   A value above ~30 means content; ~10 means a few marks; 0 means blank. Only render pages that have content.
4. **Map notes onto the lecture.** Build a contact sheet of the first page of each notes
   set (`montage ... -tile 5x2`) and look at it once. Then print the first line of every lecture page
   (`pdftotext -f p -l p`) to get the page ranges for each topic.
5. **Pre-render** the content pages at **110 dpi** (legible handwriting, reasonable size):
   `pdftoppm -q -r 110 -f 1 -l N -png notes.pdf $SCRATCH/img/notes_wK`.
   Render the exercise sets the same way.

From this, write a **chapter map**: chapter → lecture file and page range →
handwritten-notes pages. Give each topic exactly one owner, so nothing is left out and
nothing is covered twice.

## Phase 2: Skeleton (yourself)

```
StudyGuide/
  main.tex            % \newcommand{\CourseCode}{XX000} then \input{preamble}
  preamble.tex        % copy from templates/ (tested, do not "fix" the known traps below)
  compile.sh          % copy from templates/, set COURSE=
  Makefile .gitignore % ignore build/ and *.aux etc.
  chapters/howto.tex  % sources→chapters table, box legend, study path
  chapters/chNN_*.tex, exNN.tex, appendix_formulas.tex
  figures/            % <prefix>_*.pdf from matplotlib
```
`main.tex` layout: title page, `\tableofcontents`, howto, `\part{Theory}`, chapters,
`\part{Exercise Sets with Detailed Solutions}`, `\appendix` formula sheet.
For chapters that are still being written, use
`\InputIfFileExists{chapters/x}{}{}`, so the book compiles before every chapter is done.

### Preamble environments (what agents must use)
- `definition` / `theorem` / `example`: tcbtheorems, **two mandatory args**
  `\begin{theorem}{Title}{label}`, referenced as `\cref{thm:label}` (`def:`, `ex:`).
- `keyidea`, `pitfall`, `instructor` (for content from the handwritten notes), `summarybox`: take
  an optional `[title]`.
- `\begin{problem}{3(b)} … \end{problem}` followed by `\begin{solution} … \end{solution}`.
- Macros: `\R \C \N \dd \der \pder \Lap \Op \ip \norm \abs \Wr`.

### Known LaTeX traps (already fixed in the template; keep the fixes)
- **cleveref + tcbtheorem:** `crefname={..}{..}` must go in the **init options**
  (`\newtcbtheorem[number within=chapter,crefname=...]`), not in the box options,
  or you get `/tcb/crefname unknown`. Shared counters need it on each environment.
- **Commas in box titles:** the template uses `title={#1}`. A bare `title=#1` breaks on
  `[From the notes (Week 5, p. 1)]`.
- **Math/primes in box titles** (`$y'$`) can still break; keep box titles plain text.
- **Never edit the shared preamble while agents are compiling.** Test changes on a copy
  in scratch first (an untested edit once broke compiles for everyone).

## Phase 3: Fan out chapter agents (parallel, background)

Run one `general-purpose` agent per chapter, or per pair of small chapters, and one per
exercise set. Launch them all **in a single message**. Each brief must be self-contained:

```
You are writing ONE chapter of an extensive LaTeX study guide for <COURSE> (<subject>).
Other agents write other chapters in parallel; stay strictly in scope.

Shared setup (do not modify): StudyGuide/preamble.tex — READ IT FIRST. <list envs + 2-arg rule>.
Prefix ALL labels with `cN:`.

Sources (read-only, $S=<scratch>):
- Typed lecture $S/src/<file>.pdf pages A–B ONLY. Text layer garbles math: render pages
  (pdftoppm -r 100) into a NEW folder $S/work_cN/ and Read them.
- Handwritten notes pre-rendered: $S/img/notes_wK-PP.png (pages ...). <who owns what if shared>

Output: StudyGuide/chapters/<file>.tex starting with \chapter{<title>}\label{cN:chap}.

"Extensive learning PDF" means: cover EVERY topic, definition, theorem, derivation, example and
figure in the sources; then go beyond — motivation, skipped intermediate steps, physical/
geometric interpretation, keyidea + pitfall boxes, instructor boxes for handwritten material,
2–4 extra fully worked examples per major section, pgfplots/TikZ or matplotlib figures
(StudyGuide/figures/cN_*.pdf, included as figures/...). End with summarybox + self-check Q&A.
Verify every nontrivial computation with sympy. If a source has an error, correct it and
flag it in a pitfall box. Target ~N pages. No \usepackage/\documentclass.

Verify: wrapper test.tex in $S/work_cN/ that \input's the preamble + chapter by absolute
path; compile twice from StudyGuide/; fix ALL errors, minimise overfull hboxes.
Don't touch other files; don't commit.
Final report: file, page count, sections, source errors found, anything unreadable.
```

**Exercise-set agents** get the same setup plus these instructions. Transcribe every
statement faithfully (fix typos with a footnote). Give step-by-step solutions with all
the algebra. Name the method used and say why it applies. Substitute every answer back
into the equation, and check every answer with sympy (`checkodesol`, residuals). Flag any
**printed answer that is wrong**. Draw direction fields and solution plots in matplotlib.
End each problem group with a Takeaways box. Report one line per problem with the final answer.

Agents run for 10–16 minutes. While they work, write `howto.tex` and the formula-sheet
appendix yourself (no overlap with the agents).

## Phase 4: Integrate and compile

1. Compile the whole book as soon as most chapters exist:
   `pdflatex -interaction=nonstopmode -output-directory=build main.tex` (twice). Then check:
   `grep -E "^!" build/main.log`, `grep -c "Reference.*undefined"`, page count.
   `latexmk` can report "Errors" left over from an earlier failed pass; check with a clean
   pdflatex run before trusting that.
2. Copy `build/main.pdf` to `<COURSE>_StudyGuide.pdf` after every good build, so a usable
   deliverable always exists.
3. **Under a deadline:** compile with what exists, message the running agents
   ("finish within N minutes, compiling file over completeness, no new content"), and
   rebuild as each one reports back.
4. Finally, `rm -rf build && ./compile.sh` from clean, to prove the build reproduces.

## Phase 5: Report and git

- Tell the user the path, page count and a chapter/page table. List the **source errors
  found** (lecture typos and wrong printed answers). These are valuable to the student.
- Commit only when asked. If the repo routes `*.pdf` through LFS, make sure `git lfs version`
  works before adding figure or guide PDFs. If LFS is missing, do not commit PDFs as raw
  blobs without telling the user. Ask whether the compiled PDF should be committed, or
  `.gitignore`d with `compile.sh` as the way to rebuild.

## Quality bar (what made ME521 work)
- ~200 pages for 5 weeks of material. Theory chapters ran 16–29 pages each; exercise chapters 33–41.
- Every handwritten-note example appears, either in an `instructor` box or as a worked example.
- Every lecture typo found was corrected and flagged. Examples: wrong norms, a sign error
  in the periodic Sturm–Liouville (S-L) case, L² vs L in coefficients, and printed exercise
  answers with the wrong sign or a missing eigenvalue.
