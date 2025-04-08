# MACO APP Testszenarien

Dieses Repository enthält Testfälle für die MACO APP, die über die Benutzeroberfläche gestartet werden können.

## 📁 Verzeichnisstruktur

Alle Testfälle befinden sich im Ordner `testszenarios`. 

Jeder Testfall befindet sich in einem eigenen Unterordner mit folgender Namenskonvention:
`[PROZESS]_[MARKTROLLE]_[TESTSZENARIONUMMER]`

## 📄 Dateiformate

Die Testfälle werden in folgenden Dateiformaten gespeichert:

- **Eingehende Testfälle**: `.edi` Dateien
- **Ausgehende Testfälle**: `.event` Dateien

## 🚀 Verwendung

1. Navigieren Sie zum Dropdown-Menü "Testszenarien" in der MACO APP-Oberfläche
2. Wählen Sie den gewünschten Testfall aus
3. Der Testfall kann direkt gestartet werden.

## 📋 Beispielstruktur

```
testszenarios/
├── LIEFERBEGINN_NB_TESTSZENARIO1_55001/
│   └── 55001.edi
├── LIEFERENDE_NB_TESTSZENARIO1_55004/
│   └── 55004.edi
└── LIEFERENDE_LF_TESTSZENARIO1_55007/
    └── 55007.event
```
