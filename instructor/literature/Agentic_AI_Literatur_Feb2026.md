# Agentic AI – Literaturrecherche

---

## Schwerpunkt: Multi-Agent-Interaktion

Drei Quellen decken besonders Multi-Agent-Systeme ab:

- **MetaGPT (#5)** – Architektur & Rollendesign
- **Multi-Agent Risks (#8)** – Risikoklassifikation & Governance
- **A2A-Protokoll (#13, Gesamttabelle)** – Inter-Agent-Kommunikationsstandard

---

## Kernliteratur (8 Quellen)

### 1. ReAct: Synergizing Reasoning and Acting in Language Models
Yao et al. (Princeton / Google Brain, 2022) · ICLR 2023 · [arXiv:2210.03629](https://arxiv.org/abs/2210.03629)

Interleaved Reasoning-Action-Observation-Loop für LLM-Agenten. Das Modell generiert alternierend Reasoning-Traces und Aktionen (API-Calls, Suchen); die Ergebnisse fließen als Observations zurück. Übertrifft reine CoT- und reine Action-Baselines auf Wissens- und Entscheidungsaufgaben. Standardarchitektur für nahezu alle nachfolgenden Agent-Frameworks.

### 2. CoALA: Cognitive Architectures for Language Agents
Sumers, Yao, Narasimhan & Griffiths (Princeton, 2023) · TMLR · [arXiv:2309.02427](https://arxiv.org/abs/2309.02427)

Formales Framework: Dekomposition von LLM-Agenten in Working Memory (aktiver Kontext), Long-Term Memory (episodisch, semantisch, prozedural) und einen Decision Cycle aus Planning (Propose → Evaluate → Select) und Execution. Mappt moderne LLM-Agenten auf klassische kognitive Architekturen (ACT-R, Soar). Liefert eine einheitliche Terminologie und identifiziert unterexplorierte Entwicklungsrichtungen.

### 3. Tree of Thoughts: Deliberate Problem Solving with LLMs
Yao et al. (Princeton, 2023) · NeurIPS 2023 · [arXiv:2305.10601](https://arxiv.org/abs/2305.10601)

Erweitert Chain-of-Thought zu einer Baumstruktur. Pro Schritt werden mehrere Reasoning-Kandidaten generiert, heuristisch bewertet und via BFS/DFS exploriert. Ermöglicht Backtracking und Lookahead. Brücke zwischen klassischer Suche und generativer Sprachmodellierung.

### 4. Reflexion: Language Agents with Verbal Reinforcement Learning
Shinn et al. (2023) · NeurIPS 2023 · [arXiv:2303.11366](https://arxiv.org/abs/2303.11366)

Agent scheitert, generiert eine verbale Selbstreflexion, speichert sie im Kontext, und nutzt sie beim nächsten Versuch. RL ohne Gewichts-Updates – rein über natürlichsprachliches Feedback. Signifikante Verbesserungen über Iterationen auf Coding-, QA- und Web-Navigation-Tasks.

### 5. MetaGPT: Meta Programming for Multi-Agent Collaboration
Hong et al. (DeepWisdom / Tsinghua, 2023) · ICLR 2024 · [arXiv:2308.00352](https://arxiv.org/abs/2308.00352)

Multi-Agent-System mit rollenbasierter Arbeitsteilung (PM → Architekt → Entwickler → Tester). Agenten kommunizieren über strukturierte Artefakte (Requirements Spec → System Design → Code → Test Suite), nicht über freien Dialog. SOPs aus menschlichen Organisationen reduzieren Halluzinationen in Multi-Agent-Pipelines.

### 6. Model Context Protocol (MCP)
Anthropic (Nov 2024, open-source) → Agentic AI Foundation / Linux Foundation (Dez 2025) · [modelcontextprotocol.io](https://modelcontextprotocol.io) · [Spec](https://spec.modelcontextprotocol.io)

Offener Standard für die Anbindung von LLM-Agenten an externe Tools, Datenquellen und APIs. Client-Server-Architektur: MCP-Client (Agent) verbindet sich mit MCP-Servern (Tools), die Capabilities (tools, resources, prompts) exponieren. Transport via JSON-RPC 2.0 über stdio oder HTTP/SSE. 97M+ monatliche SDK-Downloads, 10.000+ aktive Server. Adoptiert von OpenAI, Google, Microsoft, Cursor, VS Code. Komplementär zu A2A (Google): MCP = Agent↔Tool (vertikal), A2A = Agent↔Agent (horizontal). Sicherheitsrisiken: Tool Poisoning, Prompt Injection via Tool-Descriptions, OAuth-Token-Leakage, Cross-Server Shadowing.

### 7. Agentic AI: A Comprehensive Survey
Abou Ali & Dornaika (U. Basque Country, 2025) · Springer Artificial Intelligence Review · [DOI](https://link.springer.com/article/10.1007/s10462-025-11422-4)

PRISMA-Review, 90 Studien (2018–2025). Duales Paradigmen-Framework: Symbolisch/Klassisch (algorithmisches Planen, deterministischer State) vs. Neural/Generativ (stochastische Generierung, prompt-basierte Orchestrierung). Paradigmenwahl ist domänenabhängig: symbolisch in sicherheitskritischen Anwendungen, neural in datenreichen Umgebungen. Identifiziert Governance-Lücken und Bedarf an hybriden neuro-symbolischen Architekturen.

### 8. Multi-Agent Risks from Advanced AI
Cooperative AI Foundation (2025) · [arXiv:2502.14143](https://arxiv.org/abs/2502.14143)

50+ Autoren (DeepMind, Anthropic, CMU, Harvard). Systematische Klassifikation von Multi-Agent-Risiken: Fehlkoordination, Konflikt, Kollusion. 7 übergreifende Risikofaktoren. Schließt mit Policy-Empfehlungen für Multi-Agent-Governance.

---

## Vollständige Quellensammlung (31 Quellen)

| # | Kategorie | Quelle | Keywords | Inhalt | Relevanz |
|---|-----------|--------|----------|--------|----------|
| 1 | Grundlagen | ReAct – Yao et al. (Princeton, 2022) [arXiv:2210.03629](https://arxiv.org/abs/2210.03629) | reasoning loop, tool use | Thought→Action→Observation-Loop | ⭐⭐⭐ |
| 2 | Grundlagen | CoALA – Sumers et al. (Princeton, 2023) [arXiv:2309.02427](https://arxiv.org/abs/2309.02427) | kognitive Architektur, memory | LLM-Agenten auf Kognitionsmodelle gemappt (TMLR) | ⭐⭐⭐ |
| 3 | Grundlagen | Tree of Thoughts – Yao et al. (Princeton, 2023) [arXiv:2305.10601](https://arxiv.org/abs/2305.10601) | Planung, BFS/DFS, Suche | Baumstrukturiertes Reasoning mit Backtracking (NeurIPS) | ⭐⭐⭐ |
| 4 | Grundlagen | Reflexion – Shinn et al. (2023) [arXiv:2303.11366](https://arxiv.org/abs/2303.11366) | Selbstkorrektur, verbal RL | Lernen aus Fehlern durch sprachliches Feedback (NeurIPS) | ⭐⭐⭐ |
| 5 | Grundlagen | Voyager – Wang et al. (NVIDIA/Caltech, 2023) [arXiv:2305.16291](https://arxiv.org/abs/2305.16291) | lifelong learning, skill library | Open-ended Agent mit wachsender Skill-Bibliothek | ⭐⭐ |
| 6 | Grundlagen | MetaGPT – Hong et al. (Tsinghua, 2023) [arXiv:2308.00352](https://arxiv.org/abs/2308.00352) | multi-agent, Rollen, SOPs | Rollenbasierte Multi-Agent-Kollaboration (ICLR 2024) | ⭐⭐⭐ |
| 7 | Grundlagen | SWE-Agent – Yang et al. (Princeton, 2024) [arXiv:2405.15793](https://arxiv.org/abs/2405.15793) | coding agent, GitHub | Autonome GitHub-Issue-Resolution | ⭐⭐⭐ |
| 8 | Survey | Abou Ali & Dornaika (2025) [Springer](https://link.springer.com/article/10.1007/s10462-025-11422-4) | dual-paradigm, PRISMA | 90 Studien; symbolisch vs. neural | ⭐⭐⭐ |
| 9 | Survey | Northwest Missouri State (MDPI, 2025) [DOI](https://www.mdpi.com/1999-5903/17/9/404) | Definitionen, Metriken | 143 Studien; Architekturen + Evaluation | ⭐⭐ |
| 10 | Survey | Sapkota et al. (2025) [arXiv:2505.10468](https://arxiv.org/abs/2505.10468) | Taxonomie, single vs. multi | AI Agents vs. Agentic AI Unterscheidung | ⭐⭐ |
| 11 | Survey | Stanford/Harvard/Berkeley (Dez 2025) | Adaptation, Produktionsfehler | Warum Agenten in der Praxis scheitern | ⭐⭐⭐ |
| 12 | Standards | MCP – Anthropic → Linux Foundation [modelcontextprotocol.io](https://modelcontextprotocol.io) | Tool-Integration, Protokoll | Agent↔Tool-Standard; 97M+ Downloads | ⭐⭐⭐ |
| 13 | Standards | A2A – Google → Linux Foundation [Blog](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/) | Inter-Agent-Komm., JSON-RPC | Agent↔Agent-Protokoll; 50+ Partner | ⭐⭐⭐ |
| 14 | Standards | AGENTS.md – OpenAI (2025) | Coding Agents, Repo-Guidance | Pro-Repo-Instruktionen für Agenten; 60K+ Repos | ⭐⭐ |
| 15 | Memory | A-MEM – Xu et al. (NeurIPS 2025) [arXiv:2502.12110](https://arxiv.org/abs/2502.12110) | Zettelkasten, dynamisch | Selbstorganisierende Agenten-Memory | ⭐⭐⭐ |
| 16 | Memory | Agent-Memory-Paper-List [GitHub](https://github.com/Shichun-Liu/Agent-Memory-Paper-List) | 100+ Papers, kuratiert | Umfassende Memory-Literaturliste | ⭐⭐⭐ |
| 17 | Memory | MAS Memory Survey (TechRxiv, 2025) | Multi-Agent, transactive | Memory in Multi-Agenten-Systemen | ⭐⭐ |
| 18 | Benchmarks | ABC Checklist – Zhu et al. (Stanford, 2025) [arXiv:2507.02825](https://arxiv.org/abs/2507.02825) | Benchmark-Rigor | ±100% Fehleinschätzung in bestehenden Benchmarks | ⭐⭐⭐ |
| 19 | Benchmarks | CLEAR – Mehta (2025) [arXiv:2511.14136](https://arxiv.org/abs/2511.14136) | Enterprise-Eval, Kosten | Cost/Latency/Efficacy/Assurance/Reliability | ⭐⭐ |
| 20 | Benchmarks | SWE-bench Pro – Scale AI (2025) [arXiv:2509.16941](https://arxiv.org/abs/2509.16941) | Coding, Long-Horizon | Top-Modelle ~23% vs. 70%+ auf einfacherem SWE-bench | ⭐⭐⭐ |
| 21 | Benchmarks | TRAIL – Patronus AI (2025) [arXiv:2505.08638](https://arxiv.org/abs/2505.08638) | Debugging, Fehlertaxonomie | 20+ Agentic Error Types; Gemini bei 11% | ⭐⭐ |
| 22 | Sicherheit | Multi-Agent Risks – Cooperative AI (2025) [arXiv:2502.14143](https://arxiv.org/abs/2502.14143) | Kollusion, Fehlkoordination | Risiko-Klassifikation für Multi-Agent-Systeme | ⭐⭐⭐ |
| 23 | Sicherheit | 2025 AI Agent Index (Cambridge/MIT/Stanford) [aiagentindex.mit.edu](https://aiagentindex.mit.edu) | Transparenz, Dokumentation | 30 Agents, 1350 Felder; Sicherheitslücken | ⭐⭐⭐ |
| 24 | Sicherheit | MIT AI Risk Repository [airisk.mit.edu](https://airisk.mit.edu) | Risikodatenbank | 1600+ Risiken aus 65+ Frameworks | ⭐⭐ |
| 25 | Governance | MIT Sloan/BCG Report (Nov 2025) [Link](https://sloanreview.mit.edu/projects/the-emerging-agentic-enterprise-how-leaders-must-navigate-a-new-age-of-ai/) | Enterprise, Org-Design | 2102 Befragte; Adoption überholt Governance | ⭐⭐⭐ |
| 26 | Wissenschaft | Agentic AI for Science (ICLR 2025) [arXiv:2503.08979](https://arxiv.org/abs/2503.08979) | Hypothesen, Lab-Automation | Agent Laboratory, BioPlanner, CALMS | ⭐⭐⭐ |
| 27 | Wissenschaft | Self-Driving Labs – Xin/Kitchin/Kulik (*Nature MI*, 2025) [Link](https://news.vt.edu/articles/2025/09/eng-coe-agentic-science-q-and-a-commentary.html) | Autonome Labore, Materialien | Co-pilot → Lab-pilot Transition | ⭐⭐⭐ |
| 28 | Wissenschaft | FORUM-AI – DOE/Berkeley (2025) [Link](https://www.labmanager.com/doe-launches-agentic-ai-platform-to-accelerate-energy-materials-discovery-34920) | Materialforschung, $10M | Hypothese→Simulation→Labor Pipeline | ⭐⭐ |
| 29 | Software Eng. | AIDev Dataset (2025) [arXiv:2507.15003](https://arxiv.org/pdf/2507.15003) | PRs, Akzeptanzraten | 456K agentic PRs; Codex 64%, Devin 49% | ⭐⭐⭐ |
| 30 | Software Eng. | Anthropic Coding Trends 2026 [PDF](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf) | Industrie, Workflows | 90%+ Teams nutzen AI in SE | ⭐⭐ |
| 31 | Leseliste | LLM-Agent-Paper-List [GitHub](https://github.com/WooooDyy/LLM-Agent-Paper-List) | 200+ Papers | Umfassendste kuratierte Sammlung | ⭐⭐⭐ |

**Relevanz:** ⭐⭐⭐ = Pflichtlektüre | ⭐⭐ = Vertiefung

---

*Stand: Februar 2026*
