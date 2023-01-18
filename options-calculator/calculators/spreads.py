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
    """ Interface for running spread strategies with BSM model.

    :return: table and/or graph calculated option values and costs
        for call/put spreads, and back spread strategies
    """

    # Add auxiliary global variables
    global long_contracts, ratio, long_options_df, short_options_df, long_total_cost

    # Print spread strategies
    print('1 - Call / Put Spreads')
    print('2 - Back Spread\n')

    # Insert selected strategy as 1 or 2
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
    print('Current Spot Price: $ ', spot_price)
    print('Annualized volatility: ', sigma)

    print('\nPlease provide one of the available expiry dates: \n')

    # Store tick data into dataframe
    ticker = Options(ticker)

    # Get expiry dates for stock
    expiry_dates = ticker.expiry_dates

    # Show available expiry dates
    for exp in expiry_dates:
        print(exp)
        # print(exp.strftime("%Y-%m-%d"))

    # Provide expiry date among shown dates
    expiry_date = input('\nExpiry date: ')

    # Fetch all data for provided ticker
    all_data = ticker.get_all_data()

    # Long option
    print('\nPlease choose an option type for Long option: \n')
    print('1 - Call')
    print('2 - Put\n')
    long_option_type = input('Option Type: ')

    print('\nPlease select a Strike Price and Bid/Ask price per option for Long option, '
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
    except ValueError:
        print("Input not valid. Please try again.")

    # Get Bid, Ask and IV indexed by strike prices
    long_filtered_df = long_options_df.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

    # Replace NaN values by 0's
    long_filtered_df.fillna(0)
    print(long_filtered_df)

    # Provide strike and bid/ask prices
    long_strike = float(input('\nStrike Price: '))
    long_bid_ask = float(input('Bid/Ask Price: '))

    # Calculate total cost for chosen strategy. Back Spread takes the ratio parameter into account
    try:
        if strategy == '1':
            long_contracts = int(input('Please select the number of contracts for Long Option: '))
            long_total_cost = round(long_bid_ask * long_contracts * 100, 2)

        elif strategy == '2':
            long_contracts = int(input('Please select the number of contracts for Long Option: '))
            ratio = input('Please select the ratio multiplier for # contracts or press enter '
                          'to use 2 as default: ')
            if ratio == '':
                ratio = 2
            long_total_cost = round(long_bid_ask * ratio * 100, 2)
    except:
        print('Please provide a valid option.')

    # show total cost
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

    # If not provided, implied volatility for given strike price
    if long_volatility == '':
        long_volatility = long_filtered_df.loc[long_strike]['IV']

    # Short option
    print('\nPlease choose an option type for Short option: \n')
    print('1 - Call')
    print('2 - Put\n')
    short_option_type = input('Option Type: ')

    print('\nPlease select a Strike Price and Bid/Ask price per option for Short Option, '
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

    # Get Bid, Ask and IV indexed by strike prices
    short_filtered_df = short_options_df.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

    # Replace NaN values by 0's
    short_filtered_df.fillna(0)
    print(short_filtered_df)

    # Provide strike and bid/ask prices
    short_strike = float(input('\nStrike Price: '))
    short_bid_ask = float(input('Bid/Ask Price: '))

    # Calculate and show total cost for short option
    short_contracts = int(input('Please select the number of contracts: '))
    short_total_cost = round(short_bid_ask * short_contracts * 100, 2)
    print('\nTotal Cost for Short Option: ', short_total_cost)

    # Provide risk free rate, dividend yield and volatility or use default values
    short_risk_free = input('\nPlease insert risk-free rate for Short Option or press enter to use default value: ')
    short_dividend_yield = input('\nPlease insert dividend yield for Short Option or press enter to use default value: ')
    short_volatility = input('\nPlease insert the volatility for Short Option or press enter to use shown implied volatility: ')

    # If not provided, set default risk-free rate as 0.005
    if short_risk_free == '':
        short_risk_free = 0.005

    # If not provided, set default dividend yield as 0
    if short_dividend_yield == '':
        short_dividend_yield = 0.0

    # If not provided, implied volatility for given strike price
    if short_volatility == '':
        short_volatility = short_filtered_df.loc[short_strike]['IV']

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

    # Invoke method for chosen strategy
    try:
        if strategy == '1':
            # Call spread() method
            opt.spread(
                spot_price=float(spot_price),
                expiration_date=str(expiry_date),
                long_contracts=int(long_contracts),
                long_price=float(long_bid_ask),
                long_type=str(long_option_type),
                long_strike_price=float(long_strike),
                long_risk_free_rate=float(long_risk_free),
                long_dividend_yield=float(long_dividend_yield),
                long_volatility=float(long_volatility),
                short_contracts=int(short_contracts),
                short_price=float(short_bid_ask),
                short_type=str(short_option_type),
                short_strike_price=float(short_strike),
                short_risk_free_rate=float(short_risk_free),
                short_dividend_yield=float(short_dividend_yield),
                short_volatility=float(short_volatility),
                graph_type=str(graph_type),
                graph_profile=str(graph_profile)
            )
        elif strategy == '2':
            # Call back_spread() method
            opt.back_spread(
                spot_price=float(spot_price),
                expiration_date=str(expiry_date),
                long_contracts=int(long_contracts),
                long_price=float(long_bid_ask),
                long_type=str(long_option_type),
                long_strike_price=float(long_strike),
                long_risk_free_rate=float(long_risk_free),
                long_dividend_yield=float(long_dividend_yield),
                long_volatility=float(long_volatility),
                ratio=int(ratio),
                short_contracts=int(short_contracts),
                short_price=float(short_bid_ask),
                short_type=str(short_option_type),
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