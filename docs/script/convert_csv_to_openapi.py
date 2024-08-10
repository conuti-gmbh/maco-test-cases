import csv
import yaml
import re
from datetime import datetime

# Pfade zu den Dateien
csv_file = 'Schnittstellen_Prozesse.csv'
output_file = '../processMappingGenerated.yaml'
log_file = 'script.log'

# Log-Datei initialisieren
with open(log_file, 'w', encoding='utf-8') as log:
    log.write(f"Skript gestartet am {datetime.now().isoformat()}\n")

# Hilfsfunktion, um Zeilenumbrüche zu entfernen und durch Komma zu ersetzen
def clean_multiline_string(value):
    if isinstance(value, str):
        return value.replace('\n', ', ')
    return value

# Hilfsfunktion, um Kapitel bis "Nr." zu extrahieren
def extract_kapitel(kapitel):
    match = re.search(r'^(.+?Nr\.)', kapitel)
    return match.group(1).replace(' ', '_') if match else kapitel.replace(' ', '_')

# Start der OpenAPI-Dokumentation
openapi_document = {
    'openapi': '3.0.0',
    'info': {
        'title': 'Generated API',
        'description': 'API basierend auf den Schnittstellenprozessen',
        'version': '1.0.0'
    },
    'paths': {},
    'components': {
        'schemas': {}
    },
    'tags': []
}

# Spaltenalias definieren
aliases = [
    'lfd_nr', 'ahb', 'beschreibung', 'pruefidentifikator', 'reaktion', 'prozessbeschreibung', 'kapitel', 'bezeichnung', 'prozessschritt',
    'aktion', 'komm_von', 'komm_an', 'objekt', 'geschaeftsvorfall', 'erweiterte_zuordnung', 'objekteigenschaft',
    'sparte_strom', 'sparte_gas', 'uebertragungsweg', 'fussnote', 'meilenstein', 'komm_von_ausloesende_events',
    'komm_von_lesende_schnittstellen', 'komm_von_schreibende_schnittstellen', 'komm_an_lesende_schnittstellen',
    'komm_an_schreibende_schnittstellen'
]

