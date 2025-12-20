import os
import time
import re
import sys

# --- SETTINGS (ADJUSTED PART) ---
# Detect the correct base directory where the program runs
if getattr(sys, 'frozen', False):
    # If running as an .exe (PyInstaller), use the executable's folder
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # If running as a .py, use the script's folder
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONTENTS_DIR = os.path.join(BASE_DIR, 'contents')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'template')
BUILD_DIR = os.path.join(BASE_DIR, 'builded')

# --- HELPER CLASSES ---

class PageBuilder:
    def __init__(self):
        self.regex_template_key = re.compile(r'\{(.*?)\}')
        # matches <dptemplate t="template.html">
        self.regex_template_tag = re.compile(r'<dptemplate t="(.+?)">')
        # matches <dpt.key>value</dpt.key> blocks (works in DOTALL mode)
        self.regex_data_block = re.compile(r'<dpt\.(.*?)>([\s\S]*?)<\/dpt\.\1>')

    def render_template(self, template_content, replacements):
        """Replace {key} placeholders in the template."""
        def replace_match(match):
            key = match.group(1)
            return replacements.get(key, match.group(0))
        
        return self.regex_template_key.sub(replace_match, template_content)

    def parse_content(self, filepath):
        """Read a content file and parse its data."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # 1. Şablon ismini bul
            tmpl_match = self.regex_template_tag.search(content)
            if not tmpl_match:
                print(f"[WARNING] Template tag not found: {filepath}")
                return None
            
            template_name = tmpl_match.group(1)

            # 2. Veri bloklarını bul
            replacements = {}
            for match in self.regex_data_block.finditer(content):
                key = match.group(1)
                value = match.group(2).strip()
                replacements[key] = value

            return template_name, replacements
        except Exception as e:
            print(f"[ERROR] Error reading file ({filepath}): {e}")
            return None

    def build_page(self, content_path):
        """Build a single page."""
        try:
            # content/en/index.dpt -> en/index.dpt
            rel_path = os.path.relpath(content_path, CONTENTS_DIR)
            
            # Find language folder (e.g., 'en')
            parts = rel_path.split(os.sep)
            lang = parts[0] if len(parts) > 1 else ""

            # Parse it
            parsed = self.parse_content(content_path)
            if not parsed:
                return

            template_name, replacements = parsed
            
            # Construct template path: template/en/main.html
            template_path = os.path.join(TEMPLATE_DIR, lang, template_name)

            if not os.path.exists(template_path):
                print(f"[ERROR] Template not found: {template_path}")
                return

            # Read template
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

            # Render
            final_html = self.render_template(template_content, replacements)

            # Prepare output path: builded/en/index.html
            output_rel = rel_path.replace('.dpt', '.html').replace('.txt', '.html') # Uzantı değişimi
            output_path = os.path.join(BUILD_DIR, output_rel)
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_html)
            
            print(f"[CREATED] {output_path}")

        except Exception as e:
            print(f"[CRITICAL ERROR] while processing {content_path}: {e}")

    def remove_page(self, content_path):
        """Remove the output for a deleted source file."""
        try:
            rel_path = os.path.relpath(content_path, CONTENTS_DIR)
            output_rel = rel_path.replace('.dpt', '.html')
            output_path = os.path.join(BUILD_DIR, output_rel)
            if os.path.exists(output_path):
                os.remove(output_path)
                print(f"[DELETED] {output_path}")
        except ValueError:
            pass # Ignore if file is outside CONTENTS_DIR

    def full_build(self):
        """Perform a full rebuild of the entire project."""
        print(f"--- Full build starting ({CONTENTS_DIR}) ---")
        if not os.path.exists(CONTENTS_DIR):
            print(f"[WARNING] '{CONTENTS_DIR}' folder not found.")
            return

        for root, dirs, files in os.walk(CONTENTS_DIR):
            for file in files:
                if file.endswith('.dpt') or file.endswith('.html'):
                    self.build_page(os.path.join(root, file))
        print("--- Full build finished ---")

# --- İZLEYİCİ (WATCHER) ---
class SimpleWatcher:
    """Simple file watcher without external libraries."""
    def __init__(self, directories, callback_change, callback_remove):
        self.directories = directories
        self.callback_change = callback_change
        self.callback_remove = callback_remove
        self.snapshot = {}
        self.running = True

    def _scan(self):
        current_files = {}
        for directory in self.directories:
            if not os.path.exists(directory): continue
            for root, _, files in os.walk(directory):
                for file in files:
                    if not (file.endswith('.dpt') or file.endswith('.html')): continue
                    
                    filepath = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(filepath)
                        current_files[filepath] = mtime
                    except OSError:
                        continue 
        return current_files

    def start(self):
        print("Watch mode active (press CTRL+C to exit)...")
        self.snapshot = self._scan()
        
        try:
            while self.running:
                time.sleep(1) 
                new_snapshot = self._scan()

                # Değişen veya Eklenenler
                for filepath, mtime in new_snapshot.items():
                    if filepath not in self.snapshot or self.snapshot[filepath] != mtime:
                            if TEMPLATE_DIR in filepath:
                                print(f"[TEMPLATE CHANGED] {os.path.basename(filepath)} -> Performing full build.")
                                builder.full_build()
                            else:
                                print(f"[MODIFIED] {os.path.basename(filepath)}")
                                self.callback_change(filepath)

                # Silinenler
                for filepath in list(self.snapshot.keys()):
                    if filepath not in new_snapshot:
                        if CONTENTS_DIR in filepath:
                            print(f"[DELETED] {os.path.basename(filepath)}")
                            self.callback_remove(filepath)

                self.snapshot = new_snapshot

        except KeyboardInterrupt:
            print("\nWatch stopped.")

# --- ANA PROGRAM ---

if __name__ == "__main__":
    builder = PageBuilder()
    
    # 1. Perform a full build at startup
    builder.full_build()

    # 2. If the --watch argument is provided, start watching
    if "--watch" in sys.argv:
        watcher = SimpleWatcher(
            directories=[CONTENTS_DIR, TEMPLATE_DIR],
            callback_change=builder.build_page,
            callback_remove=builder.remove_page
        )
        watcher.start()