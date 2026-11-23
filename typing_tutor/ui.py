"""Tkinter window, drawing, keyboard controls, and live statistics."""

from __future__ import annotations

import math
import time
import tkinter as tk

from . import theme
from .engine import GameEngine
from .models import GameState


def rounded_rectangle(
    canvas: tk.Canvas, x1: float, y1: float, x2: float, y2: float, radius: float, **options: object
) -> None:
    """Draw a smooth, filled rounded rectangle on a Tkinter canvas."""
    radius = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
    points = [
        x1 + radius,
        y1,
        x2 - radius,
        y1,
        x2,
        y1,
        x2,
        y1 + radius,
        x2,
        y2 - radius,
        x2,
        y2,
        x2 - radius,
        y2,
        x1 + radius,
        y2,
        x1,
        y2,
        x1,
        y2 - radius,
        x1,
        y1 + radius,
        x1,
        y1,
    ]
    canvas.create_polygon(points, smooth=True, splinesteps=12, **options)


class TypingTutorApp:
    """Build and update the visual game, delegating rules to GameEngine."""

    def __init__(self, root: tk.Tk | None = None) -> None:
        self.root = root or tk.Tk()
        self.engine = GameEngine()
        self.last_frame = time.monotonic()
        self.feedback = ""
        self.feedback_until = 0.0

        self.root.title("Typing Tutor • Data Structures Game")
        self.root.geometry("1120x720")
        self.root.minsize(920, 620)
        self.root.configure(bg=theme.BACKGROUND)
        self.root.bind("<KeyPress>", self._on_key)

        self._build_interface()
        self._refresh_labels()
        self.root.after(40, self._frame)

    def run(self) -> None:
        self.root.mainloop()

    def _build_interface(self) -> None:
        outer = tk.Frame(self.root, bg=theme.BACKGROUND, padx=28, pady=22)
        outer.pack(fill="both", expand=True)

        header = tk.Frame(outer, bg=theme.BACKGROUND)
        header.pack(fill="x", pady=(0, 18))
        left_title = tk.Frame(header, bg=theme.BACKGROUND)
        left_title.pack(side="left")
        tk.Label(
            left_title,
            text="KEY / QUEST",
            fg=theme.ACCENT,
            bg=theme.BACKGROUND,
            font=(theme.FONT, 12, "bold"),
        ).pack(anchor="w")
        tk.Label(
            left_title,
            text="Typing Tutor",
            fg=theme.TEXT,
            bg=theme.BACKGROUND,
            font=(theme.FONT, 29, "bold"),
        ).pack(anchor="w", pady=(1, 0))
        tk.Label(
            left_title,
            text="Catch the falling keys before they cross the line.",
            fg=theme.MUTED,
            bg=theme.BACKGROUND,
            font=(theme.FONT, 12),
        ).pack(anchor="w", pady=(3, 0))

        right_title = tk.Frame(header, bg=theme.BACKGROUND)
        right_title.pack(side="right", anchor="e")
        self.time_label = tk.Label(
            right_title,
            text="01:00",
            fg=theme.TEXT,
            bg=theme.BACKGROUND,
            font=(theme.FONT, 31, "bold"),
        )
        self.time_label.pack(anchor="e")
        tk.Label(
            right_title,
            text="TIME LEFT",
            fg=theme.MUTED,
            bg=theme.BACKGROUND,
            font=(theme.FONT, 10, "bold"),
        ).pack(anchor="e")

        body = tk.Frame(outer, bg=theme.BACKGROUND)
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, minsize=264)
        body.grid_rowconfigure(0, weight=1)

        stage_frame = tk.Frame(body, bg=theme.PANEL, padx=2, pady=2)
        stage_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        self.canvas = tk.Canvas(stage_frame, bg=theme.STAGE, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _event: self._draw())

        sidebar = tk.Frame(body, bg=theme.PANEL, padx=20, pady=20)
        sidebar.grid(row=0, column=1, sticky="nsew")
        tk.Label(
            sidebar,
            text="LIVE STATS",
            bg=theme.PANEL,
            fg=theme.ACCENT,
            font=(theme.FONT, 11, "bold"),
        ).pack(anchor="w", pady=(0, 17))

        self.stat_labels = {}
        for name, initial in (
            ("HITS", "0"),
            ("MISSES", "0"),
            ("KEY PRESSES", "0"),
            ("ACCURACY", "0%"),
            ("ON SCREEN", "0"),
        ):
            row = tk.Frame(sidebar, bg=theme.PANEL)
            row.pack(fill="x", pady=7)
            tk.Label(
                row, text=name, fg=theme.MUTED, bg=theme.PANEL, font=(theme.FONT, 10, "bold")
            ).pack(side="left")
            value = tk.Label(
                row, text=initial, fg=theme.TEXT, bg=theme.PANEL, font=(theme.FONT, 17, "bold")
            )
            value.pack(side="right")
            self.stat_labels[name] = value

        tk.Frame(sidebar, bg=theme.LINE, height=1).pack(fill="x", pady=17)
        tk.Label(
            sidebar,
            text="UP NEXT  ·  QUEUE",
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(theme.FONT, 10, "bold"),
        ).pack(anchor="w")
        self.next_label = tk.Label(
            sidebar, text="—", bg=theme.PANEL, fg=theme.GOLD, font=(theme.FONT, 20, "bold")
        )
        self.next_label.pack(anchor="w", pady=(9, 18))

        self.start_button = tk.Button(
            sidebar,
            text="Start Game",
            command=self._start,
            bg=theme.ACCENT,
            fg=theme.BACKGROUND,
            activebackground="#77EBD6",
            activeforeground=theme.BACKGROUND,
            relief="flat",
            bd=0,
            padx=17,
            pady=12,
            font=(theme.FONT, 13, "bold"),
            cursor="hand2",
        )
        self.start_button.pack(fill="x", pady=(0, 10))
        tk.Button(
            sidebar,
            text="Exit",
            command=self.root.destroy,
            bg=theme.PANEL_LIGHT,
            fg=theme.TEXT,
            activebackground=theme.LINE,
            activeforeground=theme.TEXT,
            relief="flat",
            bd=0,
            padx=17,
            pady=9,
            font=(theme.FONT, 11),
            cursor="hand2",
        ).pack(fill="x")

        help_text = "HOW TO PLAY\n\nPress the exact key shown.\nUppercase needs Shift.\nEsc ends the current game."
        tk.Label(
            sidebar,
            text=help_text,
            justify="left",
            anchor="sw",
            fg=theme.MUTED,
            bg=theme.PANEL,
            font=(theme.FONT, 10),
            wraplength=220,
        ).pack(side="bottom", anchor="w", pady=(18, 0))

        footer = tk.Frame(outer, bg=theme.BACKGROUND)
        footer.pack(fill="x", pady=(15, 0))
        self.message_label = tk.Label(
            footer,
            text="Ready when you are.",
            fg=theme.MUTED,
            bg=theme.BACKGROUND,
            font=(theme.FONT, 11),
        )
        self.message_label.pack(side="left")
        tk.Label(
            footer,
            text="a–z  ·  A–Z  ·  0–9",
            fg=theme.MUTED,
            bg=theme.BACKGROUND,
            font=(theme.FONT, 11),
        ).pack(side="right")

    def _start(self) -> None:
        self.engine.start()
        self.last_frame = time.monotonic()
        self.feedback = ""
        self.start_button.configure(text="Restart Game")
        self.message_label.configure(text="Game on — type the falling characters!", fg=theme.ACCENT)
        self.root.focus_set()
        self._refresh_labels()
        self._draw()

    def _on_key(self, event: tk.Event) -> None:
        if self.engine.state != GameState.PLAYING:
            return
        if event.keysym == "Escape":
            self.engine.stop()
            self.message_label.configure(
                text="Session ended. Press Restart Game to try again.", fg=theme.MUTED
            )
            self._draw()
            return

        if event.keysym in (
            "Shift_L",
            "Shift_R",
            "Control_L",
            "Control_R",
            "Alt_L",
            "Alt_R",
            "Meta_L",
            "Meta_R",
        ):
            return
        if not event.char or not event.char.isprintable():
            return
        hit = self.engine.press(event.char)
        self.feedback = "NICE HIT" if hit else "TRY AGAIN"
        self.feedback_until = time.monotonic() + 0.45
        self.message_label.configure(
            text="Nice hit!" if hit else "That key is not on screen yet.",
            fg=theme.ACCENT if hit else theme.WARNING,
        )
        self._refresh_labels()
        self._draw()

    def _frame(self) -> None:
        now = time.monotonic()
        delta = now - self.last_frame
        self.last_frame = now
        if self.engine.state == GameState.PLAYING:
            self.engine.update(delta)
            self._refresh_labels()
            self._draw()
            if self.engine.state == GameState.FINISHED:
                self.message_label.configure(
                    text="Time up! Press Restart Game for another round.",
                    fg=theme.GOLD,
                )
        self.root.after(33, self._frame)

    def _refresh_labels(self) -> None:
        stats = self.engine.stats
        values = {
            "HITS": str(stats.hits),
            "MISSES": str(stats.misses),
            "KEY PRESSES": str(stats.key_presses),
            "ACCURACY": f"{stats.accuracy:.0f}%",
            "ON SCREEN": str(len(self.engine.active)),
        }
        for name, value in values.items():
            self.stat_labels[name].configure(text=value)
        seconds = math.ceil(self.engine.time_left)
        self.time_label.configure(text=f"{seconds // 60:02d}:{seconds % 60:02d}")
        self.next_label.configure(text="  ".join(list(self.engine.upcoming)[:5]) or "—")

    def _draw(self) -> None:
        canvas = self.canvas
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width < 20 or height < 20:
            return
        canvas.delete("all")

        # Quiet grid keeps the play area readable while giving it depth.
        for x in range(55, width, 85):
            canvas.create_line(x, 0, x, height, fill="#18283B")
        for y in range(55, height, 85):
            canvas.create_line(0, y, width, y, fill="#18283B")
        canvas.create_text(
            25, 27, anchor="w", text="PLAY AREA", fill=theme.MUTED, font=(theme.FONT, 10, "bold")
        )
        canvas.create_text(
            width - 25,
            27,
            anchor="e",
            text="60 SECOND ROUND",
            fill=theme.MUTED,
            font=(theme.FONT, 10, "bold"),
        )

        dead_y = int(height * self.engine.settings.dead_bar_y)
        canvas.create_rectangle(0, dead_y, width, height, fill="#1C2232", outline="")
        canvas.create_line(0, dead_y, width, dead_y, fill=theme.WARNING, width=4)
        canvas.create_text(
            width / 2,
            dead_y + 25,
            text="D E A D   B A R",
            fill=theme.WARNING,
            font=(theme.FONT, 11, "bold"),
        )

        for character in self.engine.active:
            x = character.x * width
            y = character.y * height
            if y < -35:
                continue
            label_width = 54 if character.value.isupper() else 50
            rounded_rectangle(
                canvas,
                x - label_width / 2 + 3,
                y - 21 + 4,
                x + label_width / 2 + 3,
                y + 21 + 4,
                12,
                fill="#07111E",
                outline="",
            )
            rounded_rectangle(
                canvas,
                x - label_width / 2,
                y - 21,
                x + label_width / 2,
                y + 21,
                12,
                fill=theme.PANEL_LIGHT,
                outline=theme.ACCENT,
                width=2,
            )
            canvas.create_text(
                x, y, text=character.value, fill=theme.TEXT, font=(theme.FONT, 20, "bold")
            )

        if self.engine.state != GameState.PLAYING:
            self._draw_overlay(width, height, dead_y)
        elif time.monotonic() < self.feedback_until:
            color = theme.ACCENT if self.feedback == "NICE HIT" else theme.WARNING
            canvas.create_text(
                width / 2, 83, text=self.feedback, fill=color, font=(theme.FONT, 14, "bold")
            )

    def _draw_overlay(self, width: int, height: int, dead_y: int) -> None:
        canvas = self.canvas
        card_width = min(460, width - 50)
        left = (width - card_width) / 2
        center_y = dead_y / 2
        rounded_rectangle(
            canvas,
            left,
            center_y - 115,
            left + card_width,
            center_y + 115,
            18,
            fill=theme.PANEL,
            outline=theme.LINE,
            width=2,
        )
        state = self.engine.state
        if state == GameState.READY:
            title = "Ready to type?"
            subtitle = "Press Start Game to begin your 60 second round."
        elif state == GameState.FINISHED:
            title = "Time's up!"
            subtitle = f"{self.engine.stats.hits} hits  •  {self.engine.stats.misses} misses  •  {self.engine.stats.accuracy:.0f}% accuracy"
        else:
            title = "Session ended"
            subtitle = f"{self.engine.stats.hits} hits  •  {self.engine.stats.misses} misses  •  {self.engine.stats.accuracy:.0f}% accuracy"
        canvas.create_text(
            width / 2, center_y - 38, text=title, fill=theme.TEXT, font=(theme.FONT, 27, "bold")
        )
        canvas.create_text(
            width / 2, center_y + 8, text=subtitle, fill=theme.MUTED, font=(theme.FONT, 12)
        )
        canvas.create_text(
            width / 2,
            center_y + 52,
            text="Use your keyboard  •  Match uppercase with Shift",
            fill=theme.ACCENT,
            font=(theme.FONT, 11),
        )
