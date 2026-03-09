#!/usr/bin/env python3
"""Microsoft OpenTelemetry (Python) -- Architecture Diagram
Extends Azure Monitor OpenTelemetry with GenAI instrumentations,
A365 exporter & instrumentations, OTLP exporters.
Azure Monitor components are optional.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

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

# ============================================================
# AREA BACKGROUNDS
# ============================================================
# Microsoft OpenTelemetry area (main, covers everything)
area_msotel = rectangle(20, 50, 1520, 1300, color="teal", fill=True, rounded=True,
                        opacity=10, stroke_width=2, stroke_style="dashed")
area_msotel_label = text(30, 55, "Microsoft OpenTelemetry", font_size=18, color="teal", align="left")

# Azure Monitor (optional) sub-area
area_azmon = rectangle(40, 320, 420, 940, color="blue", fill=True, rounded=True,
                       opacity=15, stroke_width=2, stroke_style="dashed")
area_azmon_label = text(50, 325, "Azure Monitor (Optional)", font_size=14, color="blue", align="left")

# Agent 365 sub-area
area_a365 = rectangle(470, 320, 380, 940, color="violet", fill=True, rounded=True,
                      opacity=15, stroke_width=2, stroke_style="dashed")
area_a365_label = text(480, 325, "Agent 365", font_size=14, color="violet", align="left")

# OpenTelemetry core area
area_otel = rectangle(860, 50, 670, 1300, color="orange", fill=True, rounded=True,
                      opacity=15, stroke_width=2, stroke_style="dashed")
area_otel_label = text(870, 55, "OpenTelemetry", font_size=14, color="orange", align="left")

# ============================================================
# ROW 1: Application
# ============================================================
r1 = 100
app = arch.component("app", "Python Application", x=600, y=r1, color="blue")

# ============================================================
# ROW 2: Distro (central entry point)
# ============================================================
r2 = r1 + 200
distro = arch.component("distro", "Microsoft OpenTelemetry\nDistro\nconfigure()", x=540, y=r2, color="teal")

# ============================================================
# ROW 3: Instrumentations (wide row)
# ============================================================
r3 = r2 + 220
# Azure Monitor bundled
az_instr = arch.component("az_instr", "Azure Monitor\nInstrumentations\nDjango, Flask, FastAPI,\nRequests, UrlLib,\nPsycopg2, Azure SDK", x=50, y=r3, color="blue")

# A365 instrumentations
a365_instr = arch.component("a365_instr", "A365 Instrumentations\nOpenAI, LangChain,\nSemantic Kernel", x=490, y=r3, color="violet")

# GenAI instrumentations (OTel community)
genai_instr = arch.component("genai_instr", "GenAI Instrumentations\nopenai, langchain,\ngenai semantic conv.", x=880, y=r3, color="orange")

# Standard OTel contrib
otel_instr = arch.component("otel_instr", "OTel Contrib\nInstrumentations\nhttpx, aiohttp,\ngrpc, redis", x=1180, y=r3, color="orange")

# ============================================================
# ROW 4: Semantic Conventions + Resource Detectors
# ============================================================
r4 = r3 + 250
semconv = arch.component("semconv", "OTel Semantic Conventions\nhttp.*, db.*, gen_ai.*,\nagent.*, tool.*", x=880, y=r4, color="orange")
resource_det = arch.component("resource_det", "Azure Resource\nDetector\ncloud.provider,\ncloud.region", x=50, y=r4, color="blue")
a365_semconv = arch.component("a365_semconv", "A365 Custom Attributes\nagent_id, tenant_id,\ncorrelation_id", x=490, y=r4, color="violet")

# ============================================================
# ROW 5: OTel API + SDK
# ============================================================
r5 = r4 + 250
api = arch.component("api", "OTel API\nopentelemetry-api", x=880, y=r5, color="orange")
sdk = arch.component("sdk", "OTel SDK\nopentelemetry-sdk", x=1150, y=r5, color="orange")

# ============================================================
# ROW 6: Exporters + Backends
# ============================================================
r6 = r5 + 220
# Azure Monitor export (optional)
azure_exp = arch.component("azure_exp", "Azure Monitor\nExporter", x=50, y=r6, color="blue")
app_insights = arch.component("app_insights", "Application\nInsights", x=260, y=r6, color="cyan")

# A365 export
a365_exp = arch.component("a365_exp", "Agent365\nExporter", x=490, y=r6, color="violet")
a365_backend = arch.component("a365_backend", "Agent365\nBackend", x=690, y=r6, color="violet")

# OTLP export
otlp_exp = arch.component("otlp_exp", "OTLP Exporter", x=920, y=r6, color="orange")
collector = arch.component("collector", "OTel Collector /\nBackend", x=1150, y=r6, color="gray")

# ============================================================
# CONNECTIONS
# ============================================================
# App -> API
arch.connect("app", "api", label="Traces, Metrics, Logs")

# Distro configures everything
arch.connect("distro", "sdk", label="Configures SDK")
arch.connect("distro", "az_instr", label="Bundles (optional)")
arch.connect("distro", "a365_instr", label="Bundles")
arch.connect("distro", "genai_instr", label="Bundles")
arch.connect("distro", "resource_det", label="Configures")
arch.connect("distro", "azure_exp", label="Optional")
arch.connect("distro", "a365_exp", label="Configures")
arch.connect("distro", "otlp_exp", label="Configures")

# Instrumentations -> API
arch.connect("az_instr", "api", label="Auto-instrument")
arch.connect("a365_instr", "api", label="Auto-instrument")
arch.connect("genai_instr", "api", label="Auto-instrument")
arch.connect("otel_instr", "api", label="Auto-instrument")

# Semantic conventions
arch.connect("az_instr", "semconv", label="Uses")
arch.connect("a365_instr", "semconv", label="Uses")
arch.connect("genai_instr", "semconv", label="Uses")

# Resource & SDK
arch.connect("resource_det", "sdk", label="Resource info")
arch.connect("api", "sdk", label="Implements")

# Export
arch.connect("sdk", "azure_exp", label="Export")
arch.connect("sdk", "a365_exp", label="Export")
arch.connect("sdk", "otlp_exp", label="Export")
arch.connect("azure_exp", "app_insights", label="Ingest")
arch.connect("a365_exp", "a365_backend", label="Traces")
arch.connect("otlp_exp", "collector", label="OTLP/gRPC")

# --- Title ---
arch.text_box(350, 10, "Microsoft OpenTelemetry -- Python", font_size=28, color="black")

# ============================================================
# ELEMENT ORDERING
# ============================================================
areas = [area_msotel, area_otel, area_azmon, area_a365]
area_labels = [area_msotel_label, area_otel_label, area_azmon_label, area_a365_label]

arrows = [e for e in arch.elements if e.get("type") in ("arrow", "line")]
arrow_labels = [e for e in arch.elements if e.get("type") == "text" and e.get("containerId")]
boxes = [e for e in arch.elements if e.get("type") in ("rectangle", "ellipse", "diamond")]
box_text = [e for e in arch.elements if e.get("type") == "text" and not e.get("containerId")]

arch.elements = areas + arrows + boxes + box_text + arrow_labels + area_labels

out = Path(__file__).resolve().parent.parent.parent / "output" / "microsoft-opentelemetry.excalidraw"
arch.save(out)
print(f"Created: {out}")
