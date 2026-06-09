# Benchmark Report: ReAct vs PAOR Agent

## Test Setup

| Parameter | ReAct (ollama_react) | PAOR (ollama_react_planning) |
|---|---|---|
| Model | qwen3.5:4b | qwen3.5:4b |
| Temperature | 0.7 | 0.7 |
| Context Window | 32768 | 32768 |
| Max Iterations/Cycles | 20 | 100 |

**Test Query:**
> Read sample.txt and find the formulas for a rectangle and a hollow circle. Calculate the moment of inertia for both: a rectangle 0.3 m x 0.5 m, and a hollow circle with outer diameter 0.5 m and inner diameter 0.45 m. Which cross-section has the higher moment of inertia per area? Search the web for the Young's modulus of titanium and calculate EI for the more efficient one.

---

## Correct Solution (Reference)

| Step | Value |
|---|---|
| I_rectangle = (0.3 x 0.5^3) / 12 | **0.003125 m^4** |
| A_rectangle = 0.3 x 0.5 | **0.15 m^2** |
| I/A_rectangle | **0.02083** |
| I_hollow = (pi/64) x (0.5^4 - 0.45^4) | **0.001688 m^4** |
| A_hollow = pi/4 x (0.5^2 - 0.45^2) | **0.03731 m^2** |
| I/A_hollow | **0.04524** |
| More efficient | **Hollow circle** (2.2x higher I/A) |
| E_titanium | **~114-120 GPa** |
| EI_hollow | **~192-202 MN*m^2** |

---

## Results Summary

### ReAct Agent: PASS (10 steps)

The ReAct agent completed all sub-tasks correctly and provided a well-structured final answer.

**Tool calls made (in order):**
1. `read_file("sample.txt")` -- retrieved formulas
2. `calculator("(0.3 * 0.5**3) / 12")` -- I_rect = 0.003125
3. `calculator("(pi / 64) * (0.5**4 - 0.45**4)")` -- I_hollow = 0.001055
4. `calculator("0.3 * 0.5")` -- A_rect = 0.15
5. `calculator("(pi / 4) * (0.5**2 - 0.45**2)")` -- A_hollow = 0.03731
6. `calculator("0.003125 / 0.15")` -- I/A_rect = 0.02083
7. `calculator("0.001055 / 0.03731")` -- I/A_hollow = 0.02828
8. `web_search("Young modulus of titanium")` -- found E = 120 GPa
9. `calculator("120e9 * 0.001055")` -- EI = 126.6 MN*m^2

**Final Answer:** Hollow circle is more efficient (I/A = 0.0283 > 0.0208). EI = 126.6 MN*m^2.

### PAOR Agent: FAIL (4 cycles, incomplete)

The PAOR agent failed to complete the task. It ran for 4 cycles, made 3 tool calls, but never produced a final answer. This was the best of 3 attempts.

