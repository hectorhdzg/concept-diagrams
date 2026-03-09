#!/usr/bin/env python3
"""Agent 365 SDK Observability -- Sequence Diagram
Shows the runtime flow: request arrives, spans are created, exported.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from sequence_diagram import SequenceDiagram

sd = SequenceDiagram(
    title="Agent 365 SDK -- Observability Sequence",
    participant_gap=220,
    row_height=55,
)

# Participants (left-to-right timeline columns)
sd.participant("channel",    "Channel\n(Teams, Slack)",  color="violet")
sd.participant("hosting",    "Hosting\n(aiohttp)",       color="blue")
sd.participant("core",       "Core\n(CloudAdapter)",     color="blue")
sd.participant("agent_app",  "AgentApp\n(Routing)",      color="yellow")
sd.participant("obs_core",   "Observability\nCore",      color="teal")
sd.participant("scopes",     "Scopes\n(Invoke/Infer/Tool)", color="cyan")
sd.participant("ai_ext",     "A365 AI\nExtensions",      color="violet")
sd.participant("processing", "SpanProcessors",           color="orange")
sd.participant("exporters",  "Exporters",                color="orange")

# Initialization phase
sd.group("Initialization")
sd.call("agent_app", "obs_core", "configure()")
sd.call("obs_core", "processing", "Register A365 SpanProcessor")
sd.call("obs_core", "processing", "Register BatchSpanProcessor")
sd.call("obs_core", "exporters", "Configure Agent365Exporter + OTLP")
sd.end_group()

# Request processing
sd.group("Request Processing")
sd.call("channel", "hosting", "HTTP request")
sd.call("hosting", "core", "TurnContext")
sd.call("core", "agent_app", "Route activity")
sd.end_group()

# Observability: span creation
sd.group("Span Lifecycle")
sd.call("agent_app", "obs_core", "Start observation")
sd.call("obs_core", "scopes", "InvokeAgentScope (root span)")
sd.call("scopes", "scopes", "")
sd.self_call("scopes", "Set OTel Semantic Conventions")

# LLM call
sd.call("agent_app", "ai_ext", "LLM / tool call")
sd.call("ai_ext", "scopes", "InferenceScope (child span)")
sd.call("ai_ext", "scopes", "A365 Custom Attributes")
sd.reply("ai_ext", "agent_app", "LLM response")

# Tool execution
sd.call("agent_app", "scopes", "ExecuteToolScope (child span)")
sd.reply("scopes", "agent_app", "Tool result")
sd.end_group()

# Export phase
sd.group("Span Export")
sd.call("scopes", "processing", "Completed spans")
sd.call("processing", "processing", "")
sd.self_call("processing", "Enrich with baggage (tenant_id, agent_id)")
sd.call("processing", "exporters", "Batch export")
sd.call("exporters", "exporters", "")
sd.self_call("exporters", "Agent365Exporter -> A365 Backend")
sd.self_call("exporters", "OTLP Exporter -> Jaeger/Grafana")
sd.end_group()

# Response
sd.reply("agent_app", "core", "Response")
sd.reply("core", "hosting", "HTTP response")
sd.reply("hosting", "channel", "Reply message")

out = Path(__file__).resolve().parent / "agents-sdk-sequence.excalidraw"
sd.save(out)
print(f"Created: {out}")
