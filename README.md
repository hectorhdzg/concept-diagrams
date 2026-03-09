# concept-diagrams

Generate software architecture and sequence diagrams as [Excalidraw](https://excalidraw.com) files using Python.

Powered by [`excalidraw-diagrams`](https://github.com/robtaylor/excalidraw-diagrams) — a Python library that outputs native `.excalidraw` JSON files.

## Project Structure

```
concept-diagrams/
├── src/
│   ├── lib/                           # Generator libraries
│   │   ├── excalidraw_generator.py    # Core: Diagram, ArchitectureDiagram, etc.
│   │   ├── sequence_diagram.py        # SequenceDiagram builder
│   │   └── layout_engine.py           # Auto-layout (Sugiyama algorithm)
│   ├── architecture/                  # Architecture diagram sources
│   │   ├── agents-sdk-observability.py
│   │   ├── azure-monitor-python.py
│   │   └── microsoft-opentelemetry.py
│   └── sequence/                      # Sequence diagram sources
│       ├── agents-sdk-sequence.py
│       ├── azure-monitor-sequence.py
│       └── microsoft-otel-sequence.py
├── output/                            # Generated .excalidraw files
└── README.md
```

## Requirements

- Python 3.8+ (no external dependencies)

## Usage

### Generate diagrams

```bash
# Architecture diagrams
python src/architecture/agents-sdk-observability.py
python src/architecture/azure-monitor-python.py
python src/architecture/microsoft-opentelemetry.py

# Sequence diagrams
python src/sequence/agents-sdk-sequence.py
python src/sequence/azure-monitor-sequence.py
python src/sequence/microsoft-otel-sequence.py
```

All output goes to the `output/` directory.

### View diagrams

- **VS Code**: Install the [Excalidraw extension](https://marketplace.visualstudio.com/items?itemName=pomdtr.excalidraw-editor) and open any `.excalidraw` file
- **Browser**: Open [excalidraw.com](https://excalidraw.com) and load the `.excalidraw` file
- **Obsidian**: Use the Excalidraw plugin

### Create a new diagram

Create a Python file in `src/architecture/` or `src/sequence/`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))

from excalidraw_generator import ArchitectureDiagram, DiagramStyle

arch = ArchitectureDiagram(
    diagram_style=DiagramStyle(roughness=0, font="nunito"),
    use_astar_routing=True,
)

frontend = arch.component("fe", "Frontend", x=100, y=100, color="blue")
backend  = arch.service("be", "Backend API", x=400, y=100, color="green")
db       = arch.database("db", "PostgreSQL", x=400, y=300, color="orange")

arch.connect("fe", "be", label="REST API")
arch.connect("be", "db", label="SQL")

out = Path(__file__).resolve().parent.parent.parent / "output" / "my-system.excalidraw"
arch.save(out)
```

### Available diagram builders

| Builder | Use Case | Key Methods |
|---------|----------|-------------|
| `ArchitectureDiagram` | System architecture | `component()`, `service()`, `database()`, `connect()` |
| `SequenceDiagram` | Timeline / call flows | `participant()`, `call()`, `reply()`, `group()` |
| `Diagram` | General purpose | `box()`, `arrow_between()`, `text_box()` |
| `AutoLayoutFlowchart` | Auto-positioned flows | `add_node()`, `add_edge()`, `compute_layout()` |

### Colors

`blue`, `green`, `red`, `yellow`, `orange`, `violet`, `cyan`, `teal`, `gray`, `black`, `pink`, `grape`

### Style options

```python
DiagramStyle(
    roughness=0,         # 0=clean, 1=hand-drawn, 2=rough sketch
    font="nunito",       # hand, normal, code, nunito, excalifont
    stroke_style="solid" # solid, dashed, dotted
)
```

## Included Diagrams

### Architecture Diagrams
- **Azure Monitor Python** — Azure Monitor OpenTelemetry distro, bundled instrumentations, exporters
- **Agent 365 SDK Observability** — Full observability flow: channels, scopes, span processing, export
- **Microsoft OpenTelemetry** — Unified distro with Azure Monitor (optional), A365, and OTLP export

### Sequence Diagrams
- **Azure Monitor Sequence** — Runtime flow: init, auto-instrumented requests, export pipeline
- **Agent 365 SDK Sequence** — Request lifecycle: channel to span export with LLM/tool calls
- **Microsoft OpenTelemetry Sequence** — Multi-instrumentation and multi-exporter timeline

## License

MIT
