# course-study-guide

A Claude Code skill that turns a course folder into one compiled LaTeX study guide.
The folder can hold typed lecture PDFs, scanned or handwritten instructor notes and exercise sets.
The guide has topic chapters, worked examples, exercise solutions checked in SymPy, and a formula sheet.

## Install

```bash
git clone <this-repo> ~/Workspaces/course-study-guide
ln -s ~/Workspaces/course-study-guide ~/.claude/skills/course-study-guide
```

## Use

Open Claude Code in a course repo and run:

```
/course-study-guide  LectureNotes/ folder, course code XX000
```

Or just ask: "make a study guide PDF from my lecture notes and exercise sets".

## Contents

| File | Purpose |
|---|---|
| `SKILL.md` | The playbook: survey, skeleton, parallel chapter agents, integration, git |
| `templates/preamble.tex` | Tested shared LaTeX preamble with boxed environments and macros |
| `templates/compile.sh` | Build script (set `COURSE=`) |
| `templates/lfs_fetch.py` | Fetches Git LFS objects over SSH when `git-lfs` isn't installed |

First used for METU ME521. That repo's `StudyGuide/` folder is a complete worked example.

## Requirements

TeX Live (pdflatex, latexmk, tcolorbox, pgfplots), poppler-utils (`pdftoppm`, `pdftotext`),
ImageMagick, and Python 3 with sympy, numpy, scipy and matplotlib.
