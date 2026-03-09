#!/usr/bin/env python3
"""Microsoft OpenTelemetry (Python) -- Sequence Diagram
Shows the runtime flow: unified distro init, multi-exporter pipeline.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from sequence_diagram import SequenceDiagram

sd = SequenceDiagram(
    title="Microsoft OpenTelemetry -- Python Sequence",
    participant_gap=220,
    row_height=55,
)

# Participants
sd.participant("app",         "Python\nApplication",        color="blue")
sd.participant("distro",      "MS OTel\nDistro",            color="teal")
sd.participant("az_instr",    "Azure Monitor\nInstrumentations", color="blue")
sd.participant("a365_instr",  "A365\nInstrumentations",     color="violet")
sd.participant("genai_instr", "GenAI\nInstrumentations",    color="orange")
sd.participant("api",         "OTel API",                    color="orange")
sd.participant("sdk",         "OTel SDK",                    color="orange")
sd.participant("exporters",   "Exporters",                   color="orange")

# Initialization
sd.group("Initialization")
sd.call("app", "distro", "configure()")
sd.call("distro", "az_instr", "Bundle (optional)")
sd.call("distro", "a365_instr", "Bundle A365 extensions")
sd.call("distro", "genai_instr", "Bundle GenAI instrumentations")
sd.call("distro", "sdk", "Configure SDK + Azure Resource Detector")
sd.call("distro", "exporters", "Configure Azure Monitor (opt) + A365 + OTLP")
sd.reply("distro", "app", "Ready")
sd.end_group()

# Runtime: HTTP request (Azure Monitor instrumentation)
sd.group("HTTP Request (Azure Monitor Instrumentation)")
sd.call("app", "az_instr", "Django/Flask request arrives")
sd.call("az_instr", "api", "Start span (http.*, OTel Semantic Conventions)")
sd.call("api", "sdk", "Record span")
sd.reply("az_instr", "app", "Instrumented response")
sd.end_group()

# Runtime: LLM call (A365 instrumentation)
sd.group("LLM Call (A365 Instrumentation)")
sd.call("app", "a365_instr", "openai.chat.completions.create()")
sd.call("a365_instr", "api", "Start span (gen_ai.*, A365 custom attributes)")
sd.note("api", "agent_id, tenant_id, correlation_id", position="right")
sd.call("api", "sdk", "Record span")
sd.reply("a365_instr", "app", "LLM response")
sd.end_group()

# Runtime: GenAI community instrumentation
sd.group("GenAI Community Instrumentation")
sd.call("app", "genai_instr", "LangChain / OpenAI call")
sd.call("genai_instr", "api", "Start span (gen_ai semantic conventions)")
sd.call("api", "sdk", "Record span")
sd.reply("genai_instr", "app", "Response")
sd.end_group()

# Export
sd.group("Multi-Exporter Pipeline")
sd.call("sdk", "exporters", "Export batch")
sd.self_call("exporters", "Azure Monitor Exporter -> App Insights (optional)")
sd.self_call("exporters", "Agent365 Exporter -> A365 Backend")
sd.self_call("exporters", "OTLP Exporter -> OTel Collector")
sd.end_group()

out = Path(__file__).resolve().parent.parent.parent / "output" / "microsoft-otel-sequence.excalidraw"
sd.save(out)
print(f"Created: {out}")
