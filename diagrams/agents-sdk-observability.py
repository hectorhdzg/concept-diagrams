#!/usr/bin/env python3
"""Microsoft Agent 365 SDK (Python) -- Full Observability Architecture
Based on: https://github.com/microsoft/Agent365-python/blob/main/docs/design.md

Horizontal layout: 5 rows, components spread wide.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from excalidraw_generator import (
    ArchitectureDiagram, ArchitectureStyle, DiagramStyle,
    rectangle, text,
)

arch = ArchitectureDiagram(
    architecture_style=ArchitectureStyle(
        component_color="blue",
        service_color="violet",
    ),
    diagram_style=DiagramStyle(roughness=0, font="nunito"),
    use_astar_routing=True,
)

# Layout: wide horizontal, 5 rows with large gaps for label visibility
RG = 300  # row gap (large to give space for connector labels)

# ============================================================
# AREA BACKGROUNDS (drawn first = behind everything)
# ============================================================
# Agent 365 Owned area (rows 1-3.5: app stack, observability, scopes, AI ext, semconv)
area_a365 = rectangle(30, 70, 1380, 1080, color="violet", fill=True, rounded=True,
                      opacity=15, stroke_width=2, stroke_style="dashed")
area_a365_label = text(40, 75, "Agent 365 Owned", font_size=16, color="violet", align="left")

# Agent 365 Export sub-area (row 6 left: exporter + backend)
area_a365_exp = rectangle(30, 1560, 590, 200, color="violet", fill=True, rounded=True,
                          opacity=15, stroke_width=2, stroke_style="dashed")
area_a365_exp_label = text(40, 1565, "Agent 365 Export", font_size=14, color="violet", align="left")

# OpenTelemetry / Standards area (row 3.5: semconv + resource detectors)
area_otel_std = rectangle(30, 1160, 1380, 140, color="orange", fill=True, rounded=True,
                          opacity=15, stroke_width=2, stroke_style="dashed")
area_otel_std_label = text(40, 1165, "OpenTelemetry Standards", font_size=14, color="orange", align="left")

# OpenTelemetry Pipeline area (rows 5-6: processing + export)
area_otel = rectangle(30, 1310, 1380, 450, color="orange", fill=True, rounded=True,
                      opacity=15, stroke_width=2, stroke_style="dashed")
area_otel_label = text(40, 1315, "OpenTelemetry Pipeline", font_size=16, color="orange", align="left")

# ============================================================
# ROW 1: Application Stack (left-to-right flow)
# ============================================================
r1 = 100
channels   = arch.component("channels",   "Channels\nTeams, Copilot Studio,\nWebchat, Slack",  x=60,   y=r1, color="violet")
hosting    = arch.component("hosting",    "Hosting (aiohttp)",                                 x=340,  y=r1, color="blue")
core       = arch.component("core",       "Hosting Core\nCloudAdapter,\nTurnContext, Middleware", x=580, y=r1, color="blue")
activity   = arch.component("activity",   "Activity Protocol",                                  x=880,  y=r1, color="orange")
agent_app  = arch.component("agent_app",  "AgentApplication\nRouting & State",                   x=1120, y=r1, color="yellow")

# ============================================================
# ROW 2: Observability Extensions (hook into app stack above)
# ============================================================
r2 = r1 + RG
obs_hosting  = arch.component("obs_hosting",  "Observability\nHosting",                   x=340,  y=r2, color="teal")
ext_agentfw  = arch.component("ext_agentfw",  "AgentFramework\nExtension",                x=580,  y=r2, color="teal")
obs_core     = arch.component("obs_core",     "Observability Core\nconfigure(),\nTelemetryManager", x=880, y=r2, color="teal")
baggage      = arch.component("baggage",      "BaggageBuilder\ntenant, agent,\ncorrelation IDs",    x=1120, y=r2, color="teal")

# ============================================================
# ROW 3: Scope Spans + AI Framework Extensions (A365 custom)
# ============================================================
r3 = r2 + RG
invoke_scope    = arch.component("invoke_scope",    "InvokeAgentScope\nRoot span",      x=60,   y=r3, color="cyan")
inference_scope = arch.component("inference_scope", "InferenceScope\nLLM/AI calls,\ntoken tracking", x=320, y=r3, color="cyan")
tool_scope      = arch.component("tool_scope",      "ExecuteToolScope\nTool execution", x=580,  y=r3, color="cyan")
ext_openai      = arch.component("ext_openai",      "A365 OpenAI\nExtension",           x=820,  y=r3, color="violet")
ext_langchain   = arch.component("ext_langchain",   "A365 LangChain\nExtension",        x=1000, y=r3, color="violet")
ext_sk          = arch.component("ext_sk",          "A365 Semantic\nKernel Extension",  x=1200, y=r3, color="violet")

# ============================================================
# ROW 3.5: Semantic Conventions + Resource Detectors
# ============================================================
r3h = r3 + RG
semconv = arch.component("semconv", "OTel Semantic Conventions\ngen_ai.*, agent.*,\ntool.*, session.*", x=60, y=r3h, color="orange")
a365_semconv = arch.component("a365_semconv", "A365 Custom Attributes\nagent_id, tenant_id,\ncorrelation_id", x=380, y=r3h, color="violet")
resource_det = arch.component("resource_det", "Azure Resource Detector\nservice.name,\ncloud.provider,\ncloud.region", x=700, y=r3h, color="blue")

# ============================================================
# ROW 4: Span Processing (A365 SpanProcessor + OTel BatchSpanProcessor)
# ============================================================
r4 = r3h + RG
span_proc  = arch.component("span_proc",  "A365 SpanProcessor\nBaggage to span\nattributes", x=200,  y=r4, color="violet")
batch_proc = arch.component("batch_proc", "BatchSpanProcessor\nAccumulate & batch",           x=560,  y=r4, color="orange")

# ============================================================
# ROW 5: Exporters + Backends
# ============================================================
r5 = r4 + RG
a365_exp     = arch.component("a365_exp",     "Agent365Exporter\nPartition by\n(tenant_id, agent_id)", x=60,   y=r5, color="violet")
a365_backend = arch.component("a365_backend", "Agent365 Backend\n/maven/agent365/\nagents/{id}/traces",   x=350,  y=r5, color="violet")
otlp_exp     = arch.component("otlp_exp",     "OTLP / Console\nExporter",                              x=700,  y=r5, color="orange")
obs_backend  = arch.component("obs_backend",  "Observability Backend\nJaeger, Zipkin, Grafana",         x=980,  y=r5, color="gray")

# ============================================================
# CONNECTIONS
# ============================================================

# Row 1: Application flow (left to right)
arch.connect("channels", "hosting", label="HTTP")
arch.connect("hosting", "core", label="TurnContext")
arch.connect("core", "activity", label="Activity types")
arch.connect("core", "agent_app", label="Route activity")

# Row 1 -> Row 2: Extensions instrument the app stack
arch.connect("obs_hosting", "hosting", label="Instruments")
arch.connect("ext_agentfw", "core", label="Instruments")
arch.connect("agent_app", "obs_core", label="configure()")
arch.connect("obs_core", "baggage", label="Set context")

# Row 2 -> Row 3: Core creates scopes
arch.connect("obs_core", "invoke_scope", label="Start root span")
arch.connect("invoke_scope", "inference_scope", label="Child span")
arch.connect("invoke_scope", "tool_scope", label="Child span")

# Row 3: AI extensions feed scopes
arch.connect("ext_openai", "inference_scope", label="OpenAI calls")
arch.connect("ext_langchain", "inference_scope", label="Callbacks")
arch.connect("ext_sk", "inference_scope", label="Kernel calls")

# Row 3 -> Row 3.5: Semantic conventions & resource detection
arch.connect("invoke_scope", "semconv", label="Uses conventions")
arch.connect("a365_semconv", "baggage", label="Custom attributes")
arch.connect("resource_det", "obs_core", label="Resource info")

# Row 3 -> Row 4: Processing
arch.connect("baggage", "span_proc", label="Baggage entries")
arch.connect("invoke_scope", "span_proc", label="Spans")
arch.connect("span_proc", "batch_proc", label="Enriched spans")

# Row 4 -> Row 5: Export
arch.connect("batch_proc", "a365_exp", label="Export batch")
arch.connect("batch_proc", "otlp_exp", label="Export batch")
arch.connect("a365_exp", "a365_backend", label="Platform telemetry")
arch.connect("otlp_exp", "obs_backend", label="OTLP/gRPC")

# --- Title ---
arch.text_box(300, 30, "Microsoft Agent 365 SDK -- Observability Architecture", font_size=28, color="black")

# ============================================================
# ELEMENT ORDERING
# ============================================================
# 1) Area backgrounds (very back)
# 2) Arrows
# 3) Boxes + box text (front)
# 4) Arrow labels + standalone text + area labels (top)
areas = [area_otel, area_otel_std, area_a365, area_a365_exp]
area_labels = [area_a365_label, area_a365_exp_label, area_otel_label, area_otel_std_label]

arrows = [e for e in arch.elements if e.get("type") in ("arrow", "line")]
arrow_labels = [e for e in arch.elements if e.get("type") == "text" and e.get("containerId")]
boxes = [e for e in arch.elements if e.get("type") in ("rectangle", "ellipse", "diamond")]
box_text = [e for e in arch.elements if e.get("type") == "text" and not e.get("containerId")]

arch.elements = areas + arrows + boxes + box_text + arrow_labels + area_labels

out = Path(__file__).resolve().parent / "agents-sdk-observability.excalidraw"
arch.save(out)
print(f"Created: {out}")
