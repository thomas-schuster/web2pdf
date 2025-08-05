# Web2PDF Agent Tests

Dieses Projekt enthält umfassende Tests für den Web2PDF Python Agent mit pytest.

## Test-Struktur

### Unit Tests
- **TestFetchHTML**: Tests für das Herunterladen von HTML-Inhalten
- **TestExtractMetadata**: Tests für die Metadaten-Extraktion aus HTML
- **TestConvertToMarkdown**: Tests für die HTML-zu-Markdown-Konvertierung
- **TestDownloadImages**: Tests für das Herunterladen und Verarbeiten von Bildern
- **TestInsertMetadata**: Tests für das Einfügen von Metadaten in Markdown
- **TestGeneratePDF**: Tests für die PDF-Generierung

### Integration Tests
- **TestIntegration**: Tests mit dem tatsächlich verwendeten DeepLearning.AI Artikel
  - Überprüfung der Metadaten-Extraktion
  - Validierung heruntergeladener Bilder
  - Überprüfung generierter Dateien

## Tests ausführen

### Alle Tests
```bash
# Im virtuellen Environment (von der Projektwurzel aus)
.venv/bin/python -m pytest tests/ -v
```

### Spezifische Test-Klasse
```bash
.venv/bin/python -m pytest tests/test_agent.py::TestFetchHTML -v
```

### Einzelner Test
```bash
.venv/bin/python -m pytest tests/test_agent.py::TestFetchHTML::test_fetch_html_success -v
```

## Test-Abdeckung

Die Tests decken ab:
- ✅ HTTP-Anfragen mit Mocking
- ✅ HTML-Parsing und Metadaten-Extraktion
- ✅ Pandoc-Integration (gemockt)
- ✅ Bild-Download mit Fehlerbehandlung
- ✅ Markdown-Verarbeitung und Bereinigung
- ✅ LaTeX/PDF-Generierung (gemockt)
- ✅ Integration mit echten Daten
- ✅ Temporäre Datei-Handling

## Mocking-Strategien

- **HTTP-Requests**: Vollständig gemockt für reproduzierbare Tests
- **Subprocess-Aufrufe**: Pandoc-Aufrufe werden gemockt
- **Dateisystem**: Temporäre Dateien für sichere Tests
- **Integration Tests**: Verwenden echte Dateien wenn verfügbar

## Voraussetzungen

```bash
pip install pytest pytest-mock
```

## Test-Konfiguration

Die Konfiguration befindet sich in `pytest.ini` und umfasst:
- Verbose Ausgabe
- Kurze Tracebacks
- Filterung von Deprecation Warnings
