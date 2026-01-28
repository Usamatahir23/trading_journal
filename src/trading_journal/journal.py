"""
Main Trading Journal class
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from collections import defaultdict
from typing import List, Dict

from .calculator import TradeCalculator
from .models import Trade
from .database import DatabaseService


class TradingJournal:
    """Main Trading Journal application for Gold (XAU/USD)"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Trading Journal - Gold (XAU/USD)")
        self.root.geometry("1600x900")
        
        # Initialize database
        self.db = DatabaseService()
        
        # Load trades from database
        self.trades: List[Trade] = self.db.load_trades() if self.db.is_connected() else []
        
        # Extract unique strategies from loaded trades
        self.strategies = list(set([trade.strategy for trade in self.trades])) if self.trades else ["Strategy 1"]
        if not self.strategies:
            self.strategies = ["Strategy 1"]
        
        # Account balance: start at 10000, then add/subtract each trade's P/L so it stays current
        initial_balance = 10000.0
        self.account_balance = initial_balance + sum(t.usd_pl for t in self.trades)
        
        # Initialize calculator
        self.calculator = TradeCalculator(pip_value=0.1, pip_value_usd=1.0)
        
        # Calculated values storage
        self.calculated_tp = None
        self.calculated_lot_size = None
        self.calculated_risk_amount = None
        
        self.setup_ui()
        
        # Load and display trades if any
        if self.trades:
            self.update_table()
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Strategy and Settings frame
        self._setup_strategy_frame(main_frame)
        
        # Trade Entry frame
        self._setup_trade_entry_frame(main_frame)
        
        # Quick input frame
        self._setup_quick_input_frame(main_frame)
        
        # Table frame
        self._setup_table_frame(main_frame)
        
        # Summary frame
        self._setup_summary_frame(main_frame)
        
        # Delete button
        delete_button = ttk.Button(main_frame, text="Delete Selected Trade", command=self.delete_trade)
        delete_button.grid(row=5, column=0, columnspan=2, pady=6)
    
    def _setup_strategy_frame(self, parent):
        """Setup strategy and settings frame"""
        top_frame = ttk.LabelFrame(parent, text="Strategy & Settings", padding=(8, 6))
        top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 6))
        PAD_L, PAD_R = 2, 4  # tight spacing between label and field
        
        ttk.Label(top_frame, text="Strategy:").grid(row=0, column=0, padx=(6, PAD_L), pady=3, sticky=tk.W)
        self.strategy_var = tk.StringVar(value=self.strategies[0])
        self.strategy_combo = ttk.Combobox(top_frame, textvariable=self.strategy_var,
                                          values=self.strategies, width=18, state="readonly")
        self.strategy_combo.grid(row=0, column=1, padx=(PAD_R, 6), pady=3)
        self.strategy_combo.bind('<<ComboboxSelected>>', self.on_strategy_change)
        
        add_strategy_btn = ttk.Button(top_frame, text="Add Strategy", command=self.add_strategy)
        add_strategy_btn.grid(row=0, column=2, padx=4, pady=3)
        
        ttk.Label(top_frame, text="Account Balance:").grid(row=0, column=3, padx=(6, PAD_L), pady=3, sticky=tk.W)
        self.account_balance_var = tk.StringVar(value=str(round(self.account_balance, 2)))
        ttk.Entry(top_frame, textvariable=self.account_balance_var, width=12).grid(row=0, column=4, padx=(PAD_R, 6), pady=3)
        self.account_balance_var.trace('w', self.update_account_balance)
        
        ttk.Label(top_frame, text="Pip Value:").grid(row=0, column=5, padx=(6, PAD_L), pady=3, sticky=tk.W)
        ttk.Label(top_frame, text="0.1", font=("Arial", 9, "bold")).grid(row=0, column=6, padx=(PAD_R, 6), pady=3)
        
        ttk.Label(top_frame, text="1 Lot = 100 oz").grid(row=0, column=7, padx=6, pady=3)
        
        # Row 2: MongoDB Connection String
        ttk.Label(top_frame, text="MongoDB URI:").grid(row=1, column=0, padx=(6, PAD_L), pady=3, sticky=tk.W)
        self.mongodb_uri_var = tk.StringVar(value=self.db.connection_string if self.db.connection_string else "")
        mongodb_entry = ttk.Entry(top_frame, textvariable=self.mongodb_uri_var, width=50)
        mongodb_entry.grid(row=1, column=1, columnspan=5, padx=(PAD_R, 4), pady=3, sticky=(tk.W, tk.E))
        top_frame.columnconfigure(1, weight=1)
        
        connect_btn = ttk.Button(top_frame, text="Connect", command=self.reconnect_database)
        connect_btn.grid(row=1, column=6, padx=4, pady=3)
        
        # Connection status indicator
        self.db_status_label = ttk.Label(top_frame, text="●", font=("Arial", 12))
        self.db_status_label.grid(row=1, column=7, padx=6, pady=3)
        self.update_db_status_indicator()
    
    def _setup_trade_entry_frame(self, parent):
        """Setup trade entry frame — columns evenly distributed across full width"""
        input_frame = ttk.LabelFrame(parent, text="Add Trade Entry", padding=(8, 6))
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 6))
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(2, weight=1)
        input_frame.columnconfigure(3, weight=1)
        input_frame.columnconfigure(4, weight=1)
        input_frame.columnconfigure(5, weight=1)
        input_frame.columnconfigure(6, weight=1)
        input_frame.columnconfigure(7, weight=1)
        pad = (3, 3)
        st = (tk.W, tk.E)
        
        # Row 1: Entry, Risk %, Stop Loss, Multiplier (each pair = 2 equal columns)
        ttk.Label(input_frame, text="Entry:").grid(row=0, column=0, padx=pad, pady=2, sticky=st)
        self.entry_price_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.entry_price_var).grid(row=0, column=1, padx=pad, pady=2, sticky=st)
        
        ttk.Label(input_frame, text="Risk %:").grid(row=0, column=2, padx=pad, pady=2, sticky=st)
        self.risk_percent_var = tk.StringVar(value="6")
        ttk.Entry(input_frame, textvariable=self.risk_percent_var).grid(row=0, column=3, padx=pad, pady=2, sticky=st)
        
        ttk.Label(input_frame, text="Stop Loss:").grid(row=0, column=4, padx=pad, pady=2, sticky=st)
        self.stop_loss_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.stop_loss_var).grid(row=0, column=5, padx=pad, pady=2, sticky=st)
        
        ttk.Label(input_frame, text="Multiplier:").grid(row=0, column=6, padx=pad, pady=2, sticky=st)
        self.multiplier_var = tk.StringVar(value="1")
        ttk.Entry(input_frame, textvariable=self.multiplier_var).grid(row=0, column=7, padx=pad, pady=2, sticky=st)
        
        # Row 2: TP, Lot Size, Risk Amount, Exit
        ttk.Label(input_frame, text="TP:").grid(row=1, column=0, padx=pad, pady=2, sticky=st)
        self.take_profit_label = ttk.Label(input_frame, text="--", font=("Arial", 9, "bold"), foreground="blue")
        self.take_profit_label.grid(row=1, column=1, padx=pad, pady=2, sticky=st)
        
        ttk.Label(input_frame, text="Lot Size:").grid(row=1, column=2, padx=pad, pady=2, sticky=st)
        self.lot_size_label = ttk.Label(input_frame, text="--", font=("Arial", 9, "bold"), foreground="blue")
        self.lot_size_label.grid(row=1, column=3, padx=pad, pady=2, sticky=st)
        
        ttk.Label(input_frame, text="Risk Amount:").grid(row=1, column=4, padx=pad, pady=2, sticky=st)
        self.amount_at_risk_label = ttk.Label(input_frame, text="--", font=("Arial", 9, "bold"), foreground="red")
        self.amount_at_risk_label.grid(row=1, column=5, padx=pad, pady=2, sticky=st)
        
        ttk.Label(input_frame, text="Exit:").grid(row=1, column=6, padx=pad, pady=2, sticky=st)
        self.exit_reason_var = tk.StringVar(value="TP")
        exit_reason_combo = ttk.Combobox(input_frame, textvariable=self.exit_reason_var,
                                        values=["TP", "SL"], state="readonly")
        exit_reason_combo.grid(row=1, column=7, padx=pad, pady=2, sticky=st)
        
        # Row 3: Scenario (2 cols), Comment (6 cols) — same total 8 columns
        ttk.Label(input_frame, text="Scenario:").grid(row=2, column=0, padx=pad, pady=2, sticky=st)
        self.scenario_var = tk.StringVar(value="Strong")
        scenario_combo = ttk.Combobox(input_frame, textvariable=self.scenario_var,
                                     values=["Low", "Medium", "Strong"], state="readonly")
        scenario_combo.grid(row=2, column=1, padx=pad, pady=2, sticky=st)
        
        ttk.Label(input_frame, text="Comment:").grid(row=2, column=2, padx=pad, pady=2, sticky=st)
        self.comment_var = tk.StringVar()
        comment_entry = ttk.Entry(input_frame, textvariable=self.comment_var)
        comment_entry.grid(row=2, column=3, columnspan=5, padx=pad, pady=2, sticky=st)
        
        # Row 4: Buttons — each spanning 4 columns, centred in their half
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=3, column=0, columnspan=8, sticky=st, pady=4)
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        calc_btn = ttk.Button(btn_frame, text="Calculate TP & Lot Size", command=self.calculate_trade_values)
        calc_btn.grid(row=0, column=0, padx=4)
        add_btn = ttk.Button(btn_frame, text="Add Trade", command=self.add_trade)
        add_btn.grid(row=0, column=1, padx=4)
    
    def _setup_quick_input_frame(self, parent):
        """Setup quick input frame"""
        quick_input_frame = ttk.LabelFrame(parent, text="Quick Input (Entry Risk% StopLoss Multiplier ExitReason)", padding=(8, 6))
        quick_input_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 6))
        quick_input_frame.columnconfigure(0, weight=1)
        
        self.quick_input_var = tk.StringVar()
        quick_entry = ttk.Entry(quick_input_frame, textvariable=self.quick_input_var, width=80)
        quick_entry.grid(row=0, column=0, padx=(6, 4), pady=3, sticky=(tk.W, tk.E))
        quick_entry.bind('<Return>', lambda e: self.process_quick_input())
        
        quick_add_button = ttk.Button(quick_input_frame, text="Add", command=self.process_quick_input)
        quick_add_button.grid(row=0, column=1, padx=4, pady=3)
        
        ttk.Label(quick_input_frame, text="Example: 2000.50 1.0 1995.00 2.0 TP",
                 font=("Arial", 8), foreground="gray").grid(row=1, column=0, columnspan=2, pady=1, sticky=tk.W)
    
    def _setup_table_frame(self, parent):
        """Setup table frame"""
        table_frame = ttk.Frame(parent)
        table_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 6))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(3, weight=1)
        
        columns = ("Date", "Strategy", "Scenario", "Entry", "TP", "SL", "Multiplier", "Lot Size", "Risk %", "Risk Amount",
                  "Exit Reason", "Pips", "USD P/L", "Status", "Return Ratio", "Comment")
        
        column_widths = {
            "Date": 120, "Strategy": 90, "Scenario": 70, "Entry": 80, "TP": 80, "SL": 80,
            "Multiplier": 70, "Lot Size": 70, "Risk %": 55, "Risk Amount": 85,
            "Exit Reason": 65, "Pips": 60, "USD P/L": 85, "Status": 60, "Return Ratio": 85, "Comment": 180
        }
        
        from .ui.components import create_table_frame
        self.table_frame, self.tree = create_table_frame(table_frame, columns, column_widths)
        self.table_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def _setup_summary_frame(self, parent):
        """Setup summary frame"""
        summary_frame = ttk.LabelFrame(parent, text="Summary", padding=(8, 6))
        summary_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.summary_text = tk.Text(summary_frame, height=15, wrap=tk.WORD, font=("Courier", 9))
        self.summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=2, pady=2)
        summary_frame.columnconfigure(0, weight=1)
    
    def update_account_balance(self, *args):
        """Update account balance when changed"""
        try:
            self.account_balance = float(self.account_balance_var.get())
        except ValueError:
            pass
    
    def reconnect_database(self):
        """Reconnect to MongoDB with new connection string"""
        connection_string = self.mongodb_uri_var.get().strip()
        if not connection_string:
            messagebox.showwarning("Warning", "Please enter a MongoDB connection string")
            return
        
        # Try to reconnect
        if self.db.reconnect(connection_string):
            messagebox.showinfo("Success", "Connected to MongoDB successfully!")
            # Reload trades from new database
            self.trades = self.db.load_trades()
            # Recalculate account balance
            initial_balance = 10000.0
            self.account_balance = initial_balance + sum(t.usd_pl for t in self.trades)
            self.account_balance_var.set(str(round(self.account_balance, 2)))
            # Update table
            self.update_table()
        else:
            messagebox.showerror("Error", "Failed to connect to MongoDB. Check your connection string.")
        
        self.update_db_status_indicator()
    
    def update_db_status_indicator(self):
        """Update database connection status indicator"""
        if self.db.is_connected():
            self.db_status_label.config(text="●", foreground="green")
        else:
            self.db_status_label.config(text="●", foreground="red")
    
    def add_strategy(self):
        """Add a new strategy"""
        strategy_name = simpledialog.askstring("Add Strategy", "Enter strategy name:")
        if strategy_name and strategy_name.strip():
            strategy_name = strategy_name.strip()
            if strategy_name not in self.strategies:
                self.strategies.append(strategy_name)
                self.strategy_combo['values'] = self.strategies
                self.strategy_combo.set(strategy_name)
            else:
                messagebox.showwarning("Warning", "Strategy already exists")
    
    def on_strategy_change(self, event=None):
        """Handle strategy change"""
        pass
    
    def calculate_trade_values(self):
        """Calculate Take Profit and Lot Size"""
        try:
            entry_price = float(self.entry_price_var.get())
            risk_percent = float(self.risk_percent_var.get())
            stop_loss = float(self.stop_loss_var.get())
            multiplier = float(self.multiplier_var.get())
            
            if entry_price <= 0 or stop_loss <= 0 or risk_percent <= 0 or multiplier <= 0:
                messagebox.showerror("Error", "All values must be greater than 0")
                return
            
            # Calculate values using calculator
            take_profit = self.calculator.calculate_take_profit(entry_price, stop_loss, multiplier)
            lot_size = self.calculator.calculate_lot_size(self.account_balance, risk_percent, entry_price, stop_loss)
            amount_at_risk = self.calculator.calculate_amount_at_risk(self.account_balance, risk_percent)
            
            # Update labels
            self.take_profit_label.config(text=f"{take_profit:.2f}")
            self.lot_size_label.config(text=f"{lot_size:.3f}")
            self.amount_at_risk_label.config(text=f"${amount_at_risk:.2f}")
            
            # Store calculated values
            self.calculated_tp = take_profit
            self.calculated_lot_size = lot_size
            self.calculated_risk_amount = amount_at_risk
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def add_trade(self):
        """Add a trade from the input fields"""
        try:
            if self.calculated_tp is None:
                messagebox.showwarning("Warning", "Please calculate TP and Lot Size first")
                return
            
            entry_price = float(self.entry_price_var.get())
            stop_loss = float(self.stop_loss_var.get())
            risk_percent = float(self.risk_percent_var.get())
            multiplier = float(self.multiplier_var.get())
            exit_reason = self.exit_reason_var.get()
            strategy = self.strategy_var.get()
            scenario = self.scenario_var.get()
            comment = (self.comment_var.get() or "").strip()
            
            take_profit = self.calculated_tp
            lot_size = self.calculated_lot_size
            amount_at_risk = self.calculated_risk_amount
            
            # Determine if long or short
            is_long = entry_price > stop_loss
            
            # Determine actual exit price
            actual_exit = take_profit if exit_reason == "TP" else stop_loss
            
            # Calculate pips and USD P/L
            pips = self.calculator.calculate_pips(entry_price, actual_exit, is_long)
            usd_pl = self.calculator.calculate_usd_pl(pips, lot_size)
            
            # Determine status
            status = "Win" if exit_reason == "TP" else "Loss"
            
            # Calculate return ratio
            return_ratio = self.calculator.calculate_return_ratio(usd_pl, amount_at_risk)
            achieved_multiplier = return_ratio if return_ratio > 0 else 0
            
            # Create trade
            trade = Trade(
                date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                strategy=strategy,
                entry=entry_price,
                tp=take_profit,
                sl=stop_loss,
                multiplier=multiplier,
                lot_size=lot_size,
                risk_percent=risk_percent,
                risk_amount=amount_at_risk,
                exit_reason=exit_reason,
                actual_exit=actual_exit,
                pips=pips,
                usd_pl=usd_pl,
                status=status,
                return_ratio=return_ratio,
                achieved_multiplier=achieved_multiplier,
                scenario=scenario,
                comment=comment,
            )
            
            self.trades.append(trade)
            
            # Update account balance: add profit or subtract loss
            self.account_balance += trade.usd_pl
            self.account_balance_var.set(str(round(self.account_balance, 2)))
            
            # Save to database
            if self.db.is_connected():
                self.db.save_trade(trade)
            
            self.update_table()
            self.update_db_status_indicator()
            self.clear_inputs()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def process_quick_input(self):
        """Process quick input format: Entry Risk% StopLoss Multiplier ExitReason"""
        try:
            input_text = self.quick_input_var.get().strip()
            if not input_text:
                return
            
            parts = input_text.split()
            if len(parts) < 5:
                messagebox.showerror("Error", "Format: EntryPrice RiskPercent StopLoss Multiplier ExitReason")
                return
            
            entry_price = float(parts[0])
            risk_percent = float(parts[1])
            stop_loss = float(parts[2])
            multiplier = float(parts[3])
            exit_reason = parts[4].upper()
            
            if exit_reason not in ["TP", "SL"]:
                messagebox.showerror("Error", "Exit reason must be TP or SL")
                return
            
            # Set the input fields
            self.entry_price_var.set(str(entry_price))
            self.risk_percent_var.set(str(risk_percent))
            self.stop_loss_var.set(str(stop_loss))
            self.multiplier_var.set(str(multiplier))
            self.exit_reason_var.set(exit_reason)
            
            # Calculate values
            self.calculate_trade_values()
            
            # Add the trade
            self.add_trade()
            
            # Clear quick input
            self.quick_input_var.set("")
            
        except ValueError:
            messagebox.showerror("Error", "Invalid format. Use: EntryPrice RiskPercent StopLoss Multiplier ExitReason")
        except Exception as e:
            messagebox.showerror("Error", f"Error processing input: {str(e)}")
    
    def update_table(self):
        """Update the table with all trades"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add all trades
        for trade in self.trades:
            scenario = getattr(trade, "scenario", "Strong")
            comment = getattr(trade, "comment", "") or ""
            self.tree.insert("", tk.END, values=(
                trade.date,
                trade.strategy,
                scenario,
                f"{trade.entry:.2f}",
                f"{trade.tp:.2f}",
                f"{trade.sl:.2f}",
                f"{trade.multiplier:.1f}",
                f"{trade.lot_size:.3f}",
                f"{trade.risk_percent:.2f}%",
                f"${trade.risk_amount:.2f}",
                trade.exit_reason,
                f"{trade.pips:.2f}",
                f"${trade.usd_pl:.2f}",
                trade.status,
                f"{trade.return_ratio:.2f}x",
                (comment[:40] + "…") if len(comment) > 40 else comment,
            ))
        
        # Update summary
        self.update_summary()
    
    def update_summary(self):
        """Update the summary text"""
        if not self.trades:
            self.summary_text.delete(1.0, tk.END)
            return
        
        total_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades if t.status == "Win")
        losing_trades = sum(1 for t in self.trades if t.status == "Loss")
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Count trades with 2x or more return
        multiplier_trades = sum(1 for t in self.trades if t.achieved_multiplier >= 2.0)
        
        total_pips = sum(t.pips for t in self.trades)
        total_usd = sum(t.usd_pl for t in self.trades)
        
        avg_pips = total_pips / total_trades if total_trades > 0 else 0
        avg_usd = total_usd / total_trades if total_trades > 0 else 0
        
        # Strategy-wise statistics
        strategy_stats = defaultdict(lambda: {"total": 0, "wins": 0, "losses": 0, "tps": 0, "sls": 0})
        
        for trade in self.trades:
            strat = trade.strategy
            strategy_stats[strat]["total"] += 1
            if trade.status == "Win":
                strategy_stats[strat]["wins"] += 1
                strategy_stats[strat]["tps"] += 1
            else:
                strategy_stats[strat]["losses"] += 1
                strategy_stats[strat]["sls"] += 1
        
        summary = f"""
