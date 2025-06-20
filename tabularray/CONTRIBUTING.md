
Contributing to the Manual (manual is unmaintained in `tabularray-dev`)
--------------------------

- You need to compile the manual files with LuaLaTeX,
  because it is rather slow to compile them with XeLaTeX or PDFLaTeX.

- The manual `tabularray.tex` is split into subfiles and put in manual folder.
  You can compile each subfile and see the output.

- Now you can create a pull request for your contribution.


Contributing to the Code
------------------------

- Preparation
  - Install [`l3build`](https://ctan.org/pkg/l3build) LaTeX package.
  - Install `pdftoppm` program. 
    - Windows: `tlmgr install wintools.windows`
    - Ubuntu: `apt-get install poppler-utils`
    - macOS: `brew install poppler`
  - (optional) Install ImageMagick.
    - Windows: see https://imagemagick.org/script/download.php#windows
    - Ubuntu: `apt-get install imagemagick`
    - macOS: `brew install imagemagick`

- Run tests
  - In the root dir, run `l3build check` to check all tests.
  - Then in `./tabularray`, run `texlua buildend.lua` to PDF output of `testfiles-old` tests, by comparing md5 of images converted from PDF page by page.
    - This uses a local `./support/ppmcheckpdf.lua`, instead of the one provided by [`ppmchecmpdf`](https://ctan.org/pkg/ppmcheckpdf) CTAN package.
    - On non-Windows systems, when ImageMagick is installed (by checking existence of `magick` or `compare`), `.diff.png` diff images are created (under `./build/test/config-old`) for failed tests.
  - See also steps in `./.github/workflows/check.yml`.

- Update test results
    - In `./tabularray` or `./zutil`, run `l3build save [-c<config>] [-e<engine>] <name>...` to update corresponding `testfiles/<name>.[<engine>.]tlg` file(s). Then check if the updates are expected.
      - Consult the `l3build` doc for more info.
    - In `./tabularray`, after `l3build check -cconfig-old` passes, run `texlua buildend.lua save` to update all `testfiles/*.{png,md5}` files which failed the ppm check. Then check if the updated `.png` are expected.
