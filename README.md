# Trading Journal - Gold (XAU/USD)

A comprehensive trading journal application specifically designed for Gold (XAU/USD) trading with automatic position sizing and risk management calculations.

## Features

- **Strategy Tracking**: Track multiple trading strategies with separate statistics
- **Automatic Calculations**:
  - **Take Profit**: Automatically calculated based on entry, stop loss, and reward multiplier
  - **Lot Size**: Automatically calculated based on risk percentage and stop loss distance
  - **Risk Amount**: Calculated from account balance and risk percentage
- **Risk Management**: Built-in risk percentage calculator
- **Exit Reason**: Simple dropdown selection (TP or SL)
- **Comprehensive Summary**:
  - Overall statistics (wins, losses, win rate)
  - Trades achieving 2x+ return on risk
  - Strategy-wise breakdown (TPs, SLs per strategy)
  - Total and average pips and USD P/L

## Trading Specifications

- **Instrument**: XAU/USD (Gold)
- **Pip Value**: 0.1
- **Lot Size**: 1 lot = 100 oz
- **Pip Value in USD**: $1.00 per pip per lot

## Installation

### From Source

```bash
git clone https://github.com/Usamatahir23/trading_journal.git
cd trading_journal
python -m pip install -e .
```

### Direct Run

```bash
python -m src.trading_journal.main
```

Or:

```bash
python src/trading_journal/main.py
```

## Usage

### Running the Application

```bash
python -m src.trading_journal.main
```

### Adding Strategies

1. Click **"Add Strategy"** button at the top
2. Enter a strategy name (e.g., "Strategy 1", "Breakout Strategy")
3. Select the strategy from the dropdown before adding trades

### Adding Trades

#### Method 1: Using Input Fields

1. **Select Strategy**: Choose from the dropdown at the top
2. **Enter Trade Details**:
   - **Entry Price**: Your entry price
   - **Risk %**: Percentage of account balance to risk (e.g., 1.0 for 1%)
   - **Stop Loss**: Your stop loss price
   - **Reward Multiplier**: Risk:Reward ratio (e.g., 2.0 for 2:1)
3. Click **"Calculate TP & Lot Size"** to see calculated values:
   - Take Profit (automatically calculated)
   - Lot Size (automatically calculated)
   - Amount at Risk
4. **Select Exit Reason**: Choose "TP" or "SL" from dropdown
5. Click **"Add Trade"**

#### Method 2: Quick Input

Type in the quick input field: `EntryPrice RiskPercent StopLoss Multiplier ExitReason`

**Example**: `2000.50 1.0 1995.00 2.0 TP`

Press Enter or click "Add"

### Calculations

#### Take Profit Calculation

**For Long Positions:**
- TP = Entry + (Entry - Stop Loss) × Multiplier

**For Short Positions:**
- TP = Entry - (Stop Loss - Entry) × Multiplier

**Example (Long):**
- Entry: 2000.50
- Stop Loss: 1995.00
- Multiplier: 2.0
- TP = 2000.50 + (2000.50 - 1995.00) × 2.0 = 2000.50 + 11.00 = **2011.50**

#### Lot Size Calculation

Lot Size is calculated based on:
- Account Balance × Risk %
- Stop Loss distance in pips
- Formula: `Lot Size = Risk Amount / (SL Distance in Pips × $1)`

**Example:**
- Account Balance: $10,000
- Risk: 1% = $100
- Entry: 2000.50
- Stop Loss: 1995.00
- SL Distance: (2000.50 - 1995.00) / 0.1 = 55 pips
- Lot Size = $100 / (55 × $1) = **1.818 lots**

### Summary Statistics

The summary section displays:

1. **Overall Statistics**:
   - Total trades, wins, losses
   - Win rate percentage
   - Number of trades achieving 2x+ return
   - Total and average pips
   - Total and average USD P/L

2. **Strategy Breakdown**:
   - For each strategy:
     - Total trades
     - Wins (TPs count)
     - Losses (SLs count)
     - Win rate

### Table Columns

- **Date**: Trade entry date and time
- **Strategy**: Strategy used for the trade
- **Entry**: Entry price
- **TP**: Take profit price (calculated)
- **SL**: Stop loss price
- **Multiplier**: Reward multiplier used
- **Lot Size**: Position size in lots (calculated)
- **Risk %**: Risk percentage used
- **Risk Amount**: Dollar amount at risk
- **Exit Reason**: TP or SL
- **Pips**: Pips gained/lost
- **USD P/L**: Profit/Loss in USD
- **Status**: Win or Loss
- **Return Ratio**: Actual return / risk (e.g., 2.0x means 2x return on risk)

## Project Structure

```
trading_journal/
├── src/
│   └── trading_journal/
│       ├── __init__.py
│       ├── main.py              # Entry point
│       ├── journal.py            # Main journal class
│       ├── calculator.py         # Calculation functions
│       ├── models.py             # Data models
│       └── ui/
│           ├── __init__.py
│           └── components.py    # UI components
├── tests/
│   ├── __init__.py
│   └── test_calculator.py        # Unit tests
├── README.md
├── requirements.txt
├── setup.py
└── .gitignore
```

## Development

### Running Tests

```bash
python -m pytest tests/
```

Or:

```bash
python -m unittest discover tests
```

## Notes

- The system automatically determines if a position is Long or Short based on Entry vs Stop Loss relationship
- For Long: Entry > Stop Loss
- For Short: Entry < Stop Loss
- All calculations are based on Gold (XAU/USD) specifications
- The system tracks which trades achieved the target multiplier return (e.g., 2x)
- Strategy statistics are automatically updated as you add trades

## Requirements

- Python 3.7 or higher
- tkinter (usually included with Python)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
