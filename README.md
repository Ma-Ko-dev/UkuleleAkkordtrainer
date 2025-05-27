![Build Status](https://github.com/Ma-Ko-dev/UkuleleAkkordtrainer/actions/workflows/automatic_build.yml/badge.svg)
![GitHub Release](https://img.shields.io/github/v/release/Ma-Ko-dev/UkuleleAkkordtrainer?style=flat-square)
![GitHub issues](https://img.shields.io/github/issues/Ma-Ko-dev/UkuleleAkkordtrainer?style=flat-square)
![GitHub last commit](https://img.shields.io/github/last-commit/Ma-Ko-dev/UkuleleAkkordtrainer?style=flat-square)
![GitHub release downloads](https://img.shields.io/github/downloads/Ma-Ko-dev/UkuleleAkkordtrainer/total)
![GitHub stars](https://img.shields.io/github/stars/Ma-Ko-dev/UkuleleAkkordtrainer?style=flat-square)
![GitHub forks](https://img.shields.io/github/forks/Ma-Ko-dev/UkuleleAkkordtrainer?style=flat-square)
![License](https://img.shields.io/github/license/Ma-Ko-dev/UkuleleAkkordtrainer)
![Python](https://img.shields.io/badge/python-3.x-blue)
![Platform](https://img.shields.io/badge/platform-Windows-blue)


# Ukulele Akkordtrainer

Ein einfacher Ukulele-Akkordtrainer mit grafischem Griffbrett und Sprachsteuerung in Python.

## Funktionen

- Darstellung eines vollständigen Ukulele-Griffbretts mit Saiten- und Bundmarkierungen  
- Visualisierung von Akkorden (bis zu 12 Bünde, 4 Saiten)  
- Anzeige der Akkordnamen  
- Sprachsteuerung zur Bedienung („weiter“, „stopp“)  
- Vermeidung von Wiederholungen bei den angezeigten Akkorden
- Verlauf/Historie der letzten 4 Akkorde anzeigen

## Vorschau
![Vorschau des Ukulele Akkordtrainers](preview.png)

## Voraussetzungen

- Python 3.x  
- Tkinter 
- SpeechRecognition
- PyAudio

## Installation

Aktuellsten [Release](https://github.com/Ma-Ko-dev/UkuleleAkkordtrainer/releases/latest) herunterladen, entpacken und starten.

-- oder --

1. Repository klonen oder herunterladen  
2. Abhängigkeiten installieren
3. Ausführen


## Hinweise zur Spracherkennung

Die Sprachsteuerung verwendet die Google Web Speech API, die online ist und evt.  Nutzungslimits hat. Für umfangreiche oder kommerzielle Nutzung sollte eine eigene API-Lösung erwogen werden.
