"""
Simple desktop control panel for the bot.

This window has no trading logic of its own -- it starts/stops
scraper.py and trader.py as separate processes (they open their own
Chrome/Selenium session) and just displays what's already in the CSV
files bot/positions.py reads and writes, and lets you edit the risk
profile bot/risk_config.py reads from .env.
"""
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, ttk

from dotenv import set_key

import pnl_graph
import positions
import risk_config

BOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = positions.PROJECT_ROOT
ICON_DIR = os.path.join(PROJECT_ROOT, "assets", "icons")
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")


class BotGui:

    def __init__(self, root):
        self.root = root
        self.root.title("New List Shitcoin Bot")
        self.root.minsize(520, 480)
        self._set_icon()

        self.scraper_process = None
        self.trader_process = None

        self._build_header()
        self._build_controls()
        self._build_risk_profile()
        self._build_positions()
        self._build_chart()

        self.refresh()

    def _set_icon(self):
        try:
            self.root.iconbitmap(os.path.join(ICON_DIR, "sb.ico"))
        except Exception:
            pass

    def _build_header(self):
        try:
            self.logo_image = tk.PhotoImage(file=os.path.join(ICON_DIR, "app-icon.png")).subsample(5, 5)
            ttk.Label(self.root, image=self.logo_image).pack(pady=5)
        except Exception:
            pass

    def _build_controls(self):
        frame = ttk.LabelFrame(self.root, text="Bots")
        frame.pack(fill="x", padx=10, pady=5)

        self.scraper_status = tk.StringVar(value="stopped")
        self.trader_status = tk.StringVar(value="stopped")

        ttk.Button(frame, text="Start scraper", command=self.start_scraper).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Stop scraper", command=self.stop_scraper).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(frame, textvariable=self.scraper_status).grid(row=0, column=2, padx=5, sticky="w")

        ttk.Button(frame, text="Start trader", command=self.start_trader).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(frame, text="Stop trader", command=self.stop_trader).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(frame, textvariable=self.trader_status).grid(row=1, column=2, padx=5, sticky="w")

        frame.columnconfigure(2, weight=1)

    def _build_risk_profile(self):
        frame = ttk.LabelFrame(self.root, text="Risk profile")
        frame.pack(fill="x", padx=10, pady=5)

        profile = risk_config.get_risk_profile()

        ttk.Label(frame, text="Min spend per coin (USD)").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.min_spend_var = tk.StringVar(value=str(profile["min_spend_usd"]))
        ttk.Entry(frame, textvariable=self.min_spend_var, width=10).grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Max spend per coin (USD)").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.max_spend_var = tk.StringVar(value=str(profile["max_spend_usd"]))
        ttk.Entry(frame, textvariable=self.max_spend_var, width=10).grid(row=1, column=1, padx=5)

        ttk.Button(frame, text="Save", command=self.save_risk_profile).grid(row=0, column=2, rowspan=2, padx=10)
        ttk.Label(frame, text="Picked up by the trader on its next loop, no restart needed").grid(
            row=2, column=0, columnspan=3, padx=5, pady=(0, 5), sticky="w"
        )

    def _build_positions(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)

        open_tab = ttk.Frame(notebook)
        sold_tab = ttk.Frame(notebook)
        notebook.add(open_tab, text="Open positions")
        notebook.add(sold_tab, text="Sold")

        open_columns = ("name", "buy_price", "peak_gain")
        self.open_tree = ttk.Treeview(open_tab, columns=open_columns, show="headings", height=8)
        for col, label in zip(open_columns, ("Name", "Buy price (USD)", "Peak gain %")):
            self.open_tree.heading(col, text=label)
        self.open_tree.pack(fill="both", expand=True)

        sold_columns = ("name", "roi", "reason")
        self.sold_tree = ttk.Treeview(sold_tab, columns=sold_columns, show="headings", height=8)
        for col, label in zip(sold_columns, ("Name", "ROI %", "Reason")):
            self.sold_tree.heading(col, text=label)
        self.sold_tree.pack(fill="both", expand=True)

        ttk.Button(self.root, text="Refresh", command=self.refresh).pack(pady=(0, 5))

    def _build_chart(self):
        frame = ttk.LabelFrame(self.root, text="Weekly PNL")
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(frame, text="Generate chart", command=self.generate_chart).pack(side="left", padx=5, pady=5)
        self.chart_status = tk.StringVar(value="not generated yet")
        ttk.Label(frame, textvariable=self.chart_status).pack(side="left", padx=5)

    def start_scraper(self):
        if self.scraper_process and self.scraper_process.poll() is None:
            return
        self.scraper_process = subprocess.Popen([sys.executable, os.path.join(BOT_DIR, "scraper.py")])
        self.scraper_status.set(f"running (pid {self.scraper_process.pid})")

    def stop_scraper(self):
        if self.scraper_process and self.scraper_process.poll() is None:
            self.scraper_process.terminate()
        self.scraper_status.set("stopped")

    def start_trader(self):
        if self.trader_process and self.trader_process.poll() is None:
            return
        self.trader_process = subprocess.Popen([sys.executable, os.path.join(BOT_DIR, "trader.py")])
        self.trader_status.set(f"running (pid {self.trader_process.pid})")

    def stop_trader(self):
        if self.trader_process and self.trader_process.poll() is None:
            self.trader_process.terminate()
        self.trader_status.set("stopped")

    def save_risk_profile(self):
        try:
            min_spend = float(self.min_spend_var.get())
            max_spend = float(self.max_spend_var.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Min/max spend must be numbers.")
            return

        if not os.path.isfile(ENV_PATH):
            open(ENV_PATH, "a").close()

        set_key(ENV_PATH, "MIN_SPEND_PER_COIN_USD", str(min_spend))
        set_key(ENV_PATH, "MAX_SPEND_PER_COIN_USD", str(max_spend))
        messagebox.showinfo("Saved", "Risk profile saved to .env")

    def refresh(self):
        self.open_tree.delete(*self.open_tree.get_children())
        for position in positions.load_open_positions():
            self.open_tree.insert("", "end", values=(
                position["Name"], position["BuyPriceUsd"], position["PeakGainPct"],
            ))

        self.sold_tree.delete(*self.sold_tree.get_children())
        for position in reversed(positions.load_sold_positions()):
            self.sold_tree.insert("", "end", values=(
                position["Name"], position["RoiPct"], position["SellReason"],
            ))

    def generate_chart(self):
        path = pnl_graph.generate_weekly_chart()
        if path:
            self.chart_status.set(f"saved to {path}")
        else:
            self.chart_status.set("no sold positions in the last 7 days")


def main():
    root = tk.Tk()
    BotGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
