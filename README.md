# Static Site Generator

## How to Use

Run the following command in your command line:

`./SiteBuilder.exe --watch`

This command watches your working directory, compiles the files in `/contents`, and outputs the results to the `/builded` folder.

## How It Works

**Project Structure:**
* `/builded` - Output directory.
* `/contents` - Source content files.
* `/templates` - HTML templates.
* `SiteBuilder.exe` - The main executable.

### Example Template
File path: `/templates/template.html`

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
        <h1>Site Header</h1>
    </header>
    <main>
        {content} </main>
    <footer>
        All Rights Reserved.
    </footer>
</body>
</html>
```

### Example Content

File path: /contents/index.html

```
<dptemplate t="template.html"> 
<dpt.title>Site Title</dpt.title>
<dpt.content>
    <h2>Foo Bar</h2>
    <p>Site Content</p>
</dpt.content>
```