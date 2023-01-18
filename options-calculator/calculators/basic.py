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
    """ Interface for running basic strategies with BSM model.

    :return: table and/or graph calculated option values and costs
        for long/short call, long/short put, or covered call strategies
    """

    # Add auxiliary global variables
    global options_df, num_shares, option_type, buy_write

    # Print basic strategies
    print('1 - Long / Short call')
    print('2 - Long / Short put')
    print('3 - Covered call\n')

    # Insert selected strategy as 1, 2, or 3
    strategy = input('Strategy: ')

    # Create an instance of the Option() class
    opt = Option()

    # Insert stock symbol in capital letters (e.g. GOOG, TSLA, etc)
    ticker = input('\nPlease Insert Stock Symbol: ')

    # Get dates for today and for a year ago
    today = dt.datetime.now() # Today's date
    last_year = today.year - 1, today.month, today.day  # Last year's date
    start_date = str(last_year[0]) + '-' + str(last_year[1]) + '-' + str(last_year[2]) # Last year date as str
    end_date = today.strftime("%Y-%m-%d")  # set today as end date for fetching data

    # Fetch data to dataframe from pandas-datareader API
    df = web.DataReader(ticker, 'yahoo', start_date, end_date).sort_values(by='Date', ascending=False)

    # Get annualized volatility and Spot price
    returns = df['Adj Close'].pct_change().dropna()  # Get returns from close prices and drop NaN values
    sigma = np.std(returns) * np.sqrt(252)  # volatility of underlying asset, annualized
    spot_price = df['Adj Close'].iloc[0]  # spot (current) price
    print('Current Spot Price: $ ', np.round(spot_price, 2))
    print('Annualized volatility: ', np.round(sigma, 3))

    # If covered_call was chosen specify # of shares or use 100 as default
    if strategy == '3':
        num_shares = input('\nPlease Insert Number of Shares or press enter to use # 100: ')
        if num_shares == '':
            num_shares = 100

    # If first 2 strategies were chosen select buy or write
    if strategy == '1' or strategy == '2':
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

    # If first 2 strategies were chosen provide option type,
    # otherwise option_type is 'call' for covered_call
    if strategy == '1' or strategy == '2':
        print('\nPlease choose an option type: \n')
        print('1 - Call')
        print('2 - Put\n')
        option_type = input('Option Type: ')
    else:
        option_type = 'call'

    # Fetch all data for provided ticker
    all_data = ticker.get_all_data()

    print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')


    # Filter dataframe by according option_type and expiry_date
    if strategy == '1' or strategy == '2':
        try:
            if option_type == '1':
                option_type = 'call'
                # Filter data at expiry date and option type level based on 'expiry' and 'call' 
                # multi-index levels and store into df
                options_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                      & (all_data.index.get_level_values('Type') == 'call')]
            elif option_type == '2':
                option_type = 'put'
                # Filter data at expiry date and option type level based on 'expiry' and 'put' 
                # multi-index levels and store into df
                options_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                      & (all_data.index.get_level_values('Type') == 'put')]
        except:
            print("Input not valid. Please try again.")

    elif strategy == '3':
        # Filter data at expiry date and option type level
        # based on 'expiry' and 'call' multi-index levels and store into df
        options_df = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                      & (all_data.index.get_level_values('Type') == 'call')]

    # Get Bid, Ask and IV indexed by strike prices
    filtered_df = options_df.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

    # Replace NaN values by 0's
    filtered_df.fillna(0)
    print(filtered_df)

    # Provide strike and bid/ask prices
    strike = float(input('\nStrike Price: '))
    bid_ask = float(input('Bid/Ask Price: '))

    # Provide number of contracts
    num_contracts = int(input('Please select the number of contracts: '))

    # Calculate and show total cost
    total_cost = round(bid_ask * num_contracts * 100, 2)
    print('\nTotal Cost: ', total_cost)

    # Provide risk free rate, dividend yield and volatility or use default values
    risk_free = input('\nPlease insert risk-free rate or press enter to use default value: ')
    dividend_yield = input('\nPlease insert dividend yield or press enter to use default value: ')
    volatility = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

    if risk_free == '':
        risk_free = 0.005

    if dividend_yield == '':
        dividend_yield = 0

    if volatility == '':
        # Get implied volatility for given strike price
        volatility = filtered_df.loc[strike]['IV']

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

    # Invoke method for chosen strategy
    try:
        if strategy == '1' or strategy == '2':
            # Call call_put() method
            opt.call_put(
                spot_price=float(spot_price),
                expiration_date=str(expiry_date),
                action=str(buy_write),
                contracts=int(num_contracts),
                option_price=float(bid_ask),
                option_type=str(option_type),
                strike_price=float(strike),
                risk_free_rate=float(risk_free),
                dividend_yield=float(dividend_yield),
                volatility=float(volatility),
                graph_type=str(graph_type),
                graph_profile=str(graph_profile)
            )

        elif strategy == '3':
            # Call covered_call() method
            opt.covered_call(
                spot_price=float(spot_price),
                expiration_date=str(expiry_date),
                num_shares=int(num_shares),
                contracts=int(num_contracts),
                option_price=float(bid_ask),
                strike_price=float(strike),
                risk_free_rate=float(risk_free),
                dividend_yield=float(dividend_yield),
                volatility=float(volatility),
                graph_type=str(graph_type),
                graph_profile=str(graph_profile)
            )
    except:
        print('Please try again.')


if __name__ == '__main__':
    run()