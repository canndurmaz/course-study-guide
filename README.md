# course-study-guide

A [Claude Code](https://claude.com/claude-code) skill that turns a folder of course
materials into one compiled **LaTeX study guide**. The folder can hold typed lecture
PDFs, scanned or handwritten instructor notes and exercise sets. The guide has topic
chapters, worked examples, a solution for every exercise checked in SymPy, and a
formula sheet.

## What you get

```
StudyGuide/
├── <COURSE>_StudyGuide.pdf     compiled book (≈40 pages per week of material)
├── main.tex, preamble.tex      book skeleton + shared styles
├── chapters/                   one .tex per topic chapter and per exercise set
├── figures/                    matplotlib plots (direction fields, eigenfunctions, …)
└── compile.sh                  rebuild from source
```

What the book contains:
- **Theory chapters**, organised by topic rather than by lecture date. Each has colour-coded
  boxes for definitions, theorems and examples, *key idea* and *common pitfall* boxes,
  and the derivation steps the lecture notes skip.
- **Instructor's notes:** content transcribed from the handwritten notes, highlighted in its own box.
- **Extra examples:** 2–4 extra fully worked examples per major section, plus a summary and self-check questions per chapter.
- **Exercise solutions:** step by step, each answer substituted back and checked in SymPy.
  Errors in the source are flagged: lecture typos and wrong printed answers.
- **Appendix:** a formula sheet.

On its first course (5 weeks of a graduate differential-equations course) the guide came
to 214 pages. The process caught about a dozen errors in the source material.

## How it works

1. **Survey.** It detects Git LFS pointer stubs, duplicated lecture files, scanned
   pages (which have no text layer) and blank padding pages. It then maps each week's
   handwritten notes onto lecture page ranges, so every topic has exactly one owner.
2. **Skeleton.** It copies the tested `preamble.tex` and `compile.sh` and writes the
   `main.tex` structure.
3. **Parallel chapter agents.** One sub-agent writes each chapter or exercise set. Each
   reads the pages as images (the PDF text layer garbles math), checks its maths with
   SymPy, and compiles its own chapter on its own.
4. **Integrate.** It compiles the whole book, keeping a usable PDF at every stage, and
   proves the build works from a clean state.
5. **Report.** It gives you the chapter and page table, the source errors found, and an
   optional git commit using LFS.

The full playbook, with agent briefs and the LaTeX problems to avoid, is in [`SKILL.md`](SKILL.md).

## Install

```bash
git clone git@github.com:canndurmaz/course-study-guide.git ~/Workspaces/course-study-guide
ln -s ~/Workspaces/course-study-guide ~/.claude/skills/course-study-guide
```

## Use

Open Claude Code in a course folder and run:

```
/course-study-guide  sources in LectureNotes/, course code XX000
```

Or just ask: *"make a study guide PDF from my lecture notes and exercise sets"*.
Mention a deadline if you have one. The skill then compiles whatever is finished and
tells the chapter agents to wrap up in time.

Rebuild later with `cd StudyGuide && ./compile.sh` (set `COURSE=` in the script).

## Requirements

| Tool | Used for |
|---|---|
| TeX Live (`pdflatex`, `latexmk`, `tcolorbox`, `pgfplots`, `cleveref`) | building the book |
| poppler-utils (`pdftoppm`, `pdftotext`, `pdfinfo`) | reading and rendering source PDFs |
| ImageMagick (`convert`, `montage`) | blank-page detection, contact sheets |
| Python 3 with `sympy`, `numpy`, `scipy`, `matplotlib` | checking the maths, figures |
| `git-lfs` (optional) | course repos that store PDFs in LFS |

On Debian/Ubuntu:

```bash
sudo apt install texlive-full poppler-utils imagemagick git-lfs
pip install sympy numpy scipy matplotlib
```

## Repository layout

| File | Purpose |
|---|---|
| `SKILL.md` | The playbook Claude follows |
| `templates/preamble.tex` | Shared LaTeX preamble with boxed environments, macros and `\cref` support |
| `templates/compile.sh` | Build script: `latexmk` → `<COURSE>_StudyGuide.pdf` |
| `templates/lfs_fetch.py` | Downloads Git LFS objects over SSH when `git-lfs` isn't installed |

## Tips

- It works best when lecture and notes files follow a naming pattern (`week3_lecture.pdf`,
  `week3_notes.pdf`, `ExerciseSet02.pdf`), but the survey step copes without one.
- Handwriting is read from 110-dpi page images. Very faint scans may need a higher resolution.
- The run uses a lot of tokens, because it spawns several sub-agents that each read many page images.
