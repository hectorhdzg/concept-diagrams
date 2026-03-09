#!/usr/bin/env python3
"""Azure Monitor OpenTelemetry (Python) -- Sequence Diagram
Shows the runtime flow: app initialization, request instrumentation, export.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from sequence_diagram import SequenceDiagram

sd = SequenceDiagram(
    title="Azure Monitor OpenTelemetry -- Python Sequence",
    participant_gap=240,
    row_height=55,
)

# Participants
sd.participant("app",         "Python\nApplication",       color="blue")
sd.participant("distro",      "Azure Monitor\nDistro",     color="blue")
sd.participant("instr",       "Bundled\nInstrumentations",  color="green")
sd.participant("api",         "OTel API",                   color="orange")
sd.participant("sdk",         "OTel SDK",                   color="orange")
sd.participant("az_exporter", "Azure Monitor\nExporter",   color="blue")
sd.participant("otlp_exp",    "OTLP\nExporter",            color="orange")

# Initialization
sd.group("Initialization")
sd.call("app", "distro", "configure_azure_monitor()")
sd.call("distro", "instr", "Bundle instrumentations (Django, Flask, ...)")
sd.call("distro", "sdk", "Configure SDK + Resource Detector")
sd.call("distro", "az_exporter", "Configure Azure Monitor Exporter")
sd.call("distro", "otlp_exp", "Configure OTLP Exporter (optional)")
sd.reply("distro", "app", "Ready")
sd.end_group()

# Runtime: auto-instrumented request
sd.group("Incoming Request (auto-instrumented)")
sd.call("app", "instr", "HTTP request arrives (Django/Flask/FastAPI)")
sd.call("instr", "api", "Start span (http.method, http.url)")
sd.note("api", "OTel Semantic Conventions", position="right")
sd.call("api", "sdk", "Record span")
sd.reply("instr", "app", "Instrumented response")
sd.end_group()

# Runtime: outgoing call
sd.group("Outgoing Call (auto-instrumented)")
sd.call("app", "instr", "requests.get() / urllib.urlopen()")
sd.call("instr", "api", "Start client span")
sd.call("api", "sdk", "Record span")
sd.reply("instr", "app", "Response with trace context")
sd.end_group()

# Export
sd.group("Telemetry Export")
sd.call("sdk", "az_exporter", "Export batch (traces, metrics, logs)")
sd.call("az_exporter", "az_exporter", "")
sd.self_call("az_exporter", "POST to Application Insights")
sd.call("sdk", "otlp_exp", "Export batch (OTLP/gRPC)")
sd.call("otlp_exp", "otlp_exp", "")
sd.self_call("otlp_exp", "Send to OTel Collector")
sd.end_group()

out = Path(__file__).resolve().parent.parent.parent / "output" / "azure-monitor-sequence.excalidraw"
sd.save(out)
print(f"Created: {out}")
