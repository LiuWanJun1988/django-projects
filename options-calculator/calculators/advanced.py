import datetime as dt

import numpy as np
import pandas as pd
import pandas_datareader.data as web
from pandas_datareader.yahoo.options import Options

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.colheader_justify', 'center')

from .options.bsm import Option


def run():
    """ Interface for running advanced strategies with BSM model.

    :return: table and/or graph calculated option values and costs
        for iron condor, collar, double diagonal, strangle, synthetic put, butterfly,
        diagonal spread, straddle, covered strangle and reverse conversion strategies
    """

    # Add auxiliary global variables
    global options_df, long_options_df, short_options_df, lower_df, middle_df, upper_df

    print('1 - Iron Condor')
    print('2 - Collar')
    print('3 - Double Diagonal')
    print('4 - Strangle')
    print('5 - Synthetic Put')
    print('6 - Butterfly')
    print('7 - Diagonal Spread')
    print('8 - Straddle')
    print('9 - Covered Strangle')
    print('10 - Reverse Conversion\n')

    # Insert selected strategy as 1, 2,..., 10
    strategy = input('Strategy: ')

    # Create an instance of the Option() class
    opt = Option()

    # Insert stock symbol in capital letters (e.g. GOOG, TSLA, etc)
    ticker = input('\nPlease Insert Stock Symbol: ')

    # Get dates for today and for a year ago
    today = dt.datetime.now()  # Today's date
    last_year = today.year - 1, today.month, today.day  # Last year's date
    start_date = str(last_year[0]) + '-' + str(last_year[1]) + '-' + str(last_year[2])  # Last year date as str
    end_date = today.strftime("%Y-%m-%d")  # set today as end date for fetching data

    # Fetch data to dataframe from pandas-datareader API
    df = web.DataReader(ticker, 'yahoo', start_date, end_date).sort_values(by='Date', ascending=False)

    # Get annualized volatility and Spot price
    returns = df['Adj Close'].pct_change().dropna()  # Get returns from close prices and drop NaN values
    sigma = np.std(returns) * np.sqrt(252)  # volatility of underlying asset, annualized
    spot_price = df['Adj Close'].iloc[0]  # spot (current) price
    print('Current Spot Price: $ ', np.round(spot_price, 2))
    print('Annualized volatility: ', np.round(sigma, 2))

    print('\nPlease provide one of the available expiry dates: \n')

    # Store tick data into dataframe
    ticker = Options(ticker)

    # Get expiry dates for stock
    expiry_dates = ticker.expiry_dates

    # Show available expiry dates
    for exp in expiry_dates:
        print(exp.strftime("%Y-%m-%d"))

    # Provide expiry date among shown dates
    expiry_date = input('\nExpiry date: ')

    # Fetch all data for provided ticker
    all_data = ticker.get_all_data()

    # Compute values and parameters for BSM model at strategy level
    try:
        if strategy == '1':

            # LONG PUT

            print('\nPlease select a Strike Price and one Ask price per option for Long Put option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'expiry' and 'put'
            # multi-index levels and store into df
            long_put_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]

            # Get Ask and IV indexed by strike prices
            long_put_filtered_df = long_put_df.droplevel([1, 2, 3])[['Ask', 'IV']]

            # Replace NaN values by 0's
            long_put_filtered_df.fillna(0)
            print(long_put_filtered_df)

            # Provide strike price, ask price and # contracts
            long_put_strike = float(input('\nStrike Price: '))
            long_put_price = float(input('Ask Price: '))
            long_put_contracts = int(input('Please select the number of contracts for Long Put Option: '))

            # Calculate and show total cost for the option
            long_put_cost = round(long_put_price * long_put_contracts * 100, 2)
            print('\nTotal Cost for Long Put Option: ', long_put_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            long_put_risk_free = input('\nPlease insert risk-free rate for Long Put Option or press enter to use default value: ')
            long_put_dividend_yield = input('\nPlease insert dividend yield for Long Put Option or press enter to use default value: ')
            long_put_volatility = input('\nPlease insert the volatility for Long Put Option or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if long_put_risk_free == '':
                long_put_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if long_put_dividend_yield == '':
                long_put_dividend_yield = 0

            # If not provided, get implied volatility for given strike price
            if long_put_volatility == '':
                long_put_volatility = long_put_filtered_df.loc[long_put_strike]['IV']
            print('Implied volatility: ', long_put_volatility)

            # SHORT PUT
            print('\nPlease select a Strike Price and one Bid price per option for Short Put Option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'expiry' and 'put' 
            # multi-index levels and store into df
            short_put_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]

            # Get Bid and IV indexed by strike prices
            short_put_filtered_df = short_put_df.droplevel([1, 2, 3])[['Bid', 'IV']]

            # Replace NaN values by 0's
            short_put_filtered_df.fillna(0)
            print(short_put_filtered_df)

            # Provide strike price, ask price and # contracts
            short_put_strike = float(input('\nStrike Price: '))
            short_put_price = float(input('Bid Price: '))
            short_put_contracts = int(input('Please select the number of contracts for Short Put Option: '))

            # Calculate and show total cost for the option
            short_put_cost = round(short_put_price * short_put_contracts * 100, 2)
            print('\nTotal Cost for Short Put Option: ', short_put_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            short_put_risk_free = input('\nPlease insert risk-free rate for Short Put Option or press enter to use default value: ')
            short_put_dividend_yield = input('\nPlease insert dividend yield for Short Put Option or press enter to use default value: ')
            short_put_volatility = input('\nPlease insert the volatility for Short Put Option or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if short_put_risk_free == '':
                short_put_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if short_put_dividend_yield == '':
                short_put_dividend_yield = 0

            # If not provided, get implied volatility for given strike price
            if short_put_volatility == '':
                short_put_volatility = short_put_filtered_df.loc[short_put_strike]['IV']
            print('Implied volatility: ', short_put_volatility)
            
            # SHORT CALL
            print('\nPlease select a Strike Price and one Bid price per option for Short Call Option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            short_call_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]

            # Get Bid price and IV indexed by strike prices
            short_call_filtered_df = short_call_df.droplevel([1, 2, 3])[['Bid', 'IV']]

            # Replace NaN values by 0's
            short_call_filtered_df.fillna(0)
            print(short_call_filtered_df)

            # Provide strike price, ask price and # contracts
            short_call_strike = float(input('\nStrike Price: '))
            short_call_price = float(input('Bid Price: '))
            short_call_contracts = int(input('Please select the number of contracts for Short Call Option: '))

            # Calculate and show total cost for the option
            short_call_cost = round(short_call_price * short_call_contracts * 100, 2)
            print('\nTotal Cost for Short Call Option: ', short_call_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            short_call_risk_free = input('\nPlease insert risk-free rate for Short Call Option or press enter to use default value: ')
            short_call_dividend_yield = input('\nPlease insert dividend yield for Short Call Option or press enter to use default value: ')
            short_call_volatility = input('\nPlease insert the volatility for Short Call Option or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if short_call_risk_free == '':
                short_call_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if short_call_dividend_yield == '':
                short_call_dividend_yield = 0

            # If not provided, get implied volatility for given strike price
            if short_call_volatility == '':
                short_call_volatility = short_call_filtered_df.loc[short_call_strike]['IV']
            print('Implied volatility: ', short_call_volatility)

            # LONG CALL
            print('\nPlease select a Strike Price and one Ask price per option for Long Call Option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            long_call_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]

            # Get Ask price and IV indexed by strike prices
            long_call_filtered_df = long_call_df.droplevel([1, 2, 3])[['Ask', 'IV']]

            # Replace NaN values by 0's
            long_call_filtered_df.fillna(0)
            print(long_call_filtered_df)

            # Provide strike price, ask price and # contracts
            long_call_strike = float(input('\nStrike Price: '))
            long_call_price = float(input('Bid Price: '))
            long_call_contracts = int(input('Please select the number of contracts for Short Call Option: '))

            # Calculate and show total cost for the option
            long_call_cost = round(long_call_price * long_call_contracts * 100, 2)
            print('\nTotal Cost for Long Call Option: ', long_call_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            long_call_risk_free = input('\nPlease insert risk-free rate for Long Call Option or press enter to use default value: ')
            long_call_dividend_yield = input('\nPlease insert dividend yield for Long Call Option or press enter to use default value: ')
            long_call_volatility = input('\nPlease insert the volatility for Long Call Option or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if long_call_risk_free == '':
                long_call_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if long_call_dividend_yield == '':
                long_call_dividend_yield = 0

            # If not provided, get implied volatility for given strike price
            if long_call_volatility == '':
                long_call_volatility = long_call_filtered_df.loc[long_call_strike]['IV']
            print('Implied volatility: ', long_call_volatility)

            # Display results as table, graph or both
            print('\nPlease choose output for display results: \n')
            print('1 - Table')
            print('2 - Graph')
            print('3 - Both\n')
            graph_type = input('Output Type: ')
            try:
                if graph_type == '1':
                    graph_type = 'table'
                elif graph_type == '2':
                    graph_type = 'graph'
                elif graph_type == '3':
                    graph_type = 'both'
            except:
                print('Please provide a valid option.')

            # Select table/graph profile
            print('\nPlease choose a profile for display results: \n')
            print('1 - Profit/Loss (Dollar value)')
            print('2 - % of maximum risk')
            print('3 - Option/Spread value\n')
            graph_profile = input('Output Profile: ')
            try:
                if graph_profile == '1':
                    graph_profile = 'pnl'
                elif graph_profile == '2':
                    graph_profile = 'risk'
                elif graph_profile == '3':
                    graph_profile = 'option/spread'
            except:
                print('Please provide a valid option.')

            print('\nTable and Graphs with the results will be displayed on the browser')

            # call iron_condor() method from BSM calculator
            opt.iron_condor(
                spot_price=float(spot_price),
                expiration_date=str(expiry_date),
                long_put_price=float(long_put_price),
                long_put_strike_price=float(long_put_strike),
                long_put_risk_free_rate=float(long_put_risk_free),
                long_put_dividend_yield=float(long_put_dividend_yield),
                long_put_volatility=float(long_put_volatility),
                long_put_contracts=int(long_put_contracts),
                short_put_price=float(short_put_price),
                short_put_strike_price=float(short_put_strike),
                short_put_risk_free_rate=float(short_put_risk_free),
                short_put_dividend_yield=float(short_put_dividend_yield),
                short_put_volatility=float(short_put_volatility),
                short_put_contracts=int(short_put_contracts),
                short_call_price=float(short_call_price),
                short_call_strike_price=float(short_call_strike),
                short_call_risk_free_rate=float(short_call_risk_free),
                short_call_dividend_yield=float(short_call_dividend_yield),
                short_call_volatility=float(short_call_volatility),
                short_call_contracts=int(short_call_contracts),
                long_call_price=float(long_call_price),
                long_call_strike_price=float(long_call_strike),
                long_call_risk_free_rate=float(long_call_risk_free),
                long_call_dividend_yield=float(long_call_dividend_yield),
                long_call_volatility=float(long_call_volatility),
                long_call_contracts=int(long_call_contracts),
                graph_type=str(graph_type),
                graph_profile=str(graph_profile)
            )

        elif strategy == '2':

            # Provide # of shares or use 100 as default
            num_shares = input('\nPlease Insert Number of Shares or press enter to use # 100: ')
            if num_shares == '':
                num_shares = 100

            # LONG OPTION
            # Select option type for long option
            print('\nPlease choose an option type for Long option: \n')
            print('1 - Call')
            print('2 - Put\n')
            long_option_type = input('Option Type: ')

            print('\nPlease select a Strike Price and one Ask price per option for Long option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if long_option_type == '1':
                    long_option_type = 'call'
                    long_options_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                               & (all_data.index.get_level_values('Type') == 'call')]
                elif long_option_type == '2':
                    long_option_type = 'put'
                    long_options_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                               & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Ask and IV indexed by strike prices
            long_filtered_df = long_options_df.droplevel([1, 2, 3])[['Ask', 'IV']]

            # Replace NaN values by 0's
            long_filtered_df.fillna(0)
            print(long_filtered_df)

            # Provide strike price, ask price and # contracts
            long_strike = float(input('\nStrike Price: '))
            long_price = float(input('Ask Price: '))
            long_contracts = int(input('Please select the number of contracts for Long Option: '))

            # Calculate and show total cost for the option
            long_total_cost = round(long_price * long_contracts * 100, 2)
            print('\nTotal Cost for Long Option: ', long_total_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            long_risk_free = input('\nPlease insert risk-free rate for Long Option or press enter to use default value: ')
            long_dividend_yield = input('\nPlease insert dividend yield for Long Option or press enter to use default value: ')
            long_volatility = input('\nPlease insert the volatility for Long Option or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if long_risk_free == '':
                long_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if long_dividend_yield == '':
                long_dividend_yield = 0

            # If not provided, get implied volatility for given strike price
            if long_volatility == '':
                long_volatility = long_filtered_df.loc[long_strike]['IV']
            print('Implied volatility: ', long_volatility)

            # SHORT OPTION
            # Select option type for short option
            print('\nPlease choose an option type for Short option: \n')
            print('1 - Call')
            print('2 - Put\n')
            short_option_type = input('Option Type: ')

            print('\nPlease select a Strike Price and one Bid price per option for Short Option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if short_option_type == '1':
                    short_option_type = 'call'
                    short_options_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                                & (all_data.index.get_level_values('Type') == 'call')]
                elif short_option_type == '2':
                    short_option_type = 'put'
                    short_options_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                                & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid and IV indexed by strike prices
            short_filtered_df = short_options_df.droplevel([1, 2, 3])[['Bid', 'IV']]

            # Replace NaN values by 0's
            short_filtered_df.fillna(0)
            print(short_filtered_df)

            # Provide strike price, ask price and # contracts
            short_strike = float(input('\nStrike Price: '))
            short_price = float(input('Bid/Ask Price: '))
            short_contracts = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            short_total_cost = round(short_price * short_contracts * 100, 2)
            print('\nTotal Cost for Short Option: ', short_total_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            short_risk_free = input(
                '\nPlease insert risk-free rate for Short Option or press enter to use default value: ')
            short_dividend_yield = input(
                '\nPlease insert dividend yield for Short Option or press enter to use default value: ')
            short_volatility = input(
                '\nPlease insert the volatility for Short Option or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if short_risk_free == '':
                short_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if short_dividend_yield == '':
                short_dividend_yield = 0.0

            # If not provided, implied volatility for given strike price
            if short_volatility == '':
                short_volatility = short_filtered_df.loc[short_strike]['IV']
            print('Implied volatility: ', short_volatility)

            # Display results as table, graph or both
            print('\nPlease choose output for display results: \n')
            print('1 - Table')
            print('2 - Graph')
            print('3 - Both\n')
            graph_type = input('Output Type: ')
            try:
                if graph_type == '1':
                    graph_type = 'table'
                elif graph_type == '2':
                    graph_type = 'graph'
                elif graph_type == '3':
                    graph_type = 'both'
            except:
                print('Please provide a valid option.')

            # Select table/graph profile
            print('\nPlease choose a profile for display results: \n')
            print('1 - Profit/Loss (Dollar value)')
            print('2 - % of maximum risk')
            print('3 - Option/Spread value\n')
            graph_profile = input('Output Profile: ')
            try:
                if graph_profile == '1':
                    graph_profile = 'pnl'
                elif graph_profile == '2':
                    graph_profile = 'risk'
                elif graph_profile == '3':
                    graph_profile = 'option/spread'
            except:
                print('Please provide a valid option.')

            print('\nTable and Graphs with the results will be displayed on the browser')

            # call collar() method from BSM calculator
            opt.collar(
                spot_price=float(spot_price),
                expiration_date=str(expiry_date),
                num_shares=int(num_shares),
                long_contracts=int(long_contracts),
                long_price=float(long_price),
                long_type=str(long_option_type),
                long_strike_price=float(long_strike),
                long_risk_free_rate=float(long_risk_free),
                long_dividend_yield=float(long_dividend_yield),
                long_volatility=float(long_volatility),
                short_contracts=int(short_contracts),
                short_price=float(short_price),
                short_type=str(short_option_type),
                short_strike_price=float(short_strike),
                short_risk_free_rate=float(short_risk_free),
                short_dividend_yield=float(short_dividend_yield),
                short_volatility=float(short_volatility),
                graph_type=str(graph_type),
                graph_profile=str(graph_profile)
            )

        elif strategy == '3':

            # LONG PUT 
            print('\nPlease select a Strike Price and one Ask price per option for Long Put option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'expiry' and 'put' 
            # multi-index levels and store into df
            long_put_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]

            # Get Ask price and IV indexed by strike prices
            long_put_filtered_df = long_put_df.droplevel([1, 2, 3])[['Ask', 'IV']]

            # Replace NaN values by 0's
            long_put_filtered_df.fillna(0)
            print(long_put_filtered_df)

            # Provide strike price, ask price and # contracts
            long_put_strike = float(input('\nStrike Price: '))
            long_put_price = float(input('Ask Price: '))
            long_put_contracts = int(input('Please select the number of contracts for Long Put Option: '))

            # Calculate and show total cost for the option
            long_put_cost = round(long_put_price * long_put_contracts * 100, 2)
            print('\nTotal Cost for Long Put Option: ', long_put_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            long_put_risk_free = input('\nPlease insert risk-free rate for Long Put Option or press enter to use default value: ')
            long_put_dividend_yield = input('\nPlease insert dividend yield for Long Put Option or press enter to use default value: ')
            long_put_volatility = input('\nPlease insert the volatility for Long Put Option or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if long_put_risk_free == '':
                long_put_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if long_put_dividend_yield == '':
                long_put_dividend_yield = 0

            # If not provided, get implied volatility for given strike price
            if long_put_volatility == '':
                long_put_volatility = long_put_filtered_df.loc[long_put_strike]['IV']
            print('Implied volatility: ', long_put_volatility)

            # SHORT PUT
            print('\nPlease select a Strike Price and one Bid price per option for Short Put Option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            short_put_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]

            # Get Bid  and IV indexed by strike prices
            short_put_filtered_df = short_put_df.droplevel([1, 2, 3])[['Bid', 'IV']]

            # Replace NaN values by 0's
            short_put_filtered_df.fillna(0)
            print(short_put_filtered_df)

            # Provide strike price, ask price and # contracts
            short_put_strike = float(input('\nStrike Price: '))
            short_put_price = float(input('Bid Price: '))
            short_put_contracts = int(input('Please select the number of contracts for Short Put Option: '))

            # Calculate and show total cost for the option
            short_put_cost = round(short_put_price * short_put_contracts * 100, 2)
            print('\nTotal Cost for Short Put Option: ', short_put_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            short_put_risk_free = input('\nPlease insert risk-free rate for Short Put Option or press enter to use default value: ')
            short_put_dividend_yield = input('\nPlease insert dividend yield for Short Put Option or press enter to use default value: ')
            short_put_volatility = input('\nPlease insert the volatility for Short Put Option or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if short_put_risk_free == '':
                short_put_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if short_put_dividend_yield == '':
                short_put_dividend_yield = 0

            # If not provided, get implied volatility for given strike price
            if short_put_volatility == '':
                short_put_volatility = short_put_filtered_df.loc[short_put_strike]['IV']
            print('Implied volatility: ', short_put_volatility)

            # SHORT CALL
            print('\nPlease select a Strike Price and one Bid price per option for Short Call Option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            short_call_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]

            # Get Bid price and IV indexed by strike prices
            short_call_filtered_df = short_call_df.droplevel([1, 2, 3])[['Bid', 'IV']]

            # Replace NaN values by 0's
            short_call_filtered_df.fillna(0)
            print(short_call_filtered_df)

            # Provide strike price, bid price and # contracts
            short_call_strike = float(input('\nStrike Price: '))
            short_call_price = float(input('Bid Price: '))
            short_call_contracts = int(input('Please select the number of contracts for Short Call Option: '))

            # Calculate and show total cost for the option
            short_call_cost = round(short_call_price * short_call_contracts * 100, 2)
            print('\nTotal Cost for Short Call Option: ', short_call_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            short_call_risk_free = input('\nPlease insert risk-free rate for Short Call Option or press enter to use default value: ')
            short_call_dividend_yield = input('\nPlease insert dividend yield for Short Call Option or press enter to use default value: ')
            short_call_volatility = input('\nPlease insert the volatility for Short Call Option or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if short_call_risk_free == '':
                short_call_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if short_call_dividend_yield == '':
                short_call_dividend_yield = 0

            # If not provided, get implied volatility for given strike price
            if short_call_volatility == '':
                short_call_volatility = short_call_filtered_df.loc[short_call_strike]['IV']
            print('Implied volatility: ', short_call_volatility)

            # LONG CALL
            print('\nPlease select a Strike Price and one Ask price per option for Long Call Option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            long_call_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                & (all_data.index.get_level_values('Type') == 'call')]

            # Get Ask price and IV indexed by strike prices
            long_call_filtered_df = long_call_df.droplevel([1, 2, 3])[['Ask', 'IV']]

            # Replace NaN values by 0's
            long_call_filtered_df.fillna(0)
            print(long_call_filtered_df)

            # Provide strike price, ask price and # contracts
            long_call_strike = float(input('\nStrike Price: '))
            long_call_price = float(input('Bid Price: '))
            long_call_contracts = int(input('Please select the number of contracts for Short Call Option: '))

            # Calculate and show total cost for the option
            long_call_cost = round(long_call_price * long_call_contracts * 100, 2)
            print('\nTotal Cost for Long Call Option: ', long_call_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            long_call_risk_free = input('\nPlease insert risk-free rate for Long Call Option or press enter to use default value: ')
            long_call_dividend_yield = input('\nPlease insert dividend yield for Long Call Option or press enter to use default value: ')
            long_call_volatility = input('\nPlease insert the volatility for Long Call Option or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if long_call_risk_free == '':
                long_call_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if long_call_dividend_yield == '':
                long_call_dividend_yield = 0

            # If not provided, get implied volatility for given strike price
            if long_call_volatility == '':
                long_call_volatility = long_call_filtered_df.loc[long_call_strike]['IV']
            print('Implied volatility: ', long_call_volatility)

            # Display results as table, graph or both
            print('\nPlease choose output for display results: \n')
            print('1 - Table')
            print('2 - Graph')
            print('3 - Both\n')
            graph_type = input('Output Type: ')
            try:
                if graph_type == '1':
                    graph_type = 'table'
                elif graph_type == '2':
                    graph_type = 'graph'
                elif graph_type == '3':
                    graph_type = 'both'
            except:
                print('Please provide a valid option.')

            # Select table/graph profile
            print('\nPlease choose a profile for display results: \n')
            print('1 - Profit/Loss (Dollar value)')
            print('2 - % of maximum risk')
            print('3 - Option/Spread value\n')
            graph_profile = input('Output Profile: ')
            try:
                if graph_profile == '1':
                    graph_profile = 'pnl'
                elif graph_profile == '2':
                    graph_profile = 'risk'
                elif graph_profile == '3':
                    graph_profile = 'option/spread'
            except:
                print('Please provide a valid option.')

            print('\nTable and Graphs with the results will be displayed on the browser')

            # call iron_condor() method from BSM calculator
            opt.double_diagonal(
                spot_price=float(spot_price),
                expiration_date=str(expiry_date),
                long_put_price=float(long_put_price),
                long_put_strike_price=float(long_put_strike),
                long_put_risk_free_rate=float(long_put_risk_free),
                long_put_dividend_yield=float(long_put_dividend_yield),
                long_put_volatility=float(long_put_volatility),
                long_put_contracts=int(long_put_contracts),
                short_put_price=float(short_put_price),
                short_put_strike_price=float(short_put_strike),
                short_put_risk_free_rate=float(short_put_risk_free),
                short_put_dividend_yield=float(short_put_dividend_yield),
                short_put_volatility=float(short_put_volatility),
                short_put_contracts=int(short_put_contracts),
                short_call_price=float(short_call_price),
                short_call_strike_price=float(short_call_strike),
                short_call_risk_free_rate=float(short_call_risk_free),
                short_call_dividend_yield=float(short_call_dividend_yield),
                short_call_volatility=float(short_call_volatility),
                short_call_contracts=int(short_call_contracts),
                long_call_price=float(long_call_price),
                long_call_strike_price=float(long_call_strike),
                long_call_risk_free_rate=float(long_call_risk_free),
                long_call_dividend_yield=float(long_call_dividend_yield),
                long_call_volatility=float(long_call_volatility),
                long_call_contracts=int(long_call_contracts),
                graph_type=str(graph_type),
                graph_profile=str(graph_profile)
            )

        elif strategy == '4':

            # LONG CALL
            print('\nPlease select a Strike Price and one Ask price per option for Long Call Option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'expiry' and 'put'
            # multi-index levels and store into df
            long_call_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                    & (all_data.index.get_level_values('Type') == 'call')]

            # Get Ask price and IV indexed by strike prices
            long_call_filtered_df = long_call_df.droplevel([1, 2, 3])[['Ask', 'IV']]

            # Replace NaN values by 0's
            long_call_filtered_df.fillna(0)
            print(long_call_filtered_df)

            # Provide strike price, ask price and # contracts
            long_call_strike = float(input('\nStrike Price: '))
            long_call_price = float(input('Bid Price: '))
            long_call_contracts = int(input('Please select the number of contracts for Short Call Option: '))

            # Calculate and show total cost for the option
            long_call_cost = round(long_call_price * long_call_contracts * 100, 2)
            print('\nTotal Cost for Long Call Option: ', long_call_cost)

            long_call_risk_free = input(
                '\nPlease insert risk-free rate for Long Call Option or press enter to use default value: ')
            long_call_dividend_yield = input(
                '\nPlease insert dividend yield for Long Call Option or press enter to use default value: ')
            long_call_volatility = input(
                '\nPlease insert the volatility for Long Call Option or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if long_call_risk_free == '':
                long_call_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if long_call_dividend_yield == '':
                long_call_dividend_yield = 0

            # If not provided, get implied volatility for given strike price
            if long_call_volatility == '':
                long_call_volatility = long_call_filtered_df.loc[long_call_strike]['IV']
            print('Implied volatility: ', long_call_volatility)

            # LONG PUT 
            print('\nPlease select a Strike Price and one Ask price per option for Long Put option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'expiry' and 'put' 
            # multi-index levels and store into df
            long_put_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]

            # Get Ask and IV indexed by strike prices
            long_put_filtered_df = long_put_df.droplevel([1, 2, 3])[['Ask', 'IV']]

            # Replace NaN values by 0's
            long_put_filtered_df.fillna(0)
            print(long_put_filtered_df)

            # Provide strike price, ask price and # contracts
            long_put_strike = float(input('\nStrike Price: '))
            long_put_price = float(input('Ask Price: '))
            long_put_contracts = int(input('Please select the number of contracts for Long Put Option: '))

            # Calculate and show total cost for the option
            long_put_cost = round(long_put_price * long_put_contracts * 100, 2)
            print('\nTotal Cost for Long Put Option: ', long_put_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            long_put_risk_free = input('\nPlease insert risk-free rate for Long Put Option or press enter to use default value: ')
            long_put_dividend_yield = input('\nPlease insert dividend yield for Long Put Option or press enter to use default value: ')
            long_put_volatility = input('\nPlease insert the volatility for Long Put Option or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if long_put_risk_free == '':
                long_put_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if long_put_dividend_yield == '':
                long_put_dividend_yield = 0

            # If not provided, get implied volatility for given strike price
            if long_put_volatility == '':
                long_put_volatility = long_put_filtered_df.loc[long_put_strike]['IV']
            print('Implied volatility: ', long_put_volatility)

            # Display results as table, graph or both
            print('\nPlease choose output for display results: \n')
            print('1 - Table')
            print('2 - Graph')
            print('3 - Both\n')
            graph_type = input('Output Type: ')
            try:
                if graph_type == '1':
                    graph_type = 'table'
                elif graph_type == '2':
                    graph_type = 'graph'
                elif graph_type == '3':
                    graph_type = 'both'
            except:
                print('Please provide a valid option.')

            # Select table/graph profile
            print('\nPlease choose a profile for display results: \n')
            print('1 - Profit/Loss (Dollar value)')
            print('2 - % of maximum risk')
            print('3 - Option/Spread value\n')
            graph_profile = input('Output Profile: ')
            try:
                if graph_profile == '1':
                    graph_profile = 'pnl'
                elif graph_profile == '2':
                    graph_profile = 'risk'
                elif graph_profile == '3':
                    graph_profile = 'option/spread'
            except:
                print('Please provide a valid option.')

            print('\nTable and Graphs with the results will be displayed on the browser')

            # call strangle() method from BSM calculator
            opt.strangle(
                spot_price=float(spot_price),
                expiration_date=str(expiry_date),
                long_call_contracts=int(long_call_contracts),
                long_call_price=str(long_call_price),
                long_call_strike_price=float(long_call_strike),
                long_call_risk_free_rate=float(long_call_risk_free),
                long_call_dividend_yield=float(long_call_dividend_yield),
                long_call_volatility=float(long_call_volatility),
                long_put_contracts=int(long_put_contracts),
                long_put_price=float(long_put_price),
                long_put_strike_price=float(long_put_strike),
                long_put_risk_free_rate=float(long_put_risk_free),
                long_put_dividend_yield=float(long_put_dividend_yield),
                long_put_volatility=float(long_put_volatility),
                graph_type=str(graph_type),
                graph_profile=str(graph_profile)
            )

        elif strategy == '5':

            # Provide # of shares or use 100 as default
            num_shares = input('\nPlease Insert Number of Shares or press enter to use # 100: ')
            if num_shares == '':
                num_shares = 100

            # Select buy or write
            print('\nPlease select Buy or Write: \n')
            print('1 - Buy')
            print('2 - Write\n')
            buy_write = input('Buy or Write: ')
            try:
                if buy_write == '1':
                    buy_write = 'buy'
                elif buy_write == '2':
                    buy_write = 'write'
            except ValueError:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type == '1':
                    option_type = 'call'
                    options_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type == '2':
                    option_type = 'put'
                    options_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df = options_df.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df.fillna(0)
            print(filtered_df)

            # Provide strike price, ask price and # contracts
            option_strike = float(input('\nStrike Price: '))
            option_price = float(input('Bid/Ask Price: '))
            option_contracts = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost = round(option_price * option_contracts * 100, 2)
            print('\nTotal Cost: ', total_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free == '':
                risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield == '':
                dividend_yield = 0

            # If not provided, implied volatility for given strike price
            if volatility == '':
                volatility = filtered_df.loc[option_strike]['IV']
            print('Implied volatility: ', volatility)

            # Display results as table, graph or both
            print('\nPlease choose output for display results: \n')
            print('1 - Table')
            print('2 - Graph')
            print('3 - Both\n')
            graph_type = input('Output Type: ')
            try:
                if graph_type == '1':
                    graph_type = 'table'
                elif graph_type == '2':
                    graph_type = 'graph'
                elif graph_type == '3':
                    graph_type = 'both'
            except:
                print('Please provide a valid option.')

            # Select table/graph profile
            print('\nPlease choose a profile for display results: \n')
            print('1 - Profit/Loss (Dollar value)')
            print('2 - % of maximum risk')
            print('3 - Option/Spread value\n')
            graph_profile = input('Output Profile: ')
            try:
                if graph_profile == '1':
                    graph_profile = 'pnl'
                elif graph_profile == '2':
                    graph_profile = 'risk'
                elif graph_profile == '3':
                    graph_profile = 'option/spread'
            except:
                print('Please provide a valid option.')

            print('\nTable and Graphs with the results will be displayed on the browser')

            # call synthetic_put() method from BSM calculator
            opt.synthetic_put(
                num_shares=int(num_shares),
                spot_price=float(spot_price),
                expiration_date=str(expiry_date),
                contracts=int(option_contracts),
                option_price=float(option_price),
                strike_price=float(option_strike),
                risk_free_rate=float(risk_free),
                dividend_yield=float(dividend_yield),
                volatility=float(volatility),
                graph_type=str(graph_type),
                graph_profile=str(graph_profile)
            )

        elif strategy == '6':

            # Lower Wing
            print('\nPlease choose an option type for Lower wing option: \n')
            print('1 - Call')
            print('2 - Put\n')
            lower_type = input('Lower wing option type: ')

            print('\nPlease select a Strike Price and one Ask price per option for Lower wing option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if lower_type == '1':
                    lower_type = 'call'
                    lower_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                               & (all_data.index.get_level_values('Type') == 'call')]
                elif lower_type == '2':
                    lower_type = 'put'
                    lower_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                               & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Ask price and IV indexed by strike prices
            lower_filtered_df = lower_df.droplevel([1, 2, 3])[['Ask', 'IV']]

            # Replace NaN values by 0's
            lower_filtered_df.fillna(0)
            print(lower_filtered_df)

            # Provide strike price, ask price and # contracts
            lower_strike = float(input('\nLower wing Strike Price: '))
            lower_price = float(input('Lower wing Ask Price: '))
            lower_contracts = int(input('Please select the number of contracts for Lower wing option: '))

            # Calculate and show total cost for the option
            lower_cost = round(lower_price * lower_contracts * 100, 2)
            print('\nTotal Cost for Long wing: ', lower_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            lower_risk_free = input(
                '\nPlease insert risk-free rate for Lower Wing or press enter to use default value: ')
            lower_dividend_yield = input(
                '\nPlease insert dividend yield for Lower Wing or press enter to use default value: ')
            lower_volatility = input(
                '\nPlease insert the volatility for Lower Wing or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if lower_risk_free == '':
                lower_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if lower_dividend_yield == '':
                lower_dividend_yield = 0

            # If not provided, implied volatility for given strike price
            if lower_volatility == '':
                lower_volatility = lower_filtered_df.loc[lower_strike]['IV']
            print('Implied volatility: ', lower_volatility)

            # Middle Wing
            print('\nPlease choose an option type for Middle wing option: \n')
            print('1 - Call')
            print('2 - Put\n')
            middle_type = input('Middle wing option Type: ')

            print('\nPlease select a Strike Price and one Bid price per option for Middle wing option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if middle_type == '1':
                    short_type = 'call'
                    middle_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                                & (all_data.index.get_level_values('Type') == 'call')]
                elif middle_type == '2':
                    short_type = 'put'
                    # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
                    # multi-index levels and store into df
                    middle_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                                & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid price and IV indexed by strike prices
            middle_filtered_df = middle_df.droplevel([1, 2, 3])[['Bid', 'IV']]

            # Replace NaN values by 0's
            middle_filtered_df.fillna(0)
            print(middle_filtered_df)

            # Provide strike price, ask price and # contracts
            middle_strike = float(input('\nMiddle wing Strike Price: '))
            middle_price = float(input('Middle wing Bid Price: '))
            middle_contracts = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option. Middle implies # contracts * 2
            middle_cost = round(middle_price * middle_contracts * 2 * 100, 2)
            print('\nTotal Cost for Middle wing: ', middle_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            middle_risk_free = input(
                '\nPlease insert risk-free rate for Short Option or press enter to use default value: ')
            middle_dividend_yield = input(
                '\nPlease insert dividend yield for Short Option or press enter to use default value: ')
            middle_volatility = input(
                '\nPlease insert the volatility for Short Option or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if middle_risk_free == '':
                middle_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if middle_dividend_yield == '':
                middle_dividend_yield = 0.0

            # If not provided, get implied volatility for given strike price
            if middle_volatility == '':
                middle_volatility = middle_filtered_df.loc[middle_strike]['IV']
            print('Implied volatility: ', middle_volatility)

            # Upper Wing
            print('\nPlease choose an option type for Upper wing option: \n')
            print('1 - Call')
            print('2 - Put\n')
            upper_type = input('Upper wing option type: ')

            print('\nPlease select a Strike Price and one Ask price per option for Upper wing option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if upper_type == '1':
                    upper_type = 'call'
                    upper_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                               & (all_data.index.get_level_values('Type') == 'call')]
                elif upper_type == '2':
                    upper_type = 'put'
                    upper_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                               & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Ask price and IV indexed by strike prices
            upper_filtered_df = upper_df.droplevel([1, 2, 3])[['Ask', 'IV']]

            # Replace NaN values by 0's
            upper_filtered_df.fillna(0)
            print(upper_filtered_df)

            # Provide strike price, ask price and # contracts
            upper_strike = float(input('\nUpper wing Strike Price: '))
            upper_price = float(input('Upper wing Ask Price: '))
            upper_contracts = int(input('Please select the number of contracts for Lower wing option: '))

            # Calculate and show total cost for the option
            upper_cost = round(upper_price * upper_contracts * 100, 2)
            print('\nTotal Cost for Upper wing: ', upper_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            upper_risk_free = input(
                '\nPlease insert risk-free rate for Lower Wing or press enter to use default value: ')
            upper_dividend_yield = input(
                '\nPlease insert dividend yield for Lower Wing or press enter to use default value: ')
            upper_volatility = input(
                '\nPlease insert the volatility for Lower Wing or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if upper_risk_free == '':
                upper_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if upper_dividend_yield == '':
                upper_dividend_yield = 0

            # If not provided, get implied volatility for given strike price
            if upper_volatility == '':
                upper_volatility = upper_filtered_df.loc[upper_strike]['IV']
            print('Implied volatility: ', upper_volatility)

            # Display results as table, graph or both
            print('\nPlease choose output for display results: \n')
            print('1 - Table')
            print('2 - Graph')
            print('3 - Both\n')
            graph_type = input('Output Type: ')
            try:
                if graph_type == '1':
                    graph_type = 'table'
                elif graph_type == '2':
                    graph_type = 'graph'
                elif graph_type == '3':
                    graph_type = 'both'
            except:
                print('Please provide a valid option.')

            # Select table/graph profile
            print('\nPlease choose a profile for display results: \n')
            print('1 - Profit/Loss (Dollar value)')
            print('2 - % of maximum risk')
            print('3 - Option/Spread value\n')
            graph_profile = input('Output Profile: ')
            try:
                if graph_profile == '1':
                    graph_profile = 'pnl'
                elif graph_profile == '2':
                    graph_profile = 'risk'
                elif graph_profile == '3':
                    graph_profile = 'option/spread'
            except:
                print('Please provide a valid option.')

            print('\nTable and Graphs with the results will be displayed on the browser')

            # Call butterfly() method from BSM calculator
            opt.butterfly(
                spot_price=float(spot_price), 
                expiration_date=str(expiry_date),
                lower_contracts=int(lower_contracts),
                lower_price=float(lower_price),
                lower_option=str(lower_type),
                lower_strike_price=float(lower_strike),
                lower_risk_free_rate=float(lower_risk_free),
                lower_dividend_yield=float(lower_dividend_yield),
                lower_volatility=float(lower_volatility),
                middle_contracts=int(middle_contracts),
                middle_price=float(middle_price),
                middle_option=str(middle_type),
                middle_strike_price=float(middle_strike),
                middle_risk_free_rate=float(middle_risk_free),
                middle_dividend_yield=float(middle_dividend_yield),
                middle_volatility=float(middle_volatility),
                upper_contracts=int(upper_contracts),
                upper_price=float(upper_price),
                upper_option=str(upper_type),
                upper_strike_price=str(upper_strike),
                upper_risk_free_rate=float(upper_risk_free),
                upper_dividend_yield=float(upper_dividend_yield),
                upper_volatility=float(upper_volatility),
                graph_type=str(graph_type),
                graph_profile=str(graph_profile)
            )

        elif strategy == '7':

            # Long option
            print('\nPlease choose an option type for Long (Back-month) option: \n')
            print('1 - Call')
            print('2 - Put\n')
            long_type = input('Option Type: ')

            print('\nPlease select a Strike Price and one Ask price per option for Long option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if long_type == '1':
                    long_type = 'call'
                    long_options_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                               & (all_data.index.get_level_values('Type') == 'call')]
                elif long_type == '2':
                    long_type = 'put'
                    long_options_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                               & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Ask price and IV indexed by strike prices
            long_filtered_df = long_options_df.droplevel([1, 2, 3])[['Ask', 'IV']]

            # Replace NaN values by 0's
            long_filtered_df.fillna(0)
            print(long_filtered_df)

            # Provide strike price, ask price and # contracts
            long_strike = float(input('\nStrike Price: '))
            long_price = float(input('Ask Price: '))
            long_contracts = int(input('Please select the number of contracts for Long Option: '))

            # Calculate and show total cost for the option
            long_total_cost = round(long_price * long_contracts * 100, 2)
            print('\nTotal Cost for Long Option: ', long_total_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            long_risk_free = input(
                '\nPlease insert risk-free rate for Long Option or press enter to use default value: ')
            long_dividend_yield = input(
                '\nPlease insert dividend yield for Long Option or press enter to use default value: ')
            long_volatility = input(
                '\nPlease insert the volatility for Long Option or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if long_risk_free == '':
                long_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if long_dividend_yield == '':
                long_dividend_yield = 0

            # If not provided, get implied volatility for given strike price
            if long_volatility == '':
                long_volatility = long_filtered_df.loc[long_strike]['IV']
            print('Implied volatility: ', long_volatility)

            # Short option
            print('\nPlease choose an option type for Short (Front-month) option: \n')
            print('1 - Call')
            print('2 - Put\n')
            short_option_type = input('Option Type: ')

            print('\nPlease select a Strike Price and one Bid price per option for Short Option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if short_option_type == '1':
                    short_option_type = 'call'
                    short_options_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                                & (all_data.index.get_level_values('Type') == 'call')]
                elif short_option_type == '2':
                    short_option_type = 'put'
                    short_options_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                                & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid price and IV indexed by strike prices
            short_filtered_df = short_options_df.droplevel([1, 2, 3])[['Bid', 'IV']]

            # Replace NaN values by 0's
            short_filtered_df.fillna(0)
            print(short_filtered_df)

            # Provide strike price, ask price and # contracts
            short_strike = float(input('\nStrike Price: '))
            short_price = float(input('Bid/Ask Price: '))
            short_contracts = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            short_total_cost = round(short_price * short_contracts * 100, 2)
            print('\nTotal Cost for Short Option: ', short_total_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            short_risk_free = input(
                '\nPlease insert risk-free rate for Short Option or press enter to use default value: ')
            short_dividend_yield = input(
                '\nPlease insert dividend yield for Short Option or press enter to use default value: ')
            short_volatility = input(
                '\nPlease insert the volatility for Short Option or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if short_risk_free == '':
                short_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if short_dividend_yield == '':
                short_dividend_yield = 0.0

            # If not provided, get implied volatility for given strike price
            if short_volatility == '':
                short_volatility = short_filtered_df.loc[short_strike]['IV']
            print('Implied volatility: ', short_volatility)

            # Display results as table, graph or both
            print('\nPlease choose output for display results: \n')
            print('1 - Table')
            print('2 - Graph')
            print('3 - Both\n')
            graph_type = input('Output Type: ')
            try:
                if graph_type == '1':
                    graph_type = 'table'
                elif graph_type == '2':
                    graph_type = 'graph'
                elif graph_type == '3':
                    graph_type = 'both'
            except:
                print('Please provide a valid option.')

            # Select table/graph profile
            print('\nPlease choose a profile for display results: \n')
            print('1 - Profit/Loss (Dollar value)')
            print('2 - % of maximum risk')
            print('3 - Option/Spread value\n')
            graph_profile = input('Output Profile: ')
            try:
                if graph_profile == '1':
                    graph_profile = 'pnl'
                elif graph_profile == '2':
                    graph_profile = 'risk'
                elif graph_profile == '3':
                    graph_profile = 'option/spread'
            except:
                print('Please provide a valid option.')

            print('\nTable and Graphs with the results will be displayed on the browser')

            # call collar() method from BSM calculator
            opt.diagonal_spread(
                spot_price=float(spot_price),
                expiration_date=str(expiry_date),
                long_contracts=int(long_contracts),
                long_price=float(long_price),
                long_type=str(long_type),
                long_strike_price=float(long_strike),
                long_risk_free_rate=float(long_risk_free),
                long_dividend_yield=float(long_dividend_yield),
                long_volatility=float(long_volatility),
                short_contracts=int(short_contracts),
                short_price=float(short_price),
                short_type=str(short_option_type),
                short_strike_price=float(short_strike),
                short_risk_free_rate=float(short_risk_free),
                short_dividend_yield=float(short_dividend_yield),
                short_volatility=float(short_volatility),
                graph_type=str(graph_type),
                graph_profile=str(graph_profile)
            )

        elif strategy == '8':

            # LONG CALL
            print('\nPlease select a Strike Price and one Ask price per option for Long Call Option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            long_call_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]

            # Get Ask price and IV indexed by strike prices
            long_call_filtered_df = long_call_df.droplevel([1, 2, 3])[['Ask', 'IV']]

            # Replace NaN values by 0's
            long_call_filtered_df.fillna(0)
            print(long_call_filtered_df)

            # Provide strike price, ask price and # contracts
            strike_price = float(input('\nStrike Price for long call and long put: '))
            long_call_price = float(input('Bid Price: '))
            long_call_contracts = int(input('Please select the number of contracts for Short Call Option: '))

            # Calculate and show total cost for the option
            long_call_cost = round(long_call_price * long_call_contracts * 100, 2)
            print('\nTotal Cost for Long Call Option: ', long_call_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            long_call_risk_free = input('\nPlease insert risk-free rate for Long Call Option or press enter to use default value: ')
            long_call_dividend_yield = input('\nPlease insert dividend yield for Long Call Option or press enter to use default value: ')
            long_call_volatility = input('\nPlease insert the volatility for Long Call Option or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if long_call_risk_free == '':
                long_call_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if long_call_dividend_yield == '':
                long_call_dividend_yield = 0

            # If not provided, implied volatility for given strike price
            if long_call_volatility == '':
                long_call_volatility = long_call_filtered_df.loc[strike_price]['IV']
            print('Implied volatility: ', long_call_volatility)

            # LONG PUT 
            print('\nPlease select one Ask price per option for Long Put option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            long_put_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]

            # Get Ask price and IV indexed by strike prices
            long_put_filtered_df = long_put_df.droplevel([1, 2, 3])[['Ask', 'IV']]

            # Replace NaN values by 0's
            long_put_filtered_df.fillna(0)
            print(long_put_filtered_df)

            # Provide ask price and # contracts
            long_put_price = float(input('Ask Price: '))
            long_put_contracts = int(input('Please select the number of contracts for Long Put Option: '))

            # Calculate and show total cost for the option
            long_put_cost = round(long_put_price * long_put_contracts * 100, 2)
            print('\nTotal Cost for Long Put Option: ', long_put_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            long_put_risk_free = input('\nPlease insert risk-free rate for Long Put Option or press enter to use default value: ')
            long_put_dividend_yield = input('\nPlease insert dividend yield for Long Put Option or press enter to use default value: ')
            long_put_volatility = input('\nPlease insert the volatility for Long Put Option or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if long_put_risk_free == '':
                long_put_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if long_put_dividend_yield == '':
                long_put_dividend_yield = 0

            # If not provided, implied volatility for given strike price
            if long_put_volatility == '':
                long_put_volatility = long_put_filtered_df.loc[strike_price]['IV']
            print('Implied volatility: ', long_put_volatility)

            # Display results as table, graph or both
            print('\nPlease choose output for display results: \n')
            print('1 - Table')
            print('2 - Graph')
            print('3 - Both\n')
            graph_type = input('Output Type: ')
            try:
                if graph_type == '1':
                    graph_type = 'table'
                elif graph_type == '2':
                    graph_type = 'graph'
                elif graph_type == '3':
                    graph_type = 'both'
            except:
                print('Please provide a valid option.')

            # Select table/graph profile
            print('\nPlease choose a profile for display results: \n')
            print('1 - Profit/Loss (Dollar value)')
            print('2 - % of maximum risk')
            print('3 - Option/Spread value\n')
            graph_profile = input('Output Profile: ')
            try:
                if graph_profile == '1':
                    graph_profile = 'pnl'
                elif graph_profile == '2':
                    graph_profile = 'risk'
                elif graph_profile == '3':
                    graph_profile = 'option/spread'
            except:
                print('Please provide a valid option.')

            print('\nTable and Graphs with the results will be displayed on the browser')

            # Call straddle() method from BSM calculator
            opt.straddle(
                spot_price=float(spot_price),
                expiration_date=str(expiry_date),
                strike_price=float(strike_price),
                long_call_contracts=int(long_call_contracts),
                long_call_price=float(long_call_price),
                long_call_risk_free_rate=float(long_call_risk_free),
                long_call_dividend_yield=float(long_call_dividend_yield),
                long_call_volatility=float(long_call_volatility),
                long_put_contracts=int(long_put_contracts),
                long_put_price=float(long_put_price),
                long_put_risk_free_rate=float(long_put_risk_free),
                long_put_dividend_yield=float(long_put_dividend_yield),
                long_put_volatility=float(long_put_volatility),
                graph_type=str(graph_type),
                graph_profile=str(graph_profile)
            )

        elif strategy == '9':

            # Provide # of shares or use 100 as default
            num_shares = input('\nPlease Insert Number of Shares or press enter to use # 100: ')
            if num_shares == '':
                num_shares = 100

            # SHORT CALL
            print('\nPlease select a Strike Price and one Bid price per option for Short Call Option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            short_call_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]

            # Get Bid price and IV indexed by strike prices
            short_call_filtered_df = short_call_df.droplevel([1, 2, 3])[['Bid', 'IV']]

            # Replace NaN values by 0's
            short_call_filtered_df.fillna(0)
            print(short_call_filtered_df)

            # Provide strike price, ask price and # contracts
            short_call_strike = float(input('\nStrike Price: '))
            short_call_price = float(input('Bid Price: '))
            short_call_contracts = int(input('Please select the number of contracts for Short Call Option: '))

            # Calculate and show total cost for the option
            short_call_cost = round(short_call_price * short_call_contracts * 100, 2)
            print('\nTotal Cost for Short Call Option: ', short_call_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            short_call_risk_free = input('\nPlease insert risk-free rate for Short Call Option or press enter to use default value: ')
            short_call_dividend_yield = input('\nPlease insert dividend yield for Short Call Option or press enter to use default value: ')
            short_call_volatility = input('\nPlease insert the volatility for Short Call Option or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if short_call_risk_free == '':
                short_call_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if short_call_dividend_yield == '':
                short_call_dividend_yield = 0

            # If not provided, get implied volatility for given strike price
            if short_call_volatility == '':
                short_call_volatility = short_call_filtered_df.loc[short_call_strike]['IV']

            print('Implied volatility: ', short_call_volatility)

            # SHORT PUT
            print('\nPlease select a Strike Price and one Bid price per option for Short Put Option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            short_put_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]

            # Get Bid price and IV indexed by strike prices
            short_put_filtered_df = short_put_df.droplevel([1, 2, 3])[['Bid', 'IV']]

            # Replace NaN values by 0's
            short_put_filtered_df.fillna(0)
            print(short_put_filtered_df)

            # Provide strike price, ask price and # contracts
            short_put_strike = float(input('\nStrike Price: '))
            short_put_price = float(input('Bid Price: '))
            short_put_contracts = int(input('Please select the number of contracts for Short Put Option: '))

            # Calculate and show total cost for the option
            short_put_cost = round(short_put_price * short_put_contracts * 100, 2)
            print('\nTotal Cost for Short Put Option: ', short_put_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            short_put_risk_free = input('\nPlease insert risk-free rate for Short Put Option or press enter to use default value: ')
            short_put_dividend_yield = input('\nPlease insert dividend yield for Short Put Option or press enter to use default value: ')
            short_put_volatility = input('\nPlease insert the volatility for Short Put Option or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if short_put_risk_free == '':
                short_put_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if short_put_dividend_yield == '':
                short_put_dividend_yield = 0

            # If not provided, get implied volatility for given strike price
            if short_put_volatility == '':
                short_put_volatility = short_put_filtered_df.loc[short_put_strike]['IV']
            print('Implied volatility: ', short_put_volatility)

            # Display results as table, graph or both
            print('\nPlease choose output for display results: \n')
            print('1 - Table')
            print('2 - Graph')
            print('3 - Both\n')
            graph_type = input('Output Type: ')
            try:
                if graph_type == '1':
                    graph_type = 'table'
                elif graph_type == '2':
                    graph_type = 'graph'
                elif graph_type == '3':
                    graph_type = 'both'
            except:
                print('Please provide a valid option.')

            # Select table/graph profile
            print('\nPlease choose a profile for display results: \n')
            print('1 - Profit/Loss (Dollar value)')
            print('2 - % of maximum risk')
            print('3 - Option/Spread value\n')
            graph_profile = input('Output Profile: ')
            try:
                if graph_profile == '1':
                    graph_profile = 'pnl'
                elif graph_profile == '2':
                    graph_profile = 'risk'
                elif graph_profile == '3':
                    graph_profile = 'option/spread'
            except:
                print('Please provide a valid option.')

            print('\nTable and Graphs with the results will be displayed on the browser')

            # Call covered_strangle() method from BSM calculator
            opt.covered_strangle(
                spot_price=float(spot_price),
                expiration_date=str(expiry_date),
                num_shares=int(num_shares),
                short_call_contracts=int(short_call_contracts),
                short_call_price=float(short_call_price),
                short_call_strike_price=float(short_call_strike),
                short_call_risk_free_rate=float(short_call_risk_free),
                short_call_dividend_yield=float(short_call_dividend_yield),
                short_call_volatility=float(short_call_volatility),
                short_put_contracts=int(short_put_contracts),
                short_put_price=float(short_put_price),
                short_put_strike_price=float(short_put_strike),
                short_put_risk_free_rate=float(short_put_risk_free),
                short_put_dividend_yield=float(short_put_dividend_yield),
                short_put_volatility=float(short_put_volatility),
                graph_type=str(graph_type),
                graph_profile=str(graph_profile)
            )

        elif strategy == '10':

            # Provide # of shares or use 100 as default
            num_shares = input('\nPlease Insert Number of Shares or press enter to use # 100: ')
            if num_shares == '':
                num_shares = 100

            # LONG OPTION
            # Select option type for long option
            print('\nPlease choose an option type for Long option: \n')
            print('1 - Call')
            print('2 - Put\n')
            long_type = input('Option Type: ')

            print('\nPlease select a Strike Price and one Ask price per option for Long option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if long_type == '1':
                    long_type = 'call'
                    long_options_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                               & (all_data.index.get_level_values('Type') == 'call')]
                elif long_type == '2':
                    long_type = 'put'
                    long_options_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                               & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Ask and IV indexed by strike prices
            long_filtered_df = long_options_df.droplevel([1, 2, 3])[['Ask', 'IV']]

            # Replace NaN values by 0's
            long_filtered_df.fillna(0)
            print(long_filtered_df)

            # Provide strike price, ask price and # contracts
            long_strike = float(input('\nStrike Price: '))
            long_price = float(input('Ask Price: '))
            long_contracts = int(input('Please select the number of contracts for Long Option: '))

            # Calculate and show total cost for the option
            long_total_cost = round(long_price * long_contracts * 100, 2)
            print('\nTotal Cost for Long Option: ', long_total_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            long_risk_free = input(
                '\nPlease insert risk-free rate for Long Option or press enter to use default value: ')
            long_dividend_yield = input(
                '\nPlease insert dividend yield for Long Option or press enter to use default value: ')
            long_volatility = input(
                '\nPlease insert the volatility for Long Option or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if long_risk_free == '':
                long_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if long_dividend_yield == '':
                long_dividend_yield = 0

            # If not provided, get implied volatility for given strike price
            if long_volatility == '':
                long_volatility = long_filtered_df.loc[long_strike]['IV']
            print('Implied volatility: ', long_volatility)

            # SHORT OPTION
            # Select option type for short option
            print('\nPlease choose an option type for Short option: \n')
            print('1 - Call')
            print('2 - Put\n')
            short_type = input('Option Type: ')

            print('\nPlease select a Strike Price and one Bid price per option for Short Option, '
                  'implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if short_type == '1':
                    short_type = 'call'
                    short_options_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                                & (all_data.index.get_level_values('Type') == 'call')]
                elif short_type == '2':
                    short_type = 'put'
                    short_options_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                                & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid and IV indexed by strike prices
            short_filtered_df = short_options_df.droplevel([1, 2, 3])[['Bid', 'IV']]

            # Replace NaN values by 0's
            short_filtered_df.fillna(0)
            print(short_filtered_df)

            # Provide strike price, ask price and # contracts
            short_strike = float(input('\nStrike Price: '))
            short_price = float(input('Bid/Ask Price: '))
            short_contracts = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            short_total_cost = round(short_price * short_contracts * 100, 2)
            print('\nTotal Cost for Short Option: ', short_total_cost)

            # Provide risk free rate, dividend yield and volatility or use default values
            short_risk_free = input(
                '\nPlease insert risk-free rate for Short Option or press enter to use default value: ')
            short_dividend_yield = input(
                '\nPlease insert dividend yield for Short Option or press enter to use default value: ')
            short_volatility = input(
                '\nPlease insert the volatility for Short Option or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if short_risk_free == '':
                short_risk_free = 0.005

            # If not provided, set default dividend yield as 0
            if short_dividend_yield == '':
                short_dividend_yield = 0.0

            # If not provided, get implied volatility for given strike price
            if short_volatility == '':
                short_volatility = short_filtered_df.loc[short_strike]['IV']
            print('Implied volatility: ', short_volatility)

            # Display results as table, graph or both
            print('\nPlease choose output for display results: \n')
            print('1 - Table')
            print('2 - Graph')
            print('3 - Both\n')
            graph_type = input('Output Type: ')
            try:
                if graph_type == '1':
                    graph_type = 'table'
                elif graph_type == '2':
                    graph_type = 'graph'
                elif graph_type == '3':
                    graph_type = 'both'
            except:
                print('Please provide a valid option.')

            # Select table/graph profile
            print('\nPlease choose a profile for display results: \n')
            print('1 - Profit/Loss (Dollar value)')
            print('2 - % of maximum risk')
            print('3 - Option/Spread value\n')
            graph_profile = input('Output Profile: ')
            try:
                if graph_profile == '1':
                    graph_profile = 'pnl'
                elif graph_profile == '2':
                    graph_profile = 'risk'
                elif graph_profile == '3':
                    graph_profile = 'option/spread'
            except:
                print('Please provide a valid option.')

            print('\nTable and Graphs with the results will be displayed on the browser')

            # call reverse_conversion() method from BSM calculator
            opt.reverse_conversion(
                spot_price=float(spot_price),
                expiration_date=str(expiry_date),
                num_shares=int(num_shares),
                long_contracts=int(long_contracts),
                long_price=float(long_price),
                long_type=str(long_type),
                long_strike_price=float(long_strike),
                long_risk_free_rate=float(long_risk_free),
                long_dividend_yield=float(long_dividend_yield),
                long_volatility=float(long_volatility),
                short_contracts=int(short_contracts),
                short_price=float(short_price),
                short_type=str(short_type),
                short_strike_price=float(short_strike),
                short_risk_free_rate=float(short_risk_free),
                short_dividend_yield=float(short_dividend_yield),
                short_volatility=float(short_volatility),
                graph_type=str(graph_type),
                graph_profile=str(graph_profile)
            )

    except:
        print('Please select a valid strategy.')


if __name__ == '__main__':
    run()