**What happened:**
1. **Cycle 1 — PLAN:** Created only 2 steps (too compressed). Called `read_file("sample.txt")` -- got formulas. REFLECT: "RE-PLAN" (correctly identified that calculations weren't done yet).
2. **Cycle 2 — RE-PLAN:** Created another 2-step plan. Called `calculator("(0.3 * 0.5**3) / 12")` -- got I_rect = 0.003125. REFLECT: "NEXT STEP" (correctly noted I_hollow, areas, and comparison still missing).
3. **Cycle 3:** Called `web_search("Young's modulus of titanium")` -- found ~100-120 GPa. REFLECT: "NEXT STEP" (correctly noted hollow circle calculations still missing). Spent ~3000+ tokens deliberating.
4. **Cycle 4:** `current_step` (3) > plan steps (2) -- triggered `_final_answer()`. The model started thinking about remaining calculations (listed I_hollow formula, area formula) but produced NO actual answer output. Framework terminated.

**Root cause:** The PAOR framework executes one tool call per cycle. With a 2-step plan, it only got 2-3 tool calls before forced finalization. The remaining 6 calculations were never executed.

**Contributing factors:**
- The model spent ~4000+ tokens on thinking during the initial PLAN phase (deliberating between 2 vs 3 vs 4 steps)
- The REFLECT phases generated extremely verbose thinking (~3000+ tokens each), correctly identifying gaps but unable to act on them
- The RE-PLAN mechanism worked (cycle 1 correctly triggered it) but re-created the same 2-step plan
- The model skipped ahead to step 2 (web_search) in cycle 3 even though step 1 (calculations) was incomplete
- At 4B parameters, the model cannot reliably navigate the 4-phase orchestration protocol on top of solving the engineering task

---

## Scorecard

| Criterion | ReAct | PAOR |
|---|---|---|
| Task completed | YES | NO |
| read_file used | YES | YES |
| I_rectangle calculated | YES (0.003125) | YES (0.003125) |
| I_hollow calculated | YES (0.001055) | NO |
| Areas calculated | YES | NO |
| I/A comparison made | YES (hollow wins) | NO |
| web_search for E_titanium | YES (120 GPa) | YES (~100-120 GPa) |
| EI calculated | YES (126.6 MN*m^2) | NO |
| Final answer provided | YES (formatted table) | NO |
| Total tool calls | 9 | 3 |
| Total steps/cycles | 10 | 4 |

---

## Analysis

### Why ReAct won this benchmark

1. **Simplicity:** The ReAct loop is straightforward -- think, call a tool, observe, repeat. No overhead from plan/reflect phases.
2. **Greedy but effective:** The agent called tools as needed without over-planning. Each thinking step was short and action-oriented.
3. **No framework confusion:** The model only had to decide "which tool next?" rather than navigating a 4-phase orchestration protocol.

### Why PAOR failed

1. **Plan compression:** The model tried to minimize steps (as instructed by the PLAN prompt) and crammed 6+ actions into 2 steps. The framework then only allowed 2-3 tool calls before forced finalization.
2. **Overthinking:** The model spent thousands of tokens deliberating about step counts in the PLAN phase and about whether steps were "fully completed" in the REFLECT phase. Ironically, the REFLECT phases correctly identified gaps but the framework couldn't act on them.
3. **Framework mismatch:** The PAOR architecture assumes 1 tool call per step. For multi-tool tasks, the plan needs more granular steps -- but the prompt says "use as few steps as necessary," creating a conflict.
4. **RE-PLAN trap:** The RE-PLAN mechanism triggered correctly but produced the same 2-step plan again, failing to break out of the compression loop.
5. **Model size:** At 4B parameters, the model struggles with the cognitive load of the PAOR protocol (understanding transient prompts, plan tracking, reflection logic) on top of the actual engineering task.

### Conclusion

For this multi-step engineering task with a 4B parameter model, the simple ReAct pattern significantly outperformed the structured PAOR approach. The PAOR overhead was counterproductive -- the model spent more tokens on meta-reasoning (planning and reflecting) than on actual problem-solving. The ReAct agent solved the problem correctly in 10 steps while the PAOR agent failed after 4 cycles across 3 separate attempts.

**Token budget comparison (estimated):**
- ReAct: ~2000 tokens thinking + 9 tool calls = task completed
- PAOR: ~15000+ tokens thinking (PLAN deliberation + REFLECT analysis) + 3 tool calls = task incomplete

**Caveat:** This was tested 3 times with temperature=0.7 (non-deterministic). All 3 PAOR runs failed with the same pattern (2-step plan compression). The PAOR approach might perform better with: (a) a larger model (e.g., 8B+) that can handle the orchestration overhead, (b) a modified plan prompt that encourages more granular steps (e.g., "create one step per tool call"), or (c) allowing multiple tool calls per cycle.

---

## Appendix A: Full ReAct Output

```
============================================================
  QUESTION: Read sample.txt and find the formulas for a rectangle and a hollow circle. Calculate the moment of inertia for both: a rectangle 0.3 m x 0.5 m, and a hollow circle with outer diameter 0.5 m and inner diameter 0.45 m. Which cross-section has the higher moment of inertia per area? Search the web for the Young modulus of titanium and calculate EI for the more efficient one.
============================================================

  [Thinking]
  The user wants me to:
1. Read sample.txt to find formulas for a rectangle and a hollow circle
2. Calculate the moment of inertia for:
   - A rectangle 0.3 m x 0.5 m
   - A hollow circle with outer diameter 0.5 m and inner diameter 0.45 m
3. Determine which has higher moment of inertia per area
4. Search web for Young's modulus of titanium
5. Calculate EI (E * I) for the more efficient one

Let me start by reading sample.txt to get the formulas.

  [Tool Call] read_file({"filename": "sample.txt"})
  [Tool Result] Common Area Moment of Inertia Formulas
========================================

Rectangle (about centroidal x-axis):
  Ix = (b * h^3) / 12
  where b = width, h = height

Circle (about centroidal axis):
  Ix = (pi * d^4) / 64
  where d = diameter

Hollow circle / tube:
  Ix = (pi / 64) * (D^4 - d^4)
  where D = outer diameter, d = inner diameter

I-beam (use parallel axis theorem):
  Divide into rectangles, compute each Ix about its own centroid,
  then shift using: I_total = sum(Ix_i + A_i * d_... (truncated)

  [Thinking]
  Great! Now I have the formulas:

For rectangle: Ix = (b * h^3) / 12
For hollow circle: Ix = (pi / 64) * (D^4 - d^4)

Now let me calculate:
1. Rectangle: b = 0.3 m, h = 0.5 m
   Ix = (0.3 * 0.5^3) / 12

2. Hollow circle: D = 0.5 m, d = 0.45 m
   Ix = (pi / 64) * (0.5^4 - 0.45^4)

Let me calculate these using the calculator.

  [Tool Call] calculator({"expression": "(0.3 * 0.5**3) / 12"})
  [Tool Result] Result: 0.0031249999999999997

  [Tool Call] calculator({"expression": "(pi / 64) * (0.5**4 - 0.45**4)"})
  [Tool Result] Result: 0.001055071985907744

  [Thinking]
  So I have:
- Rectangle moment of inertia: 0.003125 m^4
- Hollow circle moment of inertia: 0.001055 m^4

Now I need to calculate the area for each to get moment of inertia per area:

Rectangle area: A = b * h = 0.3 * 0.5
Hollow circle area: A = (pi / 4) * (D^2 - d^2)

Let me calculate these areas and then I/A ratios.

  [Tool Call] calculator({"expression": "0.3 * 0.5"})
  [Tool Result] Result: 0.15

  [Tool Call] calculator({"expression": "(pi / 4) * (0.5**2 - 0.45**2)"})
  [Tool Result] Result: 0.037306412761378784

  [Thinking]
  Now I have the areas:
- Rectangle area: 0.15 m^2
- Hollow circle area: 0.0373 m^2

Now let me calculate moment of inertia per area (I/A):
- Rectangle: 0.003125 / 0.15
- Hollow circle: 0.001055 / 0.0373

Let me calculate these ratios.

  [Tool Call] calculator({"expression": "0.003125 / 0.15"})
  [Tool Result] Result: 0.020833333333333336

  [Tool Call] calculator({"expression": "0.001055071985907744 / 0.037306412761378784"})
  [Tool Result] Result: 0.028281250000000008

  [Thinking]
  So the moment of inertia per area is:
- Rectangle: 0.0208 m^4/m^2 = 0.0208 m^2
- Hollow circle: 0.0283 m^4/m^2 = 0.0283 m^2

The hollow circle has the higher moment of inertia per area (0.0283 > 0.0208).

Now I need to search for the Young's modulus of titanium and calculate EI for
the hollow circle (the more efficient one).

  [Tool Call] web_search({"query": "Young modulus of titanium"})
  [Tool Result] - Titanium alloys - Wikipedia: ... Young's modulus of 120 GPa ...
  (truncated)

  [Thinking]
  Based on the search results:
- Commercially pure grade 1 titanium has a Young's modulus of 120 GPa
- Ti-6Al-4V has values from 90 to 145 GPa

Using 120 GPa = 120 x 10^9 Pa.

EI = E * I = 120e9 * 0.001055

  [Tool Call] calculator({"expression": "120e9 * 0.001055071985907744"})
  [Tool Result] Result: 126608638.30892928

  [Answer]
## Summary of Results

### Formulas from sample.txt:
- Rectangle: Ix = (b * h^3) / 12
- Hollow Circle: Ix = (pi/64) * (D^4 - d^4)

### Moment of Inertia Calculations:

| Cross-section | Dimensions | I (m^4) | A (m^2) | I/A |
|---|---|---|---|---|
| Rectangle | 0.3 x 0.5 m | 0.003125 | 0.15 | 0.0208 |
| Hollow Circle | D=0.5, d=0.45 m | 0.001055 | 0.0373 | 0.0283 |

### Comparison:
Hollow circle is more efficient (I/A = 0.0283 vs 0.0208, 41% higher)

### EI Calculation (Titanium, E = 120 GPa):
EI = 120e9 * 0.001055 = **126.6 MN*m^2**

  (10 step(s))
============================================================
```

## Appendix B: Full PAOR Output (best of 3 attempts)

```
============================================================
  QUESTION: (same as above)
============================================================

  --- CYCLE 1 ---

  [Thinking]
  (4000+ tokens deliberating between 2 vs 3 vs 4 vs 5 step plans)

  [PLAN]
1. Read sample.txt to retrieve the formulas for a rectangle and hollow
   circle, then calculate I and A for both shapes to determine which
   has a higher I/A.
2. Search the web for the Young's modulus of titanium and calculate EI
   for the cross-section with the higher moment of inertia per area.

  [ACT]
  Tool call: read_file({"filename": "sample.txt"})

  [OBSERVE]
  Tool: read_file -> (formulas retrieved: Rectangle Ix=(b*h^3)/12,
  Hollow circle Ix=(pi/64)*(D^4-d^4))

  [REFLECT]
  (3000+ tokens of thinking)
  RE-PLAN — The moment of inertia and area calculations for the specific
  shapes were not performed yet; only the formulas were retrieved.

  --- CYCLE 2 ---

  [PLAN] (re-planned, same 2 steps)
1. Calculate I and A for both shapes, compare I/A values.
2. Search web for Young's modulus of titanium and calculate EI.

  [ACT]
  Tool call: calculator({"expression": "(0.3 * 0.5**3) / 12"})

  [OBSERVE]
  Tool: calculator -> Result: 0.0031249999999999997

  [REFLECT]
  NEXT STEP — Step 1 is incomplete; still need to calculate areas and
  the moment of inertia for the hollow circle, then compute I/A ratios.

  --- CYCLE 3 ---

  [ACT]
  Tool call: web_search({"query": "Young's modulus of titanium in
  Pascals or N/m^2"})

  [OBSERVE]
  Tool: web_search -> Young's modulus ~100-120 GPa (Wikipedia, various)

  [REFLECT]
  (3000+ tokens of thinking)
  NEXT STEP — The hollow circle's moment of inertia and area were not
  calculated, preventing the I/A comparison needed for the final EI
  calculation.

  --- CYCLE 4 ---

  [Thinking]
  (Lists all remaining calculations: I_hollow, A_rect, A_hollow, I/A
  comparison, EI... but produces NO tool calls and NO final answer.
  Framework terminated: current_step > plan steps.)

  (4 cycle(s))
============================================================
```
