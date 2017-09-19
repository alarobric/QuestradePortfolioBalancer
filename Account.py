from terminaltables import AsciiTable


class Balance(object):
    def __init__(self, currency, cash, market_value, total_equity):
        self.currency = currency
        self.cash = cash
        self.market_value = market_value
        self.total_equity = total_equity

    def cash_in_cad(self, usd_cad_exchange):
        if self.currency == 'CAD':
            return self.cash
        elif self.currency == 'USD':
            return self.cash * usd_cad_exchange

    def market_value_in_cad(self, usd_cad_exchange):
        if self.currency == 'CAD':
            return self.market_value
        elif self.currency == 'USD':
            return self.market_value * usd_cad_exchange

    def total_equity_in_cad(self, usd_cad_exchange):
        if self.currency == 'CAD':
            return self.total_equity
        elif self.currency == 'USD':
            return self.total_equity * usd_cad_exchange


class Position(object):
    def __init__(self, symbol, quantity, price, market_value):
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.market_value = market_value
        if '.TO' in symbol:
            self.currency = 'CAD'
        elif '.' not in symbol:
            self.currency = 'USD'
        else:
            raise NotImplementedError

    def price_in_cad(self, usd_cad_exchange):
        if self.currency == 'CAD':
            return self.price
        elif self.currency == 'USD':
            return self.price * usd_cad_exchange

    def market_value_in_cad(self, usd_cad_exchange):
        if self.currency == 'CAD':
            return self.market_value
        elif self.currency == 'USD':
            return self.market_value * usd_cad_exchange


class Account(object):
    def __init__(self, account_number, account_type):
        self.account_number = account_number
        self.account_type = account_type
        self.positions = []
        self.balances = []


class TargetPortfolio(object):
    def __init__(self, name):
        self.name = name
        self.positions = []
        self.accounts = []

    def print_current_positions(self, total_cash=0, total_value=0):
        print('Portfolio for accounts {}'.format(self.accounts))
        if total_value != 0:
            print('Total portfolio value $ {0:0.2f}'.format(total_value))
        if total_cash != 0:
            print('Total available cash across portfolio accounts and currencies is $ {0:0.2f}'.format(
                total_cash))

        counter = 1
        total_percentage = 0
        table_data = [
            ['Position #', 'Name', 'Stocks', 'Target Percentage']
        ]
        if total_value != 0:
            table_data[0].extend(('Current Percentage',
                                  'Difference', 'Absolute Difference',
                                  'Current Value', 'Ideal Value', 'Difference to buy/sell'))

        for position in self.positions:
            row = [counter, position.name,
                   position.stocks, position.percentage]
            if total_value != 0:
                current_percentage = position.value / total_value * 100
                difference = position.percentage - current_percentage
                row.append('{0:0.1f}'.format(current_percentage))
                row.append('{0:0.1f}'.format(difference))
                row.append('$ {0:8.2f}'.format(difference / 100 * total_value))
                row.append('$ {0:8.2f}'.format(position.value))
                row.append('$ {0:8.2f}'.format(position.ideal_value))
                row.append('$ {0:8.2f}'.format(
                    position.ideal_value - position.value))
            total_percentage += position.percentage
            table_data.append(row)
            counter += 1

        if total_value == 0:
            row = ['Total Percentage', '', '', total_percentage]
        else:
            row = ['Total Percentage', '', '',
                   total_percentage, '', '', '', '$ {0:8.2f}'.format(total_value)]
        table_data.append(row)
        ascii_table = AsciiTable(table_data)
        for i in range(3, len(table_data[0])):
            ascii_table.justify_columns[i] = 'right'
        print(ascii_table.table)

    def optional_add_position(self, position):
        self.print_current_positions()
        print('Add to an existing position by entering the number, or create a new target with 0')
        print('Considering stock: ', position.symbol)
        notvalid = True
        choice = ''
        while notvalid:
            try:
                choice = int(input(' >> '))
                notvalid = False
            except ValueError:
                print('Try again - invalid input')

        if choice == 0:
            print('Enter a name for the target')
            name = input(' >> ')
            print('Enter a target percentage')
            percentage = float(input(' >> '))
            target_position = TargetPosition(name, position.symbol, percentage)
            self.positions.append(target_position)
        else:
            self.positions[choice - 1].stocks.append(position.symbol)


class TargetPosition(object):
    def __init__(self, name, stocks, percentage):
        self.name = name
        self.stocks = [stocks]
        self.percentage = percentage
