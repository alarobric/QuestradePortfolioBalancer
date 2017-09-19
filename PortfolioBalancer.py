import pickle
from functools import reduce
import operator

from terminaltables import AsciiTable

from QuestradeApi import QuestradeApi
from CurrencyApi import CurrencyApi
from Account import Balance, Position, Account, TargetPortfolio


class PortfolioBalancer(object):
    def __init__(self):
        self.api = QuestradeApi()
        self.data = {
            'accounts': [],
            'target_portfolios': []
        }
        self.usdcad_exchange = 1.0
        api = CurrencyApi()
        self.usdcad_exchange = api.get_usd_cad_exchange()

    def menu(self):
        choice = ''
        while choice != '0':

            if self.data['accounts'] == []:
                print('')
                print('Questrade Portfolio Balancer')
                print('============================')
                print('0. Quit')
                print('1. Load portfolio data')
                print('2. Load portfolio from api')
                choice = input(' >> ')

                if choice == '0':
                    return
                elif choice == '1':
                    self.load_from_file()
                elif choice == '2':
                    self.load_from_api()

            else:  # accounts exist
                print('Questrade Portfolio Balancer')
                print('============================')
                print('0. Quit')
                print('1. Refresh portfolio from api')
                print('2. Save portfolio data')
                print('3. Display portfolio balances')
                print('4. Display portfolio holdings')
                print('5. Setup target portfolio')
                print('6. View targets')
                print('7. Calculate...')
                choice = input(' >> ')

                if choice == '0':
                    return
                elif choice == '1':
                    self.load_from_api()
                elif choice == '2':
                    self.save_to_file()
                elif choice == '3':
                    self.print_account_summary()
                elif choice == '4':
                    self.print_holdings()
                elif choice == '5':
                    self.setup_target_portfolio()
                    self.ask_for_save()
                elif choice == '6':
                    self.view_target_portfolio()
                elif choice == '7':
                    self.calculate()

    def ask_for_save(self):
        print('Save? Y/n')
        save = input(' >> ')
        if save == 'Y' or save == 'y' or save == '':
            self.save_to_file()

    def load_from_api(self):
        print('Loading data from Questrade')
        self.api.get_refresh_token()
        self.load_accounts()
        print('Loaded data')
        self.print_account_summary()
        self.ask_for_save()

    def load_from_file(self):
        with open('account_data', 'rb') as account_data_file:
            self.data = pickle.load(account_data_file)
        self.data['target_portfolios'][0].accounts = ['51546191', '51639704']

    def save_to_file(self):
        with open('account_data', 'wb') as account_data_file:
            pickle.dump(self.data, account_data_file)

    def load_accounts(self):
        accounts_response = self.api.get_accounts().json()
        accounts = accounts_response.get('accounts')
        for account in accounts:
            account_number = account.get('number')
            account_type = account.get('type')
            acc = Account(account_number, account_type)

            account_balance_response = self.api.get_account_balance(
                account_number).json()
            account_currency_balances = account_balance_response.get(
                'perCurrencyBalances')
            for account_currency_balance in account_currency_balances:
                cash = account_currency_balance.get('cash')
                market_value = account_currency_balance.get('marketValue')
                total_equity = account_currency_balance.get('totalEquity')
                account_currency = account_currency_balance.get('currency')
                if total_equity == 0:
                    continue
                balance = Balance(account_currency, cash,
                                  market_value, total_equity)
                acc.balances.append(balance)

            account_positions_response = self.api.get_account_positions(
                account_number).json()
            account_positions = account_positions_response.get('positions')
            for account_position in account_positions:
                symbol = account_position.get('symbol')
                holding = account_position.get('openQuantity')
                current_price = account_position.get('currentPrice')
                current_market_value = account_position.get(
                    'currentMarketValue')
                position = Position(
                    symbol, holding, current_price, current_market_value)
                acc.positions.append(position)

            self.data['accounts'].append(acc)

    def print_account_summary(self):
        table_data = [
            ['Account Number', 'Type', 'Currency',
             'Cash', 'Market Value', 'Total Equity']
        ]
        for account in self.data['accounts']:
            for balance in account.balances:
                row = [account.account_number, account.account_type, balance.currency,
                       '$ {0:7.2f}'.format(
                           balance.cash_in_cad(self.usdcad_exchange)),
                       '$ {0:8.2f}'.format(
                           balance.market_value_in_cad(self.usdcad_exchange)),
                       '$ {0:8.2f}'.format(balance.total_equity_in_cad(self.usdcad_exchange))]
                table_data.append(row)
        ascii_table = AsciiTable(table_data)
        ascii_table.justify_columns[3] = 'right'
        ascii_table.justify_columns[4] = 'right'
        ascii_table.justify_columns[5] = 'right'
        print(ascii_table.table)

    def print_holdings(self):
        table_data = [
            ['Symbol', 'Quantity', 'Current Price', 'Current Value']
        ]
        for account in self.data['accounts']:
            for position in account.positions:
                row = [position.symbol, position.quantity,
                       '$ {0:6.2f}'.format(
                           position.price_in_cad(self.usdcad_exchange)),
                       '$ {0:8.2f}'.format(position.market_value_in_cad(self.usdcad_exchange))]
                table_data.append(row)
        ascii_table = AsciiTable(table_data)
        ascii_table.justify_columns[2] = 'right'
        ascii_table.justify_columns[3] = 'right'
        print(ascii_table.table)

    def select_holdings(self):
        print('Enter a name for this target portfolio')
        name = input(' >> ')
        portfolio = TargetPortfolio(name)

        table_data = [
            ['Holding #', 'Account', 'Symbol', 'Quantity',
                'Current Price', 'Current Value']
        ]
        counter = 1

        for account in self.data['accounts']:
            for position in account.positions:
                row = [counter, account.account_type, position.symbol, position.quantity,
                       '$ {0:6.2f}'.format(
                           position.price_in_cad(self.usdcad_exchange)),
                       '$ {0:8.2f}'.format(position.market_value_in_cad(self.usdcad_exchange))]
                table_data.append(row)
            counter += 1
        ascii_table = AsciiTable(table_data)
        ascii_table.justify_columns[4] = 'right'
        ascii_table.justify_columns[5] = 'right'
        print(ascii_table.table)
        print('Enter a list of account numbers to target (ex. 1,3)')
        account_choice_input = input(' >> ')

        choices = [int(choice) for choice in account_choice_input.split(',')]
        for choice in choices:
            account = self.data['accounts'][choice - 1]
            portfolio.accounts.append(account.account_number)
            for position in account.positions:
                portfolio.optional_add_position(position)

        self.data['target_portfolios'].append(portfolio)

    def setup_target_portfolio(self):
        if self.data['target_portfolios'] == []:
            print('No target portfolios')
            self.select_holdings()
        else:
            print('Target portfolio already exists - will overwrite')
            self.data['target_portfolios'] = []
            self.select_holdings()

    def view_target_portfolio(self):
        if self.data['target_portfolios'] == []:
            print('No target portfolios')
            return
        self.data['target_portfolios'][0].print_current_positions()

    def calculate(self):
        print('')
        target_portfolio = self.data['target_portfolios'][0]
        print('Calculating using target portfolio: ', target_portfolio.name)

        # calculate total cash available
        total_cash = 0
        for account_number in target_portfolio.accounts:
            for account in self.data['accounts']:
                if account.account_number == account_number:
                    for balance in account.balances:
                        total_cash += balance.cash_in_cad(self.usdcad_exchange)

        # calculate value of each target position (category)
        for target_position in target_portfolio.positions:
            target_position.value = 0
            for target_stock in target_position.stocks:
                for account in self.data['accounts']:
                    if account.account_number in target_portfolio.accounts:
                        for position in account.positions:
                            if target_stock == position.symbol:
                                target_position.value += position.market_value_in_cad(
                                    self.usdcad_exchange)

        # determine total portfolio value
        values = [t.value for t in target_portfolio.positions]
        total_value = reduce(operator.add, values)
        future_value = total_value + total_cash

        # calculate ideal portfolio with new cash
        for target_position in target_portfolio.positions:
            target_position.ideal_value = target_position.percentage / 100.0 * future_value

        target_portfolio.print_current_positions(total_cash, total_value)

        # take total cash + total_value and calculate ideal portfolio with this
        # then display difference from current to this
        # then how much to buy?
        # then calculate how much stock that is in round numbers


def main():
    app = PortfolioBalancer()
    app.menu()


if __name__ == '__main__':
    main()
