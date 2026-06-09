# Labor Agentic AI — Einzelexperimente

Statt eines durchgehenden Laufbeispiels bearbeiten die Studierenden eine Reihe fokussierter Einzelexperimente, die jeweils ein einzelnes Vorlesungsthema isoliert beleuchten. Diese Datei katalogisiert die zur Auswahl stehenden Experimente. Im Semester werden daraus rund 10–12 ausgewählt, die das Kapitelmaterial abdecken; jedes Experiment ist in einer Lab-Sitzung in Zweiergruppen in Python umsetzbar und mit einem kurzen Bericht zu dokumentieren.

## Didaktische Leitprinzipien

**Design vor Code.** Vor jedem Lab-Schritt geben die Studierenden eine einseitige Design-Skizze ab — Komponenten-Diagramm, Trajektorien-Beispiel, Tool-Liste. Erst dann dürfen sie Code schreiben. Das verhindert das „ich tippe einfach mal los"-Muster und zwingt zu konzeptioneller Klärung, bevor sich Implementierungs-Details aufstauen.

**Architekturbegründung schriftlich.** Bei jedem Lab-Schritt schreiben die Studierenden eine kurze Architekturbegründung: „Ich habe für dieses Tool MCP statt Function Calling gewählt, weil …" oder „Ich habe einen Memory-Buffer statt Vektor-DB gewählt, weil …". Drei oder vier solcher Begründungen pro Sitzung schärfen den Blick für Trade-offs schneller als jede Vorlesung über Architecture Decision Records.

## Kurzübersicht nach Themen

| Thema | Experimente |
|---|---|
| **Agent-Loop & Mechanik** | Agent-Loop (minimal), Stop Conditions, Observation-Design, ReAct (handwritten) |
| **Reasoning & Prompting** | Reasoning Models, Prompt Engineering, Output Formatting |
| **Design Patterns** | Agentic Design Patterns, Pattern Selection, Planning (drei Varianten) |
| **Tool-Integration** | Function Calling (Aha-Moment), Function Calling vs. MCP, MCP Primitives |
| **Orchestrierung & Code-Struktur** | Framework vs. Plain-Code, DAG vs. Dynamic, LLM-Logik trennen |
| **Memory** | Memory-Infrastruktur (drei Stufen) |
| **Observability & Debugging** | Instrumentation, Observability (Endlosschleife), Tracing |
| **Multi-Agent** | Multi-Agent vs. Single-Agent + Critic |
| **Selbstverbessernde Agenten** | Self-Reflection (drei Setups), Reflexion (HumanEval), Drift, Reward-Hacking |
| **Sicherheit** | Prompt Injection (Knack-Challenge), Indirect Injection + Hardening, Tool Misuse, Sandboxing, Guardrails, Design Countermeasures |
| **Evaluation** | Evaluation Hygiene |

## Experimente nach Kapiteln

### Kap. 2 — Entwurfsprinzipien

**[[Agent Loop|Agent-Loop (minimal)]].** 30-zeiliger Python-Loop mit Taschenrechner als einzigem Tool. Ziel: die fünf Bausteine (LLM-Call, Tool Call, Observation, Context Buffer, Stop Condition) am eigenen Code hands-on durchlaufen.

**[[stop conditions|Stop Conditions]].** Agent mit nur einer Stop-Bedingung (LLM-Erfolgssignal) auf eine Aufgabe loslassen, bei der das LLM nicht zum Ziel kommt — etwa wegen eines kaputten Tools. 200 Iterationen, zehn Dollar verfeuert, kein Stopp. Dann mit drei kombinierten Stop-Bedingungen wiederholen. Diese Übung kostet 30 Token-Dollar — und spart später dreistellige Produktiv-Credits.

**[[observation|Observation-Design]].** Denselben Agenten zwei Mal laufen lassen — einmal mit rohen Tool-Outputs als Observations, einmal mit aufbereiteten, strukturierten Observations (Truncation, klare Fehlerformate, extrahierte Felder). Auf zehn Aufgaben Erfolgsrate und Token-Verbrauch messen. Erkenntnis: Observation-Design ist genauso ergebnisrelevant wie Prompt Engineering — „mehr Tokens raus" heißt nicht „mehr Information".

**[[ReAct|ReAct (handwritten)]].** 30-zeiligen ReAct-Loop von Hand schreiben (kein LangChain-Import) und das Modell zwingen, Thought/Action/Observation explizit auszugeben. Die Studierenden sehen die Mechanik direkt — und verstehen, dass „Agent" technisch nur „Schleife mit LLM und Tools" bedeutet, nichts Mystisches.

