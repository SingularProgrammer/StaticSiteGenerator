# Static Site Generator

A simple, fast, and dependency-free static site generator written in Python. It compiles your content files and HTML templates into fully rendered static pages with an optional file watcher that automatically rebuilds on any change.

---

## Table of Contents

- [How to Use](#how-to-use)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Content Files](#content-files)
- [Templates](#templates)
- [Multi-Language Support](#multi-language-support)
- [Watch Mode](#watch-mode)
- [Build Behavior](#build-behavior)
- [Full Example](#full-example)
- [Notes & Best Practices](#notes--best-practices)

---

## How to Use

### Run a Full Build

Compiles all content files once and exits:

```bash
./SiteBuilder.exe
```

### Run in Watch Mode

Compiles everything once, then watches for file changes and recompiles automatically:

```bash
./SiteBuilder.exe --watch
```

Press `CTRL+C` to stop the watcher.

> If you are running the Python source directly instead of the compiled executable, replace `./SiteBuilder.exe` with `python main.py`.

---

## How It Works

1. **On startup**, the builder performs a full build it walks the entire `/contents` directory and compiles every `.dpt` or `.html` content file it finds.
2. **Each content file** declares which template it uses and provides values for that template's placeholders.
3. **The builder** reads the matching template, replaces all `{key}` placeholders with the values from the content file, and writes the final HTML to the `/builded` output directory preserving the original subdirectory structure.
4. **In watch mode**, the builder polls the `/contents` and `/templates` directories every second. It detects new, modified, and deleted files and responds accordingly:
   - A changed **content file** → rebuilds that single page.
   - A changed **template file** → triggers a full rebuild of all pages (since any page may use that template).
   - A deleted **content file** → removes the corresponding output file from `/builded`.

---

## Project Structure

```
project/
├── SiteBuilder.exe         # Main executable (or main.py)
├── contents/               # Your source content files
│   └── en/
│       └── index.dpt
├── templates/              # HTML template files
│   └── en/
│       └── template.html
└── builded/                # Output directory (auto-generated)
    └── en/
        └── index.html
```

- **`/contents`** All source content files live here. Subdirectories (e.g. language codes) are mirrored in the output.
- **`/templates`** HTML templates with `{key}` placeholders. Organized into subdirectories matching the ones in `/contents`.
- **`/builded`** The generated output. Do not edit files here manually they will be overwritten on the next build.

---

## Content Files

Content files use the `.dpt` extension (or `.html`) and follow a simple custom tag syntax.

### Declaring a Template

Every content file must start with a `<dptemplate>` tag that declares which template to use:

```html
<dptemplate t="template.html">
```

The value of `t` is the filename of the template inside the corresponding language subdirectory of `/templates`.

### Providing Data

Data blocks use `<dpt.key>` tags. The `key` must match a `{key}` placeholder in your template. The content between the opening and closing tags is the value that will be injected.

```html
<dptemplate t="template.html">

<dpt.title>My Page Title</dpt.title>

<dpt.content>
    <h2>Hello World</h2>
    <p>This is my page content.</p>
</dpt.content>
```

- Values can contain any valid HTML.
- Whitespace and newlines inside `<dpt.key>` blocks are trimmed automatically.
- Any `{key}` in the template that has no matching `<dpt.key>` block will be left as-is in the output.

---

## Templates

Templates are standard HTML files stored in the `/templates` directory. Use `{key}` placeholders anywhere in the file they will be replaced with the matching values from the content file at build time.

### Example Template

File: `/templates/en/template.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body>
    <header>
        <h1>My Site</h1>
    </header>
    <main>
        {content}
    </main>
    <footer>
        All Rights Reserved.
    </footer>
</body>
</html>
```

### Placeholder Rules

- Placeholders are written as `{key}` curly braces with no spaces around the key name.
- Keys are **case-sensitive**: `{Title}` and `{title}` are different placeholders.
- **Unmatched placeholders** (no corresponding `<dpt.key>` in the content file) are left unchanged in the output.
- Values can be plain text or any amount of HTML markup.

---

## Multi-Language Support

The generator mirrors your `/contents` directory structure into both `/templates` and `/builded`. This makes multi-language sites straightforward to manage.

### Structure

```
contents/
├── en/
│   ├── index.dpt
│   └── about.dpt
└── fr/
    ├── index.dpt
    └── about.dpt

templates/
├── en/
│   └── template.html
└── fr/
    └── template.html

builded/
├── en/
│   ├── index.html
│   └── about.html
└── fr/
    ├── index.html
    └── about.html
```

The builder automatically resolves the correct template by pairing the language subdirectory of the content file with the same subdirectory under `/templates`. For example, `contents/fr/index.dpt` declaring `<dptemplate t="template.html">` will use `/templates/fr/template.html`.

---

## Watch Mode

When started with `--watch`, the builder continuously monitors both the `/contents` and `/templates` directories for changes.

| Event | What Happens |
|---|---|
| Content file **added or modified** | That single page is rebuilt. |
| Template file **added or modified** | A **full rebuild** is triggered for all pages. |
| Content file **deleted** | The corresponding `.html` file in `/builded` is deleted. |

The watcher checks for changes every **1 second** using file modification timestamps no external libraries required.

---

## Build Behavior

### File Extensions

The builder processes files with the following extensions inside `/contents`:

| Source Extension | Output Extension |
|---|---|
| `.dpt` | `.html` |
| `.html` | `.html` |

### Output Path

The output path mirrors the source path, with the base directory swapped from `/contents` to `/builded` and the extension changed to `.html`.

**Example:**
```
contents/en/blog/post.dpt  →  builded/en/blog/post.html
```

Output subdirectories are created automatically if they do not exist.

### Error Handling

- If a content file is missing a `<dptemplate>` tag, a `[WARNING]` is printed and the file is skipped.
- If the referenced template file does not exist, an `[ERROR]` is printed and the file is skipped.
- File read/write errors print a `[CRITICAL ERROR]` message with details.

---

## Full Example

### File: `contents/en/index.dpt`

```html
<dptemplate t="template.html">

<dpt.title>Welcome to My Site</dpt.title>

<dpt.content>
    <h2>Hello, World!</h2>
    <p>This page was generated by Static Site Generator.</p>
</dpt.content>
```

### File: `templates/en/template.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
</head>
<body>
    <header><h1>My Site</h1></header>
    <main>
        {content}
    </main>
    <footer>All Rights Reserved.</footer>
</body>
</html>
```

### Output: `builded/en/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Welcome to My Site</title>
</head>
<body>
    <header><h1>My Site</h1></header>
    <main>
        <h2>Hello, World!</h2>
        <p>This page was generated by Static Site Generator.</p>
    </main>
    <footer>All Rights Reserved.</footer>
</body>
</html>
```

---

## Notes & Best Practices

- **Do not edit files in `/builded` manually.** They are overwritten on every build.
- **Template changes trigger a full rebuild.** This is intentional since any content file could use the changed template, all pages are recompiled to stay consistent.
- **Keep one template per language directory.** If multiple content files share the same layout, they can all reference the same template file.
- **Content values are injected as raw HTML.** Make sure your `<dpt.key>` values are well-formed HTML to avoid broken output pages.
- **Placeholder keys are case-sensitive.** `{Content}` and `{content}` will not match each other.
- **The `/builded` folder is safe to deploy directly** to any static hosting service (GitHub Pages, Netlify, S3, etc.) after a build.
- When running from source with Python, make sure you are using **Python 3** the script uses `os`, `re`, `time`, and `sys` from the standard library, so no additional packages need to be installed.
