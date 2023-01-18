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
    """ Interface for running custom strategies with BSM model.

        :return: table and/or graph calculated option values and costs
            for 8, 6, 5, 4, 3 and 2 legs strategies
    """

    # Add auxiliary global variables
    global options_df_leg_1, options_df_leg_2, options_df_leg_3, options_df_leg_4, options_df_leg_5, \
        options_df_leg_6, options_df_leg_7, options_df_leg_8

    # Insert selected strategy as 1, 2,..., 6
    print('1 - 8 Legs')
    print('2 - 6 Legs')
    print('3 - 5 Legs')
    print('4 - 4 Legs')
    print('5 - 3 Legs')
    print('6 - 2 Legs\n')
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

            # LEG 1
            # Select buy or write 
            print('\nPlease select Buy or Write for Leg 1: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_1 = input('Buy or Write: ')
            try:
                if action_leg_1 == '1':
                    action_leg_1 = 'buy'
                elif action_leg_1 == '2':
                    action_leg_1 = 'write'
            except ValueError:
                print("Input not valid. Please try again.")

            # Select option type 
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_1 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_1 == '1':
                    option_type_leg_1 = 'call'
                    options_df_leg_1 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_1 == '2':
                    option_type_leg_1 = 'put'
                    options_df_leg_1 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_1 = options_df_leg_1.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_1.fillna(0)
            print(filtered_df_leg_1)

            # Provide strike price, ask price and # contracts
            strike_leg_1 = float(input('\nStrike Price: '))
            price_leg_1 = float(input('Bid/Ask Price: '))
            num_contracts_leg_1 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_1 = round(price_leg_1 * num_contracts_leg_1 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_1)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_1 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_1 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_1 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_1 == '':
                risk_free_leg_1 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_1 == '':
                dividend_yield_leg_1 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_1 == '':
                volatility_leg_1 = filtered_df_leg_1.loc[strike_leg_1]['IV']
            print('Implied volatility: ', volatility_leg_1)

            # LEG 2
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 2: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_2 = input('Buy or Write: ')
            try:
                if action_leg_2 == '1':
                    action_leg_2 = 'buy'
                elif action_leg_2 == '2':
                    action_leg_2 = 'write'
            except:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_2 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_2 == '1':
                    option_type_leg_2 = 'call'
                    options_df_leg_2 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_2 == '2':
                    option_type_leg_2 = 'put'
                    options_df_leg_2 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_2 = options_df_leg_2.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_2.fillna(0)
            print(filtered_df_leg_2)

            # Provide strike price, ask price and # contracts
            strike_leg_2 = float(input('\nStrike Price: '))
            price_leg_2 = float(input('Bid/Ask Price: '))
            num_contracts_leg_2 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_2 = round(price_leg_2 * num_contracts_leg_2 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_2)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_2 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_2 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_2 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_2 == '':
                risk_free_leg_2 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_2 == '':
                dividend_yield_leg_2 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_2 == '':
                volatility_leg_2 = filtered_df_leg_2.loc[strike_leg_2]['IV']

            print('Implied volatility: ', volatility_leg_2)

            # LEG 3
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 3: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_3 = input('Buy or Write: ')
            try:
                if action_leg_3 == '1':
                    action_leg_3 = 'buy'
                elif action_leg_3 == '2':
                    action_leg_3 = 'write'
            except:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_3 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_3 == '1':
                    option_type_leg_3 = 'call'
                    options_df_leg_3 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_3 == '2':
                    option_type_leg_3 = 'put'
                    options_df_leg_3 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_3 = options_df_leg_3.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_3.fillna(0)
            print(filtered_df_leg_3)

            # Get Bid, Ask and IV indexed by strike prices
            strike_leg_3 = float(input('\nStrike Price: '))
            price_leg_3 = float(input('Bid/Ask Price: '))
            num_contracts_leg_3 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_3 = round(price_leg_3 * num_contracts_leg_3 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_3)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_3 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_3 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_3 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_3 == '':
                risk_free_leg_3 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_3 == '':
                dividend_yield_leg_3 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_3 == '':
                volatility_leg_3 = filtered_df_leg_3.loc[strike_leg_3]['IV']

            print('Implied volatility: ', volatility_leg_3)

            # LEG 4
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 4: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_4 = input('Buy or Write: ')
            try:
                if action_leg_4 == '1':
                    action_leg_4 = 'buy'
                elif action_leg_4 == '2':
                    action_leg_4 = 'write'
            except:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_4 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_4 == '1':
                    option_type_leg_4 = 'call'
                    options_df_leg_4 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_4 == '2':
                    option_type_leg_4 = 'put'
                    options_df_leg_4 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_4 = options_df_leg_4.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_4.fillna(0)
            print(filtered_df_leg_4)

            # Provide strike price, ask price and # contracts
            strike_leg_4 = float(input('\nStrike Price: '))
            price_leg_4 = float(input('Bid/Ask Price: '))
            num_contracts_leg_4 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_4 = round(price_leg_4 * num_contracts_leg_4 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_4)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_4 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_4 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_4 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_4 == '':
                risk_free_leg_4 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_4 == '':
                dividend_yield_leg_4 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_4 == '':
                volatility_leg_4 = filtered_df_leg_4.loc[strike_leg_4]['IV']
            print('Implied volatility: ', volatility_leg_4)

            # LEG 5
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 5: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_5 = input('Buy or Write: ')
            try:
                if action_leg_5 == '1':
                    action_leg_5 = 'buy'
                elif action_leg_5 == '2':
                    action_leg_5 = 'write'
            except:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_5 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_5 == '1':
                    option_type_leg_5 = 'call'
                    options_df_leg_5 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_5 == '2':
                    option_type_leg_5 = 'put'
                    options_df_leg_5 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_5 = options_df_leg_5.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_5.fillna(0)
            print(filtered_df_leg_5)

            # Provide strike price, ask price and # contracts
            strike_leg_5 = float(input('\nStrike Price: '))
            price_leg_5 = float(input('Bid/Ask Price: '))
            num_contracts_leg_5 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_5 = round(price_leg_5 * num_contracts_leg_5 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_5)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_5 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_5 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_5 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_5 == '':
                risk_free_leg_5 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_5 == '':
                dividend_yield_leg_5 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_5 == '':
                volatility_leg_5 = filtered_df_leg_5.loc[strike_leg_5]['IV']
            print('Implied volatility: ', volatility_leg_5)

            # LEG 6
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 6: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_6 = input('Buy or Write: ')
            try:
                if action_leg_6 == '1':
                    action_leg_6 = 'buy'
                elif action_leg_6 == '2':
                    action_leg_6 = 'write'
            except ValueError:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_6 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_6 == '1':
                    option_type_leg_6 = 'call'
                    options_df_leg_6 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_6 == '2':
                    option_type_leg_6 = 'put'
                    options_df_leg_6 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_6 = options_df_leg_6.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_6.fillna(0)
            print(filtered_df_leg_6)

            # Provide strike price, ask price and # contracts
            strike_leg_6 = float(input('\nStrike Price: '))
            price_leg_6 = float(input('Bid/Ask Price: '))
            num_contracts_leg_6 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_6 = round(price_leg_6 * num_contracts_leg_6 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_6)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_6 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_6 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_6 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_6 == '':
                risk_free_leg_6 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_6 == '':
                dividend_yield_leg_6 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_6 == '':
                volatility_leg_6 = filtered_df_leg_6.loc[strike_leg_6]['IV']
            print('Implied volatility: ', volatility_leg_6)

            # LEG 7
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 7: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_7 = input('Buy or Write: ')
            try:
                if action_leg_7 == '1':
                    action_leg_7 = 'buy'
                elif action_leg_7 == '2':
                    action_leg_7 = 'write'
            except:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_7 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_7 == '1':
                    option_type_leg_7 = 'call'
                    options_df_leg_7 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_7 == '2':
                    option_type_leg_7 = 'put'
                    options_df_leg_7 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_7 = options_df_leg_7.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_7.fillna(0)
            print(filtered_df_leg_7)

            # Provide strike price, ask price and # contracts
            strike_leg_7 = float(input('\nStrike Price: '))
            price_leg_7 = float(input('Bid/Ask Price: '))
            num_contracts_leg_7 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_7 = round(price_leg_7 * num_contracts_leg_7 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_7)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_7 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_7 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_7 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_7 == '':
                risk_free_leg_7 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_7 == '':
                dividend_yield_leg_7 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_7 == '':
                volatility_leg_7 = filtered_df_leg_7.loc[strike_leg_7]['IV']
            print('Implied volatility: ', volatility_leg_7)

            # LEG 8
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 8: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_8 = input('Buy or Write: ')
            try:
                if action_leg_8 == '1':
                    action_leg_8 = 'buy'
                elif action_leg_8 == '2':
                    action_leg_8 = 'write'
            except:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_8 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_8 == '1':
                    option_type_leg_8 = 'call'
                    options_df_leg_8 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_8 == '2':
                    option_type_leg_8 = 'put'
                    options_df_leg_8 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except ValueError:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_8 = options_df_leg_8.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_8.fillna(0)
            print(filtered_df_leg_8)

            # Provide strike price, ask price and # contracts
            strike_leg_8 = float(input('\nStrike Price: '))
            price_leg_8 = float(input('Bid/Ask Price: '))
            num_contracts_leg_8 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_8 = round(price_leg_8 * num_contracts_leg_8 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_8)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_8 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_8 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_8 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_8 == '':
                risk_free_leg_8 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_8 == '':
                dividend_yield_leg_8 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_8 == '':
                volatility_leg_8 = filtered_df_leg_8.loc[strike_leg_8]['IV']
            print('Implied volatility: ', volatility_leg_8)

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

            # call eight_legs() method from BSM calculator
            opt.eight_legs(
                spot_price=float(spot_price),
                expiration_date=str(expiry_date),
                action_leg_1=str(action_leg_1),
                contracts_leg_1=int(num_contracts_leg_1),
                price_leg_1=float(price_leg_1),
                option_leg_1=str(option_type_leg_1),
                strike_leg_1=float(strike_leg_1),
                risk_leg_1=float(risk_free_leg_1),
                dividend_yield_leg_1=float(dividend_yield_leg_1),
                volatility_leg_1=float(volatility_leg_1),
                action_leg_2=str(action_leg_2),
                contracts_leg_2=int(num_contracts_leg_2),
                price_leg_2=float(price_leg_2),
                option_leg_2=str(option_type_leg_2),
                strike_leg_2=float(strike_leg_2),
                risk_leg_2=float(risk_free_leg_2),
                dividend_yield_leg_2=float(dividend_yield_leg_2),
                volatility_leg_2=float(volatility_leg_2),
                action_leg_3=str(action_leg_3),
                contracts_leg_3=int(num_contracts_leg_3),
                price_leg_3=float(price_leg_3),
                option_leg_3=str(option_type_leg_3),
                strike_leg_3=float(strike_leg_3),
                risk_leg_3=float(risk_free_leg_3),
                dividend_yield_leg_3=float(dividend_yield_leg_3),
                volatility_leg_3=float(volatility_leg_3),
                action_leg_4=str(action_leg_4),
                contracts_leg_4=int(num_contracts_leg_4),
                price_leg_4=float(price_leg_4),
                option_leg_4=str(option_type_leg_4),
                strike_leg_4=float(strike_leg_4),
                risk_leg_4=float(risk_free_leg_4),
                dividend_yield_leg_4=float(dividend_yield_leg_4),
                volatility_leg_4=float(volatility_leg_4),
                action_leg_5=int(action_leg_5),
                contracts_leg_5=int(num_contracts_leg_5),
                price_leg_5=float(price_leg_5),
                option_leg_5=str(option_type_leg_5),
                strike_leg_5=float(strike_leg_5),
                risk_leg_5=float(risk_free_leg_5),
                dividend_yield_leg_5=float(dividend_yield_leg_5),
                volatility_leg_5=float(volatility_leg_5),
                action_leg_6=float(action_leg_6),
                contracts_leg_6=int(num_contracts_leg_6),
                price_leg_6=float(price_leg_6),
                option_leg_6=str(option_type_leg_6),
                strike_leg_6=float(strike_leg_6),
                risk_leg_6=float(risk_free_leg_6),
                dividend_yield_leg_6=float(dividend_yield_leg_6),
                volatility_leg_6=float(volatility_leg_6),
                action_leg_7=str(action_leg_7),
                contracts_leg_7=int(num_contracts_leg_7),
                price_leg_7=float(price_leg_7),
                option_leg_7=str(option_type_leg_7),
                strike_leg_7=float(strike_leg_7),
                risk_leg_7=float(risk_free_leg_7),
                dividend_yield_leg_7=float(dividend_yield_leg_7),
                volatility_leg_7=float(volatility_leg_7),
                action_leg_8=str(action_leg_8),
                contracts_leg_8=int(num_contracts_leg_8),
                price_leg_8=float(price_leg_8),
                option_leg_8=str(option_type_leg_8),
                strike_leg_8=float(strike_leg_8),
                risk_leg_8=float(risk_free_leg_8),
                dividend_yield_leg_8=float(dividend_yield_leg_8),
                volatility_leg_8=float(volatility_leg_8),
                graph_type=str(graph_type),
                graph_profile=str(graph_profile)
            )

        elif strategy == '2':

            # LEG 1
            # Select buy or write 
            print('\nPlease select Buy or Write for Leg 1: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_1 = input('Buy or Write: ')
            try:
                if action_leg_1 == '1':
                    action_leg_1 = 'buy'
                elif action_leg_1 == '2':
                    action_leg_1 = 'write'
            except ValueError:
                print("Input not valid. Please try again.")

            # Select option type 
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_1 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_1 == '1':
                    option_type_leg_1 = 'call'
                    options_df_leg_1 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_1 == '2':
                    option_type_leg_1 = 'put'
                    options_df_leg_1 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_1 = options_df_leg_1.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_1.fillna(0)
            print(filtered_df_leg_1)

            # Provide strike price, ask price and # contracts
            strike_leg_1 = float(input('\nStrike Price: '))
            price_leg_1 = float(input('Bid/Ask Price: '))
            num_contracts_leg_1 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_1 = round(price_leg_1 * num_contracts_leg_1 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_1)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_1 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_1 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_1 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_1 == '':
                risk_free_leg_1 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_1 == '':
                dividend_yield_leg_1 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_1 == '':
                volatility_leg_1 = filtered_df_leg_1.loc[strike_leg_1]['IV']
            print('Implied volatility: ', volatility_leg_1)

            # LEG 2
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 2: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_2 = input('Buy or Write: ')
            try:
                if action_leg_2 == '1':
                    action_leg_2 = 'buy'
                elif action_leg_2 == '2':
                    action_leg_2 = 'write'
            except:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_2 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_2 == '1':
                    option_type_leg_2 = 'call'
                    options_df_leg_2 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_2 == '2':
                    option_type_leg_2 = 'put'
                    options_df_leg_2 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_2 = options_df_leg_2.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_2.fillna(0)
            print(filtered_df_leg_2)

            # Provide strike price, ask price and # contracts
            strike_leg_2 = float(input('\nStrike Price: '))
            price_leg_2 = float(input('Bid/Ask Price: '))
            num_contracts_leg_2 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_2 = round(price_leg_2 * num_contracts_leg_2 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_2)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_2 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_2 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_2 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_2 == '':
                risk_free_leg_2 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_2 == '':
                dividend_yield_leg_2 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_2 == '':
                volatility_leg_2 = filtered_df_leg_2.loc[strike_leg_2]['IV']

            print('Implied volatility: ', volatility_leg_2)

            # LEG 3
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 3: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_3 = input('Buy or Write: ')
            try:
                if action_leg_3 == '1':
                    action_leg_3 = 'buy'
                elif action_leg_3 == '2':
                    action_leg_3 = 'write'
            except:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_3 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_3 == '1':
                    option_type_leg_3 = 'call'
                    options_df_leg_3 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_3 == '2':
                    option_type_leg_3 = 'put'
                    options_df_leg_3 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_3 = options_df_leg_3.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_3.fillna(0)
            print(filtered_df_leg_3)

            # Get Bid, Ask and IV indexed by strike prices
            strike_leg_3 = float(input('\nStrike Price: '))
            price_leg_3 = float(input('Bid/Ask Price: '))
            num_contracts_leg_3 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_3 = round(price_leg_3 * num_contracts_leg_3 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_3)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_3 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_3 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_3 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_3 == '':
                risk_free_leg_3 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_3 == '':
                dividend_yield_leg_3 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_3 == '':
                volatility_leg_3 = filtered_df_leg_3.loc[strike_leg_3]['IV']

            print('Implied volatility: ', volatility_leg_3)

            # LEG 4
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 4: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_4 = input('Buy or Write: ')
            try:
                if action_leg_4 == '1':
                    action_leg_4 = 'buy'
                elif action_leg_4 == '2':
                    action_leg_4 = 'write'
            except:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_4 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_4 == '1':
                    option_type_leg_4 = 'call'
                    options_df_leg_4 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_4 == '2':
                    option_type_leg_4 = 'put'
                    options_df_leg_4 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_4 = options_df_leg_4.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_4.fillna(0)
            print(filtered_df_leg_4)

            # Provide strike price, ask price and # contracts
            strike_leg_4 = float(input('\nStrike Price: '))
            price_leg_4 = float(input('Bid/Ask Price: '))
            num_contracts_leg_4 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_4 = round(price_leg_4 * num_contracts_leg_4 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_4)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_4 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_4 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_4 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_4 == '':
                risk_free_leg_4 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_4 == '':
                dividend_yield_leg_4 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_4 == '':
                volatility_leg_4 = filtered_df_leg_4.loc[strike_leg_4]['IV']
            print('Implied volatility: ', volatility_leg_4)

            # LEG 5
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 5: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_5 = input('Buy or Write: ')
            try:
                if action_leg_5 == '1':
                    action_leg_5 = 'buy'
                elif action_leg_5 == '2':
                    action_leg_5 = 'write'
            except:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_5 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_5 == '1':
                    option_type_leg_5 = 'call'
                    options_df_leg_5 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_5 == '2':
                    option_type_leg_5 = 'put'
                    options_df_leg_5 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_5 = options_df_leg_5.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_5.fillna(0)
            print(filtered_df_leg_5)

            # Provide strike price, ask price and # contracts
            strike_leg_5 = float(input('\nStrike Price: '))
            price_leg_5 = float(input('Bid/Ask Price: '))
            num_contracts_leg_5 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_5 = round(price_leg_5 * num_contracts_leg_5 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_5)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_5 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_5 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_5 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_5 == '':
                risk_free_leg_5 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_5 == '':
                dividend_yield_leg_5 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_5 == '':
                volatility_leg_5 = filtered_df_leg_5.loc[strike_leg_5]['IV']
            print('Implied volatility: ', volatility_leg_5)

            # LEG 6
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 6: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_6 = input('Buy or Write: ')
            try:
                if action_leg_6 == '1':
                    action_leg_6 = 'buy'
                elif action_leg_6 == '2':
                    action_leg_6 = 'write'
            except ValueError:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_6 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_6 == '1':
                    option_type_leg_6 = 'call'
                    options_df_leg_6 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_6 == '2':
                    option_type_leg_6 = 'put'
                    options_df_leg_6 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_6 = options_df_leg_6.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_6.fillna(0)
            print(filtered_df_leg_6)

            # Provide strike price, ask price and # contracts
            strike_leg_6 = float(input('\nStrike Price: '))
            price_leg_6 = float(input('Bid/Ask Price: '))
            num_contracts_leg_6 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_6 = round(price_leg_6 * num_contracts_leg_6 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_6)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_6 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_6 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_6 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_6 == '':
                risk_free_leg_6 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_6 == '':
                dividend_yield_leg_6 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_6 == '':
                volatility_leg_6 = filtered_df_leg_6.loc[strike_leg_6]['IV']
            print('Implied volatility: ', volatility_leg_6)

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

            # call six_legs() method from BSM calculator
            opt.six_legs(
                spot_price=float(spot_price),
                expiration_date=str(expiry_date),
                action_leg_1=str(action_leg_1),
                contracts_leg_1=int(num_contracts_leg_1),
                price_leg_1=float(price_leg_1),
                option_leg_1=str(option_type_leg_1),
                strike_leg_1=float(strike_leg_1),
                risk_leg_1=float(risk_free_leg_1),
                dividend_yield_leg_1=float(dividend_yield_leg_1),
                volatility_leg_1=float(volatility_leg_1),
                action_leg_2=str(action_leg_2),
                contracts_leg_2=int(num_contracts_leg_2),
                price_leg_2=float(price_leg_2),
                option_leg_2=str(option_type_leg_2),
                strike_leg_2=float(strike_leg_2),
                risk_leg_2=float(risk_free_leg_2),
                dividend_yield_leg_2=float(dividend_yield_leg_2),
                volatility_leg_2=float(volatility_leg_2),
                action_leg_3=str(action_leg_3),
                contracts_leg_3=int(num_contracts_leg_3),
                price_leg_3=float(price_leg_3),
                option_leg_3=str(option_type_leg_3),
                strike_leg_3=float(strike_leg_3),
                risk_leg_3=float(risk_free_leg_3),
                dividend_yield_leg_3=float(dividend_yield_leg_3),
                volatility_leg_3=float(volatility_leg_3),
                action_leg_4=str(action_leg_4),
                contracts_leg_4=int(num_contracts_leg_4),
                price_leg_4=float(price_leg_4),
                option_leg_4=str(option_type_leg_4),
                strike_leg_4=float(strike_leg_4),
                risk_leg_4=float(risk_free_leg_4),
                dividend_yield_leg_4=float(dividend_yield_leg_4),
                volatility_leg_4=float(volatility_leg_4),
                action_leg_5=int(action_leg_5),
                contracts_leg_5=int(num_contracts_leg_5),
                price_leg_5=float(price_leg_5),
                option_leg_5=str(option_type_leg_5),
                strike_leg_5=float(strike_leg_5),
                risk_leg_5=float(risk_free_leg_5),
                dividend_yield_leg_5=float(dividend_yield_leg_5),
                volatility_leg_5=float(volatility_leg_5),
                action_leg_6=float(action_leg_6),
                contracts_leg_6=int(num_contracts_leg_6),
                price_leg_6=float(price_leg_6),
                option_leg_6=str(option_type_leg_6),
                strike_leg_6=float(strike_leg_6),
                risk_leg_6=float(risk_free_leg_6),
                dividend_yield_leg_6=float(dividend_yield_leg_6),
                volatility_leg_6=float(volatility_leg_6),
                graph_type=str(graph_type),
                graph_profile=str(graph_profile)
            )

        elif strategy == '3':

            # LEG 1
            # Select buy or write 
            print('\nPlease select Buy or Write for Leg 1: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_1 = input('Buy or Write: ')
            try:
                if action_leg_1 == '1':
                    action_leg_1 = 'buy'
                elif action_leg_1 == '2':
                    action_leg_1 = 'write'
            except ValueError:
                print("Input not valid. Please try again.")

            # Select option type 
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_1 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_1 == '1':
                    option_type_leg_1 = 'call'
                    options_df_leg_1 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_1 == '2':
                    option_type_leg_1 = 'put'
                    options_df_leg_1 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_1 = options_df_leg_1.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_1.fillna(0)
            print(filtered_df_leg_1)

            # Provide strike price, ask price and # contracts
            strike_leg_1 = float(input('\nStrike Price: '))
            price_leg_1 = float(input('Bid/Ask Price: '))
            num_contracts_leg_1 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_1 = round(price_leg_1 * num_contracts_leg_1 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_1)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_1 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_1 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_1 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_1 == '':
                risk_free_leg_1 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_1 == '':
                dividend_yield_leg_1 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_1 == '':
                volatility_leg_1 = filtered_df_leg_1.loc[strike_leg_1]['IV']
            print('Implied volatility: ', volatility_leg_1)

            # LEG 2
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 2: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_2 = input('Buy or Write: ')
            try:
                if action_leg_2 == '1':
                    action_leg_2 = 'buy'
                elif action_leg_2 == '2':
                    action_leg_2 = 'write'
            except:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_2 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_2 == '1':
                    option_type_leg_2 = 'call'
                    options_df_leg_2 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_2 == '2':
                    option_type_leg_2 = 'put'
                    options_df_leg_2 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_2 = options_df_leg_2.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_2.fillna(0)
            print(filtered_df_leg_2)

            # Provide strike price, ask price and # contracts
            strike_leg_2 = float(input('\nStrike Price: '))
            price_leg_2 = float(input('Bid/Ask Price: '))
            num_contracts_leg_2 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_2 = round(price_leg_2 * num_contracts_leg_2 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_2)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_2 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_2 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_2 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_2 == '':
                risk_free_leg_2 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_2 == '':
                dividend_yield_leg_2 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_2 == '':
                volatility_leg_2 = filtered_df_leg_2.loc[strike_leg_2]['IV']

            print('Implied volatility: ', volatility_leg_2)

            # LEG 3
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 3: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_3 = input('Buy or Write: ')
            try:
                if action_leg_3 == '1':
                    action_leg_3 = 'buy'
                elif action_leg_3 == '2':
                    action_leg_3 = 'write'
            except:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_3 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_3 == '1':
                    option_type_leg_3 = 'call'
                    options_df_leg_3 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_3 == '2':
                    option_type_leg_3 = 'put'
                    options_df_leg_3 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_3 = options_df_leg_3.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_3.fillna(0)
            print(filtered_df_leg_3)

            # Get Bid, Ask and IV indexed by strike prices
            strike_leg_3 = float(input('\nStrike Price: '))
            price_leg_3 = float(input('Bid/Ask Price: '))
            num_contracts_leg_3 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_3 = round(price_leg_3 * num_contracts_leg_3 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_3)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_3 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_3 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_3 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_3 == '':
                risk_free_leg_3 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_3 == '':
                dividend_yield_leg_3 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_3 == '':
                volatility_leg_3 = filtered_df_leg_3.loc[strike_leg_3]['IV']

            print('Implied volatility: ', volatility_leg_3)

            # LEG 4
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 4: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_4 = input('Buy or Write: ')
            try:
                if action_leg_4 == '1':
                    action_leg_4 = 'buy'
                elif action_leg_4 == '2':
                    action_leg_4 = 'write'
            except:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_4 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_4 == '1':
                    option_type_leg_4 = 'call'
                    options_df_leg_4 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_4 == '2':
                    option_type_leg_4 = 'put'
                    options_df_leg_4 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_4 = options_df_leg_4.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_4.fillna(0)
            print(filtered_df_leg_4)

            # Provide strike price, ask price and # contracts
            strike_leg_4 = float(input('\nStrike Price: '))
            price_leg_4 = float(input('Bid/Ask Price: '))
            num_contracts_leg_4 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_4 = round(price_leg_4 * num_contracts_leg_4 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_4)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_4 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_4 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_4 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_4 == '':
                risk_free_leg_4 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_4 == '':
                dividend_yield_leg_4 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_4 == '':
                volatility_leg_4 = filtered_df_leg_4.loc[strike_leg_4]['IV']
            print('Implied volatility: ', volatility_leg_4)

            # LEG 5
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 5: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_5 = input('Buy or Write: ')
            try:
                if action_leg_5 == '1':
                    action_leg_5 = 'buy'
                elif action_leg_5 == '2':
                    action_leg_5 = 'write'
            except:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_5 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_5 == '1':
                    option_type_leg_5 = 'call'
                    options_df_leg_5 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_5 == '2':
                    option_type_leg_5 = 'put'
                    options_df_leg_5 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_5 = options_df_leg_5.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_5.fillna(0)
            print(filtered_df_leg_5)

            # Provide strike price, ask price and # contracts
            strike_leg_5 = float(input('\nStrike Price: '))
            price_leg_5 = float(input('Bid/Ask Price: '))
            num_contracts_leg_5 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_5 = round(price_leg_5 * num_contracts_leg_5 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_5)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_5 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_5 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_5 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_5 == '':
                risk_free_leg_5 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_5 == '':
                dividend_yield_leg_5 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_5 == '':
                volatility_leg_5 = filtered_df_leg_5.loc[strike_leg_5]['IV']
            print('Implied volatility: ', volatility_leg_5)

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

            # call five_legs() method from BSM calculator
            opt.five_legs(
                spot_price=float(spot_price),
                expiration_date=str(expiry_date),
                action_leg_1=str(action_leg_1),
                contracts_leg_1=int(num_contracts_leg_1),
                price_leg_1=float(price_leg_1),
                option_leg_1=str(option_type_leg_1),
                strike_leg_1=float(strike_leg_1),
                risk_leg_1=float(risk_free_leg_1),
                dividend_yield_leg_1=float(dividend_yield_leg_1),
                volatility_leg_1=float(volatility_leg_1),
                action_leg_2=str(action_leg_2),
                contracts_leg_2=int(num_contracts_leg_2),
                price_leg_2=float(price_leg_2),
                option_leg_2=str(option_type_leg_2),
                strike_leg_2=float(strike_leg_2),
                risk_leg_2=float(risk_free_leg_2),
                dividend_yield_leg_2=float(dividend_yield_leg_2),
                volatility_leg_2=float(volatility_leg_2),
                action_leg_3=str(action_leg_3),
                contracts_leg_3=int(num_contracts_leg_3),
                price_leg_3=float(price_leg_3),
                option_leg_3=str(option_type_leg_3),
                strike_leg_3=float(strike_leg_3),
                risk_leg_3=float(risk_free_leg_3),
                dividend_yield_leg_3=float(dividend_yield_leg_3),
                volatility_leg_3=float(volatility_leg_3),
                action_leg_4=str(action_leg_4),
                contracts_leg_4=int(num_contracts_leg_4),
                price_leg_4=float(price_leg_4),
                option_leg_4=str(option_type_leg_4),
                strike_leg_4=float(strike_leg_4),
                risk_leg_4=float(risk_free_leg_4),
                dividend_yield_leg_4=float(dividend_yield_leg_4),
                volatility_leg_4=float(volatility_leg_4),
                action_leg_5=int(action_leg_5),
                contracts_leg_5=int(num_contracts_leg_5),
                price_leg_5=float(price_leg_5),
                option_leg_5=str(option_type_leg_5),
                strike_leg_5=float(strike_leg_5),
                risk_leg_5=float(risk_free_leg_5),
                dividend_yield_leg_5=float(dividend_yield_leg_5),
                volatility_leg_5=float(volatility_leg_5),
                graph_type=str(graph_type),
                graph_profile=str(graph_profile)
            )


        elif strategy == '4':

            # LEG 1
            # Select buy or write 
            print('\nPlease select Buy or Write for Leg 1: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_1 = input('Buy or Write: ')
            try:
                if action_leg_1 == '1':
                    action_leg_1 = 'buy'
                elif action_leg_1 == '2':
                    action_leg_1 = 'write'
            except ValueError:
                print("Input not valid. Please try again.")

            # Select option type 
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_1 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_1 == '1':
                    option_type_leg_1 = 'call'
                    options_df_leg_1 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_1 == '2':
                    option_type_leg_1 = 'put'
                    options_df_leg_1 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_1 = options_df_leg_1.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_1.fillna(0)
            print(filtered_df_leg_1)

            # Provide strike price, ask price and # contracts
            strike_leg_1 = float(input('\nStrike Price: '))
            price_leg_1 = float(input('Bid/Ask Price: '))
            num_contracts_leg_1 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_1 = round(price_leg_1 * num_contracts_leg_1 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_1)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_1 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_1 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_1 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_1 == '':
                risk_free_leg_1 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_1 == '':
                dividend_yield_leg_1 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_1 == '':
                volatility_leg_1 = filtered_df_leg_1.loc[strike_leg_1]['IV']
            print('Implied volatility: ', volatility_leg_1)

            # LEG 2
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 2: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_2 = input('Buy or Write: ')
            try:
                if action_leg_2 == '1':
                    action_leg_2 = 'buy'
                elif action_leg_2 == '2':
                    action_leg_2 = 'write'
            except:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_2 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_2 == '1':
                    option_type_leg_2 = 'call'
                    options_df_leg_2 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_2 == '2':
                    option_type_leg_2 = 'put'
                    options_df_leg_2 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_2 = options_df_leg_2.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_2.fillna(0)
            print(filtered_df_leg_2)

            # Provide strike price, ask price and # contracts
            strike_leg_2 = float(input('\nStrike Price: '))
            price_leg_2 = float(input('Bid/Ask Price: '))
            num_contracts_leg_2 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_2 = round(price_leg_2 * num_contracts_leg_2 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_2)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_2 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_2 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_2 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_2 == '':
                risk_free_leg_2 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_2 == '':
                dividend_yield_leg_2 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_2 == '':
                volatility_leg_2 = filtered_df_leg_2.loc[strike_leg_2]['IV']

            print('Implied volatility: ', volatility_leg_2)

            # LEG 3
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 3: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_3 = input('Buy or Write: ')
            try:
                if action_leg_3 == '1':
                    action_leg_3 = 'buy'
                elif action_leg_3 == '2':
                    action_leg_3 = 'write'
            except:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_3 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_3 == '1':
                    option_type_leg_3 = 'call'
                    options_df_leg_3 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_3 == '2':
                    option_type_leg_3 = 'put'
                    options_df_leg_3 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_3 = options_df_leg_3.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_3.fillna(0)
            print(filtered_df_leg_3)

            # Get Bid, Ask and IV indexed by strike prices
            strike_leg_3 = float(input('\nStrike Price: '))
            price_leg_3 = float(input('Bid/Ask Price: '))
            num_contracts_leg_3 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_3 = round(price_leg_3 * num_contracts_leg_3 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_3)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_3 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_3 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_3 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_3 == '':
                risk_free_leg_3 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_3 == '':
                dividend_yield_leg_3 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_3 == '':
                volatility_leg_3 = filtered_df_leg_3.loc[strike_leg_3]['IV']

            print('Implied volatility: ', volatility_leg_3)

            # LEG 4
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 4: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_4 = input('Buy or Write: ')
            try:
                if action_leg_4 == '1':
                    action_leg_4 = 'buy'
                elif action_leg_4 == '2':
                    action_leg_4 = 'write'
            except:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_4 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_4 == '1':
                    option_type_leg_4 = 'call'
                    options_df_leg_4 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_4 == '2':
                    option_type_leg_4 = 'put'
                    options_df_leg_4 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_4 = options_df_leg_4.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_4.fillna(0)
            print(filtered_df_leg_4)

            # Provide strike price, ask price and # contracts
            strike_leg_4 = float(input('\nStrike Price: '))
            price_leg_4 = float(input('Bid/Ask Price: '))
            num_contracts_leg_4 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_4 = round(price_leg_4 * num_contracts_leg_4 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_4)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_4 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_4 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_4 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_4 == '':
                risk_free_leg_4 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_4 == '':
                dividend_yield_leg_4 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_4 == '':
                volatility_leg_4 = filtered_df_leg_4.loc[strike_leg_4]['IV']
            print('Implied volatility: ', volatility_leg_4)

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

            # call four_legs() method from BSM calculator
            opt.four_legs(
                spot_price=float(spot_price),
                expiration_date=str(expiry_date),
                action_leg_1=str(action_leg_1),
                contracts_leg_1=int(num_contracts_leg_1),
                price_leg_1=float(price_leg_1),
                option_leg_1=str(option_type_leg_1),
                strike_leg_1=float(strike_leg_1),
                risk_leg_1=float(risk_free_leg_1),
                dividend_yield_leg_1=float(dividend_yield_leg_1),
                volatility_leg_1=float(volatility_leg_1),
                action_leg_2=str(action_leg_2),
                contracts_leg_2=int(num_contracts_leg_2),
                price_leg_2=float(price_leg_2),
                option_leg_2=str(option_type_leg_2),
                strike_leg_2=float(strike_leg_2),
                risk_leg_2=float(risk_free_leg_2),
                dividend_yield_leg_2=float(dividend_yield_leg_2),
                volatility_leg_2=float(volatility_leg_2),
                action_leg_3=str(action_leg_3),
                contracts_leg_3=int(num_contracts_leg_3),
                price_leg_3=float(price_leg_3),
                option_leg_3=str(option_type_leg_3),
                strike_leg_3=float(strike_leg_3),
                risk_leg_3=float(risk_free_leg_3),
                dividend_yield_leg_3=float(dividend_yield_leg_3),
                volatility_leg_3=float(volatility_leg_3),
                action_leg_4=str(action_leg_4),
                contracts_leg_4=int(num_contracts_leg_4),
                price_leg_4=float(price_leg_4),
                option_leg_4=str(option_type_leg_4),
                strike_leg_4=float(strike_leg_4),
                risk_leg_4=float(risk_free_leg_4),
                dividend_yield_leg_4=float(dividend_yield_leg_4),
                volatility_leg_4=float(volatility_leg_4),
                graph_type=str(graph_type),
                graph_profile=str(graph_profile)
            )

        elif strategy == '5':

            # LEG 1
            # Select buy or write 
            print('\nPlease select Buy or Write for Leg 1: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_1 = input('Buy or Write: ')
            try:
                if action_leg_1 == '1':
                    action_leg_1 = 'buy'
                elif action_leg_1 == '2':
                    action_leg_1 = 'write'
            except ValueError:
                print("Input not valid. Please try again.")

            # Select option type 
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_1 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_1 == '1':
                    option_type_leg_1 = 'call'
                    options_df_leg_1 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_1 == '2':
                    option_type_leg_1 = 'put'
                    options_df_leg_1 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_1 = options_df_leg_1.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_1.fillna(0)
            print(filtered_df_leg_1)

            # Provide strike price, ask price and # contracts
            strike_leg_1 = float(input('\nStrike Price: '))
            price_leg_1 = float(input('Bid/Ask Price: '))
            num_contracts_leg_1 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_1 = round(price_leg_1 * num_contracts_leg_1 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_1)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_1 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_1 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_1 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_1 == '':
                risk_free_leg_1 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_1 == '':
                dividend_yield_leg_1 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_1 == '':
                volatility_leg_1 = filtered_df_leg_1.loc[strike_leg_1]['IV']
            print('Implied volatility: ', volatility_leg_1)

            # LEG 2
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 2: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_2 = input('Buy or Write: ')
            try:
                if action_leg_2 == '1':
                    action_leg_2 = 'buy'
                elif action_leg_2 == '2':
                    action_leg_2 = 'write'
            except:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_2 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_2 == '1':
                    option_type_leg_2 = 'call'
                    options_df_leg_2 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_2 == '2':
                    option_type_leg_2 = 'put'
                    options_df_leg_2 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_2 = options_df_leg_2.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_2.fillna(0)
            print(filtered_df_leg_2)

            # Provide strike price, ask price and # contracts
            strike_leg_2 = float(input('\nStrike Price: '))
            price_leg_2 = float(input('Bid/Ask Price: '))
            num_contracts_leg_2 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_2 = round(price_leg_2 * num_contracts_leg_2 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_2)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_2 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_2 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_2 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_2 == '':
                risk_free_leg_2 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_2 == '':
                dividend_yield_leg_2 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_2 == '':
                volatility_leg_2 = filtered_df_leg_2.loc[strike_leg_2]['IV']

            print('Implied volatility: ', volatility_leg_2)

            # LEG 3
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 3: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_3 = input('Buy or Write: ')
            try:
                if action_leg_3 == '1':
                    action_leg_3 = 'buy'
                elif action_leg_3 == '2':
                    action_leg_3 = 'write'
            except:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_3 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_3 == '1':
                    option_type_leg_3 = 'call'
                    options_df_leg_3 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_3 == '2':
                    option_type_leg_3 = 'put'
                    options_df_leg_3 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_3 = options_df_leg_3.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_3.fillna(0)
            print(filtered_df_leg_3)

            # Get Bid, Ask and IV indexed by strike prices
            strike_leg_3 = float(input('\nStrike Price: '))
            price_leg_3 = float(input('Bid/Ask Price: '))
            num_contracts_leg_3 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_3 = round(price_leg_3 * num_contracts_leg_3 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_3)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_3 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_3 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_3 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_3 == '':
                risk_free_leg_3 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_3 == '':
                dividend_yield_leg_3 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_3 == '':
                volatility_leg_3 = filtered_df_leg_3.loc[strike_leg_3]['IV']

            print('Implied volatility: ', volatility_leg_3)

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

            # call three_legs() method from BSM calculator
            opt.three_legs(
                spot_price=float(spot_price),
                expiration_date=str(expiry_date),
                action_leg_1=str(action_leg_1),
                contracts_leg_1=int(num_contracts_leg_1),
                price_leg_1=float(price_leg_1),
                option_leg_1=str(option_type_leg_1),
                strike_leg_1=float(strike_leg_1),
                risk_leg_1=float(risk_free_leg_1),
                dividend_yield_leg_1=float(dividend_yield_leg_1),
                volatility_leg_1=float(volatility_leg_1),
                action_leg_2=str(action_leg_2),
                contracts_leg_2=int(num_contracts_leg_2),
                price_leg_2=float(price_leg_2),
                option_leg_2=str(option_type_leg_2),
                strike_leg_2=float(strike_leg_2),
                risk_leg_2=float(risk_free_leg_2),
                dividend_yield_leg_2=float(dividend_yield_leg_2),
                volatility_leg_2=float(volatility_leg_2),
                action_leg_3=str(action_leg_3),
                contracts_leg_3=int(num_contracts_leg_3),
                price_leg_3=float(price_leg_3),
                option_leg_3=str(option_type_leg_3),
                strike_leg_3=float(strike_leg_3),
                risk_leg_3=float(risk_free_leg_3),
                dividend_yield_leg_3=float(dividend_yield_leg_3),
                volatility_leg_3=float(volatility_leg_3),
                graph_type=str(graph_type),
                graph_profile=str(graph_profile)
            )

        elif strategy == '6':

            # LEG 1
            # Select buy or write 
            print('\nPlease select Buy or Write for Leg 1: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_1 = input('Buy or Write: ')
            try:
                if action_leg_1 == '1':
                    action_leg_1 = 'buy'
                elif action_leg_1 == '2':
                    action_leg_1 = 'write'
            except ValueError:
                print("Input not valid. Please try again.")

            # Select option type 
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_1 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_1 == '1':
                    option_type_leg_1 = 'call'
                    options_df_leg_1 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_1 == '2':
                    option_type_leg_1 = 'put'
                    options_df_leg_1 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_1 = options_df_leg_1.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_1.fillna(0)
            print(filtered_df_leg_1)

            # Provide strike price, ask price and # contracts
            strike_leg_1 = float(input('\nStrike Price: '))
            price_leg_1 = float(input('Bid/Ask Price: '))
            num_contracts_leg_1 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_1 = round(price_leg_1 * num_contracts_leg_1 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_1)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_1 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_1 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_1 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_1 == '':
                risk_free_leg_1 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_1 == '':
                dividend_yield_leg_1 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_1 == '':
                volatility_leg_1 = filtered_df_leg_1.loc[strike_leg_1]['IV']
            print('Implied volatility: ', volatility_leg_1)

            # LEG 2
            # Select buy or write
            print('\nPlease select Buy or Write for Leg 2: \n')
            print('1 - Buy')
            print('2 - Write\n')
            action_leg_2 = input('Buy or Write: ')
            try:
                if action_leg_2 == '1':
                    action_leg_2 = 'buy'
                elif action_leg_2 == '2':
                    action_leg_2 = 'write'
            except:
                print("Input not valid. Please try again.")

            # Select option type
            print('\nPlease choose an option type: \n')
            print('1 - Call')
            print('2 - Put\n')
            option_type_leg_2 = input('Option Type: ')

            print('\nPlease select a Strike Price and Bid/Ask price per option, implied volatility is also shown: \n')

            # Filter data at expiry date and option type level based on 'Expiry' and 'Type'
            # multi-index levels and store into df
            try:
                if option_type_leg_2 == '1':
                    option_type_leg_2 = 'call'
                    options_df_leg_2 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'call')]
                elif option_type_leg_2 == '2':
                    option_type_leg_2 = 'put'
                    options_df_leg_2 = all_data[(all_data.index.get_level_values('Expiry') == expiry_date) \
                                          & (all_data.index.get_level_values('Type') == 'put')]
            except:
                print("Input not valid. Please try again.")

            # Get Bid, Ask and IV indexed by strike prices
            filtered_df_leg_2 = options_df_leg_2.droplevel([1, 2, 3])[['Bid', 'Ask', 'IV']]

            # Replace NaN values by 0's
            filtered_df_leg_2.fillna(0)
            print(filtered_df_leg_2)

            # Provide strike price, ask price and # contracts
            strike_leg_2 = float(input('\nStrike Price: '))
            price_leg_2 = float(input('Bid/Ask Price: '))
            num_contracts_leg_2 = int(input('Please select the number of contracts: '))

            # Calculate and show total cost for the option
            total_cost_leg_2 = round(price_leg_2 * num_contracts_leg_2 * 100, 2)
            print('\nTotal Cost: ', total_cost_leg_2)

            # Provide risk free rate, dividend yield and volatility or use default values
            risk_free_leg_2 = input('\nPlease insert risk-free rate or press enter to use default value: ')
            dividend_yield_leg_2 = input('\nPlease insert dividend yield or press enter to use default value: ')
            volatility_leg_2 = input('\nPlease insert the volatility or press enter to use shown implied volatility: ')

            # If not provided, set default risk-free rate as 0.005
            if risk_free_leg_2 == '':
                risk_free_leg_2 = 0.005

            # If not provided, set default dividend yield as 0
            if dividend_yield_leg_2 == '':
                dividend_yield_leg_2 = 0

            # If not provided, get implied volatility for given strike price
            if volatility_leg_2 == '':
                volatility_leg_2 = filtered_df_leg_2.loc[strike_leg_2]['IV']

            print('Implied volatility: ', volatility_leg_2)

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

            # call two_legs() method from BSM calculator
            opt.two_legs(
                spot_price=float(spot_price),
                expiration_date=str(expiry_date),
                action_leg_1=str(action_leg_1),
                contracts_leg_1=int(num_contracts_leg_1),
                price_leg_1=float(price_leg_1),
                option_leg_1=str(option_type_leg_1),
                strike_leg_1=float(strike_leg_1),
                risk_leg_1=float(risk_free_leg_1),
                dividend_yield_leg_1=float(dividend_yield_leg_1),
                volatility_leg_1=float(volatility_leg_1),
                action_leg_2=str(action_leg_2),
                contracts_leg_2=int(num_contracts_leg_2),
                price_leg_2=float(price_leg_2),
                option_leg_2=str(option_type_leg_2),
                strike_leg_2=float(strike_leg_2),
                risk_leg_2=float(risk_free_leg_2),
                dividend_yield_leg_2=float(dividend_yield_leg_2),
                volatility_leg_2=float(volatility_leg_2),
                graph_type=str(graph_type),
                graph_profile=str(graph_profile)
            )

    except:
        print('Please select a valid strategy.')


if __name__ == '__main__':
    run()
