═══════════════════════════════════════════════════════════════
                    TRADING JOURNAL SUMMARY
═══════════════════════════════════════════════════════════════

OVERALL STATISTICS:
───────────────────────────────────────────────────────────────
Total Trades:          {total_trades}
Winning Trades:        {winning_trades}
Losing Trades:         {losing_trades}
Win Rate:              {win_rate:.2f}%
Trades with 2x+ Return: {multiplier_trades}

Total Pips:            {total_pips:+.2f}
Average Pips/Trade:    {avg_pips:+.2f}

Total USD P/L:         ${total_usd:+.2f}
Average USD/Trade:     ${avg_usd:+.2f}

═══════════════════════════════════════════════════════════════
                    STRATEGY BREAKDOWN
═══════════════════════════════════════════════════════════════
"""
        
        for strategy in sorted(strategy_stats.keys()):
            stats = strategy_stats[strategy]
            strat_win_rate = (stats["wins"] / stats["total"] * 100) if stats["total"] > 0 else 0
            summary += f"""
{strategy}:
  Total Trades:    {stats["total"]}
  Wins (TPs):      {stats["wins"]} ({stats["tps"]} TPs)
  Losses (SLs):    {stats["losses"]} ({stats["sls"]} SLs)
  Win Rate:        {strat_win_rate:.2f}%
