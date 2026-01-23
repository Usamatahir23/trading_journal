"""
Main entry point for Trading Journal application
"""
import tkinter as tk
from .journal import TradingJournal


def main():
    """Main function to run the trading journal application"""
    root = tk.Tk()
    app = TradingJournal(root)
    root.mainloop()


if __name__ == "__main__":
    main()
