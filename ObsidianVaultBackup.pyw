import json
import os
import shutil
import sys
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_NAME = "Obsidian Vault Backup"
APP_VERSION = "1.0.1"
APP_DIR_NAME = "ObsidianVaultBackup"


def config_dir() -> Path:
    if os.name == "nt":
        base = os.environ.get("APPDATA") or str(Path.home())
        p = Path(base) / APP_DIR_NAME
    else:
        p = Path.home() / f".{APP_DIR_NAME.lower()}"
    p.mkdir(parents=True, exist_ok=True)
    return p


CONFIG_FILE = config_dir() / "config.json"


def load_config() -> dict:
    try:
        if CONFIG_FILE.exists():
            with CONFIG_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
    except Exception:
        pass
    return {}


def save_config(data: dict) -> None:
    try:
        with CONFIG_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def same_file(src: Path, dst: Path) -> bool:
    """Confronto rapido: dimensione + data/ora di modifica."""
    try:
        s1 = src.stat()
        s2 = dst.stat()
        return s1.st_size == s2.st_size and s1.st_mtime_ns == s2.st_mtime_ns
    except OSError:
        return False


def list_source_files(source: Path) -> list[Path]:
    files: list[Path] = []
    for root, _, filenames in os.walk(source):
        root_path = Path(root)
        for name in filenames:
            files.append(root_path / name)
    return files


def ensure_not_nested(source: Path, destination: Path) -> tuple[bool, str]:
    """Evita che sorgente e destinazione si contengano a vicenda."""
    try:
        s = source.resolve()
        d = destination.resolve()
        if s == d:
            return False, "Il percorso sorgente e quello di destinazione coincidono."
        if d.is_relative_to(s):
            return False, "La cartella di destinazione non può trovarsi dentro la sorgente."
        if s.is_relative_to(d):
            return False, "La cartella sorgente non può trovarsi dentro la destinazione."
    except Exception:
        pass
    return True, ""


