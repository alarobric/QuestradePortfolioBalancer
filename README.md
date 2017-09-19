# QuestradePortfolio

## Summary

A simple CLI written in Python to collect Questrade account information, calculate a portfolio and any trades that could be made to better match the portfolio.

Uses the Questrade API to gather account balances and positions.
Uses the fixer.io api to handle USD/CAD conversion if necessary.

Allows the user to save his account information and model portfolio setup for repeated use.
Will calculate and display the current allocation of your portfolio, difference from ideal, and amount to buy or sell.

Supports portfolio spread across multiple accounts (TFSA and RRSP etc.), and also USD and CAD currencies.

## Future plans

- Clean up data structures, code layout
- Suggest stocks to buy/sell based on current stock price. (Tricky when multiple stocks per category and also cash balances across acounts)
- Allow adding arbitrary cash to calculation.
- Consider a UI or better way to edit the portfolio.