# CSV-Datei einlesen und OpenAPI-Dokument erstellen
with open(csv_file, mode='r', encoding='utf-8') as file:
    reader = csv.reader(file, delimiter=';')
    for row in reader:
        # Mapping der CSV-Daten auf die Aliase
        data = {alias: clean_multiline_string(value) for alias, value in zip(aliases, row)}

        # Prozessbeschreibung als Tag hinzufügen, wenn nicht bereits vorhanden
        if data['prozessbeschreibung'] not in [tag['name'] for tag in openapi_document['tags']]:
            openapi_document['tags'].append({'name': data['prozessbeschreibung']})

        # Pfad für die OpenAPI-Dokumentation generieren
        if data['sparte_gas'].strip().upper() == 'X':
            # Verwenden des Kapitels als Pfad, aber nur bis "Nr."
            path = extract_kapitel(data['kapitel'].strip())
        else:
            # Verwenden der Bezeichnung als Pfad
            path = data['bezeichnung'].strip().replace(' ', '_')
        
        if not path:
            path = f"default_path_{data['lfd_nr']}"

        # Wenn der Prüfidentifikator `--` ist, verwenden wir REF und Aktion
        if data['pruefidentifikator'].strip() == '--':
            schema_name = f"REF{data['aktion'].strip()}"
            display_name = f"→ {data['aktion'].strip()}"
        else:
            schema_name = f"PI{data['pruefidentifikator'].strip()}"
            display_name = schema_name
        
        # Pfad hinzufügen, wenn nicht schon vorhanden
        if f"/{path}" not in openapi_document['paths']:
            openapi_document['paths'][f"/{path}"] = {
                'options': {
                    'summary': path,
                    'description': '',
                    'tags': [data['prozessbeschreibung']],  # Prozessbeschreibung als Tag hinzufügen
                    'responses': {
                        '200': {
                            'description': '',  # Dieser wird später mit der Tabelle gefüllt
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'anyOf': []
                                    },
                                    'examples': {
                                        'example': {
                                            'value': []
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            # Markdown-Tabelle für die description erstellen (nur einmal hinzufügen)
            markdown_table_header = (
                "| Prüfidentifikator | Von | An | Beschreibung | Reaktion | Prozessschritt |\n"
                "|-------------------|-----|----|--------------|----------|----------------|\n"
            )
            openapi_document['paths'][f"/{path}"]['options']['description'] += markdown_table_header
        
        # Tabellenzeile für die description hinzufügen
        markdown_table_row = (
            f"| {display_name} | {data['komm_von']} | {data['komm_an']} | {data['beschreibung']} | {data['reaktion']} | {data['prozessschritt']} |\n"
        )
        openapi_document['paths'][f"/{path}"]['options']['description'] += markdown_table_row
        
        # Example-Datenstruktur (nur für PI, nicht für REF)
        if not schema_name.startswith("REF"):
            example = {
                'PRUEFIDENTIFIKATOR': schema_name,
                'VON [' + data['komm_von'] + '] TRIGGER EVENT' : data['komm_von_ausloesende_events'],
                'VON [' + data['komm_von'] + '] LESENDE API': data['komm_von_lesende_schnittstellen'],
                'VON [' + data['komm_von'] + '] SCHREIBENDE API': data['komm_von_schreibende_schnittstellen'],
                'AN [' + data['komm_an'] + '] LESENDE API': data['komm_an_lesende_schnittstellen'],
                'AN [' + data['komm_an'] + '] SCHREIBENDE API': data['komm_an_schreibende_schnittstellen']
            }
            openapi_document['paths'][f"/{path}"]['options']['responses']['200']['content']['application/json']['examples']['example']['value'].append(
                example
            )

        # Schema-Referenz hinzufügen, wenn es ein PI ist
        if not schema_name.startswith("REF"):
            openapi_document['paths'][f"/{path}"]['options']['responses']['200']['content']['application/json']['schema']['anyOf'].append(
                {'$ref': f'#/components/schemas/{schema_name}'}
            )
        
        # Schema in den Komponenten hinzufügen, wenn es ein PI ist und nicht schon vorhanden
        if not schema_name.startswith("REF") and schema_name not in openapi_document['components']['schemas']:
            openapi_document['components']['schemas'][schema_name] = {
                'type': 'object',
                'description': data['pruefidentifikator'] + ' ' + data['komm_von'] + '→' +  data['komm_an']+ ' ' + data['beschreibung'],
                'properties': {
                    'VON:TRIGGER_EVENT': {
                        'type': 'string',
                        'description': data['komm_von_ausloesende_events'],
                        'enum': [data['komm_von']]
                    },
                    'VON:LESENDE_API': {
                        'type': 'string',
                        'description': data['komm_von_lesende_schnittstellen'],
                        'enum': [data['komm_von']]                        
                    },
                    'VON:SCHREIBENDE_API': {
                        'type': 'string',
                        'description': data['komm_von_schreibende_schnittstellen'],
                        'enum': [data['komm_von']]                        
                    },
                    'AN:LESENDE_API': {
                        'type': 'string',
                        'description': data['komm_an_lesende_schnittstellen'],
                        'enum': [data['komm_an']]                        
                    },
                    'AN:SCHREIBENDE_API': {
                        'type': 'string',
                        'description': data['komm_an_schreibende_schnittstellen'],
                        'enum': [data['komm_an']]                        
                    }
                }
            }

        # Log-Eintrag
        with open(log_file, 'a', encoding='utf-8') as log:
            log.write(f"Pfad /{path} und Schema {schema_name} hinzugefügt.\n")

# YAML-Datei schreiben
with open(output_file, 'w', encoding='utf-8') as yaml_file:
    yaml.dump(openapi_document, yaml_file, allow_unicode=True, sort_keys=False)

with open(log_file, 'a', encoding='utf-8') as log:
    log.write(f"Generierung abgeschlossen. Die Datei {output_file} wurde erstellt.\n")