def copy_tree(source: Path, destination: Path, progress_cb, log_cb, stop_event: threading.Event) -> dict:
    source = source.resolve()
    destination.mkdir(parents=True, exist_ok=True)

    files = list_source_files(source)
    total = len(files)
    copied = 0
    skipped = 0
    failed = 0

    for root, dirs, _ in os.walk(source):
        rel_root = Path(root).relative_to(source)
        target_root = destination / rel_root
        target_root.mkdir(parents=True, exist_ok=True)
        for directory in dirs:
            (target_root / directory).mkdir(parents=True, exist_ok=True)

    for idx, src in enumerate(files, start=1):
        if stop_event.is_set():
            break

        rel = src.relative_to(source)
        dst = destination / rel
        progress_cb(idx - 1, total, str(rel))

        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists() and same_file(src, dst):
                skipped += 1
            else:
                shutil.copy2(src, dst)
                copied += 1
                log_cb(f"COPIATO  {rel}")
        except Exception as exc:
            failed += 1
            log_cb(f"ERRORE   {rel} -> {exc}")

        progress_cb(idx, total, str(rel))

    return {
        "total": total,
        "copied": copied,
        "skipped": skipped,
        "failed": failed,
        "cancelled": stop_event.is_set(),
    }


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("860x650")
        self.minsize(760, 560)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.stop_event = threading.Event()
        self.worker = None
        cfg = load_config()

        self.vault_var = tk.StringVar(value=cfg.get("vault", ""))
        self.backup_var = tk.StringVar(value=cfg.get("backup", ""))
        self.status_var = tk.StringVar(value="Pronto")
        self.current_var = tk.StringVar(value="")
        self.progress_var = tk.DoubleVar(value=0)

        self._build_ui()
        self._apply_style()

    def _apply_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("vista" if os.name == "nt" else "clam")
        except tk.TclError:
            pass

        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Sub.TLabel", font=("Segoe UI", 10))
        style.configure("Action.TButton", font=("Segoe UI", 11, "bold"), padding=(12, 10))

    def _build_ui(self):
        outer = ttk.Frame(self, padding=18)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="Obsidian Vault Backup", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            outer,
            text="Copia il Vault verso il backup e viceversa. Non elimina mai i file presenti nella destinazione.",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(2, 18))

        paths = ttk.LabelFrame(outer, text="Percorsi", padding=12)
        paths.pack(fill="x")
        paths.columnconfigure(1, weight=1)

        ttk.Label(paths, text="Vault locale:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=6)
        ttk.Entry(paths, textvariable=self.vault_var).grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Button(paths, text="Sfoglia…", command=self.choose_vault).grid(row=0, column=2, padx=(8, 0), pady=6)
        ttk.Button(
            paths,
            text="Apri",
            command=lambda: self.open_folder(self.vault_var.get()),
        ).grid(row=0, column=3, padx=(8, 0), pady=6)

        ttk.Label(paths, text="Cartella backup:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=6)
        ttk.Entry(paths, textvariable=self.backup_var).grid(row=1, column=1, sticky="ew", pady=6)
        ttk.Button(paths, text="Sfoglia…", command=self.choose_backup).grid(row=1, column=2, padx=(8, 0), pady=6)
        ttk.Button(
            paths,
            text="Apri",
            command=lambda: self.open_folder(self.backup_var.get()),
        ).grid(row=1, column=3, padx=(8, 0), pady=6)

        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=16)
        actions.columnconfigure((0, 1), weight=1)

        self.to_backup_btn = ttk.Button(
            actions,
            text="VAULT  →  BACKUP",
            style="Action.TButton",
            command=lambda: self.start_copy("backup"),
        )
        self.to_backup_btn.grid(row=0, column=0, sticky="ew", padx=(0, 7))

        self.to_vault_btn = ttk.Button(
            actions,
            text="BACKUP  →  VAULT",
            style="Action.TButton",
            command=lambda: self.start_copy("restore"),
        )
        self.to_vault_btn.grid(row=0, column=1, sticky="ew", padx=(7, 0))

        prog = ttk.LabelFrame(outer, text="Operazione", padding=12)
        prog.pack(fill="x")
        ttk.Label(prog, textvariable=self.status_var).pack(anchor="w")
        ttk.Progressbar(prog, variable=self.progress_var, maximum=100).pack(fill="x", pady=(8, 6))
        ttk.Label(prog, textvariable=self.current_var).pack(anchor="w")

        log_frame = ttk.LabelFrame(outer, text="Log", padding=8)
        log_frame.pack(fill="both", expand=True, pady=(16, 0))

        text_container = ttk.Frame(log_frame)
        text_container.pack(fill="both", expand=True)

        self.log = tk.Text(
            text_container,
            wrap="none",
            height=14,
            font=("Consolas", 9),
            state="disabled",
        )
        yscroll = ttk.Scrollbar(text_container, orient="vertical", command=self.log.yview)
        xscroll = ttk.Scrollbar(text_container, orient="horizontal", command=self.log.xview)
        self.log.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        self.log.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        text_container.rowconfigure(0, weight=1)
        text_container.columnconfigure(0, weight=1)

        footer = ttk.Frame(outer)
        footer.pack(fill="x", pady=(10, 0))

        self.cancel_btn = ttk.Button(
            footer,
            text="Annulla operazione",
            command=self.cancel_copy,
            state="disabled",
        )
        self.cancel_btn.pack(side="left")

        ttk.Button(footer, text="Pulisci log", command=self.clear_log).pack(side="right")

    def choose_vault(self):
        path = filedialog.askdirectory(title="Seleziona il Vault Obsidian")
        if path:
            self.vault_var.set(path)
            self.save_paths()

    def choose_backup(self):
        path = filedialog.askdirectory(title="Seleziona la cartella di backup")
        if path:
            self.backup_var.set(path)
            self.save_paths()

    def save_paths(self):
        save_config({
            "vault": self.vault_var.get().strip(),
            "backup": self.backup_var.get().strip(),
        })

    def open_folder(self, raw_path: str):
        raw_path = raw_path.strip()
        if not raw_path:
            messagebox.showwarning(APP_NAME, "Seleziona prima una cartella.")
            return

        path = Path(raw_path)
        if not path.exists():
            messagebox.showerror(APP_NAME, "La cartella non esiste.")
            return

        try:
            if os.name == "nt":
                os.startfile(str(path))
            elif sys.platform == "darwin":
                os.system(f'open "{path}"')
            else:
                os.system(f'xdg-open "{path}" >/dev/null 2>&1 &')
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"Impossibile aprire la cartella:\n{exc}")

    def validate_paths(self, mode: str):
        vault_raw = self.vault_var.get().strip()
        backup_raw = self.backup_var.get().strip()

        if not vault_raw or not backup_raw:
            messagebox.showwarning(APP_NAME, "Seleziona sia il Vault sia la cartella di backup.")
            return None

        vault = Path(vault_raw)
        backup = Path(backup_raw)
        source, destination = (vault, backup) if mode == "backup" else (backup, vault)

        if not source.exists() or not source.is_dir():
            messagebox.showerror(APP_NAME, f"La cartella sorgente non esiste:\n{source}")
            return None

        ok, msg = ensure_not_nested(source, destination)
        if not ok:
            messagebox.showerror(APP_NAME, msg)
            return None

        return source, destination

    def start_copy(self, mode: str):
        if self.worker and self.worker.is_alive():
            return

        validated = self.validate_paths(mode)
        if not validated:
            return

        source, destination = validated
        self.save_paths()

        if mode == "restore":
            answer = messagebox.askyesno(
                "Conferma ripristino",
                "Stai per copiare il BACKUP nel VAULT locale.\n\n"
                "I file con lo stesso nome possono essere sovrascritti con la versione del backup.\n"
                "Nessun file extra del Vault verrà eliminato.\n\n"
                "Vuoi continuare?",
                icon="warning",
            )
            if not answer:
                return

        self.stop_event.clear()
        self.progress_var.set(0)
        self.current_var.set("")

        direction = "Vault → Backup" if mode == "backup" else "Backup → Vault"
        self.status_var.set(f"Avvio: {direction}")
        self.append_log("")
        self.append_log(f"=== {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | {direction} ===")
        self.append_log(f"Sorgente:      {source}")
        self.append_log(f"Destinazione: {destination}")
        self.set_running(True)

        self.worker = threading.Thread(
            target=self._worker_copy,
            args=(source, destination, direction),
            daemon=True,
        )
        self.worker.start()

    def _worker_copy(self, source: Path, destination: Path, direction: str):
        try:
            result = copy_tree(
                source,
                destination,
                lambda done, total, current: self.after(
                    0,
                    self.update_progress,
                    done,
                    total,
                    current,
                ),
                lambda msg: self.after(0, self.append_log, msg),
                self.stop_event,
            )
            self.after(0, self.copy_done, result, direction)
        except Exception as exc:
            self.after(0, self.copy_failed, exc)

    def update_progress(self, done: int, total: int, current: str):
        percent = 100 if total == 0 else (done / total) * 100
        self.progress_var.set(percent)
        self.status_var.set(f"File elaborati: {done}/{total} ({percent:.0f}%)")
        self.current_var.set(current)

    def copy_done(self, result: dict, direction: str):
        self.set_running(False)
        self.current_var.set("")

        if result["cancelled"]:
            self.status_var.set("Operazione annullata")
            self.append_log("OPERAZIONE ANNULLATA")
            return

        self.progress_var.set(100)
        self.status_var.set("Operazione completata")

        summary = (
            f"Completato {direction}\n\n"
            f"File totali: {result['total']}\n"
            f"Copiati/aggiornati: {result['copied']}\n"
            f"Già aggiornati: {result['skipped']}\n"
            f"Errori: {result['failed']}"
        )

        self.append_log(
            f"RISULTATO: totali={result['total']}, copiati={result['copied']}, "
            f"già aggiornati={result['skipped']}, errori={result['failed']}"
        )

        if result["failed"]:
            messagebox.showwarning(APP_NAME, summary)
        else:
            messagebox.showinfo(APP_NAME, summary)

    def copy_failed(self, exc: Exception):
        self.set_running(False)
        self.status_var.set("Errore")
        self.append_log(f"ERRORE GENERALE: {exc}")
        messagebox.showerror(APP_NAME, f"Operazione non riuscita:\n{exc}")

    def cancel_copy(self):
        if self.worker and self.worker.is_alive():
            self.stop_event.set()
            self.status_var.set("Annullamento in corso…")

    def set_running(self, running: bool):
        state_actions = "disabled" if running else "normal"
        self.to_backup_btn.configure(state=state_actions)
        self.to_vault_btn.configure(state=state_actions)
        self.cancel_btn.configure(state="normal" if running else "disabled")

    def append_log(self, text: str):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def on_close(self):
        if self.worker and self.worker.is_alive():
            if not messagebox.askyesno(APP_NAME, "È in corso una copia. Vuoi chiudere comunque?"):
                return
            self.stop_event.set()

        self.save_paths()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
