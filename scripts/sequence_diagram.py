#!/usr/bin/env python3
"""Sequence Diagram Generator for Excalidraw.

Generates timeline-style sequence diagrams with participants (columns),
lifelines, and horizontal call/reply arrows between them.

Usage:
    from sequence_diagram import SequenceDiagram

    sd = SequenceDiagram("My Sequence")
    sd.participant("a", "Service A", color="blue")
    sd.participant("b", "Service B", color="green")
    sd.call("a", "b", "request()")
    sd.reply("b", "a", "response")
    sd.save("my-sequence.excalidraw")
"""
import json
import uuid
import random
from pathlib import Path
from typing import Optional, List

# Re-use primitives from excalidraw_generator
from excalidraw_generator import (
    rectangle, text, line, arrow, _gen_id, _gen_seed, _base_element,
    COLORS, BG_FOR_STROKE, FONT_FAMILY, FONT_METRICS,
)


class SequenceDiagram:
    """Builds an Excalidraw sequence diagram.

    Participants are laid out as boxes across the top.  Vertical dashed
    lifelines extend downward.  Calls are solid arrows, replies are dashed.
    """

    def __init__(
        self,
        title: str = "",
        participant_gap: int = 260,
        row_height: int = 60,
        font: str = "nunito",
        roughness: int = 0,
        start_x: int = 80,
        start_y: int = 80,
    ):
        self.title = title
        self.participant_gap = participant_gap
        self.row_height = row_height
        self.font = font
        self.roughness = roughness
        self.start_x = start_x
        self.start_y = start_y

        self._participants: list[dict] = []   # ordered list of {id, label, color, x}
        self._participant_index: dict[str, int] = {}
        self._messages: list[dict] = []       # {type, from, to, label, ...}
        self._current_row = 0                 # advances with each message
        self._groups: list[dict] = []         # {label, start_row, end_row}
        self._group_stack: list[dict] = []

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    def participant(self, pid: str, label: str, color: str = "blue"):
        """Add a participant (column)."""
        idx = len(self._participants)
        x = self.start_x + idx * self.participant_gap
        self._participants.append({"id": pid, "label": label, "color": color, "x": x})
        self._participant_index[pid] = idx

    def call(self, from_id: str, to_id: str, label: str = ""):
        """Add a synchronous call (solid arrow)."""
        self._messages.append({"type": "call", "from": from_id, "to": to_id, "label": label})
        self._current_row += 1

    def reply(self, from_id: str, to_id: str, label: str = ""):
        """Add a reply (dashed arrow)."""
        self._messages.append({"type": "reply", "from": from_id, "to": to_id, "label": label})
        self._current_row += 1

    def self_call(self, pid: str, label: str = ""):
        """Add a self-call (arrow looping back to same participant)."""
        self._messages.append({"type": "self", "from": pid, "to": pid, "label": label})
        self._current_row += 1

    def note(self, pid: str, content: str, position: str = "right"):
        """Add a note next to a participant's lifeline."""
        self._messages.append({"type": "note", "from": pid, "to": pid,
                                "label": content, "position": position})
        self._current_row += 1

    def group(self, label: str):
        """Start a named group (alt/loop/opt box)."""
        self._group_stack.append({"label": label, "start_row": self._current_row})

    def end_group(self):
        """End the current group."""
        if self._group_stack:
            g = self._group_stack.pop()
            g["end_row"] = self._current_row
            self._groups.append(g)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _participant_center_x(self, pid: str) -> float:
        idx = self._participant_index[pid]
        p = self._participants[idx]
        # Center of the participant box
        label = p["label"]
        lines = label.split("\n")
        max_len = max(len(l) for l in lines)
        box_w = max(120, max_len * 18 * 0.55 + 40)
        return p["x"] + box_w / 2

    def _row_y(self, row: int) -> float:
        """Y position for a given message row."""
        # First row starts below participant boxes
        box_h = 50  # approximate participant box height
        return self.start_y + box_h + 40 + row * self.row_height

    def build(self) -> list[dict]:
        """Build all Excalidraw elements."""
        elements: list[dict] = []
        title_offset = 0

        # Title
        if self.title:
            title_offset = 40
            total_width = (len(self._participants) - 1) * self.participant_gap + 200
            t = text(
                self.start_x, self.start_y - 50,
                self.title, font_size=28, font_family=self.font, color="black",
            )
            t["width"] = total_width
            t["textAlign"] = "center"
            elements.append(t)

        # Participant boxes
        participant_elements: list[dict] = []
        participant_text_elements: list[dict] = []
        box_bottoms = []
        for p in self._participants:
            label = p["label"]
            color = p["color"]
            lines = label.split("\n")
            max_len = max(len(l) for l in lines)
            metrics = FONT_METRICS.get(self.font, FONT_METRICS["nunito"])
            box_w = max(120, max_len * 18 * metrics["char_width"] + 40)
            box_h = max(50, len(lines) * 18 * metrics["line_height"] + 24)

            stroke = COLORS.get(color, color)
            bg_key = BG_FOR_STROKE.get(color, "transparent")
            bg = COLORS.get(bg_key, "transparent")

            r = rectangle(p["x"], self.start_y, box_w, box_h,
                          color=color, roughness=self.roughness)
            participant_elements.append(r)

            # Centered text
            t = text(p["x"], self.start_y + (box_h - len(lines) * 18 * metrics["line_height"]) / 2,
                     label, font_size=18, font_family=self.font, color="black")
            t["width"] = box_w
            t["textAlign"] = "center"
            t["verticalAlign"] = "middle"
            t["containerId"] = r["id"]
            if r.get("boundElements") is None:
                r["boundElements"] = []
            r["boundElements"].append({"type": "text", "id": t["id"]})
            participant_text_elements.append(t)

            box_bottoms.append(self.start_y + box_h)

        # Calculate lifeline extent
        total_rows = self._current_row
        lifeline_bottom = self._row_y(total_rows) + 40

        # Lifelines (dashed vertical lines)
        lifeline_elements = []
        for p in self._participants:
            cx = self._participant_center_x(p["id"])
            # Find this participant's box bottom
            idx = self._participant_index[p["id"]]
            top_y = box_bottoms[idx]

            ll = line(cx, top_y, cx, lifeline_bottom, color="gray",
                      stroke_style="dashed", stroke_width=1, roughness=0)
            lifeline_elements.append(ll)

        # Groups (background rectangles)
        group_elements = []
        for g in self._groups:
            gy1 = self._row_y(g["start_row"]) - 20
            gy2 = self._row_y(g["end_row"]) + 20
            gx1 = self.start_x - 20
            gx2 = self.start_x + (len(self._participants) - 1) * self.participant_gap + 200
            gr = rectangle(gx1, gy1, gx2 - gx1, gy2 - gy1,
                           color="gray", fill=True, rounded=True,
                           opacity=10, stroke_width=1, stroke_style="dashed",
                           roughness=0)
            group_elements.append(gr)
            # Group label
            gl = text(gx1 + 8, gy1 + 4, g["label"],
                      font_size=14, font_family=self.font, color="gray")
            group_elements.append(gl)

        # Messages (arrows)
        arrow_elements = []
        arrow_label_elements = []
        note_elements = []

        for i, msg in enumerate(self._messages):
            row = i + 1
            y = self._row_y(row)

            if msg["type"] in ("call", "reply"):
                from_cx = self._participant_center_x(msg["from"])
                to_cx = self._participant_center_x(msg["to"])

                is_dashed = msg["type"] == "reply"
                stroke_style = "dashed" if is_dashed else "solid"

                dx = to_cx - from_cx
                dy = 0

                a = _base_element(
                    "arrow", from_cx, y,
                    abs(dx) or 1, 1,
                    stroke_color=COLORS.get("black", "#1e1e1e"),
                    bg_color="transparent",
                    roughness=self.roughness,
                    stroke_style=stroke_style,
                    stroke_width=2,
                )
                a.update({
                    "points": [[0, 0], [dx, 0]],
                    "startBinding": None,
                    "endBinding": None,
                    "startArrowhead": None,
                    "endArrowhead": "arrow",
                    "elbowed": False,
                    "roundness": {"type": 2},
                })
                arrow_elements.append(a)

                # Label above arrow
                if msg["label"]:
                    mid_x = from_cx + dx / 2
                    lbl = text(mid_x, y - 22, msg["label"],
                               font_size=14, font_family=self.font, color="black")
                    # Bind label to arrow
                    lbl["containerId"] = a["id"]
                    lbl["textAlign"] = "center"
                    if a.get("boundElements") is None:
                        a["boundElements"] = []
                    a["boundElements"].append({"type": "text", "id": lbl["id"]})
                    arrow_label_elements.append(lbl)

            elif msg["type"] == "self":
                cx = self._participant_center_x(msg["from"])
                loop_w = 60
                loop_h = 30

                # Outgoing arrow (right and down)
                a1 = _base_element(
                    "arrow", cx, y,
                    loop_w, loop_h,
                    stroke_color=COLORS.get("black", "#1e1e1e"),
                    bg_color="transparent",
                    roughness=self.roughness,
                    stroke_width=2,
                )
                a1.update({
                    "points": [[0, 0], [loop_w, 0], [loop_w, loop_h], [0, loop_h]],
                    "startBinding": None,
                    "endBinding": None,
                    "startArrowhead": None,
                    "endArrowhead": "arrow",
                    "elbowed": True,
                    "roundness": None,
                })
                arrow_elements.append(a1)

                if msg["label"]:
                    lbl = text(cx + loop_w + 8, y + loop_h / 2 - 10, msg["label"],
                               font_size=14, font_family=self.font, color="black")
                    arrow_label_elements.append(lbl)

            elif msg["type"] == "note":
                cx = self._participant_center_x(msg["from"])
                note_w = max(100, len(msg["label"]) * 14 * 0.55 + 30)
                note_h = 36

                if msg.get("position", "right") == "right":
                    nx = cx + 40
                else:
                    nx = cx - 40 - note_w

                nr = rectangle(nx, y - note_h / 2, note_w, note_h,
                               color="yellow", fill=True, roughness=self.roughness)
                note_elements.append(nr)

                nt = text(nx + 8, y - 8, msg["label"],
                          font_size=14, font_family=self.font, color="black")
                note_elements.append(nt)

        # Assemble in z-order: groups -> lifelines -> arrows -> participant boxes -> text -> labels -> notes
        elements = (group_elements + lifeline_elements + arrow_elements +
                    participant_elements + participant_text_elements +
                    arrow_label_elements + note_elements)

        return elements

    def to_dict(self) -> dict:
        return {
            "type": "excalidraw",
            "version": 2,
            "source": "https://excalidraw.com",
            "elements": self.build(),
            "appState": {
                "gridSize": 20,
                "gridStep": 5,
                "gridModeEnabled": False,
                "viewBackgroundColor": "#ffffff",
            },
            "files": {},
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def save(self, path) -> Path:
        path = Path(path)
        if not path.suffix:
            path = path.with_suffix(".excalidraw")
        path.write_text(self.to_json())
        return path
