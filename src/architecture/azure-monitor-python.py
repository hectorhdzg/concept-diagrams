#!/usr/bin/env python3
"""Azure Monitor OpenTelemetry (Python) -- Architecture Diagram
Instrumentations: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/monitor/azure-monitor-opentelemetry
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
        database_color="green",
        service_color="violet",
    ),
    diagram_style=DiagramStyle(roughness=0, font="nunito"),
    use_astar_routing=True,
)

# ============================================================
# AREA BACKGROUNDS (drawn first = behind everything)
# ============================================================
# Azure Monitor owned area (left side)
area_azmon = rectangle(30, 60, 560, 880, color="blue", fill=True, rounded=True,
                       opacity=20, stroke_width=2, stroke_style="dashed")
area_azmon_label = text(40, 65, "Azure Monitor Owned", font_size=16, color="blue", align="left")

# OpenTelemetry owned area (right side)
area_otel = rectangle(600, 60, 440, 880, color="orange", fill=True, rounded=True,
                      opacity=20, stroke_width=2, stroke_style="dashed")
area_otel_label = text(610, 65, "OpenTelemetry Owned", font_size=16, color="orange", align="left")

# ============================================================
# ROW 1: Application (spans both areas)
# ============================================================
r1 = 100
app = arch.component("app", "Python Application", x=380, y=r1, color="blue")

# ============================================================
# ROW 2: Distro + Instrumentations
# ============================================================
r2 = r1 + 180
distro = arch.component("distro", "Azure Monitor\nOpenTelemetry Distro\nconfigure_azure_monitor()", x=60, y=r2, color="blue")
instr = arch.component("instr", "Bundled Instrumentations\nDjango, FastAPI, Flask,\nRequests, UrlLib, UrlLib3,\nPsycopg2, Azure SDK", x=340, y=r2, color="green")
genai = arch.component("genai", "Community\nInstrumentations\nOpenAI, LangChain", x=640, y=r2, color="violet")

# ============================================================
# ROW 3: Semantic Conventions + Resource Detectors
# ============================================================
r3 = r2 + 220
semconv = arch.component("semconv", "OTel Semantic Conventions\nhttp.*, db.*, gen_ai.*", x=640, y=r3, color="orange")
resource_det = arch.component("resource_det", "Azure Resource Detector\nservice.name,\ncloud.provider, cloud.region", x=60, y=r3, color="blue")

# ============================================================
# ROW 4: API + SDK
# ============================================================
r4 = r3 + 200
api = arch.component("api", "OTel API\nopentelemetry-api", x=640, y=r4, color="orange")
sdk = arch.component("sdk", "OTel SDK\nopentelemetry-sdk", x=860, y=r4, color="orange")

# ============================================================
# ROW 5: Exporters + Backends
# ============================================================
r5 = r4 + 200
azure_exp = arch.component("azure_exp", "Azure Monitor\nExporter", x=60, y=r5, color="blue")
app_insights = arch.component("app_insights", "Application Insights", x=340, y=r5, color="cyan")
otlp_exp = arch.component("otlp_exp", "OTLP Exporter", x=640, y=r5, color="orange")
collector = arch.component("collector", "OTel Collector /\nBackend", x=860, y=r5, color="gray")

# ============================================================
# CONNECTIONS
# ============================================================
arch.connect("app", "api", label="Traces, Metrics, Logs")
arch.connect("api", "sdk", label="Implements")
arch.connect("instr", "api", label="Auto-instrument")
arch.connect("genai", "api", label="Auto-instrument")
arch.connect("instr", "semconv", label="Uses conventions")
arch.connect("resource_det", "sdk", label="Resource info")
arch.connect("distro", "resource_det", label="Configures")
arch.connect("distro", "sdk", label="Configures SDK")
arch.connect("distro", "instr", label="Bundles")
arch.connect("distro", "azure_exp", label="Configures")
arch.connect("sdk", "azure_exp", label="Export")
arch.connect("sdk", "otlp_exp", label="Export")
arch.connect("azure_exp", "app_insights", label="Ingest")
arch.connect("otlp_exp", "collector", label="OTLP/gRPC")

# --- Title ---
arch.text_box(200, 20, "Azure Monitor OpenTelemetry -- Python", font_size=28, color="black")

# ============================================================
# ELEMENT ORDERING
# ============================================================
# 1) Area backgrounds (very back)
# 2) Arrows + arrow labels
# 3) Boxes + box text (front)
# 4) Standalone text labels (title, area labels) on top
areas = [area_azmon, area_otel]
area_labels = [area_azmon_label, area_otel_label]

arrows = [e for e in arch.elements if e.get("type") in ("arrow", "line")]
arrow_labels = [e for e in arch.elements if e.get("type") == "text" and e.get("containerId")]
boxes = [e for e in arch.elements if e.get("type") in ("rectangle", "ellipse", "diamond")]
box_text = [e for e in arch.elements if e.get("type") == "text" and not e.get("containerId")]

arch.elements = areas + arrows + boxes + box_text + arrow_labels + area_labels

out = Path(__file__).resolve().parent.parent.parent / "output" / "azure-monitor-python.excalidraw"
arch.save(out)
print(f"Created: {out}")
