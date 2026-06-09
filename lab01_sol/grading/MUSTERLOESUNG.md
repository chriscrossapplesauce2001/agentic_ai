# Musterlösung Lab 01 — Scoring-Rubrik

**Intern, nicht an Studierende verteilen.** Referenz für das automatische Scoring. Pro Frage: `✓` Kernpunkt (muss da sein), `±` auch akzeptabel / modellabhängig, `✗` typischer Fehler. Der Grader bewertet je Frage **correct / partial / incorrect** anhand des Kernpunkts, nicht des Wortlauts.

---

## Exercise 0 — How an LLM API Call Works (Freitext, LLM-gegradet)

### Part 1: A Single LLM Call

**Q1 — `<think>\n` entfernen: was verschwindet?**
- ✓ Der Reasoning-/Thinking-Block (`<think>...</think>`) verschwindet, Output startet direkt mit der Antwort.
- ✓ Das `<think>`-Prefill ist der Auslöser für den Thinking-Modus.

**Q2 — Prompt "Answer once, then stop ...": läuft es weiter? Was stoppt Generierung wirklich?**
- ✓ Ja, läuft weiter. Eine Text-Anweisung stoppt nichts.
- ✓ Gestoppt wird durch ein Stop-Token (`<|im_end|>` / EOS) aus dem Chat-Template, nicht durch den Prompt-Inhalt. `raw=True` ohne Template = kein Stop-Token.
- ✗ "Das Modell hat die Anweisung ignoriert / versteht sie nicht" ohne den Stop-Token-Punkt.

**Q3 — `think=False`: welches Feld leer, welches wächst?**
- ✓ `thinking` ist leer (None/""), `content` enthält die ganze Antwort.
- ✓ Begründung: beide werden aus einem Textstrom geparst, ohne `<think>`-Block landet alles in `content`.

### Part 2: Statelessness

**Q1 — `assistant`-Eintrag entfernen: weiß das Modell den Namen noch? Warum?**
- ✓ Ja. Der Fakt steht in der ersten user-Nachricht, die noch da ist. Der assistant-Echo ist nicht nötig.
- ✓ Kern: das Modell weiß nur, was in `messages` steht; History muss den Fakt nur *enthalten*.

**Q2 — `r1.message.content` durch "Nice to meet you, Anna!" ersetzen: welcher Name?**
- ✓ Anna. Das Modell hat kein eigenes Gedächtnis, es vertraut der übergebenen History, auch wenn sie erfunden ist.
- ✓ Bonus: das ist die Keimzelle von Prompt-Injection.

**Q3 — Fakt in `system`-Nachricht verschieben: funktioniert es? Welche Rolle für Instruktionen/stabile Fakten, warum anders als Mid-Conversation-Fakten?**
- ✓ Ja, Modell antwortet "Max"; system-Inhalt ist Teil des Kontexts.
- ✓ Instruktionen + stabile Fakten konventionell in `system` (zuerst, höher gewichtet/standing); was der User im Dialog sagt, gehört in `user`-Turns.
- ✓ Kern: alle Rollen sind nur Text, die Rolle ist eine (im Training verstärkte) Konvention für Dauerhaftigkeit/Autorität.

### Part 3: Tool Calling

**Q1 — `description` leeren: ruft das Modell das Tool noch?**
- ± Modellabhängig, bei dieser offensichtlichen Aufgabe meist ja (Name + Schema reichen).
- ✓ Kern: die Beschreibung ist das Haupt-Signal *wann* ein Tool genutzt wird; leer = unzuverlässiger, v.a. bei mehrdeutigen Aufgaben.
- Bewertung: beide beobachteten Ausgänge ok, wenn "description = Routing-Signal" erkannt wird.

**Q2 — Prompt "What is 2 + 2?": Tool oder direkte Antwort? `content` vs `tool_calls`?**
- ± Modellabhängig, bei Trivial-Mathe oft direkte Antwort (`content` gefüllt, `tool_calls` leer/None).
- ✓ Kern: das Modell entscheidet selbst, ob ein Tool sich lohnt.

**Q3 — Tool in Definition zu `"math_thing"` umbenennen, `tool_map` unverändert: Fehler + Zeile?**
- ✓ `KeyError: 'math_thing'` an `func = tool_map[tc.function.name]`.
- ✓ Kern: Tool-Name in der Definition muss mit dem Key in `tool_map` übereinstimmen, verbunden nur über den String-Namen.

### Part 4: Tool-Use Loop

**Q1 — `messages.append(response.message.model_dump())` entfernen (tool-result bleibt): finale Antwort?**
- ✓ History wird inkonsistent: `tool`-Nachricht ohne vorangehende assistant-`tool_calls`. Ergebnis falsch/verwirrt oder Tool wird neu aufgerufen.
- ✓ Kern: beide Nachrichten müssen rein, in Reihenfolge: erst assistant mit `tool_calls`, dann `tool`-Ergebnis.

**Q2 — "... then divide the result by 2." mit `while`-Loop (Cap 5): ein kombinierter oder zwei sequentielle Calls?**
- ± Beides gültig: ein Call `(17*23)/2` ODER zwei Calls (`17*23` → 391 → `391/2`).
- ✓ Kern: der `while`-Loop ist nötig, weil das Modell mehrere Tool-Calls über Iterationen verketten kann; Cap verhindert Endlosschleife.

**Q3 — Prompt "Tell me a short joke." (Tools bleiben): Calculator angefasst?**
- ✓ Nein. `content` = Witz, `tool_calls` leer/None.
- ✓ Kern: Tools bereitstellen erzwingt keine Nutzung; das Modell wählt pro Anfrage, ob ein Tool relevant ist.

---

## Exercise 1 — ReAct-Loop (Code, deterministisch gegradet, kein LLM nötig)

**TODO 1** `response = ollama.chat(model=MODEL, messages=messages, tools=TOOLS, options={"num_ctx": NUM_CTX, "temperature": TEMPERATURE})`

**TODO 2** `if msg.get("tool_calls"):` (auch: `is not None`, oder Truthiness-Check)

**TODO 3**
```python
func = tool_map[name]
result = func(**args)
messages.append({"role": "tool", "content": result})
```

**TODO 4** `final_answer = msg["content"]` (auch: `msg.get("content", "")`)

**Erwartetes Testverhalten** (Plausibilitätscheck):
- Test 1 `(0.2 * 0.4**3) / 12`: ein `calculator`-Call, ≈ `0.0010667` m⁴.
- Test 2 `sample.txt`: ein `read_file`-Call, Antwort nennt die Formeln.
- Test 3 `E-Modul S235`: ein `web_search`-Call, Antwort nennt ~210 GPa.

---

## Exercise 2 — LangChain

**Offen:** `exercise2.ipynb` existiert noch nicht. Rubrik folgt nach dem Bau. Kern: gleicher Agent via `create_react_agent()` + `@tool`-Funktionen, funktional identisch zu Exercise 1, deutlich weniger Code.
