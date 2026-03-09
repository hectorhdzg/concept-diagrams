# concept-diagrams

Generate software architecture and workflow diagrams as [Excalidraw](https://excalidraw.com) files using Python.

Powered by [`excalidraw-diagrams`](https://github.com/robtaylor/excalidraw-diagrams) — a Python library that outputs native `.excalidraw` JSON files with hand-drawn aesthetics.

## Project Structure

```
concept-diagrams/
├── scripts/                    # Excalidraw generator library
│   ├── excalidraw_generator.py # Core: Diagram, Flowchart, ArchitectureDiagram
│   └── layout_engine.py        # Auto-layout (Sugiyama algorithm)
├── diagrams/                   # Diagram source scripts + output
│   ├── otel-python.py
│   ├── otel-python.excalidraw
│   ├── agents-sdk-observability.py
│   └── agents-sdk-observability.excalidraw
└── README.md
```

## Requirements

- Python 3.8+ (no external dependencies)

## Usage

### Generate a diagram

```bash
python diagrams/otel-python.py
python diagrams/agents-sdk-observability.py
```

Each script produces a `.excalidraw` file in the same directory.

### View diagrams

- **VS Code**: Install the [Excalidraw extension](https://marketplace.visualstudio.com/items?itemName=pomdtr.excalidraw-editor) and open any `.excalidraw` file
- **Browser**: Open [excalidraw.com](https://excalidraw.com) → "Open" → select the `.excalidraw` file
- **Obsidian**: Use the Excalidraw plugin

### Create a new diagram

Create a Python file in `diagrams/` using the generator API:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from excalidraw_generator import ArchitectureDiagram, DiagramStyle

arch = ArchitectureDiagram(
    diagram_style=DiagramStyle(roughness=1, font="hand"),
    use_astar_routing=True,
)

frontend = arch.component("fe", "Frontend", x=100, y=100, color="blue")
backend  = arch.service("be", "Backend API", x=400, y=100, color="green")
db       = arch.database("db", "PostgreSQL", x=400, y=300, color="orange")

arch.connect("fe", "be", label="REST API")
arch.connect("be", "db", label="SQL")

arch.save("diagrams/my-system.excalidraw")
```

### Available diagram builders

| Builder | Use Case | Key Methods |
|---------|----------|-------------|
| `Diagram` | General purpose | `box()`, `arrow_between()`, `text_box()` |
| `Flowchart` | Process flows | `start()`, `process()`, `decision()`, `end()`, `connect()` |
| `AutoLayoutFlowchart` | Auto-positioned flows | `add_node()`, `add_edge()`, `compute_layout()` |
| `ArchitectureDiagram` | System architecture | `component()`, `service()`, `database()`, `user()`, `connect()` |

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

### OpenTelemetry Python Ecosystem
Architecture showing the OTel Python stack: API, SDK, instrumentations (including GenAI), Azure Monitor distro, exporters, and collector.

### Microsoft 365 Agents SDK — Observability
Architecture showing the Agents SDK Python observability flow: Channels → Hosting → Core → AgentApplication → OpenTelemetry API/SDK → Exporter → Backend.

## License

MIT
