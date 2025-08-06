# Web2PDF Agent Tests

Dieses Projekt enthält umfassende Tests für den Web2PDF Python Agent mit pytest. Die Test-Suite umfasst sowohl den Haupt-Agent als auch das LaTeX-Compiler-Modul.

## Test-Struktur

### Unit Tests - Haupt-Agent (`test_agent.py`)
- **TestFetchHTML**: Tests für das Herunterladen von HTML-Inhalten
- **TestExtractMetadata**: Tests für die Metadaten-Extraktion aus HTML
- **TestConvertToMarkdown**: Tests für die HTML-zu-Markdown-Konvertierung
- **TestDownloadImages**: Tests für das Herunterladen und Verarbeiten von Bildern
- **TestInsertMetadata**: Tests für das Einfügen von Metadaten in Markdown
- **TestGeneratePDF**: Tests für die PDF-Generierung

### Unit Tests - LaTeX-Compiler (`test_latex_compiler.py`)
- **TestLaTeXCompiler**: Tests für die LaTeX-Compiler-Klasse
  - Initialisierung und Konfiguration
  - Farbige Terminal-Ausgabe
  - XeLaTeX-Verfügbarkeitsprüfung
  - Dateigröße-Berechnung
  - Kompilierungsprozess
  - Aufräumung von Hilfsdateien
- **TestColors**: Tests für ANSI-Farbcode-Konstanten

### Integration Tests
- **TestIntegration**: Tests mit dem tatsächlich verwendeten DeepLearning.AI Artikel
  - Überprüfung der Metadaten-Extraktion
  - Validierung heruntergeladener Bilder
  - Überprüfung generierter Dateien

## Tests ausführen

### Alle Tests (beide Module)
```bash
# Im virtuellen Environment (von der Projektwurzel aus)
.venv/bin/python -m pytest tests/ -v

# Mit detaillierter Ausgabe und Coverage
.venv/bin/python -m pytest tests/ -v --tb=short --cov=. --cov-report=term-missing
```

### Tests nach Modul getrennt

**Haupt-Agent Tests:**
```bash
.venv/bin/python -m pytest tests/test_agent.py -v
```

**LaTeX-Compiler Tests:**
```bash
.venv/bin/python -m pytest tests/test_latex_compiler.py -v
```

### Spezifische Test-Klassen
```bash
# Agent-spezifische Tests
.venv/bin/python -m pytest tests/test_agent.py::TestFetchHTML -v
.venv/bin/python -m pytest tests/test_agent.py::TestDownloadImages -v

# LaTeX-Compiler-spezifische Tests
.venv/bin/python -m pytest tests/test_latex_compiler.py::TestLaTeXCompiler -v
.venv/bin/python -m pytest tests/test_latex_compiler.py::TestColors -v
```

### Einzelne Tests
```bash
# Agent-Tests
.venv/bin/python -m pytest tests/test_agent.py::TestFetchHTML::test_fetch_html_success -v

# LaTeX-Compiler Tests
.venv/bin/python -m pytest tests/test_latex_compiler.py::TestLaTeXCompiler::test_compile_document_file_not_found -v
```

## Test-Abdeckung

### Haupt-Agent Tests (15 Tests)
- ✅ HTTP-Anfragen mit Mocking
- ✅ HTML-Parsing und Metadaten-Extraktion
- ✅ Pandoc-Integration (gemockt)
- ✅ Bild-Download mit Fehlerbehandlung
- ✅ Markdown-Verarbeitung und Bereinigung
- ✅ LaTeX/PDF-Generierung (gemockt)
- ✅ Integration mit echten Daten
- ✅ Temporäre Datei-Handling

### LaTeX-Compiler Tests (13 Tests)
- ✅ Kompiler-Initialisierung und Konfiguration
- ✅ Farbige Terminal-Ausgabe (verbose/quiet Modi)
- ✅ XeLaTeX-Verfügbarkeitsprüfung
- ✅ Dateigröße-Berechnung für verschiedene Dateigrößen
- ✅ Fehlerbehandlung bei nicht existierenden Dateien
- ✅ Validierung von Dateierweiterungen
- ✅ Kompilierungsprozess ohne XeLaTeX
- ✅ Aufräumung von LaTeX-Hilfsdateien
- ✅ ANSI-Farbcode-Konstanten