**[[agentic design patterns|Agentic Design Patterns]].** Jedes Pattern (Planning, Tool Use, Reflection, Multi-Agent) in der Vorlesung mit einem 10–20-zeiligen Mini-Codebeispiel illustriert; im Lab anschließend an einem realen System (z. B. SWE-agent, Devin) zeigen, wie die Patterns dort kombiniert sind. Patterns werden so nicht akademische Klassifikation, sondern tägliches Handwerkszeug.

**[[pattern selection|Pattern Selection]].** Eine Aufgabe geben („Schreibe einen einseitigen Bericht über die Wirtschaftslage in Schleswig-Holstein, mit drei Quellen") und zwei Architekturen skizzieren lassen: eine minimale (nur Tool Use), eine voll ausgebaute (alle vier Patterns). In der Diskussion: Welche Patterns hätten wirklich gebraucht werden müssen? Overhead in Tokens und Latenz? Sparsamkeit als Designwert.

**[[reasoning models|Reasoning Models]].** Denselben Tool-Agenten (z. B. Web-Search-Rechercheur) einmal mit klassischem LLM (plus ReAct-Wrapper) und einmal mit Reasoning-Modell (minimaler Loop) bauen. Messen: Token-Verbrauch, Latenz, Erfolgsrate, Code-Komplexität des Wrappers. Die Studierenden sehen unmittelbar, was es bedeutet, wenn Logik vom Prompt ins Modell wandert — und welche Konsequenzen das für Architektur, Kosten und Debug-Praxis hat.

### Kap. 3 — LLM-Agenten-Infrastruktur

**[[function calling|Function Calling — Aha-Moment]].** Funktion `multiply(a, b)` definieren, dem LLM die Signatur geben, eine Mathe-Aufgabe stellen — und beobachten, wie das LLM `multiply(7, 11)` aufruft, das Ergebnis 77 zurückbekommt und die finale Antwort daraus baut. Drei Zeilen Code — und „LLM kann nichts" wird zu „LLM kann alles, was ich ihm als Tool gebe".

**Function Calling vs. [[Model Context Protocol|MCP]].** Stunde 1: dasselbe Tool als Plain-Function-Call hart in den Agenten einbauen. Stunde 2: dasselbe Tool als MCP-Server abkapseln und aus dem Agenten heraus aufrufen. Gewinn der Indirektion wird unmittelbar sichtbar: Wiederverwendbarkeit, scharfe Sicherheitsgrenze (Berechtigungen, Logging, Sandboxing am Server), unabhängige Weiterentwicklung. MCP wird konkret statt Buzzword.

**[[MCP primitives|MCP Primitives]].** Ein minimaler MCP-Server mit je einem Tool-, Resource- und Prompt-Endpoint. Aufgabe: ein *Personal Wiki*, in dem der Agent Notizen schreibt (Tool), bestehende Notizen liest (Resource) und eine Zusammenfassungs-Anweisung anwendet (Prompt). Studierende sehen, wie die drei Primitive ineinandergreifen — und warum keines redundant ist.

**[[prompt engineering|Prompt Engineering]].** Denselben Agenten mit drei verschiedenen System-Prompts vergleichen: (1) minimal („Du bist ein Assistent"), (2) ausgearbeitet mit Rolle und Constraints, (3) ausgearbeitet plus drei Few-Shot-Beispiele. Auf zehn Aufgaben Erfolgsrate messen. Studierende sehen unmittelbar, dass derselbe Modell-Aufruf mit besserem Prompt eine messbar andere Leistung liefert.

**[[output formatting|Output Formatting]].** Aufgabe mit strukturiertem Output („Extrahiere aus diesem Artikel die fünf wichtigsten Fakten als JSON"). Drei Varianten testen: (1) ohne Format-Vorgabe, (2) mit Format-Beispiel im Prompt, (3) mit `structured output`-API. Auf 50 Texten messen, wie viele Outputs parsebar sind. Die typischen Zahlen 30 % / 80 % / 100 % sprechen für sich.

**[[framework vs plain-code|Framework vs. Plain-Code]] (Orchestrierung).** Denselben Agenten zweimal bauen: als 30–50-Zeilen-Plain-Python-Loop und als LangGraph-Implementierung. Funktional identisch, im Code radikal verschieden. Messen: Implementierungszeit, Debugging-Zeit, Lines of Code, eigenes Verständnis. Drei von vier Studierenden erkennen am Ende: Plain-Code bringt schneller ans Ziel, das Framework schenkt bessere Visualisierung, Persistenz und Branching — kostet aber Lernkurve, Indirektion und Lock-in.

**[[DAG-based vs. dynamic|DAG-based vs. Dynamic]].** Denselben Agenten in beiden Stilen bauen: einmal als plain-Python-`while`-Schleife (dynamisch), einmal als LangGraph-DAG. Messen: Lines of Code, Implementierungszeit, Debugging-Aufwand, Verhalten bei unerwarteter Eingabe. Trade-off wird sichtbar: der DAG ist anfangs aufwändiger, aber langfristig auditierbar.

**[[LLM-Logik]] vs. [[orchestration|Orchestrierung]] trennen.** Code-Vorlage, in der LLM-Logik und Orchestrierung in eine Klasse gepresst sind. Aufgabe: in zwei separate Module trennen, anschließend einen Test für die LLM-Logik *ohne* echte API-Aufrufe schreiben. Schärft das Verständnis der Architektur-Trennung schneller als jede Vorlesung über *Separation of Concerns*.

**[[planning|Planning]] (drei Varianten).** Eine mittelschwere Aufgabe in drei Varianten lösen: (1) ReAct-Loop ohne expliziten Plan, (2) [[plan-and-execute|Plan-and-Execute]] mit vorab generiertem Plan, (3) Plan-and-Execute mit Re-Planning nach jedem Schritt. Vergleich auf Erfolgsrate, Tokenverbrauch, Latenz, Plan-Qualität bei unerwarteten Eingaben. Lehrreich: keine Variante ist universell überlegen — die Wahl hängt am Aufgabentyp.

**[[memory infrastructure|Memory-Infrastruktur (drei Stufen)]].** Agenten in drei Memory-Stufen bauen: (1) nur Conversation-Buffer, (2) plus In-Memory-Liste mit Tool-basierten Reads, (3) plus Vektor-DB mit automatischem Retrieval. Verhalten über eine simulierte Drei-Sitzungen-Konversation messen. Studierende sehen, wann welche Stufe wirklich nötig ist — und wann sie nur Overhead produziert. Drei Qualitätssprünge, drei Kostensprünge.

**[[instrumentation|Instrumentation]].** Agenten zunächst ohne Instrumentation bauen, ein gezielt eingebautes Fehlverhalten debuggen — und scheitern oder lange brauchen. Anschließend mit LangSmith oder manuellem Trace-Logger instrumentieren und denselben Fehler in fünf Minuten finden. Erzeugt das Gefühl dafür, warum Instrumentation kein *nice to have* ist.

**[[observability|Observability]] (Endlosschleife).** Bewusst falsch geprompteten Agenten geben, der nach drei Tool-Calls in einer Endlosschleife landet — ohne und mit Trace nebeneinander. Mit Trace finden die Studierenden den Fehler in fünf Minuten; ohne Trace in einer Stunde nicht. Eine Übung ersetzt drei Folien Theorie.

**[[tracing|Tracing (lesen)]].** Aufgezeichneten Trace eines kaputten Agenten geben (ohne Code, nur den Trace im LangSmith- oder LangFuse-Viewer). Aufgabe: „Was lief schief, und wo im Trace siehst du es?" Wer Traces lesen kann, kann Agenten debuggen — eine Kompetenz, die nur durch Übung an echten Traces wächst.

**[[guardrails|Guardrails]].** Agenten mit drei deaktivierten Guardrails (Input-Filter, Output-Filter, Action-Confirm) geben. Zehn Eingaben testen — fünf normal, fünf adversarial. Alle Probleme treten auf. Dann Guardrails einzeln aktivieren und beobachten, wie sich Erfolgs- und Fehlerquote verschieben. Studierende sehen: jede Schicht fängt eine eigene Klasse von Problemen ab, keine alleine reicht.

**[[sandboxing|Sandboxing]].** Tool geben, das beliebigen Python-Code ausführt — *ohne* Sandbox. Aufgabe: einen Prompt schreiben, der den Agenten zu `os.listdir('/')` oder einer HTTP-Anfrage an eine externe URL bringt. Erfolg in zehn Minuten. Dann dasselbe Tool in einer Docker-Sandbox neu starten und denselben Prompt versuchen — die Eskapaden bleiben in der Sandbox.

### Kap. 4 — Multi-Agent Collaboration

**[[multi-agent collaboration|Multi-Agent vs. Single-Agent + Critic]].** Zuerst einen Single-Agent mit Critic-Loop bauen lassen (Reflection als Pattern), dann den Critic als eigenen Agenten herausziehen, schließlich messbar vergleichen: Qualität, Latenz, Kosten. In neun von zehn Fällen werden die Studierenden feststellen, dass die Multi-Agent-Variante schöner aussieht, aber schlechter und teurer performt — eine Lektion, die in der Praxis Tausende von Token-Dollars erspart.

### Kap. 5 — Selbstverbessernde Agenten

**[[self-reflection|Self-Reflection (drei Setups)]].** Aufgabe wählen, die offensichtlich von Reflection profitiert (z. B. Bug in Python-Snippet finden und fixen), in drei Setups bearbeiten: (1) Single-Pass ohne Reflection, (2) Self-Reflection mit demselben Modell, (3) External Critic mit zweitem, ggf. anderem Modell. Vergleich Erfolgsrate, Kosten, Latenz. Erkenntnis: Reflection ist kein Allheilmittel — Qualität gegen Tokens, ob der Kauf sich lohnt, hängt am Aufgabentyp.

**[[Reflexion]] (HumanEval).** HumanEval-Beispiel reproduzieren: ein Modell mit drei Versuchen pro Aufgabe und einem einfachen pass/fail-Evaluator. Erfolgsrate ohne Reflexion (Multi-Try) und mit Reflexion (mit Memory zwischen Versuchen) messen. Der Unterschied — typisch fünf bis zehn Prozentpunkte — macht das Konzept unmittelbar greifbar.

**[[Drift]] in Reflection.** Reflection-Schleife mit zehn Iterationen, Antwort an jeder Iteration speichern. Frage: „Antwortet Iteration 10 noch auf die ursprüngliche Frage?" In etwa der Hälfte der Fälle nicht mehr. Die Erfahrung, dass *„mehr ist mehr"* für Reflection nicht stimmt, sitzt nach dieser Übung.

**[[Reward-Hacking]].** Reflection-Schleife mit einer absichtlich schwachen Critic-Rubrik („Antwort enthält Wort X"). Beobachten, wie der Generator nach drei Iterationen lernt, X einzubauen, ohne die Aufgabe wirklich besser zu lösen. Genau dieses Aha-Erlebnis trägt 80 % des Verständnisses.

### Kap. 6 — Sicherheit und Evaluation

**[[prompt injection|Prompt Injection — Knack-Challenge]].** Aufgabe an die Studierenden: „Knack meinen Agenten — bring ihn dazu, sein System-Prompt auszugeben." Innerhalb von 15 Minuten haben mindestens drei Studierende Erfolg. Dann diskutieren, warum es funktioniert hat — und welche Gegenmaßnahmen geholfen hätten.

**[[indirect injection|Indirect Injection + Hardening]].** Research-Agent geben und eine speziell präparierte Test-Webseite mit subtilem Injection-Versuch. Messen: kommt der Agent durchs Filter, ist der Angriff durch? Anschließend Gegenmaßnahmen ergänzen (Allow-Listing, Output-Filter, Sandboxing der Tool-Calls) und neu testen. Die Erfahrung, dass der eigene Agent über eine neutral aussehende Webseite zu unerwünschten Aktionen überredet werden kann, ist eindrücklicher als jede Folie.

**[[tool misuse|Tool Misuse]].** Bewusst schlecht designtes Tool geben (z. B. `execute_python(code)`), Aufgabe: es absichtlich missbrauchen. Anschließend dieselbe Funktionalität in einem sicherer designten Tool nachbauen (z. B. `compute_metric(metric_name, params)` mit fester Funktionsbibliothek). Erkenntnis: Tool-Design ist genauso ergebnisrelevant für Sicherheit wie Prompt Engineering.

**[[design countermeasures|Design Countermeasures]].** Agenten in zwei Versionen bauen: Version A ohne explizite Gegenmaßnahmen (alles erlaubt, kein Logging, kein HITL); Version B mit allen vier Maßnahmen (Allow-Listing, Sandbox, HITL für externe Aktionen, Logging). Beide gegen denselben Satz von Angriffsversuchen testen. Version A fällt in 60–80 % der Fälle, Version B in 0–10 %. Die Zahlen erzeugen Überzeugung, die jede Folie nicht erreicht.

**[[evaluation|Evaluation Hygiene]].** Agenten gegen zehn fix definierte Aufgaben antreten lassen — drei Mal hintereinander. Messen: Erfolgsquote, Token-Kosten, Wandzeit. Anschließend eine kleine LLM-as-Judge-Auswertung gegen eine Rubrik durchführen und mit eigener manueller Einschätzung vergleichen. Studierende sehen sofort, wie sehr Stochastik die Ergebnisse streut und wie wichtig wiederholte Läufe sind. Eine Eval-Pipeline, die in vier Stunden Lab steht, hebt das Verständnis von *evaluation hygiene* deutlich.
