from __future__ import annotations

import json
import os
import queue
import shutil
import sys
import threading
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tkinter import BOTH, END, LEFT, RIGHT, X, filedialog, messagebox
import tkinter as tk
from tkinter import ttk


def resource_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


ROOT = resource_root()
sys.path.insert(0, str(ROOT / "src"))

from itr_pipeline.engine import Pipeline  # noqa: E402

APP_TITLE = "ITR-status Desktop"
GENERIC_IR_PATTERN = (
    r"^(?P<base>[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*-IR-\d{5})"
    r"(?:-(?P<revision>\d{2}))?$"
)
DASHBOARD_FILES = (
    "index.html", "app.js", "styles.css", "guide.css", "customize.js", "settings.js"
)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *args: object) -> None:
        return


class DesktopApp:
    def __init__(self, window: tk.Tk):
        self.window = window
        self.events: queue.Queue[dict[str, object]] = queue.Queue()
        self.server: ThreadingHTTPServer | None = None
        self.server_thread: threading.Thread | None = None
        self.last_dashboard: Path | None = None
        self.running = False

        self.project_var = tk.StringVar(value="ITR Status Check")
        self.ledger_var = tk.StringVar()
        self.sheet_var = tk.StringVar()
        self.portal_mode_var = tk.StringVar(value="离线结果 JSON")
        self.portal_var = tk.StringVar()
        self.token_var = tk.StringVar()
        self.output_var = tk.StringVar(value=str(Path.home() / "ITR-status Workspace"))
        self.pattern_var = tk.StringVar(value=GENERIC_IR_PATTERN)
        self.state_var = tk.StringVar(value="等待开始")
        self.row_count_var = tk.StringVar(value="—")
        self.scan_count_var = tk.StringVar(value="—")
        self.change_count_var = tk.StringVar(value="—")
        self.error_count_var = tk.StringVar(value="—")
        self.progress_var = tk.DoubleVar(value=0)

        self._configure_window()
        self._configure_style()
        self._build_ui()
        self._load_demo()
        self.window.after(100, self._drain_events)
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

    def _configure_window(self) -> None:
        self.window.title(APP_TITLE)
        self.window.geometry("1040x760")
        self.window.minsize(900, 680)
        self.window.configure(bg="#0b1220")

    def _configure_style(self) -> None:
        style = ttk.Style(self.window)
        style.theme_use("clam")
        style.configure("Root.TFrame", background="#0b1220")
        style.configure("Panel.TFrame", background="#121d2f")
        style.configure("Card.TFrame", background="#17243a")
        style.configure("Title.TLabel", background="#0b1220", foreground="#f4f8ff", font=("Segoe UI Semibold", 24))
        style.configure("Subtitle.TLabel", background="#0b1220", foreground="#8da2bf", font=("Segoe UI", 10))
        style.configure("PanelTitle.TLabel", background="#121d2f", foreground="#dce8f8", font=("Segoe UI Semibold", 11))
        style.configure("Label.TLabel", background="#121d2f", foreground="#9db0ca", font=("Segoe UI", 9))
        style.configure("Hint.TLabel", background="#121d2f", foreground="#6f86a6", font=("Segoe UI", 8))
        style.configure("CardValue.TLabel", background="#17243a", foreground="#ffffff", font=("Segoe UI Semibold", 20))
        style.configure("CardName.TLabel", background="#17243a", foreground="#8ea4c3", font=("Segoe UI", 8))
        style.configure("Safety.TLabel", background="#12382f", foreground="#7ce7c2", padding=(10, 5), font=("Segoe UI Semibold", 9))
        style.configure("TEntry", fieldbackground="#0e1726", foreground="#eaf1fb", insertcolor="#ffffff", bordercolor="#263957", padding=7)
        style.configure("TCombobox", fieldbackground="#0e1726", foreground="#eaf1fb", arrowcolor="#76d7c4", padding=5)
        style.map("TCombobox", fieldbackground=[("readonly", "#0e1726")], foreground=[("readonly", "#eaf1fb")])
        style.configure("Primary.TButton", background="#26b99a", foreground="#06110f", padding=(18, 10), font=("Segoe UI Semibold", 10), borderwidth=0)
        style.map("Primary.TButton", background=[("active", "#51d8ba"), ("disabled", "#34524e")])
        style.configure("Secondary.TButton", background="#20314d", foreground="#dbe8f8", padding=(13, 8), borderwidth=0)
        style.map("Secondary.TButton", background=[("active", "#2c4265")])
        style.configure("Horizontal.TProgressbar", troughcolor="#17243a", background="#26b99a", bordercolor="#17243a", lightcolor="#26b99a", darkcolor="#26b99a")

    def _build_ui(self) -> None:
        root = ttk.Frame(self.window, style="Root.TFrame", padding=(28, 22))
        root.pack(fill=BOTH, expand=True)

        header = ttk.Frame(root, style="Root.TFrame")
        header.pack(fill=X, pady=(0, 18))
        heading = ttk.Frame(header, style="Root.TFrame")
        heading.pack(side=LEFT, fill=X, expand=True)
        ttk.Label(heading, text="ITR-status Desktop", style="Title.TLabel").pack(anchor="w")
        ttk.Label(heading, text="选台账 · 运行核查 · 看结果，不需要命令行", style="Subtitle.TLabel").pack(anchor="w", pady=(3, 0))
        ttk.Label(header, text="只读核查 · 不写回台账", style="Safety.TLabel").pack(side=RIGHT, anchor="n")

        body = ttk.Frame(root, style="Root.TFrame")
        body.pack(fill=BOTH, expand=True)
        left = ttk.Frame(body, style="Panel.TFrame", padding=20)
        left.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 12))
        right = ttk.Frame(body, style="Panel.TFrame", padding=20, width=310)
        right.pack(side=RIGHT, fill="y")
        right.pack_propagate(False)

        ttk.Label(left, text="运行设置", style="PanelTitle.TLabel").pack(anchor="w", pady=(0, 14))
        self._entry_row(left, "项目显示名称", self.project_var)
        self._path_row(left, "源台账（JSON / CSV / XLSX）", self.ledger_var, self._choose_ledger)
        self._entry_row(left, "Excel 工作表（留空使用当前表）", self.sheet_var)

        ttk.Label(left, text="查询来源", style="Label.TLabel").pack(anchor="w", pady=(3, 5))
        mode = ttk.Combobox(left, textvariable=self.portal_mode_var, values=("离线结果 JSON", "私有 HTTP JSON 网关"), state="readonly")
        mode.pack(fill=X, pady=(0, 8))
        mode.bind("<<ComboboxSelected>>", lambda _event: self._sync_mode())
        self.portal_label = ttk.Label(left, text="查询结果 JSON", style="Label.TLabel")
        self.portal_label.pack(anchor="w", pady=(3, 5))
        portal_row = ttk.Frame(left, style="Panel.TFrame")
        portal_row.pack(fill=X, pady=(0, 8))
        self.portal_entry = ttk.Entry(portal_row, textvariable=self.portal_var)
        self.portal_entry.pack(side=LEFT, fill=X, expand=True)
        self.portal_button = ttk.Button(portal_row, text="选择", style="Secondary.TButton", command=self._choose_portal)
        self.portal_button.pack(side=RIGHT, padx=(8, 0))
        self.token_frame = ttk.Frame(left, style="Panel.TFrame")
        ttk.Label(self.token_frame, text="令牌环境变量名（可留空）", style="Label.TLabel").pack(anchor="w", pady=(3, 5))
        ttk.Entry(self.token_frame, textvariable=self.token_var).pack(fill=X)

        self._path_row(left, "输出目录", self.output_var, self._choose_output, directory=True)
        ttk.Label(left, text="编号规则（正则，必须包含命名组 base）", style="Label.TLabel").pack(anchor="w", pady=(3, 5))
        ttk.Entry(left, textvariable=self.pattern_var).pack(fill=X, pady=(0, 5))
        ttk.Label(left, text="默认规则兼容常见的 ...-IR-00001 与可选修订后缀；可按组织规则修改。", style="Hint.TLabel").pack(anchor="w")

        actions = ttk.Frame(left, style="Panel.TFrame")
        actions.pack(fill=X, pady=(18, 0))
        self.run_button = ttk.Button(actions, text="开始核查", style="Primary.TButton", command=self._start_run)
        self.run_button.pack(side=LEFT)
        ttk.Button(actions, text="载入安全样例", style="Secondary.TButton", command=self._load_demo).pack(side=LEFT, padx=(8, 0))
        self.dashboard_button = ttk.Button(actions, text="打开仪表盘", style="Secondary.TButton", command=self._open_dashboard, state="disabled")
        self.dashboard_button.pack(side=RIGHT)

        ttk.Label(right, text="本次运行", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(right, textvariable=self.state_var, style="Subtitle.TLabel").pack(anchor="w", pady=(4, 12))
        ttk.Progressbar(right, variable=self.progress_var, maximum=100).pack(fill=X, pady=(0, 15))

        cards = ttk.Frame(right, style="Panel.TFrame")
        cards.pack(fill=X)
        self._card(cards, "台账行数", self.row_count_var, 0, 0)
        self._card(cards, "已查询", self.scan_count_var, 0, 1)
        self._card(cards, "变更建议", self.change_count_var, 1, 0)
        self._card(cards, "未解决", self.error_count_var, 1, 1)

        ttk.Label(right, text="运行日志", style="PanelTitle.TLabel").pack(anchor="w", pady=(18, 7))
        self.log = tk.Text(right, height=14, bg="#0e1726", fg="#b9c8dc", insertbackground="#ffffff", relief="flat", padx=10, pady=9, font=("Cascadia Mono", 8), wrap="word")
        self.log.pack(fill=BOTH, expand=True)
        ttk.Button(right, text="打开产物目录", style="Secondary.TButton", command=self._open_output).pack(fill=X, pady=(10, 0))
        self._sync_mode()

    def _entry_row(self, parent: ttk.Frame, label: str, variable: tk.StringVar) -> None:
        ttk.Label(parent, text=label, style="Label.TLabel").pack(anchor="w", pady=(3, 5))
        ttk.Entry(parent, textvariable=variable).pack(fill=X, pady=(0, 8))

    def _path_row(self, parent: ttk.Frame, label: str, variable: tk.StringVar, command, directory: bool = False) -> None:
        ttk.Label(parent, text=label, style="Label.TLabel").pack(anchor="w", pady=(3, 5))
        row = ttk.Frame(parent, style="Panel.TFrame")
        row.pack(fill=X, pady=(0, 8))
        ttk.Entry(row, textvariable=variable).pack(side=LEFT, fill=X, expand=True)
        ttk.Button(row, text="选择", style="Secondary.TButton", command=command).pack(side=RIGHT, padx=(8, 0))

    def _card(self, parent: ttk.Frame, name: str, variable: tk.StringVar, row: int, column: int) -> None:
        card = ttk.Frame(parent, style="Card.TFrame", padding=12)
        card.grid(row=row, column=column, sticky="nsew", padx=(0 if column == 0 else 5, 5 if column == 0 else 0), pady=5)
        ttk.Label(card, textvariable=variable, style="CardValue.TLabel").pack(anchor="w")
        ttk.Label(card, text=name, style="CardName.TLabel").pack(anchor="w")
        parent.columnconfigure(column, weight=1)

    def _choose_ledger(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Ledger", "*.json *.csv *.xlsx"), ("All files", "*.*")])
        if path:
            self.ledger_var.set(path)

    def _choose_portal(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("All files", "*.*")])
        if path:
            self.portal_var.set(path)

    def _choose_output(self) -> None:
        path = filedialog.askdirectory()
        if path:
            self.output_var.set(path)

    def _load_demo(self) -> None:
        self.project_var.set("ITR-status 安全样例")
        self.ledger_var.set(str(ROOT / "sample_data" / "ledger.json"))
        self.portal_mode_var.set("离线结果 JSON")
        self.portal_var.set(str(ROOT / "sample_data" / "portal_results.json"))
        self.pattern_var.set(r"^(?P<base>DEMO-GQC-IR-\d{5})(?:-(?P<revision>\d{2}))?$")
        self._sync_mode()
        self._append_log("已载入合成数据样例，可直接点击“开始核查”。")

    def _sync_mode(self) -> None:
        offline = self.portal_mode_var.get() == "离线结果 JSON"
        self.portal_label.configure(text="查询结果 JSON" if offline else "私有 JSON 网关地址")
        self.portal_button.configure(state="normal" if offline else "disabled")
        if offline:
            self.token_frame.pack_forget()
        else:
            self.token_frame.pack(fill=X, pady=(0, 8), before=self.portal_label.master.winfo_children()[-5] if False else None)

    def _build_config(self, output: Path) -> Path:
        ledger = Path(self.ledger_var.get()).expanduser().resolve()
        if not ledger.is_file():
            raise ValueError("请选择存在的源台账文件。")
        suffix = ledger.suffix.lower()
        adapters = {".json": "json-ledger", ".csv": "csv-ledger", ".xlsx": "xlsx-ledger"}
        if suffix not in adapters:
            raise ValueError("台账只支持 JSON、CSV 或 XLSX。")
        pattern = self.pattern_var.get().strip()
        import re
        compiled = re.compile(pattern)
        if "base" not in compiled.groupindex:
            raise ValueError("编号规则必须包含命名组 (?P<base>...)。")

        if self.portal_mode_var.get() == "离线结果 JSON":
            portal = Path(self.portal_var.get()).expanduser().resolve()
            if not portal.is_file():
                raise ValueError("请选择存在的查询结果 JSON。")
            crawler = {"adapter": "fixture", "path": str(portal)}
        else:
            crawler = {"adapter": "http-json", "base_url": self.portal_var.get().strip(), "token_env": self.token_var.get().strip()}

        dashboard = output / "dashboard"
        artifacts = output / "artifacts"
        config = {
            "project": {
                "name": self.project_var.get().strip() or "ITR Status Check",
                "name_zh": self.project_var.get().strip() or "ITR 状态核查",
                "description": "Local read-only inspection status run.",
                "description_zh": "本地只读报验状态核查。",
            },
            "source": {"adapter": adapters[suffix], "path": str(ledger), "sheet": self.sheet_var.get().strip()},
            "crawler": crawler,
            "rules": {
                "skip_current_statuses": ["CODE-1", "CODE-5", "N/A", "NA", "NO", ""],
                "identity_pattern": pattern,
            },
            "writeback": {"enabled": False},
            "report": {"output": str(dashboard / "data" / "dashboard.json"), "artifact_dir": str(artifacts)},
        }
        state_dir = output / ".itr-status"
        state_dir.mkdir(parents=True, exist_ok=True)
        config_path = state_dir / "last-run.json"
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return config_path

    def _copy_dashboard(self, output: Path) -> Path:
        destination = output / "dashboard"
        destination.mkdir(parents=True, exist_ok=True)
        for name in DASHBOARD_FILES:
            shutil.copy2(ROOT / "public" / name, destination / name)
        (destination / "data").mkdir(exist_ok=True)
        return destination

    def _start_run(self) -> None:
        if self.running:
            return
        try:
            output = Path(self.output_var.get()).expanduser().resolve()
            output.mkdir(parents=True, exist_ok=True)
            self._copy_dashboard(output)
            config_path = self._build_config(output)
        except Exception as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return
        self.running = True
        self.run_button.configure(state="disabled")
        self.dashboard_button.configure(state="disabled")
        self.progress_var.set(0)
        self.state_var.set("正在预检…")
        for variable in (self.row_count_var, self.scan_count_var, self.change_count_var, self.error_count_var):
            variable.set("—")
        self.log.delete("1.0", END)
        self._append_log("安全边界：只读运行，writeback.enabled=false。")
        thread = threading.Thread(target=self._run_pipeline, args=(config_path, output), daemon=True)
        thread.start()

    def _run_pipeline(self, config_path: Path, output: Path) -> None:
        try:
            result = Pipeline(ROOT, config_path, observer=self.events.put).run()
            self.events.put({"kind": "result", "result": result, "output": output})
        except Exception as exc:
            self.events.put({"kind": "fatal", "message": str(exc)})

    def _drain_events(self) -> None:
        try:
            while True:
                event = self.events.get_nowait()
                kind = event.get("kind")
                if kind == "phase":
                    self.state_var.set(str(event.get("message", "")))
                    self._append_log(f"[{str(event.get('status', '')).upper()}] {event.get('message', '')}")
                elif kind == "progress":
                    current = int(event.get("current", 0))
                    total = max(1, int(event.get("total", 1)))
                    self.progress_var.set(current / total * 100)
                    self.state_var.set(f"正在核查 {current}/{total} · {event.get('itr_id', '')}")
                elif kind == "error":
                    self._append_log(f"[WARN] {event.get('itr_id', '')}: {event.get('message', '')}")
                elif kind == "result":
                    self._finish_run(event)
                elif kind == "fatal":
                    self._fail_run(str(event.get("message", "未知错误")))
        except queue.Empty:
            pass
        self.window.after(100, self._drain_events)

    def _finish_run(self, event: dict[str, object]) -> None:
        result = event["result"]
        assert isinstance(result, dict)
        summary = result["summary"]
        self.row_count_var.set(str(summary["source_rows"]))
        self.scan_count_var.set(str(summary["scanned"]))
        self.change_count_var.set(str(summary["changes"]))
        self.error_count_var.set(str(summary["unresolved"]))
        self.progress_var.set(100)
        self.state_var.set("完成（有待处理项）" if summary["unresolved"] else "核查完成")
        self.last_dashboard = Path(event["output"]) / "dashboard"
        self.running = False
        self.run_button.configure(state="normal")
        self.dashboard_button.configure(state="normal")
        self._append_log("运行结束。已生成仪表盘、汇总、变更建议和错误清单。")

    def _fail_run(self, message: str) -> None:
        self.running = False
        self.run_button.configure(state="normal")
        self.state_var.set("运行失败，未写回")
        self._append_log(f"[STOP] {message}")
        messagebox.showerror(APP_TITLE, f"运行已安全停止：\n\n{message}")

    def _append_log(self, text: str) -> None:
        self.log.insert(END, text + "\n")
        self.log.see(END)

    def _start_dashboard_server(self) -> str:
        assert self.last_dashboard is not None
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        handler = partial(QuietHandler, directory=str(self.last_dashboard))
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
        port = self.server.server_address[1]
        return f"http://127.0.0.1:{port}/?lang=zh"

    def _open_dashboard(self) -> None:
        if not self.last_dashboard:
            messagebox.showinfo(APP_TITLE, "请先完成一次核查。")
            return
        webbrowser.open(self._start_dashboard_server())

    def _open_output(self) -> None:
        output = Path(self.output_var.get()).expanduser()
        output.mkdir(parents=True, exist_ok=True)
        os.startfile(output)

    def _on_close(self) -> None:
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        self.window.destroy()


def main() -> int:
    window = tk.Tk()
    DesktopApp(window)
    window.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