───────────────────────────────────────────────────────────────
"""
        
        summary += "\n═══════════════════════════════════════════════════════════════\n"
        
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary)
        
        # Save summary to database
        if self.db.is_connected():
            summary_data = {
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate": win_rate,
                "multiplier_trades": multiplier_trades,
                "total_pips": total_pips,
                "avg_pips": avg_pips,
                "total_usd": total_usd,
                "avg_usd": avg_usd,
                "strategy_stats": dict(strategy_stats)
            }
            self.db.save_summary(summary_data)
    
    def clear_inputs(self):
        """Clear input fields"""
        self.entry_price_var.set("")
        self.risk_percent_var.set("6")
        self.stop_loss_var.set("")
        self.multiplier_var.set("1")
        self.exit_reason_var.set("TP")
        self.scenario_var.set("Strong")
        self.comment_var.set("")
        self.take_profit_label.config(text="--")
        self.lot_size_label.config(text="--")
        self.amount_at_risk_label.config(text="--")
        self.calculated_tp = None
        self.calculated_lot_size = None
        self.calculated_risk_amount = None
    
    def delete_trade(self):
        """Delete selected trade"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a trade to delete")
            return
        
        item = selected[0]
        index = self.tree.index(item)
        trade = self.trades[index]
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this trade?"):
            # Reverse account balance change for this trade
            self.account_balance -= trade.usd_pl
            self.account_balance_var.set(str(round(self.account_balance, 2)))
            
            # Delete from database
            if self.db.is_connected():
                self.db.delete_trade(trade.date)
            
            # Delete from list
            del self.trades[index]
            self.update_table()
            self.update_db_status_indicator()
    
    def on_closing(self):
        """Handle window close event"""
        # Save final summary
        if self.trades and self.db.is_connected():
            self.update_summary()
        
        # Close database connection
        if self.db.is_connected():
            self.db.close()
        
        # Destroy window
        self.root.destroy()
