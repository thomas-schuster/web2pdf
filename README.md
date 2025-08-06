[![Linting and Testing](https://github.com/thomas-schuster/web2pdf/actions/workflows/ci.yml/badge.svg)](https://github.com/thomas-schuster/web2pdf/actions/workflows/ci.yml)

# Web2PDF Python Agent

Ein Python-Agent zum Konvertieren von Web-Artikeln in professionelle PDF-Dokumente mit automatischer Bildverarbeitung, interaktiver Metadaten-Bearbeitung und erweiterten LaTeX-Kompilierungsoptionen.

## 🌟 Features

- **📄 Vollständige Konvertierung**: HTML → Markdown → LaTeX → PDF
- **🖼️ Intelligente Bildverarbeitung**: Automatischer Download und Integration von Web-Bildern
- **📝 Interaktive Metadaten**: Bearbeitung von Titel, Autor, Datum und URL
- **🔗 Klickbare QR-Codes**: Großer, klickbarer QR-Code auf dem Deckblatt
- **📚 Mehrfache Ausgaben**: HTML, Markdown, LaTeX und PDF für maximale Flexibilität
- **🧹 Automatische Bereinigung**: Entfernung problematischer HTML-Elemente und LaTeX-Konflikte
- **⚡ LuaLaTeX-Kompilierung**: Optionales LaTeX-Compiler-Modul mit LuaLaTeX für erweiterte Bildformat-Unterstützung
- **🖼️ GIF-Konvertierung**: Automatische Konvertierung von GIF-Bildern zu JPEG für LaTeX-Kompatibilität
- **🎨 Farbige Terminal-Ausgabe**: Detaillierte Fortschrittsinformationen und Fehlerdiagnose
- **🔧 Modulare Architektur**: Eigenständige Komponenten für maximale Flexibilität

## 🚀 Installation

### Voraussetzungen

1. **Python 3.8+** 
2. **Pandoc** für die Dokumentkonvertierung:
   ```bash
   # macOS
   brew install pandoc
   
   # Ubuntu/Debian
   sudo apt-get install pandoc
   
   # Windows
   # Download von https://pandoc.org/installing.html
   ```
3. **LuaLaTeX** für PDF-Generierung:
   ```bash
   # macOS
   brew install --cask mactex
   
   # Ubuntu/Debian
   sudo apt-get install texlive-luatex texlive-fonts-recommended
   ```
   
   **Hinweis:** Das System verwendet LuaLaTeX für verbesserte Bildformat-Unterstützung (GIF → JPEG Konvertierung).

### Setup

```bash
# Repository klonen
git clone https://github.com/thomas-schuster/web2pdf.git
cd web2pdf_python_agent

# Virtuelle Umgebung erstellen
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# oder
# .venv\Scripts\activate   # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt

# Für Entwicklung und Testing (optional)
pip install -r requirements-dev.txt
```

## 📖 Verwendung

### Basis-Verwendung

```bash
# Konvertiere einen Web-Artikel
python agent.py https://example.com/article

# Beispiel mit dem DeepLearning.AI Newsletter
python agent.py https://www.deeplearning.ai/the-batch/issue-312/
```

### Interaktive Sitzung

Der Agent führt Sie durch eine interaktive Metadaten-Bearbeitung:

```
✅ Please confirm or edit the following metadata:
(Press Enter to keep the current value, or type a new value)
Title  [Original Title]: Mein angepasster Titel
Author [Original Author]: 
Editor [thomas]: 
Date   [2025-08-05]: 
URL    [https://example.com]: 

🔧 Optional: Advanced LaTeX compilation
Would you like to compile the LaTeX file with our enhanced compiler?
(This provides better error handling and detailed output)
Compile LaTeX? (y/N): y

🔄 Compiling article.tex with enhanced LaTeX compiler...
📝 Compiling: article.tex
📁 Output directory: .
🔄 Running: lualatex -interaction=nonstopmode -halt-on-error article.tex
✅ LuaLaTeX compilation successful
🔄 Running second pass for references...
✅ LuaLaTeX compilation successful
✅ PDF created: article.pdf (125.3 KB)
🧹 Cleaning up auxiliary files...
🗑️  Removed: article.aux
🗑️  Removed: article.log
🗑️  Removed: article.out
✅ Enhanced LaTeX compilation completed successfully!
```

### LaTeX-Compiler-Modul (eigenständig)

Das LaTeX-Compiler-Modul kann auch eigenständig verwendet werden:

```bash
# Basis-Kompilierung
python latex_compiler.py document.tex

# Mit Optionen
python latex_compiler.py document.tex --no-cleanup --single-pass --quiet

# Hilfe anzeigen
python latex_compiler.py --help
```

**LaTeX-Compiler Features:**
- **LuaLaTeX-Engine**: Bessere Unterstützung für verschiedene Bildformate (einschließlich GIF → JPEG Konvertierung)
- **Zwei-Pass-Kompilierung**: Automatisch für korrekte Referenzen und Inhaltsverzeichnisse
- **Detaillierte Fehlerdiagnose**: Farbige Ausgabe mit spezifischen Fehlermeldungen
- **Automatische Aufräumung**: Entfernung von .aux, .log, .out Dateien
- **Dateigröße-Anzeige**: Information über das generierte PDF
- **Cross-Platform**: Funktioniert auf Windows, macOS und Linux
- **Timeout-Behandlung**: Schutz vor hängenden Kompilierungen

### Ausgabe-Dateien

Nach der Ausführung erhalten Sie:
- `article.html` - Originaler HTML-Inhalt
- `article.md` - Bereinigtes Markdown mit Metadaten
- `article.tex` - LaTeX-Quelldatei für manuelle Bearbeitung
- `article.pdf` - Finales PDF-Dokument
- `img/` - Ordner mit heruntergeladenen Bildern

## 🏗️ Architektur

### Workflow

```
🌐 Web-URL → 📥 HTML Download → 🔍 Metadaten-Extraktion
    ↓
📝 Markdown-Konvertierung → 🖼️ Bild-Download → ✏️ Interaktive Bearbeitung
    ↓
📄 LaTeX-Generierung → 🧹 Post-Processing → 📊 PDF-Erstellung
    ↓
🔧 Optionale erweiterte LaTeX-Kompilierung (mit Benutzerbestätigung)
```

### Kern-Funktionen

**Haupt-Agent (`agent.py`):**
- **`fetch_html()`**: Lädt HTML-Inhalt von URLs herunter
- **`extract_metadata()`**: Extrahiert Titel und Autor aus HTML
- **`convert_to_markdown()`**: Konvertiert HTML zu Markdown mit Pandoc
- **`download_images()`**: Lädt Bilder herunter und speichert sie lokal
- **`insert_metadata()`**: Fügt YAML-Metadaten hinzu und bereinigt Inhalt
- **`generate_pdf()`**: Erstellt LaTeX und PDF mit Post-Processing

**LaTeX-Compiler-Modul (`latex_compiler.py`):**
- **`LaTeXCompiler`**: Hauptklasse für erweiterte LaTeX-Kompilierung
- **`compile_document()`**: Zwei-Pass XeLaTeX-Kompilierung mit Fehlerbehandlung
- **`check_xelatex()`**: Überprüfung der XeLaTeX-Verfügbarkeit
- **`cleanup_aux_files()`**: Automatische Aufräumung von Hilfsdateien
- **`get_file_size()`**: Berechnung und Anzeige der PDF-Dateigröße
- **`Colors`**: ANSI-Farbcodes für verbesserte Terminal-Ausgabe

### LaTeX-Template

Das Projekt verwendet ein angepasstes LaTeX-Template (`webarticle.latex`) mit:
- **Professionellem Layout**: Moderne Typografie und Formatierung
- **QR-Code Integration**: 3cm großer, klickbarer QR-Code auf dem Deckblatt
- **Bildunterstützung**: Automatische Bildpfade und -verarbeitung
- **Pandoc-Kompatibilität**: Nahtlose Integration mit Pandoc-Output

## 🧪 Tests

Das Projekt verfügt über eine umfassende Test-Suite mit pytest. Für Details siehe [tests/README.md](tests/README.md).

### Tests ausführen

```bash
# Alle Tests ausführen
.venv/bin/python -m pytest tests/ -v

# Tests für den Haupt-Agent
.venv/bin/python -m pytest tests/test_agent.py -v

# Tests für das LaTeX-Compiler-Modul
.venv/bin/python -m pytest tests/test_latex_compiler.py -v

# Spezifische Test-Klassen
.venv/bin/python -m pytest tests/test_agent.py::TestDownloadImages -v

# Mit Coverage-Report
.venv/bin/python -m pytest tests/ --cov=. --cov-report=html
```

### Test-Abdeckung
- ✅ **28 Tests gesamt** (Unit + Integration)
- ✅ **15 Tests** für Haupt-Agent (agent.py)
- ✅ **13 Tests** für LaTeX-Compiler-Modul (latex_compiler.py)
- ✅ HTTP-Mocking für reproduzierbare Tests
- ✅ Temporäre Dateien für sichere Testumgebung
- ✅ Integration mit echten Daten
- ✅ Umfassende Fehlerbehandlung-Tests

## 🔧 Entwicklung

### Code-Qualität

Das Projekt verwendet verschiedene Tools für Code-Qualität:

```bash
# Linting mit flake8
.venv/bin/flake8 agent.py tests/

# Code-Formatierung mit black
.venv/bin/black agent.py tests/

# Import-Sortierung mit isort
.venv/bin/isort agent.py tests/

# Type-Checking mit mypy
.venv/bin/mypy agent.py --ignore-missing-imports
```

### CI/CD Pipeline

GitHub Actions führt automatisch bei jedem Push/PR aus:
- **Linting**: flake8, black, isort, mypy
- **Tests**: Alle 15 Tests auf Python 3.13
- **Integration**: Test mit echter URL
- **Coverage**: Code-Abdeckung mit pytest-cov

### Lokale CI-Simulation

Die CI-Pipeline kann lokal vor dem Push getestet werden:

```bash
# Lokale CI ausführen
./local-ci.sh

# Alternative: act (erfordert Docker)
act push --container-architecture linux/amd64
```

## 🛠️ Erweiterte Konfiguration

### Environment Variables

```bash
# GPG-Konfiguration für PDF-Signing (optional)
export GPG_TTY=$(tty)

# Benutzer-Information
export USER=your_username
```

### Anpassungen

**LaTeX-Template bearbeiten:**
```bash
# Bearbeite webarticle.latex für Layout-Anpassungen
vim webarticle.latex
```

**Bildverarbeitung anpassen:**
- Bildgrößen in `download_images()` ändern
- Unterstützte Formate in regex-Patterns erweitern
- Fallback-Bilder in `webarticle.latex` definieren

## 🐛 Fehlerbehebung

### Häufige Probleme

**Pandoc nicht gefunden:**
```bash
# Prüfe Installation
pandoc --version
which pandoc
```

**LuaTeX Fehler:**
```bash
# Prüfe LaTeX-Installation
luatex --version

# Fehlende Pakete installieren
sudo tlmgr install <package-name>
```

**Bild-Download schlägt fehl:**
- Überprüfe Internetverbindung
- Manche Bilder verwenden Placeholder (`example-image-a`)
- Images werden in `img/` Ordner gespeichert

**LaTeX-Kompilierung:**
- Prüfe `article.tex` auf Syntaxfehler
- Verwende `--debug` für detaillierte Pandoc-Ausgabe
- Für erweiterte Diagnostik: `python latex_compiler.py article.tex`

**LaTeX-Compiler-Modul Fehler:**
```bash
# LuaTeX nicht verfügbar
python latex_compiler.py --help  # Zeigt Hilfe ohne LuaTeX

# Detaillierte Fehlerdiagnose
python latex_compiler.py document.tex  # Zeigt farbige Fehlermeldungen

# Aufräumung deaktivieren für Debug
python latex_compiler.py document.tex --no-cleanup
```

### Debug-Modus

```bash
# Verbose Pandoc-Ausgabe
pandoc --verbose input.md -o output.pdf

# LaTeX-Zwischendateien behalten
pandoc --keep-tex input.md -o output.pdf

# Erweiterte LaTeX-Kompilierung mit Details
python latex_compiler.py document.tex --verbose

# Einzelner Kompilierungspass
python latex_compiler.py document.tex --single-pass
```

## 🚀 Erweiterte Nutzung

### LaTeX-Anpassungen

**Eigenes LaTeX-Template verwenden:**
```bash
# Template kopieren und anpassen
cp webarticle.latex my_template.latex
# Dann in agent.py den Template-Pfad ändern
```

**Manuelle LaTeX-Kompilierung:**
```bash
# Nach agent.py Ausführung:
python latex_compiler.py article.tex

# Mit benutzerdefinierten Optionen:
python latex_compiler.py article.tex --no-cleanup --single-pass
```

### Automatisierung

**Batch-Verarbeitung:**
```bash
#!/bin/bash
urls=(
  "https://example.com/article1"
  "https://example.com/article2"
  "https://example.com/article3"
)

for url in "${urls[@]}"; do
  echo "Processing: $url"
  echo -e "\n\n\n\nn" | python agent.py "$url"
done
```

**Headless-Modus (ohne Interaktion):**
```bash
# Mit Standard-Metadaten
echo -e "\n\n\n\nn" | python agent.py https://example.com/article
```

## 📚 API-Dokumentation

### LaTeXCompiler Klasse

```python
from latex_compiler import LaTeXCompiler, Colors

# Initialisierung
compiler = LaTeXCompiler(verbose=True)  # Mit detaillierter Ausgabe
compiler = LaTeXCompiler(verbose=False) # Stille Ausführung

# Kompilierung
success = compiler.compile_document(
    tex_file_path="document.tex",  # Pfad zur .tex Datei
    cleanup=True,                  # Hilfsdateien automatisch löschen
    two_pass=True                  # Zwei-Pass-Kompilierung für Referenzen
)

# Einzelne Methoden
compiler.check_lualatex()                  # LuaTeX verfügbar?
compiler.get_file_size(Path("file.pdf"))   # Dateigröße berechnen
compiler.cleanup_aux_files(tex_file)       # Hilfsdateien aufräumen
compiler.print_colored("Message", Colors.GREEN)  # Farbige Ausgabe
```
### Verwendung im Code

```python
#!/usr/bin/env python3
import sys
from latex_compiler import LaTeXCompiler

def main():
    if len(sys.argv) != 2:
        print("Usage: script.py file.tex")
        return 1
    
    compiler = LaTeXCompiler(verbose=True)
    
    if not compiler.check_lualatex():
        print("❌ LuaTeX not available")
        return 1
    
    success = compiler.compile_document(
        sys.argv[1],
        cleanup=True,
        two_pass=True
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
```

### Code-Standards

- **PEP 8** für Python-Code
- **Docstrings** für alle Funktionen
- **Tests** für neue Features
- **Type Hints** wo möglich

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz.

## 🙏 Danksagungen

- **Pandoc**: Für die excellente Dokumentkonvertierung
- **BeautifulSoup**: Für zuverlässiges HTML-Parsing  
- **LuaTeX**: Für professionelle PDF-Generierung
- **Python Community**: Für die großartigen Libraries

## 🤝 Beitragen

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/amazing-feature`)
3. Committe deine Änderungen (`git commit -m 'Add amazing feature'`)
4. Pushe zum Branch (`git push origin feature/amazing-feature`)
5. Öffne eine Pull Request


## 📧 Kontakt

Für Fragen, Verbesserungsvorschläge oder Bug-Reports öffne bitte ein Issue im Repository.
