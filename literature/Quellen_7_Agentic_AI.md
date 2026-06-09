# Besprechungsprotokoll – Agentic AI Kernliteratur

**Datum:** _______________  
**Teilnehmer:** _______________, Prof. _______________  
**Dauer:** 45 min  
**Ziel:** Die 7 stabilsten Grundlagenquellen für eine mehrjährige Vorlesung vorstellen und abstimmen

---

## Übersicht der 7 Kernquellen

| # | Quelle | Jahr | Vermittelt |
|---|--------|------|------------|
| 1 | ReAct | 2022 | Der Agent-Loop |
| 2 | CoALA | 2023 | Kognitive Architektur |
| 3 | Tree of Thoughts | 2023 | Nicht-lineares Planen |
| 4 | Reflexion | 2023 | Selbstkorrektur |
| 5 | MetaGPT | 2023 | Multi-Agenten-Kollaboration |
| 6 | Abou Ali & Dornaika Survey | 2025 | Feldtaxonomie |
| 7 | Multi-Agent Risks | 2025 | Sicherheit |

---

## Zusammenfassungen

### 1. ReAct – Yao et al. (Princeton, 2022)
**Synergizing Reasoning and Acting in Language Models** · [arXiv:2210.03629](https://arxiv.org/abs/2210.03629)

> **Einfach erklärt:** Die KI denkt laut nach, probiert etwas aus, schaut was passiert – und wiederholt das, bis sie fertig ist. Wie ein Kind, das ein Puzzle löst: überlegen, ein Teil probieren, schauen ob es passt.

Kernidee: LLMs erzeugen abwechselnd **Gedanken** (Reasoning-Traces) und **Aktionen** (Tool-Aufrufe, Suchen), deren Ergebnisse als **Beobachtungen** zurückfließen. Dieser Thought→Action→Observation-Loop ist heute der Standardbaustein jeder Agentenarchitektur. Vor ReAct waren Reasoning (Chain-of-Thought) und Acting (Tool-Use) getrennte Forschungsstränge. Das Paper zeigt, dass die Kombination beider auf Wissens- und Entscheidungsaufgaben besser abschneidet als jeder Ansatz allein. De facto das meistzitierte Paper im Feld.

---

### 2. CoALA – Sumers et al. (2023)
**Cognitive Architectures for Language Agents** · [arXiv:2309.02427](https://arxiv.org/abs/2309.02427)

> **Einfach erklärt:** Ein Bauplan, der zeigt, aus welchen Teilen ein KI-Agent besteht – Kurzzeitgedächtnis, Langzeitgedächtnis und ein Entscheidungssystem. Wie eine Anleitung für ein Lego-Modell: welche Steine braucht man, und wo kommen sie hin?

Kernidee: Formales Framework, das LLM-Agenten auf klassische kognitive Architekturen (wie ACT-R, Soar) abbildet. Zerlegt einen Agenten in **Working Memory** (aktueller Kontext), **Long-Term Memory** (Wissen, Erfahrungen) und einen **Decision-Making-Zyklus** (Planen, Ausführen, Bewerten). Gibt damit eine theoretische Antwort auf die Frage *was ein Agent eigentlich ist*. Wichtig, weil es die Brücke zwischen klassischer KI und modernen LLM-Agenten schlägt.

---

### 3. Tree of Thoughts – Yao et al. (Princeton, 2023)
**Deliberate Problem Solving with Large Language Models** · [arXiv:2305.10601](https://arxiv.org/abs/2305.10601)

> **Einfach erklärt:** Statt nur einen Weg auszuprobieren, überlegt die KI mehrere Möglichkeiten gleichzeitig – wie bei einem Labyrinth, wo man an jeder Kreuzung alle Wege im Kopf durchgeht und den besten wählt.

Kernidee: Erweitert Chain-of-Thought von einer linearen Kette zu einem **Baum**. Das LLM generiert an jedem Schritt mehrere mögliche Gedanken, bewertet sie, und exploriert den Baum mit klassischen Suchverfahren (BFS, DFS). Ermöglicht Backtracking und Lookahead. Verbindet klassische KI-Suche mit generativer Sprachmodellierung. Zentral für das Verständnis, wie Agenten komplexe, nicht-lineare Probleme lösen.

---

### 4. Reflexion – Shinn et al. (2023)
**Language Agents with Verbal Reinforcement Learning** · [arXiv:2303.11366](https://arxiv.org/abs/2303.11366)

> **Einfach erklärt:** Die KI macht einen Fehler, schreibt sich auf *was* schiefgelaufen ist, und versucht es nochmal – diesmal mit dem Spickzettel. Wie ein Schüler, der nach einer Klausur seine Fehler aufschreibt und beim nächsten Mal besser abschneidet.

Kernidee: Agent führt eine Aufgabe aus, scheitert, und schreibt sich dann eine **verbale Selbstreflexion**. Diese Reflexion wird dem Kontext beim nächsten Versuch hinzugefügt. Das ist Reinforcement Learning ohne Gewichts-Updates – nur durch natürlichsprachliches Feedback. Einfaches aber mächtiges Pattern: der Agent lernt aus Fehlern innerhalb einer Sitzung. Heute in den meisten Agent-Frameworks als Standard-Modul implementiert.

---

### 5. MetaGPT – Hong et al. (Tsinghua, 2023)
**Meta Programming for Multi-Agent Collaboration** · [arXiv:2308.00352](https://arxiv.org/abs/2308.00352)

> **Einfach erklärt:** Statt einer einzigen KI arbeitet ein ganzes Team: einer plant, einer baut, einer prüft. Wie eine Gruppe in der Schule, in der jeder eine Aufgabe hat und alle zusammen ein Projekt abgeben.

Kernidee: Mehrere LLM-Agenten übernehmen definierte **Rollen** (Produktmanager, Architekt, Entwickler, Tester) und arbeiten in einem strukturierten Workflow zusammen. Die Agenten kommunizieren über standardisierte Artefakte (Requirements → Design → Code → Tests), nicht über freien Chat. Zeigt, dass menschliche Organisationsmuster (Arbeitsteilung, Dokument-Standards) auf Multi-Agenten-Systeme übertragbar sind. Grundlegende Referenz für jeden Multi-Agent-Ansatz.

---

### 6. Abou Ali & Dornaika Survey (U. Basque Country, 2025)
**Agentic AI: A Comprehensive Survey** · [Springer](https://link.springer.com/article/10.1007/s10462-025-11422-4)

> **Einfach erklärt:** Ein Buch, das alles sortiert, was bisher über KI-Agenten geschrieben wurde – aufgeteilt in zwei große Familien: die nach festen Regeln arbeiten und die, die kreativ improvisieren.

Kernidee: PRISMA-basierter Review von 90 Studien (2018–2025) mit einem **dualen Paradigmen-Framework**: *Symbolisch/Klassisch* (algorithmisches Planen, persistenter State) vs. *Neural/Generativ* (stochastische Generierung, prompt-basierte Orchestrierung). Die Paradigmenwahl ist domänenabhängig: symbolisch dominiert in sicherheitskritischen Bereichen (Medizin), neural in datenreichen Umgebungen (Finanz). Bester strukturierter Überblick über das gesamte Feld; peer-reviewed in Springer AI Review.

---

### 7. Multi-Agent Risks – Cooperative AI Foundation (2025)
**Multi-Agent Risks from Advanced AI** · [arXiv:2502.14143](https://arxiv.org/abs/2502.14143)

> **Einfach erklärt:** Was passiert, wenn viele KI-Agenten gleichzeitig arbeiten und keiner richtig aufpasst? Sie können aneinander vorbeireden, sich streiten oder sich heimlich verbünden. Dieses Paper schreibt auf, was alles schiefgehen kann.

Kernidee: 50+ Forscher (DeepMind, Anthropic, CMU, Harvard) klassifizieren systematisch Risiken bei interagierenden KI-Agenten. Drei Hauptkategorien: **Fehlkoordination** (Agenten arbeiten aneinander vorbei), **Konflikt** (widersprüchliche Ziele), **Kollusion** (Agenten kooperieren gegen menschliche Interessen). Dazu 7 übergreifende Risikofaktoren. Autoritative Quelle durch die breite institutionelle Beteiligung.

---

## Diskussion

1. Decken diese 7 Quellen die Grundlagen ausreichend ab?
2. Fehlt etwas Wesentliches für den Einstieg?
3. Reihenfolge in der Vorlesung: chronologisch oder thematisch?

## Nächste Schritte

- [ ] Leseliste freigegeben
- [ ] Nächster Termin: _______________

---

*Anlage: Vollständige Literatur-Navigationstabelle (31 Quellen) für spätere Vertiefung*