### Gesamt: 28 Tests
- **Unit Tests**: 25 Tests für spezifische Funktionen
- **Integration Tests**: 3 Tests mit echten Daten
- **Mocking**: Umfassende Mocks für externe Abhängigkeiten
- **Error Handling**: Tests für alle Fehlerfälle

## Mocking-Strategien

### Haupt-Agent Mocking
- **HTTP-Requests**: Vollständig gemockt für reproduzierbare Tests
- **Subprocess-Aufrufe**: Pandoc-Aufrufe werden gemockt
- **Dateisystem**: Temporäre Dateien für sichere Tests
- **Integration Tests**: Verwenden echte Dateien wenn verfügbar

### LaTeX-Compiler Mocking
- **Subprocess XeLaTeX**: Mock für XeLaTeX-Verfügbarkeitsprüfung
- **Dateisystem-Operationen**: Temporäre Verzeichnisse für Cleanup-Tests
- **Objekt-Patching**: Mock von LaTeXCompiler-Methoden für Fehlerszenarien
- **Exception-Handling**: Simulation von FileNotFoundError und anderen Exceptions

## Test-Daten und Fixtures

### Agent Test-Daten
- **HTML-Beispiele**: Vordefinierte HTML-Strings für Parsing-Tests
- **Mock-Responses**: HTTP-Response-Objekte für Request-Tests
- **Temporäre Dateien**: Sichere Datei-Erstellung und -Löschung

### LaTeX-Compiler Test-Daten
- **Temporäre LaTeX-Dateien**: Minimal-LaTeX für Kompilierungstests
- **Mock-Dateisysteme**: Simulation von Dateistrukturen
- **ANSI-Farbcodes**: Validierung von Terminal-Ausgabe-Formatierung

## Voraussetzungen

```bash
# Basis-Test-Dependencies
pip install pytest pytest-mock

# Für Coverage-Reports
pip install pytest-cov

# Alle Entwicklungs-Dependencies (empfohlen)
pip install -r requirements-dev.txt
```

## Test-Konfiguration

Die Konfiguration befindet sich in `pytest.ini` und umfasst:
- Verbose Ausgabe für detaillierte Test-Resultate
- Kurze Tracebacks für bessere Lesbarkeit
- Filterung von Deprecation Warnings
- Test-Discovery-Pfade
- Coverage-Integration

## Continuous Integration

Die Tests werden automatisch in der GitHub Actions CI/CD-Pipeline ausgeführt:

```yaml
# .github/workflows/ci.yml
- name: Run tests
  run: |
    python -m pytest tests/ -v --cov=. --cov-report=xml
```

**CI-Matrix:**
- Python 3.8, 3.9, 3.10, 3.11, 3.12
- Ubuntu Latest
- Alle 28 Tests müssen bestehen

## Lokale Test-Entwicklung

### Neuen Test hinzufügen

1. **Agent-Test** in `test_agent.py`:
```python
def test_new_feature(self):
    """Test für neue Agent-Funktionalität"""
    # Test-Implementation
    pass
```

2. **LaTeX-Compiler-Test** in `test_latex_compiler.py`:
```python
def test_new_compiler_feature(self):
    """Test für neue Compiler-Funktionalität"""
    compiler = LaTeXCompiler(verbose=False)
    # Test-Implementation
    pass
```

### Test-Debugging

```bash
# Einzelnen Test mit maximalen Details
.venv/bin/python -m pytest tests/test_agent.py::TestFetchHTML::test_fetch_html_success -v -s --tb=long

# Tests mit Pdb-Debugging
.venv/bin/python -m pytest tests/ -v --pdb

# Tests ohne Capture für print-Debugging
.venv/bin/python -m pytest tests/ -v -s
```
