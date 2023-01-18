import datetime as dt

import scipy.stats as si
import numpy as np
import pandas as pd
import plotly.figure_factory as ff


class Option:
    """
    Option class to calculate option pricing for multiple strategies with Black-Scholes-Merton formula.
    The class is created without initializing any parameters so they must be provided explicitly.
    """

    def _get_dist(self, S, K, T, r, q, sigma):
        """ Calculates parameters and distributions to be used in BSM formula.

        :param S: (float) underlying stock price
        :param K: (float) strike price for the option
        :param T: (float) annualized time to maturity
        :param r: (float) risk-free interest rate
        :param q: (float) dividend yield
        :param sigma: (float) implied volatility
        :return: (various) parameters used by BSM formula
        """

        # Cost of carry as risk free rate less dividend yield
        b = r - q
        carry = np.exp((b - r) * T)
        discount = np.exp(-r * T)

        # Ignore possible division by 0 warnings
        with np.errstate(divide='ignore', invalid='ignore'):

            # Calculate d1 and d2 parameters to use in BSM formula
            d1 = ((np.log(S / K) + (b + (0.5 * sigma ** 2)) * T) / (sigma * np.sqrt(T)))
            d2 = ((np.log(S / K) + (b - (0.5 * sigma ** 2)) * T) / (sigma * np.sqrt(T)))

            # Standardised normal density function
            nd1 = ((1 / np.sqrt(2 * np.pi)) * (np.exp(-d1 ** 2 * 0.5)))

            # Cumulative normal distributions functions
            # For more information: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html
            Nd1 = si.norm.cdf(d1, 0.0, 1.0)
            minusNd1 = si.norm.cdf(-d1, 0.0, 1.0)
            Nd2 = si.norm.cdf(d2, 0.0, 1.0)
            minusNd2 = si.norm.cdf(-d2, 0.0, 1.0)

        return b, carry, discount, d1, d2, nd1, Nd1, minusNd1, Nd2, minusNd2


    def _bsm_price(self, S, K, T, r, q, sigma, option):
        """ Option pricing with BSM model.

        :param S: (float) underlying stock price
        :param K: (float) strike price for the option
        :param T: (float) annualized time to maturity
        :param r: (float) risk-free interest rate
        :param q: (float) dividend yield
        :param sigma: (float) implied volatility
        :param option: (str) option type as 'put' or 'call'
        :return: (float) option price with BSM model
        """

        global option_price

        # Calculate distribution parameters
        b, carry, discount, d1, d2, nd1, Nd1, minusNd1, Nd2, minusNd2 = self._get_dist(S, K, T, r, q, sigma)
        
        # Calculate call / put option price with input values and distribution parameters
        try:
            if option == "call":
                option_price = ((S * carry * Nd1) - (K * np.exp(-r * T) * Nd2))  

            elif option == "put":
                option_price = ((K * np.exp(-r * T) * minusNd2) - (S * carry * minusNd1))
            
            # Replace NaN with zero and infinity with large finite numbers
            np.nan_to_num(option_price, copy=False)
            
            return option_price
        except:
            print("Please confirm if call or put option") 


    def _get_maturity_dates(self, expiry_date):
        """Get days until expiry as strings in the format 'YYYY-MM-DD' and floats for annualized time until expiration.

        :param expiry_date: (str) expiration / maturity date
        :return: (array) array of tuples with dates until maturity as strings and floats
        """
        
        # Date formatting
        date_fmt = "%Y-%m-%d"

        # Get today's date as str with date format
        today_str = dt.datetime.now().strftime(date_fmt)

        # Specify today's date as starting date for calculation
        start_date = dt.datetime.strptime(today_str, date_fmt)

        # Specify expiry date as end date for calculation
        end_date = dt.datetime.strptime(expiry_date, date_fmt)

        # Get list with dates difference between expiry date and today
        # Add 2 days so the expiration is one day later following the profit calculator convention
        expiry_days = range(0, (end_date - start_date).days + 2)

        # Get each date until maturity as str in the specified date format ("%Y-%m-%d")
        dates_until_maturity_strings = [(start_date + dt.timedelta(days=x)).strftime(date_fmt) for x in expiry_days]

        # Rename the last date from the list as 'Expiration date' for posterior labelling
        dates_until_maturity_strings[-1] = 'Expiration date'

        # Get annualized dates as floats dividing each day in the list by 365 and sort by descending values
        dates_until_maturity_floats = [float(x / 365) for x in expiry_days][::-1]

        return list(zip(dates_until_maturity_strings, dates_until_maturity_floats))


    def _get_labels(self, expiry_date):
        """ Get clean dates and labels for option pricing and visualization.

        :param expiry_date: (str) expiration / maturity date
        :return: (lists) dates until expiry list in the format "%Y-%m-%d"
            for labelling and dates until expiry as floats for BSM formulas
        """

        # Get dates until maturity labels in the format "%Y-%m-%d" and "Expiration date" for labelling
        labels = [maturity_dates[0] for maturity_dates in self._get_maturity_dates(expiry_date)] 

        # Get dates until maturity as floats except by the last value that corresponds to expiration date (i.e. T = 0)
        dates = [maturity_dates[1] for maturity_dates in self._get_maturity_dates(expiry_date)
                    if maturity_dates[-1] != 0]

        return labels, dates


    def _heatmap(self, strike_prices, labels, df, title, yaxis_title):
        """ Renders annotated heatmap to display tabular results.
        For more information please refer to https://plotly.com/python/annotated-heatmap/
        and https://plotly.github.io/plotly.py-docs/generated/plotly.figure_factory.html

        :param strike_prices: (array_like) strike prices distribution
        :param labels: (list) dates as "%Y-%m-%d" and 'Expiration date'
        :param df: (dataframe) dataframe with results for profit/loss, % of max risk and option/spread values
        :param title: (str) title for each option strategy
        :return: annotated heatmap table with Plotly
        """
    
        #init_notebook_mode(connected=True)

        # Add '_' to each date for x axis labels, otherwise plotly heatmap breaks
        # Issue: https://github.com/plotly/plotly.py/issues/2782
        xaxis_labels = list(map(lambda x:  x + '_', labels))

        # Create annotated heatmap with figure_factory module from Plotly
        fig = ff.create_annotated_heatmap(
            z=list(df.values), 
            x=xaxis_labels, 
            y=strike_prices.tolist(),
            annotation_text = np.around(list(df.values), decimals=2),
            colorscale='rdylgn',
            hoverinfo='z')

        # Make text size smaller
        for i in range(len(fig.layout.annotations)):
            fig.layout.annotations[i].font.size = 10

        # Update table layout structure
        fig.update_layout(
            autosize = False,
            width = 500 / 3 * len(labels),
            height = 50 * len(strike_prices),
            yaxis = dict(
                tickmode = 'linear',
                tick0 = strike_prices[-1],
                dtick = 2
            ),
            title_text=title + ': ' + yaxis_title
        )                
        fig.show()


    def _graphs(self, spot_price, strike_prices, df, title, yaxis_title):
        """ Renders graph charts with calculated results.
        For more information please refer to https://plotly.com/python-api-reference/generated/plotly.graph_objects

        :param spot_price: (float) underlying spot price for vertical line in red
        :param strike_prices: (array_like) strike prices distribution
        :param df: (dataframe) dataframe with results for profit/loss, % of max risk and option/spread values
        :param title: (str) title for each option strategy
        :param yaxis_title: (str) yaxis title as 'Profit and Loss (USD)', 'Risk Percent' and 'Option/Spread Values'
        :return: interactive traces with Plotly
        """

        # Import graph_objects from plotly
        import plotly.graph_objects as go
    
        # Create traces
        fig = go.Figure()

        # Plot the terminal payoff for each day
        for (columns, rows) in df.iteritems():
            fig.add_trace(go.Scatter(
                x=strike_prices,
                y=rows.values,
                mode='lines', 
                name=columns))
            
        # Set a horizontal line at zero P&L 
        fig.add_hline(y=0, line_width=3, line_color='green')

        # Set a vertical line at ATM strike
        fig.add_vline(x=spot_price, line_width=3, line_color='red', name='Spot Price')

        # Set x and y axis labels and title
        fig.update_layout(title=title, xaxis_title='Underlying Price', yaxis_title=yaxis_title)

        # Display the chart
        fig.show()  


    def _vis_pnl(self, spot_price, strike_prices, labels, df, graph_type, title, yaxis_title):
        """ Selects visualization option such as 'table', 'graph', or 'both' for each strategy.
         
        :param spot_price: (float) underlying spot price for vertical line in red
        :param strike_prices: (array_like) strike prices distribution
        :param labels: (list) dates as "%Y-%m-%d" and 'Expiration date'
        :param df: (dataframe) dataframe with results for profit/loss, % of max risk and option/spread values
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param title: (str) title for each option strategy
        :param yaxis_title: (str) yaxis title as 'Profit and Loss (USD)', 'Risk Percent' and 'Option/Spread Values'
        :return: annotated heatmap table and/or graph traces with calculated results
        """

        # Plot table and/or graphs
        try:
            if graph_type == 'table':
                self._heatmap(strike_prices=strike_prices, labels=labels, df=df, title=title, yaxis_title=yaxis_title)

            elif graph_type == 'graph':
                self._graphs(spot_price=spot_price, strike_prices=strike_prices, df=df,
                                 title=title, yaxis_title=yaxis_title)

            elif graph_type == 'both':
                self._heatmap(strike_prices=strike_prices, labels=labels, df=df, title=title, yaxis_title=yaxis_title)
                self._graphs(spot_price=spot_price, strike_prices=strike_prices, df=df,
                                 title=title, yaxis_title=yaxis_title)
        except:
            print('Please select a valid option.')


    def _show_results(self, spot_price, pnl, df, option_spreads, strike_prices, labels, title,
                      graph_type, graph_profile):
        """ Shows results for calculated pnl, risk % or option/spread value by calling _vis_pnl().

        :param spot_price: (float) underlying spot price for vertical line in red
        :param pnl: (array_like) calculated profit and loss with BSM model to get max_loss_at_expiry value
        :param df: (dataframe) dataframe with results for profit/loss, % of max risk and option/spread values
        :param option_spreads: (array_like) calculated options/spread values
        :param strike_prices: (array_like) strike prices distribution
        :param labels: (list) dates as "%Y-%m-%d" and 'Expiration date'
        :param title: (str) title for each option strategy
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param graph_profile: (str) graph profile such as 'pnl', 'risk' or 'option/spread'
        :return: (figure) renders annotated heatmap table and/or graph traces with calculated results
        """

        # Define auxiliary global variables
        global yaxis_title

        # Select specific data for results visualization
        try:
            if graph_profile == 'pnl':

                # yaxis label for payoff graphs
                yaxis_title = 'Profit and Loss (USD)'

            elif graph_profile == 'risk':

                # yaxis label for payoff graphs
                yaxis_title = 'Risk Percent'

                # Calculate maximum loss at expiry
                max_loss_at_expiry = abs(min(pnl[-1]))

                # Create risk % dataframe
                df = (df / max_loss_at_expiry) * 100

            elif graph_profile == 'option/spread':

                # yaxis label for payoff graphs
                yaxis_title = 'Option/Spread Values'

                # Calculate purchased value per option without multiplying by 100
                # option_spreads = prices

                # Create option/spread value dataframe
                df = pd.DataFrame(data=option_spreads.T, index=strike_prices, columns=labels)

            # Visualize results
            self._vis_pnl(spot_price=spot_price, strike_prices=strike_prices, labels=labels, df=df,
                          graph_type=graph_type, title=title, yaxis_title=yaxis_title)

        except AttributeError:
            print('Please provide a graph profile.')


    def _get_option_prices(self, legs, S, T, K_1, r_1, q_1, sigma_1, option_type_1,
                          K_2=None, r_2=None, q_2=None, sigma_2=None, option_type_2=None,
                          K_3=None, r_3=None, q_3=None, sigma_3=None, option_type_3=None,
                          K_4=None, r_4=None, q_4=None, sigma_4=None, option_type_4=None,
                          K_5=None, r_5=None, q_5=None, sigma_5=None, option_type_5=None,
                          K_6=None, r_6=None, q_6=None, sigma_6=None, option_type_6=None,
                          K_7=None, r_7=None, q_7=None, sigma_7=None, option_type_7=None,
                          K_8=None, r_8=None, q_8=None, sigma_8=None, option_type_8=None):
        """ Calculates option prices with BSM options.

        :param legs: (int) amount of legs for each strategy
        :param S: (float) underlying stock price
        :param T: (float) annualized time to maturity
        :param K_1: (float) strike price for option 1
        :param r_1: (float) risk-free interest rate for option 1
        :param q_1: (float) dividend yield for option 1
        :param sigma_1: (float) implied volatility for option 1
        :param option_type_1: (str) 'put' or 'call' option type for option 1
        :param K_2: (float) strike price for option 2. Default is None
        :param r_2: (float) risk-free interest rate for option 2. Default is None
        :param q_2: (float) dividend yield for option 2. Default is None
        :param sigma_2: (float) implied volatility for option 2. Default is None
        :param option_type_2: (str) 'put' or 'call' option type for option 2. Default is None
        :param K_3: (float) strike price for option 3. Default is None
        :param r_3: (float) risk-free interest rate for option 3. Default is None
        :param q_3: (float) dividend yield for option 3. Default is None
        :param sigma_3: (float) implied volatility for option 3. Default is None
        :param option_type_3: (str) 'put' or 'call' option type for option 3. Default is None
        :param K_4: (float) strike price for option 4. Default is None
        :param r_4: (float) risk-free interest rate for option 4. Default is None
        :param q_4: (float) dividend yield for option 4. Default is None
        :param sigma_4: (float) implied volatility for option 4. Default is None
        :param option_type_4: (str) 'put' or 'call' option type for option 4. Default is None
        :param K_5: (float) strike price for option 5. Default is None
        :param r_5: (float) risk-free interest rate for option 5. Default is None
        :param q_5: (float) dividend yield for option 5. Default is None
        :param sigma_5: (float) implied volatility for option 5. Default is None
        :param option_type_5: (str) 'put' or 'call' option type for option 5. Default is None
        :param K_6: (float) strike price for option 6. Default is None
        :param r_6: (float) risk-free interest rate for option 6. Default is None
        :param q_6: (float) dividend yield for option 6. Default is None
        :param sigma_6: (float) implied volatility for option 6. Default is None
        :param option_type_6: (str) 'put' or 'call' option type for option 6. Default is None
        :param K_7: (float) strike price for option 7. Default is None
        :param r_7: (float) risk-free interest rate for option 7. Default is None
        :param q_7: (float) dividend yield for option 7. Default is None
        :param sigma_7: (float) implied volatility for option 7. Default is None
        :param option_type_7: (str) 'put' or 'call' option type for option 6. Default is None
        :param K_8: (float) strike price for option 8. Default is None
        :param r_8: (float) risk-free interest rate for option 8. Default is None
        :param q_8: (float) dividend yield for option 8. Default is None
        :param sigma_8: (float) implied volatility for option 8. Default is None
        :param option_type_8: (str) 'put' or 'call' option type for option 8. Default is None
        :return: strike_prices, labels, dates_until_maturity, prices_at_expiration and estimated_prices for each option
        """

        # Define auxiliary global variables
        global labels_op2, dates_until_maturity_op2, prices_at_expiration_op2, estimated_prices_op2, \
            labels_op3, dates_until_maturity_op3, prices_at_expiration_op3, estimated_prices_op3, \
            labels_op4, dates_until_maturity_op4, prices_at_expiration_op4, estimated_prices_op4, \
            prices_at_expiration_op5, estimated_prices_op5, prices_at_expiration_op6, estimated_prices_op6, \
            prices_at_expiration_op7, estimated_prices_op7, prices_at_expiration_op8, estimated_prices_op8

        # Create strike array between 93 % and 1.1 % at steps of 3.
        # This values are used to reflect the strike distribution of options calculator
        strike_prices = np.arange(np.around(S * 0.93), np.around(S * 1.1), 2)
        strike_prices = np.flipud(strike_prices)

        # Get labels and dates for expiry date
        labels, dates_until_maturity = self._get_labels(expiry_date=T)

        # Store option_price arrays in lambda functions to improve performance
        prices_at_expiration = lambda S: self._bsm_price(S, K_1, 0, r_1, q_1, sigma_1, option_type_1)
        estimated_prices = lambda S, T: self._bsm_price(S, K_1, T, r_1, q_1, sigma_1, option_type_1)

        # Next steps must run at execution

        # Unpack lambda functions values for cleansing
        prices_at_expiration = prices_at_expiration(strike_prices)
        estimated_prices = [estimated_prices(strike_prices, date) for date in dates_until_maturity]

        # Replace NaN with zero and infinity with large finite numbers
        prices_at_expiration = np.nan_to_num(prices_at_expiration, copy=False)
        estimated_prices = np.nan_to_num(estimated_prices, copy=False)

        # print('Prices at expiration: \n', prices_at_expiration)
        # print('Estimated prices: \n', estimated_prices)

        if legs > 1:
            # Store option_price arrays in lambda functions to improve performance
            prices_at_expiration_op2 = lambda S: self._bsm_price(S, K_2, 0, r_2, q_2, sigma_2, option_type_2)
            estimated_prices_op2 = lambda S, T: self._bsm_price(S, K_2, T, r_2, q_2, sigma_2, option_type_2)

            # Unpack lambda functions values for cleansing
            prices_at_expiration_op2 = prices_at_expiration_op2(strike_prices)
            estimated_prices_op2 = [estimated_prices_op2(strike_prices, date) for date in dates_until_maturity]

            # Replace NaN with zero and infinity with large finite numbers
            prices_at_expiration_op2 = np.nan_to_num(prices_at_expiration_op2, copy=False)
            estimated_prices_op2 = np.nan_to_num(estimated_prices_op2, copy=False)

        if legs > 2:
            # Store option_price arrays in lambda functions to improve performance
            prices_at_expiration_op3 = lambda S: self._bsm_price(S, K_3, 0, r_3, q_3, sigma_3, option_type_3)
            estimated_prices_op3 = lambda S, T: self._bsm_price(S, K_3, T, r_3, q_3, sigma_3, option_type_3)

            # Unpack lambda functions values for cleansing
            prices_at_expiration_op3 = prices_at_expiration_op3(strike_prices)
            estimated_prices_op3 = [estimated_prices_op3(strike_prices, date) for date in dates_until_maturity]

            # Replace NaN with zero and infinity with large finite numbers
            prices_at_expiration_op3 = np.nan_to_num(prices_at_expiration_op3, copy=False)
            estimated_prices_op3 = np.nan_to_num(estimated_prices_op3, copy=False)

        if legs > 3:
            # Store option_price arrays in lambda functions to improve performance
            prices_at_expiration_op4 = lambda S: self._bsm_price(S, K_4, 0, r_4, q_4, sigma_4, option_type_4)
            estimated_prices_op4 = lambda S, T: self._bsm_price(S, K_4, T, r_4, q_4, sigma_4, option_type_4)

            # Unpack lambda functions values for cleansing
            prices_at_expiration_op4 = prices_at_expiration_op4(strike_prices)
            estimated_prices_op4 = [estimated_prices_op4(strike_prices, date) for date in dates_until_maturity]

            # Replace NaN with zero and infinity with large finite numbers
            prices_at_expiration_op4 = np.nan_to_num(prices_at_expiration_op4, copy=False)
            estimated_prices_op4 = np.nan_to_num(estimated_prices_op4, copy=False)

        if legs > 4:
            # Store option_price arrays in lambda functions to improve performance
            prices_at_expiration_op5 = lambda S: self._bsm_price(S, K_5, 0, r_5, q_5, sigma_5, option_type_5)
            estimated_prices_op5 = lambda S, T: self._bsm_price(S, K_5, T, r_5, q_5, sigma_5, option_type_5)

            # Unpack lambda functions values for cleansing
            prices_at_expiration_op5 = prices_at_expiration_op5(strike_prices)
            estimated_prices_op5 = [estimated_prices_op5(strike_prices, date) for date in dates_until_maturity]

            # Replace NaN with zero and infinity with large finite numbers
            prices_at_expiration_op5 = np.nan_to_num(prices_at_expiration_op5, copy=False)
            estimated_prices_op5 = np.nan_to_num(estimated_prices_op5, copy=False)

        if legs > 5:
            # Store option_price arrays in lambda functions to improve performance
            prices_at_expiration_op6 = lambda S: self._bsm_price(S, K_6, 0, r_6, q_6, sigma_6, option_type_6)
            estimated_prices_op6 = lambda S, T: self._bsm_price(S, K_6, T, r_6, q_6, sigma_6, option_type_6)

            # Unpack lambda functions values for cleansing
            prices_at_expiration_op6 = prices_at_expiration_op6(strike_prices)
            estimated_prices_op6 = [estimated_prices_op6(strike_prices, date) for date in dates_until_maturity]

            # Replace NaN with zero and infinity with large finite numbers
            prices_at_expiration_op6 = np.nan_to_num(prices_at_expiration_op6, copy=False)
            estimated_prices_op6 = np.nan_to_num(estimated_prices_op6, copy=False)

        if legs > 6:
            # Store option_price arrays in lambda functions to improve performance
            prices_at_expiration_op7 = lambda S: self._bsm_price(S, K_7, 0, r_7, q_7, sigma_7, option_type_7)
            estimated_prices_op7 = lambda S, T: self._bsm_price(S, K_7, T, r_7, q_7, sigma_7, option_type_7)

            # Unpack lambda functions values for cleansing
            prices_at_expiration_op7 = prices_at_expiration_op7(strike_prices)
            estimated_prices_op7 = [estimated_prices_op7(strike_prices, date) for date in dates_until_maturity]

            # Replace NaN with zero and infinity with large finite numbers
            prices_at_expiration_op7 = np.nan_to_num(prices_at_expiration_op7, copy=False)
            estimated_prices_op7 = np.nan_to_num(estimated_prices_op7, copy=False)

        if legs > 7:
            # Store option_price arrays in lambda functions to improve performance
            prices_at_expiration_op8 = lambda S: self._bsm_price(S, K_8, 0, r_8, q_8, sigma_8, option_type_8)
            estimated_prices_op8 = lambda S, T: self._bsm_price(S, K_8, T, r_8, q_8, sigma_8, option_type_8)

            # Unpack lambda functions values for cleansing
            prices_at_expiration_op8 = prices_at_expiration_op8(strike_prices)
            estimated_prices_op8 = [estimated_prices_op8(strike_prices, date) for date in dates_until_maturity]

            # Replace NaN with zero and infinity with large finite numbers
            prices_at_expiration_op8 = np.nan_to_num(prices_at_expiration_op8, copy=False)
            estimated_prices_op8 = np.nan_to_num(estimated_prices_op8, copy=False)

        if legs == 1:
            return strike_prices, labels, dates_until_maturity, prices_at_expiration, estimated_prices

        if legs == 2:
            return strike_prices, labels, dates_until_maturity, prices_at_expiration, estimated_prices, \
                   prices_at_expiration_op2, estimated_prices_op2

        if legs == 3:
            return strike_prices, labels, dates_until_maturity, prices_at_expiration, estimated_prices, \
                   prices_at_expiration_op2, estimated_prices_op2, \
                   prices_at_expiration_op3, estimated_prices_op3

        if legs == 4:
            return strike_prices, labels, dates_until_maturity, prices_at_expiration, estimated_prices, \
                   prices_at_expiration_op2, estimated_prices_op2, \
                   prices_at_expiration_op3, estimated_prices_op3, \
                   prices_at_expiration_op4, estimated_prices_op4

        if legs == 5:
            return strike_prices, labels, dates_until_maturity, prices_at_expiration, estimated_prices, \
                   prices_at_expiration_op2, estimated_prices_op2, \
                   prices_at_expiration_op3, estimated_prices_op3, \
                   prices_at_expiration_op4, estimated_prices_op4, \
                   prices_at_expiration_op5, estimated_prices_op5

        if legs == 6:
            return strike_prices, labels, dates_until_maturity, prices_at_expiration, estimated_prices, \
                   prices_at_expiration_op2, estimated_prices_op2, \
                   prices_at_expiration_op3, estimated_prices_op3, \
                   prices_at_expiration_op4, estimated_prices_op4, \
                   prices_at_expiration_op5, estimated_prices_op5, \
                   prices_at_expiration_op6, estimated_prices_op6

        if legs == 7:
            return strike_prices, labels, dates_until_maturity, prices_at_expiration, estimated_prices, \
                   prices_at_expiration_op2, estimated_prices_op2, \
                   prices_at_expiration_op3, estimated_prices_op3, \
                   prices_at_expiration_op4, estimated_prices_op4, \
                   prices_at_expiration_op5, estimated_prices_op5, \
                   prices_at_expiration_op6, estimated_prices_op6, \
                   prices_at_expiration_op7, estimated_prices_op7

        if legs == 8:
            return strike_prices, labels, dates_until_maturity, prices_at_expiration, estimated_prices, \
                   prices_at_expiration_op2, estimated_prices_op2, \
                   prices_at_expiration_op3, estimated_prices_op3, \
                   prices_at_expiration_op4, estimated_prices_op4, \
                   prices_at_expiration_op5, estimated_prices_op5, \
                   prices_at_expiration_op6, estimated_prices_op6, \
                   prices_at_expiration_op7, estimated_prices_op7, \
                   prices_at_expiration_op8, estimated_prices_op8


    ########################################### BASIC STRATEGIES #######################################################

    def call_put(self, spot_price, expiration_date, action, contracts, option_price, option_type, strike_price,
                 risk_free_rate, dividend_yield, volatility, graph_type, graph_profile):
        """ Displays calculated option values for the long/short call or long/short put strategy.

        :param spot_price: (float) underlying stock price
        :param expiration_date: (str) expiration date
        :param action: (str) whether the action is a buy or write
        :param contracts: (int) # of contracts to buy/write
        :param option_price: (float) bid/ask price per option
        :param option_type: (str) 'put' or 'call' option type
        :param strike_price: (float) strike price
        :param risk_free_rate: (float) risk-free interest rate
        :param dividend_yield: (float) dividend yield
        :param volatility: (float) implied volatility
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param graph_profile: (str) graph profile such as 'pnl', 'risk' or 'option/spread'
        :return: annotated heatmap table and/or graph traces with calculated results
        """

        # Define auxiliary global variables
        global sign, title

        # Calculate option prices
        strike_prices, labels, dates_until_maturity, maturity_prices, estimated_prices = self._get_option_prices(
            legs=1, S=spot_price, T=expiration_date, K_1=strike_price, r_1=risk_free_rate, q_1=dividend_yield,
            sigma_1=volatility, option_type_1=option_type)

        # Set title and direction sign as -1 if write and +1 if buy
        try:
            if action == 'buy':
                sign = 1
                title = 'Long ' + str(option_type)
            elif action == 'write':
                sign = -1
                title = 'Short ' + str(option_type)
        except AttributeError:
            print('Please provide action as buy/write')

        # Concatenate calculated prices and multiply by # contracts and 100
        option_prices = sign * np.asarray(
            np.concatenate(
                (estimated_prices, maturity_prices.T.reshape(
                    1, maturity_prices.shape[0]))))
        option_values = option_prices * contracts * 100

        # Calculate Entry Costs
        entry_cost = option_price * contracts * sign * 100

        # Calculate total payoff
        pnl = option_values - entry_cost

        # Create pnl dataframe
        df = pd.DataFrame(data=pnl.T, index=strike_prices, columns=labels)

        # Calculate purchased value per option / 100
        option_spreads = option_values / 100

        # Visualize results
        self._show_results(spot_price=spot_price, pnl=pnl, df=df, option_spreads=option_spreads,
                           strike_prices=strike_prices, labels=labels, title=title,
                           graph_type=graph_type, graph_profile=graph_profile)


    def covered_call(self, spot_price, expiration_date, num_shares, contracts, option_price,
                     strike_price, risk_free_rate, dividend_yield, volatility, graph_type, graph_profile):
        """ Displays calculated option values for the covered call strategy.

        :param spot_price: (float) underlying stock price
        :param expiration_date: (str) expiration date
        :para num_shares: (int) # of shares of the underlying stock to hold
        :param contracts: (int) # of contracts to buy/write
        :param option_price: (float) bid/ask price per option
        :param strike_price: (float) strike price
        :param risk_free_rate: (float) risk-free interest rate
        :param dividend_yield: (float) dividend yield
        :param volatility: (float) implied volatility
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param graph_profile: (str) graph profile such as 'pnl', 'risk' or 'option/spread'
        :return: annotated heatmap table and/or graph traces with calculated results
        """

        # Calculate option prices with BSM options
        strike_prices, labels, dates_until_maturity, maturity_prices, \
        estimated_prices = self._get_option_prices(
            legs=1, S=spot_price, T=expiration_date, K_1=strike_price,
            r_1=risk_free_rate, q_1=dividend_yield, sigma_1=volatility, option_type_1='call')

        # Concatenate calculated prices and multiply by # contracts and 100
        option_prices = (-1.0) * np.asarray(
            np.concatenate(
                (estimated_prices, maturity_prices.T.reshape(
                    1, maturity_prices.shape[0]))))
        option_values = option_prices * contracts * 100

        # Create array with change in stock value as (K - S0) per strike and multiply by # shares
        stock_only_values = (strike_prices - spot_price) * num_shares  # len(stock_only_array) = len(strike_prices)

        # Calculate Entry Costs
        entry_cost = - option_price * contracts * 100

        # Calculate total payoff
        pnl = option_values + stock_only_values - entry_cost

        # Create pnl dataframe
        df = pd.DataFrame(data=pnl.T, index=strike_prices, columns=labels)

        # Calculate purchased value per option / 100 - stock only values / num_shares
        option_spreads = option_values / 100 + stock_only_values / num_shares

        # Make title for visualization
        title = 'Covered Call'

        # Visualize results
        self._show_results(spot_price=spot_price, pnl=pnl, df=df, option_spreads=option_spreads,
                           strike_prices=strike_prices, labels=labels, title=title,
                           graph_type=graph_type, graph_profile=graph_profile)


    ########################################### SPREAD STRATEGIES ######################################################

    def spread(self, spot_price, expiration_date, long_contracts, long_price, long_type, long_strike_price,
               long_risk_free_rate, long_dividend_yield, long_volatility, short_contracts, short_price, short_type,
               short_strike_price, short_risk_free_rate, short_dividend_yield, short_volatility,
               graph_type, graph_profile):
        """ Displays calculated option values for spread strategies: credit, call, put and calendar.

        :param spot_price: (float) underlying stock price
        :param expiration_date: (str) expiration date
        :param long_contracts: (int) # of contracts to buy/write for long option
        :param long_price: (float) ask price for long option
        :param long_type: (str) 'put' or 'call' option type for long option
        :param long_strike_price: (float) strike price for long option
        :param long_risk_free_rate: (float) risk-free interest rate for long option
        :param long_dividend_yield: (float) dividend yield for long option
        :param long_volatility: (float) implied volatility for long option
        :param short_contracts: (int) # of contracts to buy/write for short option
        :param short_price: (float) ask price for short option
        :param short_type: (str) 'put' or 'call' option type for short option
        :param short_strike_price: (float) strike price for short option
        :param short_risk_free_rate: (float) risk-free interest rate for short option
        :param short_dividend_yield: (float) dividend yield for short option
        :param short_volatility: (float) implied volatility for short option
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param graph_profile: (str) graph profile such as 'pnl', 'risk' or 'option/spread'
        :return: annotated heatmap table and/or graph traces with calculated results
        """

        # Calculate option prices with BSM options
        strike_prices, labels, dates_until_maturity, maturity_prices_long, estimated_prices_long, \
        maturity_short_prices, estimated_short_prices = self._get_option_prices(
            legs=2, S=spot_price, T=expiration_date, K_1=long_strike_price, r_1=long_risk_free_rate,
            q_1=long_dividend_yield, sigma_1=long_volatility, option_type_1=long_type, K_2=short_strike_price,
            r_2=short_risk_free_rate, q_2=short_dividend_yield, sigma_2=short_volatility, option_type_2=short_type)

        # Concatenate calculated prices and multiply by # contracts and 100
        # Long option
        long_prices = np.asarray(
            np.concatenate(
                (estimated_prices_long, maturity_prices_long.T.reshape(
                    1, maturity_prices_long.shape[0]))))
        long_values = long_prices * long_contracts * 100

        # Short option
        short_prices = (-1.0) * np.asarray(
            np.concatenate(
                (estimated_short_prices, maturity_short_prices.T.reshape(
                    1, maturity_short_prices.shape[0]))))
        short_values = short_prices * short_contracts * 100

        # Calculate entry cost
        long_cost = long_price * long_contracts * 100
        short_cost = - short_price * short_contracts * 100
        entry_cost = long_cost + short_cost

        # Get total payoff by adding estimated values minus entry cost
        pnl = long_values + short_values - entry_cost

        # Sum all pnl minus the total cost
        df = pd.DataFrame(data=pnl.T, index=strike_prices, columns=labels)

        # Calculate purchased value per option / 100
        option_spreads = long_values/100 + short_values/100

        # Make title for visualization
        title = 'Spread: Long ' + str(long_type) + ' - Short ' + str(short_type)

        # Visualize results
        self._show_results(spot_price=spot_price, pnl=pnl, df=df, option_spreads=option_spreads,
                           strike_prices=strike_prices, labels=labels, title=title,
                           graph_type=graph_type, graph_profile=graph_profile)


    def back_spread(self, spot_price, expiration_date, long_contracts, long_price, long_type,
               long_strike_price, long_risk_free_rate, long_dividend_yield, long_volatility, ratio,
               short_contracts, short_price, short_type, short_strike_price, short_risk_free_rate,
               short_dividend_yield, short_volatility, graph_type, graph_profile):
        """ Displays calculated option values for the back spread strategy:
                Short one ITM option
                Long ratio * OTM options

        :param spot_price: (float) underlying stock price
        :param expiration_date: (str) expiration date
        :param long_contracts: (int) # of contracts to buy/write for long option
        :param long_price: (float) ask price for long option
        :param long_type: (str) 'put' or 'call' option type for long option
        :param long_strike_price: (float) strike price for long option
        :param long_risk_free_rate: (float) risk-free interest rate for long option
        :param long_dividend_yield: (float) dividend yield for long option
        :param long_volatility: (float) implied volatility for long option
        :param ratio: (int) ratio for long option, it should be twice as # contracts for short option
        :param short_contracts: (int) # of contracts to buy/write for short option
        :param short_price: (float) ask price for short option
        :param short_type: (str) 'put' or 'call' option type for short option
        :param short_strike_price: (float) strike price for short option
        :param short_risk_free_rate: (float) risk-free interest rate for short option
        :param short_dividend_yield: (float) dividend yield for short option
        :param short_volatility: (float) implied volatility for short option
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param graph_profile: (str) graph profile such as 'pnl', 'risk' or 'option/spread'
        :return: annotated heatmap table and/or graph traces with calculated results
        """

        # Calculate option prices with BSM options
        strike_prices, labels, dates_until_maturity, maturity_prices_long, estimated_prices_long, \
        maturity_short_prices, estimated_short_prices = self._get_option_prices(
            legs=2, S=spot_price, T=expiration_date, K_1=long_strike_price, r_1=long_risk_free_rate,
            q_1=long_dividend_yield, sigma_1=long_volatility, option_type_1=long_type, K_2=short_strike_price,
            r_2=short_risk_free_rate, q_2=short_dividend_yield, sigma_2=short_volatility, option_type_2=short_type)

        # Concatenate calculated prices and multiply by # contracts and 100
        # Long option
        long_prices = np.asarray(
            np.concatenate(
                (estimated_prices_long, maturity_prices_long.T.reshape(
                    1, maturity_prices_long.shape[0]))))
        long_values = long_prices * long_contracts * ratio * 100
        # Short option
        short_prices = (-1.0) * np.asarray(
            np.concatenate(
                (estimated_short_prices, maturity_short_prices.T.reshape(
                    1, maturity_short_prices.shape[0]))))
        short_values = short_prices * short_contracts * 100

        # Calculate entry cost
        long_cost = long_price * long_contracts * ratio * 100
        short_cost = - short_price * short_contracts * 100
        entry_cost = long_cost + short_cost

        # Get pnl by adding estimated values minus entry cost
        pnl = long_values + short_values - entry_cost

        # Sum all pnl minus the total cost
        df = pd.DataFrame(data=pnl.T, index=strike_prices, columns=labels)

        # Calculate purchased value per option / 100
        option_spreads = long_values/100 + short_values/100

        # Make title for visualization
        title = 'Back Spread: ' + 'Long ' + str(long_type) + ' - ' + 'Short ' + str(short_type)

        # Visualize results
        self._show_results(spot_price=spot_price, pnl=pnl, df=df, option_spreads=option_spreads,
                           strike_prices=strike_prices, labels=labels, title=title,
                           graph_type=graph_type, graph_profile=graph_profile)

    ########################################## ADVANCED STRATEGIES #####################################################

    def iron_condor(self, spot_price, expiration_date, long_put_price, long_put_strike_price, long_put_risk_free_rate,
                    long_put_dividend_yield, long_put_volatility, long_put_contracts, short_put_price,
                    short_put_strike_price, short_put_risk_free_rate, short_put_dividend_yield, short_put_volatility,
                    short_put_contracts, short_call_price, short_call_strike_price, short_call_risk_free_rate,
                    short_call_dividend_yield, short_call_volatility, short_call_contracts, long_call_price,
                    long_call_strike_price, long_call_risk_free_rate, long_call_dividend_yield, long_call_volatility,
                    long_call_contracts, graph_type, graph_profile):
        """ Displays calculated option values for the iron condor strategy:
                Long one OTM put
                Short one OTM put with a higher strike
                Short one OTM call
                Long one OTM call with a higher strike
                Akin to having a long strangle inside a larger short strangle
                (or vice-versa)

        :param spot_price: (float) underlying stock price
        :param expiration_date: (str) expiration date
        :param long_put_price: (float) ask price for long put option
        :param long_put_strike_price: (float) strike price for long put option
        :param long_put_risk_free_rate: (float) risk-free interest rate for long put option
        :param long_put_dividend_yield: (float) dividend yield for long put option
        :param long_put_volatility: (float) implied volatility for long put option
        :param long_put_contracts: (int) # of contracts to buy/write for long put option
        :param short_put_price: (float) bid price for short put option
        :param short_put_strike_price: (float) strike price for short put option
        :param short_put_risk_free_rate: (float) risk-free interest rate for short put option
        :param short_put_dividend_yield: (float) dividend yield for short put option
        :param short_put_volatility: (float) implied volatility for short put option
        :param short_put_contracts: (int) # of contracts to buy/write for short put option
        :param short_call_price: (float) bid price for short call option
        :param short_call_strike_price: (float) strike price for short call option
        :param short_call_risk_free_rate: (float) risk-free interest rate for short call option
        :param short_call_dividend_yield: (float) dividend yield for short call option
        :param short_call_volatility: (float) implied volatility for short call option
        :param short_call_contracts: (int) # of contracts to buy/write for short call option
        :param long_call_price: (float) ask price for long call option
        :param long_call_strike_price: (float) strike price for long call option
        :param long_call_risk_free_rate: (float) risk-free interest rate for long call option
        :param long_call_dividend_yield: (float) implied volatility for long call option
        :param long_call_volatility: (float) implied volatility for long call option
        :param long_call_contracts: (int) # of contracts to buy/write for long call option
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param graph_profile: (str) graph profile such as 'pnl', 'risk' or 'option/spread'
        :return: annotated heatmap table and/or graph traces with calculated results
        """

        # Calculate option prices with BSM options
        strike_prices, labels, dates_until_maturity, maturity_prices_long_put, estimated_prices_long_put, \
        maturity_short_prices_put, estimated_short_prices_put, maturity_short_prices_call, estimated_short_prices_call, \
        maturity_prices_long_call, estimated_prices_long_call = self._get_option_prices(
            legs=4, S=spot_price, T=expiration_date, K_1=long_put_strike_price, r_1=long_put_risk_free_rate,
            q_1=long_put_dividend_yield, sigma_1=long_put_volatility, option_type_1='put', K_2=short_put_strike_price,
            r_2=short_put_risk_free_rate, q_2=short_put_dividend_yield, sigma_2=short_put_volatility,
            option_type_2='put', K_3=short_call_strike_price, r_3=short_call_risk_free_rate,
            q_3=short_call_dividend_yield, sigma_3=short_call_volatility, option_type_3='call',
            K_4=long_call_strike_price, r_4=long_call_risk_free_rate, q_4=long_call_dividend_yield,
            sigma_4=long_call_volatility, option_type_4='call')

        # Concatenate calculated prices and multiply by # contracts and 100
        # Long put
        long_put_prices = np.asarray(
            np.concatenate(
                (estimated_prices_long_put, maturity_prices_long_put.T.reshape(
                    1, maturity_prices_long_put.shape[0]))))
        long_put_values = long_put_prices * long_put_contracts * 100
        # Short put
        short_put_prices = (-1.0) * np.asarray(
            np.concatenate(
                (estimated_short_prices_put, maturity_short_prices_put.T.reshape(
                    1, maturity_short_prices_put.shape[0]))))
        short_put_values = short_put_prices * short_put_contracts * 100
        # Short call
        short_call_prices = (-1.0) * np.asarray(
            np.concatenate(
                (estimated_short_prices_call, maturity_short_prices_call.T.reshape(
                    1, maturity_short_prices_call.shape[0]))))
        short_call_values = short_call_prices * short_call_contracts * 100
        # Long call
        long_call_prices = np.asarray(
            np.concatenate(
                (estimated_prices_long_call, maturity_prices_long_call.T.reshape(
                    1, maturity_prices_long_call.shape[0]))))
        long_call_values = long_call_prices * long_call_contracts * 100

        # Calculate entry cost
        long_put_cost = long_put_price * long_put_contracts * 100
        short_put_cost = - short_put_price * short_put_contracts * 100
        short_call_cost = - short_call_price * short_call_contracts * 100
        long_call_cost = long_call_price * long_call_price * 100
        entry_cost = long_put_cost + short_put_cost + short_call_cost + long_call_cost

        # Calculate pnl by adding estimated values minus entry cost
        pnl = long_put_values + short_put_values + short_call_values + long_call_values - entry_cost

        # Create pnl dataframe
        df = pd.DataFrame(data=pnl.T, index=strike_prices, columns=labels)

        # Calculate purchased value per option / 100
        option_spreads = long_put_values/100 + short_put_values/100 + short_call_values/100 + long_call_values/100
        
        # Make title for visualization
        title = 'Iron Condor'

        # Visualize results
        self._show_results(spot_price=spot_price, pnl=pnl, df=df, option_spreads=option_spreads,
                           strike_prices=strike_prices, labels=labels, title=title,
                           graph_type=graph_type, graph_profile=graph_profile)

    def collar(self, spot_price, expiration_date, num_shares, long_contracts, long_price, long_type, long_strike_price,
               long_risk_free_rate, long_dividend_yield, long_volatility, short_contracts, short_price, short_type,
               short_strike_price, short_risk_free_rate, short_dividend_yield, short_volatility,
               graph_type, graph_profile):
        """ Displays calculated option values for the collar strategy:
                Long one OTM put
                Short one OTM call

        :param spot_price: (float) underlying stock price
        :param expiration_date: (str) expiration date
        :param num_shares: (int) # of shares of the underlying stock to hold
        :param long_contracts: (int) # of contracts to buy/write for long option
        :param long_price: (float) ask price for long option
        :param long_type: (str) 'put' or 'call' option type for long option
        :param long_strike_price: (float) strike price for long option
        :param long_risk_free_rate: (float) risk-free interest rate for long option
        :param long_dividend_yield: (float) dividend yield for long option
        :param long_volatility: (float) implied volatility for long option
        :param ratio: (int) ratio for long option, it should be twice as # contracts for short option
        :param short_contracts: (int) # of contracts to buy/write for short option
        :param short_price: (float) ask price for short option
        :param short_type: (str) 'put' or 'call' option type for short option
        :param short_strike_price: (float) strike price for short option
        :param short_risk_free_rate: (float) risk-free interest rate for short option
        :param short_dividend_yield: (float) dividend yield for short option
        :param short_volatility: (float) implied volatility for short option
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param graph_profile: (str) graph profile such as 'pnl', 'risk' or 'option/spread'
        :return: annotated heatmap table and/or graph traces with calculated results
        """

        # Calculate option prices with BSM options
        strike_prices, labels, dates_until_maturity, maturity_prices_long, estimated_prices_long, \
        maturity_short_prices, estimated_short_prices = self._get_option_prices(
            legs=2, S=spot_price, T=expiration_date, K_1=long_strike_price, r_1=long_risk_free_rate,
            q_1=long_dividend_yield, sigma_1=long_volatility, option_type_1=long_type, K_2=short_strike_price,
            r_2=short_risk_free_rate, q_2=short_dividend_yield, sigma_2=short_volatility, option_type_2=short_type)

        # Concatenate calculated prices and multiply by # contracts and 100
        # Long option
        long_prices = np.asarray(np.concatenate(
            (estimated_prices_long, maturity_prices_long.T.reshape(
                1, maturity_prices_long.shape[0]))))
        long_values = long_prices * long_contracts * 100
        # Short option
        short_prices = (-1.0) * np.asarray(np.concatenate(
            (estimated_short_prices, maturity_short_prices.T.reshape(
                1, maturity_short_prices.shape[0]))))
        short_values = short_prices * short_contracts * 100

        # Create array with change in stock value as (K - S0) per strike and multiply by # shares
        stock_only_values = (strike_prices - spot_price) * num_shares  # len(stock_only_array) = len(strike_prices)

        # Calculate entry cost
        long_cost = long_price * long_contracts * 100
        short_cost = - short_price * short_contracts * 100
        entry_cost = long_cost + short_cost

        # Calculate pnl by adding estimated values minus entry cost
        pnl = long_values + short_values + stock_only_values - entry_cost

        # Create pnl dataframe
        df = pd.DataFrame(data=pnl.T, index=strike_prices, columns=labels)

        # Calculate purchased value per option / 100
        option_spreads = long_values / 100 + short_values / 100 + stock_only_values / num_shares

        # Title for plotting
        title = 'Collar: ' + 'Long ' + str(long_type) + ' - ' + 'Short ' + str(short_type)

        # Visualize results
        self._show_results(spot_price=spot_price, pnl=pnl, df=df, option_spreads=option_spreads,
                           strike_prices=strike_prices, labels=labels, title=title,
                           graph_type=graph_type, graph_profile=graph_profile)

    def double_diagonal(self, spot_price, expiration_date, long_put_price, long_put_strike_price,
                        long_put_risk_free_rate, long_put_dividend_yield, long_put_volatility, long_put_contracts,
                        short_put_price, short_put_strike_price, short_put_risk_free_rate, short_put_dividend_yield, 
                        short_put_volatility, short_put_contracts, short_call_price, short_call_strike_price, 
                        short_call_risk_free_rate, short_call_dividend_yield, short_call_volatility,
                        short_call_contracts, long_call_price, long_call_strike_price, long_call_risk_free_rate,
                        long_call_dividend_yield, long_call_volatility, long_call_contracts, graph_type, graph_profile):
        """ Displays calculated option values for the double diagonal strategy.
            This strategy combines a diagonal put spread and diagonal call spread.

        :param spot_price: (float) underlying stock price
        :param expiration_date: (str) expiration date
        :param long_put_price: (float) ask price for long put option
        :param long_put_strike_price: (float) strike price for long put option
        :param long_put_risk_free_rate: (float) risk-free interest rate for long put option
        :param long_put_dividend_yield: (float) dividend yield for long put option
        :param long_put_volatility: (float) implied volatility for long put option
        :param long_put_contracts: (int) # of contracts to buy/write for long put option
        :param short_put_price: (float) bid price for short put option
        :param short_put_strike_price: (float) strike price for short put option
        :param short_put_risk_free_rate: (float) risk-free interest rate for short put option
        :param short_put_dividend_yield: (float) dividend yield for short put option
        :param short_put_volatility: (float) implied volatility for short put option
        :param short_put_contracts: (int) # of contracts to buy/write for short put option
        :param short_call_price: (float) bid price for short call option
        :param short_call_strike_price: (float) strike price for short call option
        :param short_call_risk_free_rate: (float) risk-free interest rate for short call option
        :param short_call_dividend_yield: (float) dividend yield for short call option
        :param short_call_volatility: (float) implied volatility for short call option
        :param short_call_contracts: (int) # of contracts to buy/write for short call option
        :param long_call_price: (float) ask price for long call option
        :param long_call_strike_price: (float) strike price for long call option
        :param long_call_risk_free_rate: (float) risk-free interest rate for long call option
        :param long_call_dividend_yield: (float) implied volatility for long call option
        :param long_call_volatility: (float) implied volatility for long call option
        :param long_call_contracts: (int) # of contracts to buy/write for long call option
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param graph_profile: (str) graph profile such as 'pnl', 'risk' or 'option/spread'
        :return: annotated heatmap table and/or graph traces with calculated results
        """

        # Calculate option prices with BSM options
        strike_prices, labels, dates_until_maturity, maturity_prices_long_put, estimated_prices_long_put, \
        maturity_short_prices_put, estimated_short_prices_put, maturity_short_prices_call, estimated_short_prices_call, \
        maturity_prices_long_call, estimated_prices_long_call = self._get_option_prices(
            legs=4, S=spot_price, T=expiration_date, K_1=long_put_strike_price, r_1=long_put_risk_free_rate,
            q_1=long_put_dividend_yield, sigma_1=long_put_volatility, option_type_1='put', K_2=short_put_strike_price,
            r_2=short_put_risk_free_rate, q_2=short_put_dividend_yield, sigma_2=short_put_volatility,
            option_type_2='put', K_3=short_call_strike_price, r_3=short_call_risk_free_rate,
            q_3=short_call_dividend_yield, sigma_3=short_call_volatility, option_type_3='call',
            K_4=long_call_strike_price, r_4=long_call_risk_free_rate, q_4=long_call_dividend_yield,
            sigma_4=long_call_volatility, option_type_4='call')

        # Concatenate calculated prices and multiply by # contracts and 100
        # Long put
        long_put_prices = np.asarray(
            np.concatenate(
                (estimated_prices_long_put, maturity_prices_long_put.T.reshape(
                    1, maturity_prices_long_put.shape[0]))))
        long_put_values = long_put_prices * long_put_contracts * 100
        # Short put
        short_put_prices = (-1.0) * np.asarray(
            np.concatenate(
                (estimated_short_prices_put, maturity_short_prices_put.T.reshape(
                    1, maturity_short_prices_put.shape[0]))))
        short_put_values = short_put_prices * short_put_contracts * 100
        # Short call
        short_call_prices = (-1.0) * np.asarray(
            np.concatenate(
                (estimated_short_prices_call, maturity_short_prices_call.T.reshape(
                    1, maturity_short_prices_call.shape[0]))))
        short_call_values = short_call_prices * short_call_contracts * 100
        # Long call
        long_call_prices = np.asarray(
            np.concatenate(
                (estimated_prices_long_call, maturity_prices_long_call.T.reshape(
                    1, maturity_prices_long_call.shape[0]))))
        long_call_values = long_call_prices * long_call_contracts * 100

        # Calculate entry cost
        long_put_cost = long_put_price * long_put_contracts * 100
        short_put_cost = - short_put_price * short_put_contracts * 100
        short_call_cost = - short_call_price * short_call_contracts * 100
        long_call_cost = long_call_price * long_call_price * 100
        entry_cost = long_put_cost + short_put_cost + short_call_cost + long_call_cost

        # Calculate pnl by adding estimated values minus entry cost
        pnl = long_put_values + short_put_values + short_call_values + long_call_values - entry_cost

        # Create pnl dataframe
        df = pd.DataFrame(data=pnl.T, index=strike_prices, columns=labels)

        # Calculate purchased value per option /  100
        option_spreads = long_put_values/100 + short_put_values/100 + short_call_values/100 + long_call_values/100

        # Make title for visualization
        title = 'Double Diagonal'

        # Visualize results
        self._show_results(spot_price=spot_price, pnl=pnl, df=df, option_spreads=option_spreads,
                           strike_prices=strike_prices, labels=labels, title=title, graph_type=graph_type,
                           graph_profile=graph_profile)


    def strangle(self, spot_price, expiration_date, long_call_contracts, long_call_price,
               long_call_strike_price, long_call_risk_free_rate, long_call_dividend_yield, long_call_volatility,
               long_put_contracts, long_put_price, long_put_strike_price, long_put_risk_free_rate,
               long_put_dividend_yield, long_put_volatility, graph_type, graph_profile):
        """ Displays calculated option values for the strangle strategy:
                Long one OTM put
                Long one OTM call

        :param spot_price: (float) underlying stock price
        :param expiration_date: (str) expiration date
        :param long_call_contracts: (int) # of contracts to buy/write for long call option
        :param long_call_price: (float) ask price for long call option
        :param long_call_strike_price: (float) strike price for long call option
        :param long_call_risk_free_rate: (float) risk-free interest rate for long call option
        :param long_call_dividend_yield: (float) implied volatility for long call option
        :param long_call_volatility: (float) implied volatility for long call option
        :param long_put_contracts: (int) # of contracts to buy/write for long put option
        :param long_put_price: (float) ask price for long put option
        :param long_put_strike_price: (float) strike price for long put option
        :param long_put_risk_free_rate: (float) risk-free interest rate for long put option
        :param long_put_dividend_yield: (float) dividend yield for long put option
        :param long_put_volatility: (float) implied volatility for long put option
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param graph_profile: (str) graph profile such as 'pnl', 'risk' or 'option/spread'
        :return:
        """

        # Calculate option prices with BSM options
        strike_prices, labels, dates_until_maturity, maturity_prices_long_call, estimated_prices_long_call, \
        maturity_prices_long_put, estimated_prices_long_put = self._get_option_prices(
            legs=2, S=spot_price, T=expiration_date,
            K_1=long_call_strike_price, r_1=long_call_risk_free_rate, q_1=long_call_dividend_yield,
            sigma_1=long_call_volatility, option_type_1='call', K_2=long_put_strike_price, r_2=long_put_risk_free_rate,
            q_2=long_put_dividend_yield, sigma_2=long_put_volatility, option_type_2='put')

        # Concatenate calculated prices and multiply by # contracts and 100
        # Long call
        long_call_prices = np.asarray(
            np.concatenate(
                (estimated_prices_long_call, maturity_prices_long_call.T.reshape(
                    1, maturity_prices_long_call.shape[0]))))
        long_call_values = long_call_prices * long_call_contracts * 100
        # Long put
        long_put_prices = np.asarray(
            np.concatenate(
                (estimated_prices_long_put, maturity_prices_long_put.T.reshape(
                    1, maturity_prices_long_put.shape[0]))))
        long_put_values = long_put_prices * long_put_contracts * 100

        # Calculate entry cost
        long_call_cost = long_call_price * long_call_contracts * 100
        long_put_cost = long_put_price * long_put_contracts * 100
        entry_cost = long_call_cost + long_put_cost

        # Get pnl by adding estimated values minus entry cost
        pnl = long_call_values + long_put_values - entry_cost

        # Calculate pnl by adding estimated values minus entry cost
        df = pd.DataFrame(data=pnl.T, index=strike_prices, columns=labels)

        # Calculate purchased value per option without multiplying by 100
        option_spreads = long_call_values / 100 + long_put_values / 100

        # Make title for visualization
        title = 'Strangle: Long Call - Long Put'

        # Visualize results
        self._show_results(spot_price=spot_price, pnl=pnl, df=df, option_spreads=option_spreads,
                           strike_prices=strike_prices, labels=labels, title=title, graph_type=graph_type,
                           graph_profile=graph_profile)


    def synthetic_put(self, spot_price, expiration_date, num_shares, contracts, option_price,
                      strike_price, risk_free_rate, dividend_yield, volatility, graph_type, graph_profile):
        """ Displays calculated option values for the synthetic put strategy:
            Long a call option
            Short the equivalent amount of the underlying stock

        :param spot_price: (float) underlying stock price
        :param expiration_date: (str) expiration date
        :para num_shares: (int) # of shares of the underlying stock to hold
        :param contracts: (int) # of contracts to buy/write
        :param option_price: (float) bid/ask price per option
        :param strike_price: (float) strike price
        :param risk_free_rate: (float) risk-free interest rate
        :param dividend_yield: (float) dividend yield
        :param volatility: (float) implied volatility
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param graph_profile: (str) graph profile such as 'pnl', 'risk' or 'option/spread'
        :return: annotated heatmap table and/or graph traces with calculated results
        """

        # Calculate option prices with BSM options
        strike_prices, labels, dates_until_maturity, maturity_prices, estimated_prices = self._get_option_prices(
            legs=1, S=spot_price, T=expiration_date, K_1=strike_price, r_1=risk_free_rate, q_1=dividend_yield,
            sigma_1=volatility, option_type_1='call')

        # Create array with change in stock value as (K - S0) per strike and multiply by # shares
        stock_only_values = (strike_prices - spot_price) * num_shares  # len(stock_only_array) = len(strike_prices)

        # Concatenate calculated prices and multiply by # contracts and 100
        option_prices =  np.asarray(
            np.concatenate(
                (estimated_prices, maturity_prices.T.reshape(
                    1, maturity_prices.shape[0]))))
        option_value = option_prices * contracts * 100

        # Calculate Entry Costs
        entry_cost = option_price * contracts * sign * 100

        # Calculate pnl by adding estimated values minus entry cost
        pnl = option_value - stock_only_values - entry_cost

        # Create pnl dataframe
        df = pd.DataFrame(data=pnl.T, index=strike_prices, columns=labels)

        # Calculate purchased value per option / 100 minus stock only values / num_shares
        option_spreads = option_value / 100 - stock_only_values / num_shares

        # Title for plotting
        title = 'Synthetic put'

        # Visualize results
        self._show_results(spot_price=spot_price, pnl=pnl, df=df, option_spreads=option_spreads,
                           strike_prices=strike_prices, labels=labels, title=title,
                           graph_type=graph_type, graph_profile=graph_profile)


    def butterfly(self, spot_price, expiration_date, lower_contracts, lower_price, lower_option, lower_strike_price,
                  lower_risk_free_rate, lower_dividend_yield, lower_volatility, middle_contracts, middle_price,
                  middle_option, middle_strike_price, middle_risk_free_rate, middle_dividend_yield, middle_volatility,
                  upper_contracts, upper_price, upper_option, upper_strike_price, upper_risk_free_rate,
                  upper_dividend_yield, upper_volatility, graph_type, graph_profile):
        """ Displays calculated option values for the butterfly strategy:
                Long one ITM option
                Short two ATM options
                Long one OTM option

        :param spot_price: (float) underlying stock price
        :param expiration_date: (str) expiration date
        :param lower_contracts: (int) # of contracts to buy for lower wing option
        :param lower_price: (float) ask price for lower wing option
        :param lower_option: (str) 'put' or 'call' option type for lower wing option
        :param lower_strike_price: (float) strike price for lower wing option
        :param lower_risk_free_rate: (float) risk-free interest rate for lower wing option
        :param lower_dividend_yield: (float) dividend yield for lower wing option
        :param lower_volatility: (float) implied volatility for lower wing option
        :param middle_contracts: (int) # of contracts to write for middle wing option
        :param middle_price: (float) bid price for middle wing option
        :param middle_option: (str) 'put' or 'call' option type for middle wing option
        :param middle_strike_price: (float) strike price for middle wing option
        :param middle_risk_free_rate: (float) risk-free interest rate for middle wing option
        :param middle_dividend_yield: (float) dividend yield for middle wing option
        :param middle_volatility: (float) implied volatility for middle wing option
        :param upper_contracts: (int) # of contracts to buy for upper wing option
        :param upper_price: (float) ask price for upper wing option
        :param upper_option: (str) 'put' or 'call' option type for upper wing option
        :param upper_strike_price: (float) strike price for upper wing option
        :param upper_risk_free_rate: (float) risk-free interest rate for upper wing option
        :param upper_dividend_yield: (float) dividend yield for upper wing option
        :param upper_volatility: (float) implied volatility for upper wing option
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param graph_profile: (str) graph profile such as 'pnl', 'risk' or 'option/spread'
        :return: annotated heatmap table and/or graph traces with calculated results
        """

        # Calculate option prices with BSM options
        strike_prices, labels, dates_until_maturity, maturity_prices_lower, estimated_prices_lower, \
        maturity_prices_middle, estimated_prices_middle, maturity_prices_upper, \
        estimated_prices_upper = self._get_option_prices(
            legs=3, S=spot_price, T=expiration_date, K_1=lower_strike_price, r_1=lower_risk_free_rate,
            q_1=lower_dividend_yield, sigma_1=lower_volatility, option_type_1=lower_option, K_2=middle_strike_price,
            r_2=middle_risk_free_rate, q_2=middle_dividend_yield, sigma_2=middle_volatility,
            option_type_2=middle_option, K_3=upper_strike_price, r_3=upper_risk_free_rate, q_3=upper_dividend_yield,
            sigma_3=upper_volatility, option_type_3=upper_option)

        # Concatenate calculated prices and multiply by # contracts and 100
        # Lower wing
        lower_prices =  np.asarray(
            np.concatenate(
                (estimated_prices_lower, maturity_prices_lower.T.reshape(
                    1, maturity_prices_lower.shape[0]))))
        lower_values = lower_prices * lower_contracts * 100
        # Middle wing
        middle_prices = (-1.0) * np.asarray(
            np.concatenate(
                (estimated_prices_middle, maturity_prices_middle.T.reshape(
                    1, maturity_prices_middle.shape[0]))))
        middle_values = middle_prices * middle_contracts * 100 * 2
        # Upper wing
        upper_prices = np.asarray(
            np.concatenate(
                (estimated_prices_upper, maturity_prices_upper.T.reshape(
                    1, maturity_prices_upper.shape[0]))))
        upper_values = upper_prices * upper_contracts * 100

        # Calculate entry cost
        lower_cost = lower_price * lower_contracts * 100
        middle_cost = - middle_price * middle_contracts * 100 * 2
        upper_cost = upper_price * upper_contracts * 100
        entry_cost = lower_cost + middle_cost + upper_cost

        # Calculate pnl by adding estimated values minus entry cost
        pnl = lower_values + middle_values + middle_values - entry_cost

        # Create pnl dataframe
        df = pd.DataFrame(data=pnl.T, index=strike_prices, columns=labels)

        # Calculate purchased value per option / 100
        option_spreads = lower_values / 100 + middle_values / 100 + upper_values / 100 

        # Make title for visualization
        title = 'Butterfly: Long ' + str(lower_option) + ' - ' + 'Short ' + str(middle_option) + ' - ' + \
                'Long ' + str(upper_option)

        # Visualize results
        self._show_results(spot_price=spot_price, pnl=pnl, df=df, option_spreads=option_spreads,
                           strike_prices=strike_prices, labels=labels, title=title,
                           graph_type=graph_type, graph_profile=graph_profile)


    def diagonal_spread(self, spot_price, expiration_date, long_contracts, long_price, long_type, long_strike_price,
                        long_risk_free_rate, long_dividend_yield, long_volatility, short_contracts, short_price,
                        short_type, short_strike_price, short_risk_free_rate, short_dividend_yield, short_volatility,
                        graph_type, graph_profile):
        """ Displays calculated option values for the diagonal spread strategy:
        Long and short position on two options, usually at different strikes price

        :param spot_price: (float) underlying stock price
        :param expiration_date: (str) expiration date
        :param long_contracts: (int) # of contracts to buy/write for long option
        :param long_price: (float) ask price for long option
        :param long_type: (str) 'put' or 'call' option type for long option
        :param long_strike_price: (float) strike price for long option
        :param long_risk_free_rate: (float) risk-free interest rate for long option
        :param long_dividend_yield: (float) dividend yield for long option
        :param long_volatility: (float) implied volatility for long option
        :param ratio: (int) ratio for long option, it should be twice as # contracts for short option
        :param short_contracts: (int) # of contracts to buy/write for short option
        :param short_price: (float) ask price for short option
        :param short_type: (str) 'put' or 'call' option type for short option
        :param short_strike_price: (float) strike price for short option
        :param short_risk_free_rate: (float) risk-free interest rate for short option
        :param short_dividend_yield: (float) dividend yield for short option
        :param short_volatility: (float) implied volatility for short option
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param graph_profile: (str) graph profile such as 'pnl', 'risk' or 'option/spread'
        :return: annotated heatmap table and/or graph traces with calculated results
        """

        # Calculate option prices with BSM options
        strike_prices, labels, dates_until_maturity, maturity_prices_long, estimated_prices_long, \
        maturity_short_prices, estimated_short_prices = self._get_option_prices(
            legs=2, S=spot_price, T=expiration_date,
            K_1=long_strike_price, r_1=long_risk_free_rate, q_1=long_dividend_yield, sigma_1=long_volatility,
            option_type_1=long_type,
            K_2=short_strike_price, r_2=short_risk_free_rate, q_2=short_dividend_yield, sigma_2=short_volatility,
            option_type_2=short_type)

        # Concatenate calculated prices and multiply by # contracts and 100
        # Long option
        long_prices = np.asarray(
            np.concatenate(
                (estimated_prices_long, maturity_prices_long.T.reshape(
                    1, maturity_prices_long.shape[0]))))
        long_values = long_prices * long_contracts * 100
        # Short option
        short_prices = (-1.0) * np.asarray(
            np.concatenate(
                (estimated_short_prices, maturity_short_prices.T.reshape(
                    1, maturity_short_prices.shape[0]))))
        short_values = short_prices * short_contracts * 100

        # Calculate entry cost
        long_cost = long_price * long_contracts * 100
        short_cost = - short_price * short_contracts * 100
        entry_cost = long_cost + short_cost

        # Get pnl by adding estimated values minus entry cost
        pnl = long_values + short_values - entry_cost

        # Sum all pnl minus the total cost
        df = pd.DataFrame(data=pnl.T, index=strike_prices, columns=labels)

        # Calculate purchased value per option without multiplying by 100
        option_spreads = long_values / 100 + short_values / 100

        # Make title for visualization
        title = 'Diagonal Spread: ' + 'Long ' + str(long_type) + ' - ' + 'Short ' + str(short_type)

        # Visualize results
        self._show_results(spot_price=spot_price, pnl=pnl, df=df, option_spreads=option_spreads,
                           strike_prices=strike_prices, labels=labels, title=title, graph_type=graph_type,
                           graph_profile=graph_profile)


    def straddle(self, spot_price, expiration_date, strike_price, long_call_contracts, long_call_price,
                 long_call_risk_free_rate, long_call_dividend_yield, long_call_volatility, long_put_contracts,
                 long_put_price, long_put_risk_free_rate, long_put_dividend_yield, long_put_volatility,
                 graph_type, graph_profile):
        """ Displays calculated option values for the straddle strategy:
            * Long one ATM put
            * Long one ATM call
        Both have the same strike price

        :param spot_price: (float) underlying stock price
        :param expiration_date: (str) expiration date
        :param strike_price: (float) strike price for long call and long put option
        :param long_call_contracts: (int) # of contracts to buy/write for long call option
        :param long_call_price: (float) ask price for long call option
        :param long_call_risk_free_rate: (float) risk-free interest rate for long call option
        :param long_call_dividend_yield: (float) implied volatility for long call option
        :param long_call_volatility: (float) implied volatility for long call option
        :param long_put_contracts: (int) # of contracts to buy/write for long put option
        :param long_put_price: (float) ask price for long put option
        :param long_put_risk_free_rate: (float) risk-free interest rate for long put option
        :param long_put_dividend_yield: (float) dividend yield for long put option
        :param long_put_volatility: (float) implied volatility for long put option
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param graph_profile: (str) graph profile such as 'pnl', 'risk' or 'option/spread'
        :return: annotated heatmap table and/or graph traces with calculated results
        """

        # Calculate option prices with BSM options
        strike_prices, labels, dates_until_maturity, maturity_prices_long_call, estimated_prices_long_call, \
        maturity_prices_long_put, estimated_prices_long_put = self._get_option_prices(
            legs=2, S=spot_price, T=expiration_date,
            K_1=strike_price, r_1=long_call_risk_free_rate, q_1=long_call_dividend_yield,
            sigma_1=long_call_volatility, option_type_1='call', K_2=strike_price, r_2=long_put_risk_free_rate,
            q_2=long_put_dividend_yield, sigma_2=long_put_volatility, option_type_2='put')

        # Concatenate calculated prices and multiply by # contracts and 100
        # Long option
        long_call_prices = np.asarray(
            np.concatenate(
                (estimated_prices_long_call, maturity_prices_long_call.T.reshape(
                    1, maturity_prices_long_call.shape[0]))))
        long_call_values = long_call_prices * long_call_contracts * 100
        # Short option
        long_put_prices = np.asarray(
            np.concatenate(
                (estimated_prices_long_put, maturity_prices_long_put.T.reshape(
                    1, maturity_prices_long_put.shape[0]))))
        long_put_values = long_put_prices * long_put_contracts * 100

        # Calculate entry cost
        long_call_cost = long_call_price * long_call_contracts * 100
        long_put_cost = long_put_price * long_put_contracts * 100
        entry_cost = long_call_cost + long_put_cost

        # Get pnl by adding estimated values minus entry cost
        pnl = long_call_values + long_put_values - entry_cost

        # Calculate pnl by adding estimated values minus entry cost
        df = pd.DataFrame(data=pnl.T, index=strike_prices, columns=labels)

        # Calculate purchased value per option without multiplying by 100
        option_spreads = long_call_values / 100 + long_put_values / 100

        # Make title for visualization
        title = 'Straddle: Long Call - Long Put'

        # Visualize results
        self._show_results(spot_price=spot_price, pnl=pnl, df=df, option_spreads=option_spreads,
                           strike_prices=strike_prices, labels=labels, title=title,
                           graph_type=graph_type, graph_profile=graph_profile)


    def covered_strangle(self, spot_price, expiration_date, num_shares, short_call_contracts, short_call_price,
                         short_call_strike_price, short_call_risk_free_rate, short_call_dividend_yield, short_call_volatility,
                         short_put_contracts, short_put_price, short_put_strike_price, short_put_risk_free_rate,
                         short_put_dividend_yield, short_put_volatility, graph_type, graph_profile):
        """ Displays calculated option values for the strangle strategy:
                Short one OTM put
                Short one OTM call

        :param spot_price: (float) underlying stock price
        :param expiration_date: (str) expiration date
        :param num_shares: (int) # of shares of the underlying stock to hold
        :param short_call_contracts: (int) # of contracts to buy/write for short call option
        :param short_call_price: (float) bid price for short call option
        :param short_call_strike_price: (float) strike price for short call option
        :param short_call_risk_free_rate: (float) risk-free interest rate for short call option
        :param short_call_dividend_yield: (float) dividend yield for short call option
        :param short_call_volatility: (float) implied volatility for short call option
        :param short_put_contracts: (int) # of contracts to buy/write for short put option
        :param short_put_price: (float) bid price for short put option
        :param short_put_strike_price: (float) strike price for short put option
        :param short_put_risk_free_rate: (float) risk-free interest rate for short put option
        :param short_put_dividend_yield: (float) dividend yield for short put option
        :param short_put_volatility: (float) implied volatility for short put option
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param graph_profile: (str) graph profile such as 'pnl', 'risk' or 'option/spread'
        :return: annotated heatmap table and/or graph traces with calculated results
        """

        # Calculate option prices with BSM options
        strike_prices, labels, dates_until_maturity, maturity_prices_short_call, estimated_prices_short_call, \
        maturity_prices_short_put, estimated_prices_short_put = self._get_option_prices(
            legs=2, S=spot_price, T=expiration_date,
            K_1=short_call_strike_price, r_1=short_call_risk_free_rate, q_1=short_call_dividend_yield,
            sigma_1=short_call_volatility, option_type_1='call', K_2=short_put_strike_price, r_2=short_put_risk_free_rate,
            q_2=short_put_dividend_yield, sigma_2=short_put_volatility, option_type_2='put')

        # Concatenate calculated prices and multiply by # contracts and 100
        # Short call
        short_call_prices = (-1.0) * np.asarray(
            np.concatenate(
                (estimated_prices_short_call, maturity_prices_short_call.T.reshape(
                    1, maturity_prices_short_call.shape[0]))))
        short_call_values = short_call_prices * short_call_contracts * 100
        # Short put
        short_put_prices = (-1.0) * np.asarray(
            np.concatenate(
                (estimated_prices_short_put, maturity_prices_short_put.T.reshape(
                    1, maturity_prices_short_put.shape[0]))))
        short_put_values = short_put_prices * short_put_contracts * 100

        # Create array with change in stock value as (K - S0) per strike and multiply by # shares
        stock_only_values = (strike_prices - spot_price) * num_shares  # len(stock_only_array) = len(strike_prices)

        # Calculate entry cost
        short_call_cost = short_call_price * short_call_contracts * 100
        short_put_cost = short_put_price * short_put_contracts * 100
        entry_cost = short_call_cost + short_put_cost

        # Calculate pnl by adding estimated values minus entry cost
        pnl = short_call_values + short_put_values + stock_only_values - entry_cost

        # Make pnl dataframe
        df = pd.DataFrame(data=pnl.T, index=strike_prices, columns=labels)

        # Calculate purchased value per option / 100 minus stock only values / num_shares
        option_spreads = short_call_values / 100 + short_put_values / 100 - stock_only_values / num_shares

        # Make title for visualization
        title = 'Covered Strangle: Short Call - Short Put'

        # Visualize results
        self._show_results(spot_price=spot_price, pnl=pnl, df=df, option_spreads=option_spreads,
                           strike_prices=strike_prices, labels=labels, title=title, graph_type=graph_type,
                           graph_profile=graph_profile)


    def reverse_conversion(self, spot_price, expiration_date, num_shares, long_type, long_price, long_strike_price,
                           long_risk_free_rate, long_dividend_yield, long_volatility, long_contracts, short_type,
                           short_price, short_strike_price, short_risk_free_rate, short_dividend_yield,
                           short_volatility, short_contracts, graph_type, graph_profile):
        """ Displays calculated option values for the reverse conversion strategy:
                Sell a put
                Buy a call to create a synthetic long position
                Short the underlying stock

        :param spot_price: (float) underlying stock price
        :param expiration_date: (str) expiration date
        :param num_shares: (int) # of shares of the underlying stock to hold
        :param long_type: (str) 'put' or 'call' option type for long option
        :param long_price: (float) ask price for long option
        :param long_strike_price: (float) strike price for long option
        :param long_risk_free_rate: (float) risk-free interest rate for long option
        :param long_dividend_yield: (float) dividend yield for long option
        :param long_volatility: (float) implied volatility for long option
        :param long_contracts: (int) # of contracts to buy/write for long option
        :param short_type: (str) 'put' or 'call' option type for short option
        :param short_price: (float) ask price for short option
        :param short_strike_price: (float) strike price for short option
        :param short_risk_free_rate: (float) risk-free interest rate for short option
        :param short_dividend_yield: (float) dividend yield for short option
        :param short_volatility: (float) implied volatility for short option
        :param short_contracts: (int) # of contracts to buy/write for short option
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param graph_profile: (str) graph profile such as 'pnl', 'risk' or 'option/spread'
        :return: annotated heatmap table and/or graph traces with calculated results
        """

        # Calculate option prices with BSM options
        strike_prices, labels, dates_until_maturity, maturity_prices_long, estimated_prices_long, \
        maturity_prices_short, estimated_prices_short = self._get_option_prices(
            legs=2, S=spot_price, T=expiration_date, K_1=long_strike_price, r_1=long_risk_free_rate, q_1=long_dividend_yield,
            sigma_1=long_volatility, option_type_1=long_type, K_2=short_strike_price, r_2=short_risk_free_rate,
            q_2=short_dividend_yield, sigma_2=short_volatility, option_type_2=short_type)

        # Concatenate calculated prices and multiply by # contracts and 100
        # Long option
        long_prices = np.asarray(
            np.concatenate(
                (estimated_prices_long, maturity_prices_long.T.reshape(
                    1, maturity_prices_long.shape[0]))))
        long_values = long_prices * long_contracts * 100
        # Short option
        short_prices = np.asarray(
            np.concatenate(
                (estimated_prices_short, maturity_prices_short.T.reshape(
                    1, maturity_prices_short.shape[0]))))
        short_values = short_prices * short_contracts * 100

        # Create array with change in stock value as (K - S0) per strike and multiply by # shares
        stock_only_values = (strike_prices - spot_price) * num_shares  # len(stock_only_array) = len(strike_prices)

        # Calculate entry cost
        long_cost = long_price * long_contracts * 100
        short_cost = short_price * short_contracts * 100
        entry_cost = long_cost - short_cost

        # Calculate pnl by adding estimated values minus entry cost
        pnl = long_values + short_values - entry_cost - stock_only_values

        # Make pnl dataframe
        df = pd.DataFrame(data=pnl.T, index=strike_prices, columns=labels)

        # Calculate purchased value per option / 100 minus stock only values / num_shares
        option_spreads = long_values / 100 + short_values / 100 - stock_only_values / num_shares

        # Make title for visualization
        title = 'Reverse Conversion: Long ' + str(long_type) + ' -  Short ' + str(short_type)

        # Visualize results
        self._show_results(spot_price=spot_price, pnl=pnl, df=df, option_spreads=option_spreads,
                           strike_prices=strike_prices, labels=labels, title=title, graph_type=graph_type,
                           graph_profile=graph_profile)


    ################################################ CUSTOM STRATEGIES ####################################################

    def eight_legs(self, spot_price, expiration_date,
                action_leg_1, contracts_leg_1, price_leg_1, option_leg_1, strike_leg_1, risk_leg_1, dividend_yield_leg_1,
                volatility_leg_1,

                action_leg_2, contracts_leg_2, price_leg_2, option_leg_2, strike_leg_2, risk_leg_2, dividend_yield_leg_2,
                volatility_leg_2,

                action_leg_3, contracts_leg_3, price_leg_3, option_leg_3, strike_leg_3, risk_leg_3, dividend_yield_leg_3,
                volatility_leg_3,

                action_leg_4, contracts_leg_4, price_leg_4, option_leg_4, strike_leg_4, risk_leg_4, dividend_yield_leg_4,
                volatility_leg_4,

                action_leg_5, contracts_leg_5, price_leg_5, option_leg_5, strike_leg_5, risk_leg_5, dividend_yield_leg_5,
                volatility_leg_5,

                action_leg_6, contracts_leg_6, price_leg_6, option_leg_6, strike_leg_6, risk_leg_6, dividend_yield_leg_6,
                volatility_leg_6,

                action_leg_7, contracts_leg_7, price_leg_7, option_leg_7, strike_leg_7, risk_leg_7, dividend_yield_leg_7,
                volatility_leg_7,

                action_leg_8, contracts_leg_8, price_leg_8, option_leg_8, strike_leg_8, risk_leg_8, dividend_yield_leg_8,
                volatility_leg_8,

                graph_type, graph_profile):
        """ Displays calculated option values for the 8 legs strategy.

        :param spot_price: (float) underlying stock price
        :param expiration_date: (str) expiration date
        :param action_leg_1: (str) whether the action is a buy or write for leg 1
        :param contracts_leg_1: (int) # of contracts to buy/write for leg 1 
        :param price_leg_1: (float) ask price for leg 1
        :param option_leg_1: (str) 'put' or 'call' option type for leg 1
        :param strike_leg_1: (float) strike price for leg 1
        :param risk_leg_1: (float) risk-free interest rate for leg 1
        :param dividend_yield_leg_1: float) dividend yield for leg 1
        :param volatility_leg_1: (float) implied volatility for leg 1
        :param action_leg_2: (str) whether the action is a buy or write for leg 2
        :param contracts_leg_2: (int) # of contracts to buy/write for leg 2
        :param price_leg_2: (float) ask price for leg 2
        :param option_leg_2: (str) 'put' or 'call' option type for leg 2
        :param strike_leg_2: (float) strike price for leg 2
        :param risk_leg_2: (float) risk-free interest rate for leg 2
        :param dividend_yield_leg_2: float) dividend yield for leg 2
        :param volatility_leg_2: (float) implied volatility for leg 2
        :param action_leg_1: (str) whether the action is a buy or write for leg 3
        :param contracts_leg_1: (int) # of contracts to buy/write for leg 3
        :param price_leg_3: (float) ask price for leg 3
        :param option_leg_3: (str) 'put' or 'call' option type for leg 3
        :param strike_leg_3: (float) strike price for leg 3
        :param risk_leg_3: (float) risk-free interest rate for leg 3
        :param dividend_yield_leg_3: float) dividend yield for leg 3
        :param volatility_leg_3: (float) implied volatility for leg 3
        :param action_leg_4: (str) whether the action is a buy or write for leg 4
        :param contracts_leg_4: (int) # of contracts to buy/write for leg 4
        :param price_leg_4: (float) ask price for leg 4
        :param option_leg_4: (str) 'put' or 'call' option type for leg 4
        :param strike_leg_4: (float) strike price for leg 4
        :param risk_leg_4: (float) risk-free interest rate for leg 4
        :param dividend_yield_leg_4: float) dividend yield for leg 4
        :param volatility_leg_4: (float) implied volatility for leg 4
        :param action_leg_5: (str) whether the action is a buy or write for leg 5
        :param contracts_leg_5: (int) # of contracts to buy/write for leg 5
        :param price_leg_5: (float) ask price for leg 5
        :param option_leg_5: (str) 'put' or 'call' option type for leg 5
        :param strike_leg_5: (float) strike price for leg 5
        :param risk_leg_5: (float) risk-free interest rate for leg 5
        :param dividend_yield_leg_5: float) dividend yield for leg 5
        :param volatility_leg_5: (float) implied volatility for leg 5
        :param action_leg_6: (str) whether the action is a buy or write for leg 6
        :param contracts_leg_6: (int) # of contracts to buy/write for leg 6
        :param price_leg_6: (float) ask price for leg 6
        :param option_leg_6: (str) 'put' or 'call' option type for leg 6
        :param strike_leg_6: (float) strike price for leg 6
        :param risk_leg_6: (float) risk-free interest rate for leg 6
        :param dividend_yield_leg_6: float) dividend yield for leg 6
        :param volatility_leg_6: (float) implied volatility for leg 6
        :param action_leg_7: (str) whether the action is a buy or write for leg 7
        :param contracts_leg_7: (int) # of contracts to buy/write for leg 7
        :param price_leg_7: (float) ask price for leg 7
        :param option_leg_7: (str) 'put' or 'call' option type for leg 7
        :param strike_leg_7: (float) strike price for leg 7
        :param risk_leg_7: (float) risk-free interest rate for leg 7
        :param dividend_yield_leg_7: float) dividend yield for leg 7
        :param volatility_leg_7: (float) implied volatility for leg 7
        :param action_leg_8: (str) whether the action is a buy or write for leg 8
        :param contracts_leg_8: (int) # of contracts to buy/write for leg 8
        :param price_leg_8: (float) ask price for leg 8
        :param option_leg_8: (str) 'put' or 'call' option type for leg 8
        :param strike_leg_8: (float) strike price for leg 8
        :param risk_leg_8: (float) risk-free interest rate for leg 8
        :param dividend_yield_leg_8: float) dividend yield for leg 8
        :param volatility_leg_8: (float) implied volatility for leg 8
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param graph_profile: (str) graph profile such as 'pnl', 'risk' or 'option/spread'
        :return: annotated heatmap table and/or graph traces with calculated results
        """

        # Define auxiliary global variables
        global sign_leg_1, sign_leg_2, sign_leg_3, sign_leg_4, sign_leg_5, sign_leg_6, sign_leg_7, sign_leg_8, sub_leg_1, \
            sub_leg_2, sub_leg_3, sub_leg_4, sub_leg_5, sub_leg_6, sub_leg_7, sub_leg_8

        # Calculate option prices with BSM options
        strike_prices, labels, dates_until_maturity, maturity_prices_leg_1, estimated_prices_leg_1, maturity_prices_leg_2, \
        estimated_prices_leg_2, maturity_prices_leg_3, estimated_prices_leg_3, maturity_prices_leg_4, estimated_prices_leg_4, \
        maturity_prices_leg_5, estimated_prices_leg_5, maturity_prices_leg_6, estimated_prices_leg_6, maturity_prices_leg_7, \
        estimated_prices_leg_7, maturity_prices_leg_8, estimated_prices_leg_8 = self._get_option_prices(
            legs=8, S=spot_price, T=expiration_date,
            K_1=strike_leg_1, r_1=risk_leg_1, q_1=dividend_yield_leg_1, sigma_1=volatility_leg_1, option_type_1=option_leg_1,
            K_2=strike_leg_2, r_2=risk_leg_2, q_2=dividend_yield_leg_2, sigma_2=volatility_leg_2, option_type_2=option_leg_2,
            K_3=strike_leg_3, r_3=risk_leg_3, q_3=dividend_yield_leg_3, sigma_3=volatility_leg_3, option_type_3=option_leg_3,
            K_4=strike_leg_4, r_4=risk_leg_4, q_4=dividend_yield_leg_4, sigma_4=volatility_leg_4, option_type_4=option_leg_4,
            K_5=strike_leg_5, r_5=risk_leg_5, q_5=dividend_yield_leg_5, sigma_5=volatility_leg_5, option_type_5=option_leg_5,
            K_6=strike_leg_6, r_6=risk_leg_6, q_6=dividend_yield_leg_6, sigma_6=volatility_leg_6, option_type_6=option_leg_6,
            K_7=strike_leg_7, r_7=risk_leg_7, q_7=dividend_yield_leg_7, sigma_7=volatility_leg_7, option_type_7=option_leg_7,
            K_8=strike_leg_8, r_8=risk_leg_8, q_8=dividend_yield_leg_8, sigma_8=volatility_leg_8, option_type_8=option_leg_8)

        # Set title and direction sign as -1 if write and +1 if buy
        # Leg 1
        try:
            if action_leg_1 == 'buy':
                sign_leg_1 = 1
                sub_leg_1 = 'Long ' + str(option_leg_1)
            elif action_leg_1 == 'write':
                sign_leg_1 = -1
                sub_leg_1 = 'Short ' + str(option_leg_1)

        except AttributeError:
            print('Please try again.')

        # Leg 2
        try:
            if action_leg_2 == 'buy':
                sign_leg_2 = 1
                sub_leg_2 = 'Long ' + str(option_leg_2)
            elif action_leg_2 == 'write':
                sign_leg_2 = -1
                sub_leg_2 = 'Short ' + str(option_leg_2)
        except AttributeError:
            print('Please try again.')

        # Leg 3
        try:
            if action_leg_3 == 'buy':
                sign_leg_3 = 1
                sub_leg_3 = 'Long ' + str(option_leg_3)
            elif action_leg_3 == 'write':
                sign_leg_3 = -1
                sub_leg_3 = 'Short ' + str(option_leg_3)
        except AttributeError:
            print('Please try again.')

        # Leg 4
        try:
            if action_leg_4 == 'buy':
                sign_leg_4 = 1
                sub_leg_4 = 'Long ' + str(option_leg_4)
            elif action_leg_4 == 'write':
                sub_leg_4 = 'Short ' + str(option_leg_4)
                sign_leg_4 = -1
        except AttributeError:
            print('Please try again.')

        # Leg 5
        try:
            if action_leg_5 == 'buy':
                sign_leg_5 = 1
                sub_leg_5 = 'Long ' + str(option_leg_5)
            elif action_leg_5 == 'write':
                sign_leg_5 = -1
                sub_leg_5 = 'Short ' + str(option_leg_5)
        except AttributeError:
            print('Please try again.')

        # Leg 6
        try:
            if action_leg_6 == 'buy':
                sign_leg_6 = 1
                sub_leg_6 = 'Long ' + str(option_leg_6)
            elif action_leg_6 == 'write':
                sign_leg_6 = -1
                sub_leg_6 = 'Short ' + str(option_leg_6)
        except AttributeError:
            print('Please try again.')

        # Leg 7
        try:
            if action_leg_7 == 'buy':
                sign_leg_7 = 1
                sub_leg_7 = 'Long ' + str(option_leg_7)
            elif action_leg_7 == 'write':
                sign_leg_7 = -1
                sub_leg_7 = 'Short ' + str(option_leg_7)
        except AttributeError:
            print('Please try again.')

        # Leg 8
        try:
            if action_leg_8 == 'buy':
                sign_leg_8 = 1
                sub_leg_8 = 'Long ' + str(option_leg_8)
            elif action_leg_8 == 'write':
                sign_leg_8 = -1
                sub_leg_8 = 'Short ' + str(option_leg_8)
        except AttributeError:
            print('Please try again.')


        # Concatenate pnl arrays and multiply by # contracts and 100
        # Leg 1
        prices_leg_1 = sign_leg_1 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_1, maturity_prices_leg_1.T.reshape(
                    1, maturity_prices_leg_1.shape[0]))))
        values_leg_1 = prices_leg_1 * contracts_leg_1 * 100

        # Leg 2
        prices_leg_2 = sign_leg_2 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_2, maturity_prices_leg_2.T.reshape(
                    1, maturity_prices_leg_2.shape[0]))))
        values_leg_2 = prices_leg_2 * contracts_leg_2 * 100

        # Leg 3
        prices_leg_3 = sign_leg_3 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_3, maturity_prices_leg_3.T.reshape(
                    1, maturity_prices_leg_3.shape[0]))))
        values_leg_3 = prices_leg_3 * contracts_leg_3 * 100

        # Leg 4
        prices_leg_4 = sign_leg_4 * np.asarray(np.concatenate(
            (estimated_prices_leg_4, maturity_prices_leg_4.T.reshape(
                1, maturity_prices_leg_4.shape[0]))))
        values_leg_4 = prices_leg_4 * contracts_leg_4 * 100

        # Leg 5
        prices_leg_5 = sign_leg_5 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_5, maturity_prices_leg_5.T.reshape(
                    1, maturity_prices_leg_5.shape[0]))))
        values_leg_5 = prices_leg_5 * contracts_leg_5 * 100

        # Leg 6
        prices_leg_6 = sign_leg_6 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_6, maturity_prices_leg_6.T.reshape(
                    1, maturity_prices_leg_6.shape[0]))))
        values_leg_6 = prices_leg_6 * contracts_leg_6 * 100

        # Leg 7
        prices_leg_7 = sign_leg_7 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_7, maturity_prices_leg_7.T.reshape(
                    1, maturity_prices_leg_7.shape[0]))))
        values_leg_7 = prices_leg_7 * contracts_leg_7 * 100

        # Leg 8
        prices_leg_8 = sign_leg_8 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_8, maturity_prices_leg_8.T.reshape(
                    1, maturity_prices_leg_8.shape[0]))))
        values_leg_8 = prices_leg_8 * contracts_leg_8 * 100

        # Calculate Costs
        cost_leg_1 = price_leg_1 * contracts_leg_1 * sign_leg_1 * 100
        cost_leg_2 = price_leg_2 * contracts_leg_2 * sign_leg_2 * 100
        cost_leg_3 = price_leg_3 * contracts_leg_3 * sign_leg_3 * 100
        cost_leg_4 = price_leg_4 * contracts_leg_4 * sign_leg_4 * 100
        cost_leg_5 = price_leg_5 * contracts_leg_5 * sign_leg_5 * 100
        cost_leg_6 = price_leg_6 * contracts_leg_6 * sign_leg_6 * 100
        cost_leg_7 = price_leg_7 * contracts_leg_7 * sign_leg_7 * 100
        cost_leg_8 = price_leg_8 * contracts_leg_8 * sign_leg_8 * 100
        entry_cost = cost_leg_1 + cost_leg_2 + cost_leg_3 + cost_leg_4 + cost_leg_5 + cost_leg_6 + cost_leg_7 + cost_leg_8

        # Sum all PnL minus the total cost
        pnl = values_leg_1 + values_leg_2 + values_leg_3 + values_leg_4 + values_leg_5 + values_leg_6 + \
                    values_leg_7 + values_leg_8 - entry_cost

        # Create pnl dataframe
        df = pd.DataFrame(data=pnl.T, index=strike_prices, columns=labels)

        # Calculate purchased value per leg / 100
        option_spreads = values_leg_1/100 + values_leg_2/100 + values_leg_3/100 + values_leg_4/100 + values_leg_5/100 + \
                         values_leg_6/100 + values_leg_7/100 + values_leg_8/100

        # Make title for visualization
        title = '8 legs: ' + sub_leg_1 + ' - ' + sub_leg_2 + ' - ' + sub_leg_3 + ' - ' + sub_leg_4 + ' - ' + sub_leg_5 + \
            ' - ' + sub_leg_6 + ' - ' + sub_leg_7 + ' - ' + sub_leg_8

        # Visualize results
        self._show_results(spot_price=spot_price, pnl=pnl, df=df, option_spreads=option_spreads,
                           strike_prices=strike_prices, labels=labels, title=title, graph_type=graph_type,
                           graph_profile=graph_profile)

    def six_legs(self, spot_price, expiration_date,
                action_leg_1, contracts_leg_1, price_leg_1, option_leg_1, strike_leg_1, risk_leg_1, dividend_yield_leg_1,
                volatility_leg_1,

                action_leg_2, contracts_leg_2, price_leg_2, option_leg_2, strike_leg_2, risk_leg_2, dividend_yield_leg_2,
                volatility_leg_2,

                action_leg_3, contracts_leg_3, price_leg_3, option_leg_3, strike_leg_3, risk_leg_3, dividend_yield_leg_3,
                volatility_leg_3,

                action_leg_4, contracts_leg_4, price_leg_4, option_leg_4, strike_leg_4, risk_leg_4, dividend_yield_leg_4,
                volatility_leg_4,

                action_leg_5, contracts_leg_5, price_leg_5, option_leg_5, strike_leg_5, risk_leg_5, dividend_yield_leg_5,
                volatility_leg_5,

                action_leg_6, contracts_leg_6, price_leg_6, option_leg_6, strike_leg_6, risk_leg_6, dividend_yield_leg_6,
                volatility_leg_6,

                graph_type, graph_profile):
        """ Displays calculated option values for the 6 legs strategy.

        :param spot_price: (float) underlying stock price
        :param expiration_date: (str) expiration date
        :param action_leg_1: (str) whether the action is a buy or write for leg 1
        :param contracts_leg_1: (int) # of contracts to buy/write for leg 1 
        :param price_leg_1: (float) ask price for leg 1
        :param option_leg_1: (str) 'put' or 'call' option type for leg 1
        :param strike_leg_1: (float) strike price for leg 1
        :param risk_leg_1: (float) risk-free interest rate for leg 1
        :param dividend_yield_leg_1: float) dividend yield for leg 1
        :param volatility_leg_1: (float) implied volatility for leg 1
        :param action_leg_2: (str) whether the action is a buy or write for leg 2
        :param contracts_leg_2: (int) # of contracts to buy/write for leg 2
        :param price_leg_2: (float) ask price for leg 2
        :param option_leg_2: (str) 'put' or 'call' option type for leg 2
        :param strike_leg_2: (float) strike price for leg 2
        :param risk_leg_2: (float) risk-free interest rate for leg 2
        :param dividend_yield_leg_2: float) dividend yield for leg 2
        :param volatility_leg_2: (float) implied volatility for leg 2
        :param action_leg_3: (str) whether the action is a buy or write for leg 3
        :param contracts_leg_3: (int) # of contracts to buy/write for leg 3
        :param price_leg_3: (float) ask price for leg 3
        :param option_leg_3: (str) 'put' or 'call' option type for leg 3
        :param strike_leg_3: (float) strike price for leg 3
        :param risk_leg_3: (float) risk-free interest rate for leg 3
        :param dividend_yield_leg_3: float) dividend yield for leg 3
        :param volatility_leg_3: (float) implied volatility for leg 3
        :param action_leg_4: (str) whether the action is a buy or write for leg 4
        :param contracts_leg_4: (int) # of contracts to buy/write for leg 4
        :param price_leg_4: (float) ask price for leg 4
        :param option_leg_4: (str) 'put' or 'call' option type for leg 4
        :param strike_leg_4: (float) strike price for leg 4
        :param risk_leg_4: (float) risk-free interest rate for leg 4
        :param dividend_yield_leg_4: float) dividend yield for leg 4
        :param volatility_leg_4: (float) implied volatility for leg 4
        :param action_leg_5: (str) whether the action is a buy or write for leg 5
        :param contracts_leg_5: (int) # of contracts to buy/write for leg 5
        :param price_leg_5: (float) ask price for leg 5
        :param option_leg_5: (str) 'put' or 'call' option type for leg 5
        :param strike_leg_5: (float) strike price for leg 5
        :param risk_leg_5: (float) risk-free interest rate for leg 5
        :param dividend_yield_leg_5: float) dividend yield for leg 5
        :param volatility_leg_5: (float) implied volatility for leg 5
        :param action_leg_6: (str) whether the action is a buy or write for leg 6
        :param contracts_leg_6: (int) # of contracts to buy/write for leg 6
        :param price_leg_6: (float) ask price for leg 6
        :param option_leg_6: (str) 'put' or 'call' option type for leg 6
        :param strike_leg_6: (float) strike price for leg 6
        :param risk_leg_6: (float) risk-free interest rate for leg 6
        :param dividend_yield_leg_6: float) dividend yield for leg 6
        :param volatility_leg_6: (float) implied volatility for leg 6
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param graph_profile: (str) graph profile such as 'pnl', 'risk' or 'option/spread'
        :return: annotated heatmap table and/or graph traces with calculated results
        """
        # Define auxiliary global variables
        global sign_leg_1, sign_leg_2, sign_leg_3, sign_leg_4, sign_leg_5, sign_leg_6, sub_leg_1, sub_leg_2, sub_leg_3, \
            sub_leg_4, sub_leg_5, sub_leg_6

        # Calculate option prices with BSM options
        strike_prices, labels, dates_until_maturity, maturity_prices_leg_1, estimated_prices_leg_1, maturity_prices_leg_2, \
        estimated_prices_leg_2, maturity_prices_leg_3, estimated_prices_leg_3, maturity_prices_leg_4, \
        estimated_prices_leg_4, maturity_prices_leg_5, estimated_prices_leg_5, maturity_prices_leg_6, \
        estimated_prices_leg_6 = self._get_option_prices(
            legs=6, S=spot_price, T=expiration_date,
            K_1=strike_leg_1, r_1=risk_leg_1, q_1=dividend_yield_leg_1, sigma_1=volatility_leg_1, option_type_1=option_leg_1,
            K_2=strike_leg_2, r_2=risk_leg_2, q_2=dividend_yield_leg_2, sigma_2=volatility_leg_2, option_type_2=option_leg_2,
            K_3=strike_leg_3, r_3=risk_leg_3, q_3=dividend_yield_leg_3, sigma_3=volatility_leg_3, option_type_3=option_leg_3,
            K_4=strike_leg_4, r_4=risk_leg_4, q_4=dividend_yield_leg_4, sigma_4=volatility_leg_4, option_type_4=option_leg_4,
            K_5=strike_leg_5, r_5=risk_leg_5, q_5=dividend_yield_leg_5, sigma_5=volatility_leg_5, option_type_5=option_leg_5,
            K_6=strike_leg_6, r_6=risk_leg_6, q_6=dividend_yield_leg_6, sigma_6=volatility_leg_6, option_type_6=option_leg_6)

        # Set title and direction sign as -1 if write and +1 if buy
        # Leg 1
        try:
            if action_leg_1 == 'buy':
                sign_leg_1 = 1
                sub_leg_1 = 'Long ' + str(option_leg_1)
            elif action_leg_1 == 'write':
                sign_leg_1 = -1
                sub_leg_1 = 'Short ' + str(option_leg_1)

        except AttributeError:
            print('Please try again.')

        # Leg 2
        try:
            if action_leg_2 == 'buy':
                sign_leg_2 = 1
                sub_leg_2 = 'Long ' + str(option_leg_2)
            elif action_leg_2 == 'write':
                sign_leg_2 = -1
                sub_leg_2 = 'Short ' + str(option_leg_2)
        except AttributeError:
            print('Please try again.')

        # Leg 3
        try:
            if action_leg_3 == 'buy':
                sign_leg_3 = 1
                sub_leg_3 = 'Long ' + str(option_leg_3)
            elif action_leg_3 == 'write':
                sign_leg_3 = -1
                sub_leg_3 = 'Short ' + str(option_leg_3)
        except AttributeError:
            print('Please try again.')

        # Leg 4
        try:
            if action_leg_4 == 'buy':
                sign_leg_4 = 1
                sub_leg_4 = 'Long ' + str(option_leg_4)
            elif action_leg_4 == 'write':
                sub_leg_4 = 'Short ' + str(option_leg_4)
                sign_leg_4 = -1
        except AttributeError:
            print('Please try again.')

        # Leg 5
        try:
            if action_leg_5 == 'buy':
                sign_leg_5 = 1
                sub_leg_5 = 'Long ' + str(option_leg_5)
            elif action_leg_5 == 'write':
                sign_leg_5 = -1
                sub_leg_5 = 'Short ' + str(option_leg_5)
        except AttributeError:
            print('Please try again.')

        # Leg 6
        try:
            if action_leg_6 == 'buy':
                sign_leg_6 = 1
                sub_leg_6 = 'Long ' + str(option_leg_6)
            elif action_leg_6 == 'write':
                sign_leg_6 = -1
                sub_leg_6 = 'Short ' + str(option_leg_6)
        except AttributeError:
            print('Please try again.')

        # Concatenate pnl arrays and multiply by # contracts and 100
        # Leg 1
        prices_leg_1 = sign_leg_1 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_1, maturity_prices_leg_1.T.reshape(
                    1, maturity_prices_leg_1.shape[0]))))
        values_leg_1 = prices_leg_1 * contracts_leg_1 * 100

        # Leg 2
        prices_leg_2 = sign_leg_2 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_2, maturity_prices_leg_2.T.reshape(
                    1, maturity_prices_leg_2.shape[0]))))
        values_leg_2 = prices_leg_2 * contracts_leg_2 * 100

        # Leg 3
        prices_leg_3 = sign_leg_3 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_3, maturity_prices_leg_3.T.reshape(
                    1, maturity_prices_leg_3.shape[0]))))
        values_leg_3 = prices_leg_3 * contracts_leg_3 * 100

        # Leg 4
        prices_leg_4 = sign_leg_4 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_4, maturity_prices_leg_4.T.reshape(
                    1, maturity_prices_leg_4.shape[0]))))
        values_leg_4 = prices_leg_4 * contracts_leg_4 * 100

        # Leg 5
        prices_leg_5 = sign_leg_5 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_5, maturity_prices_leg_5.T.reshape(
                    1, maturity_prices_leg_5.shape[0]))))
        values_leg_5 = prices_leg_5 * contracts_leg_5 * 100

        # Leg 6
        prices_leg_6 = sign_leg_6 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_6, maturity_prices_leg_6.T.reshape(
                    1, maturity_prices_leg_6.shape[0]))))
        values_leg_6 = prices_leg_6 * contracts_leg_6 * 100

        # Calculate Costs
        cost_leg_1 = price_leg_1 * contracts_leg_1 * sign_leg_1 * 100
        cost_leg_2 = price_leg_2 * contracts_leg_2 * sign_leg_2 * 100
        cost_leg_3 = price_leg_3 * contracts_leg_3 * sign_leg_3 * 100
        cost_leg_4 = price_leg_4 * contracts_leg_4 * sign_leg_4 * 100
        cost_leg_5 = price_leg_5 * contracts_leg_5 * sign_leg_5 * 100
        cost_leg_6 = price_leg_6 * contracts_leg_6 * sign_leg_6 * 100
        entry_cost = cost_leg_1 + cost_leg_2 + cost_leg_3 + cost_leg_4 + cost_leg_5 + cost_leg_6

        # Sum all PnL minus the total cost
        pnl = values_leg_1 + values_leg_2 + values_leg_3 + values_leg_4 + values_leg_5 + values_leg_6 + \
                - entry_cost

        # Create pnl dataframe
        df = pd.DataFrame(data=pnl.T, index=strike_prices, columns=labels)

        # Calculate purchased value per leg / 100
        option_spreads = values_leg_1/100 + values_leg_2/100 + values_leg_3/100 + values_leg_4/100 + values_leg_5/100 + \
                         values_leg_6/100

        # Make title for visualization
        title = '6 legs: ' + sub_leg_1 + ' - ' + sub_leg_2 + ' - ' + sub_leg_3 + ' - ' + sub_leg_4 + ' - ' + sub_leg_5 + \
            ' - ' + sub_leg_6

        # Visualize results
        self._show_results(spot_price=spot_price, pnl=pnl, df=df, option_spreads=option_spreads,
                           strike_prices=strike_prices, labels=labels, title=title, graph_type=graph_type,
                           graph_profile=graph_profile)

    def five_legs(self, spot_price, expiration_date,
                action_leg_1, contracts_leg_1, price_leg_1, option_leg_1, strike_leg_1, risk_leg_1, dividend_yield_leg_1,
                volatility_leg_1,

                action_leg_2, contracts_leg_2, price_leg_2, option_leg_2, strike_leg_2, risk_leg_2, dividend_yield_leg_2,
                volatility_leg_2,

                action_leg_3, contracts_leg_3, price_leg_3, option_leg_3, strike_leg_3, risk_leg_3, dividend_yield_leg_3,
                volatility_leg_3,

                action_leg_4, contracts_leg_4, price_leg_4, option_leg_4, strike_leg_4, risk_leg_4, dividend_yield_leg_4,
                volatility_leg_4,

                action_leg_5, contracts_leg_5, price_leg_5, option_leg_5, strike_leg_5, risk_leg_5, dividend_yield_leg_5,
                volatility_leg_5,
                graph_type, graph_profile):
        """ Displays calculated option values for the 5 legs strategy.

        :param spot_price: (float) underlying stock price
        :param expiration_date: (str) expiration date
        :param action_leg_1: (str) whether the action is a buy or write for leg 1
        :param contracts_leg_1: (int) # of contracts to buy/write for leg 1
        :param price_leg_1: (float) ask price for leg 1
        :param option_leg_1: (str) 'put' or 'call' option type for leg 1
        :param strike_leg_1: (float) strike price for leg 1
        :param risk_leg_1: (float) risk-free interest rate for leg 1
        :param dividend_yield_leg_1: float) dividend yield for leg 1
        :param volatility_leg_1: (float) implied volatility for leg 1
        :param action_leg_2: (str) whether the action is a buy or write for leg 2
        :param contracts_leg_2: (int) # of contracts to buy/write for leg 2
        :param price_leg_2: (float) ask price for leg 2
        :param option_leg_2: (str) 'put' or 'call' option type for leg 2
        :param strike_leg_2: (float) strike price for leg 2
        :param risk_leg_2: (float) risk-free interest rate for leg 2
        :param dividend_yield_leg_2: float) dividend yield for leg 2
        :param volatility_leg_2: (float) implied volatility for leg 2
        :param action_leg_3: (str) whether the action is a buy or write for leg 3
        :param contracts_leg_3: (int) # of contracts to buy/write for leg 3
        :param price_leg_3: (float) ask price for leg 3
        :param option_leg_3: (str) 'put' or 'call' option type for leg 3
        :param strike_leg_3: (float) strike price for leg 3
        :param risk_leg_3: (float) risk-free interest rate for leg 3
        :param dividend_yield_leg_3: float) dividend yield for leg 3
        :param volatility_leg_3: (float) implied volatility for leg 3
        :param action_leg_4: (str) whether the action is a buy or write for leg 4
        :param contracts_leg_4: (int) # of contracts to buy/write for leg 4
        :param price_leg_4: (float) ask price for leg 4
        :param option_leg_4: (str) 'put' or 'call' option type for leg 4
        :param strike_leg_4: (float) strike price for leg 4
        :param risk_leg_4: (float) risk-free interest rate for leg 4
        :param dividend_yield_leg_4: float) dividend yield for leg 4
        :param volatility_leg_4: (float) implied volatility for leg 4
        :param action_leg_5: (str) whether the action is a buy or write for leg 5
        :param contracts_leg_5: (int) # of contracts to buy/write for leg 5
        :param price_leg_5: (float) ask price for leg 5
        :param option_leg_5: (str) 'put' or 'call' option type for leg 5
        :param strike_leg_5: (float) strike price for leg 5
        :param risk_leg_5: (float) risk-free interest rate for leg 5
        :param dividend_yield_leg_5: float) dividend yield for leg 5
        :param volatility_leg_5: (float) implied volatility for leg 5
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param graph_profile: (str) graph profile such as 'pnl', 'risk' or 'option/spread'
        :return: annotated heatmap table and/or graph traces with calculated results
        """

        # Define auxiliary global variables
        global sign_leg_1, sign_leg_2, sign_leg_3, sign_leg_4, sign_leg_5, sub_leg_1, sub_leg_2, sub_leg_3, sub_leg_4, sub_leg_5

        # Calculate option prices with BSM options
        strike_prices, labels, dates_until_maturity, maturity_prices_leg_1, estimated_prices_leg_1, maturity_prices_leg_2, \
        estimated_prices_leg_2, maturity_prices_leg_3, estimated_prices_leg_3, maturity_prices_leg_4, \
        estimated_prices_leg_4, maturity_prices_leg_5, estimated_prices_leg_5 = self._get_option_prices(
            legs=5, S=spot_price, T=expiration_date,
            K_1=strike_leg_1, r_1=risk_leg_1, q_1=dividend_yield_leg_1, sigma_1=volatility_leg_1, option_type_1=option_leg_1,
            K_2=strike_leg_2, r_2=risk_leg_2, q_2=dividend_yield_leg_2, sigma_2=volatility_leg_2, option_type_2=option_leg_2,
            K_3=strike_leg_3, r_3=risk_leg_3, q_3=dividend_yield_leg_3, sigma_3=volatility_leg_3, option_type_3=option_leg_3,
            K_4=strike_leg_4, r_4=risk_leg_4, q_4=dividend_yield_leg_4, sigma_4=volatility_leg_4, option_type_4=option_leg_4,
            K_5=strike_leg_5, r_5=risk_leg_5, q_5=dividend_yield_leg_5, sigma_5=volatility_leg_5, option_type_5=option_leg_5)

        # Set title and direction sign as -1 if write and +1 if buy
        # Leg 1
        try:
            if action_leg_1 == 'buy':
                sign_leg_1 = 1
                sub_leg_1 = 'Long ' + str(option_leg_1)
            elif action_leg_1 == 'write':
                sign_leg_1 = -1
                sub_leg_1 = 'Short ' + str(option_leg_1)

        except AttributeError:
            print('Please try again.')

        # Leg 2
        try:
            if action_leg_2 == 'buy':
                sign_leg_2 = 1
                sub_leg_2 = 'Long ' + str(option_leg_2)
            elif action_leg_2 == 'write':
                sign_leg_2 = -1
                sub_leg_2 = 'Short ' + str(option_leg_2)
        except AttributeError:
            print('Please try again.')

        # Leg 3
        try:
            if action_leg_3 == 'buy':
                sign_leg_3 = 1
                sub_leg_3 = 'Long ' + str(option_leg_3)
            elif action_leg_3 == 'write':
                sign_leg_3 = -1
                sub_leg_3 = 'Short ' + str(option_leg_3)
        except AttributeError:
            print('Please try again.')

        # Leg 4
        try:
            if action_leg_4 == 'buy':
                sign_leg_4 = 1
                sub_leg_4 = 'Long ' + str(option_leg_4)
            elif action_leg_4 == 'write':
                sub_leg_4 = 'Short ' + str(option_leg_4)
                sign_leg_4 = -1
        except AttributeError:
            print('Please try again.')

        # Leg 5
        try:
            if action_leg_5 == 'buy':
                sign_leg_5 = 1
                sub_leg_5 = 'Long ' + str(option_leg_5)
            elif action_leg_5 == 'write':
                sign_leg_5 = -1
                sub_leg_5 = 'Short ' + str(option_leg_5)
        except AttributeError:
            print('Please try again.')

        # Concatenate pnl arrays and multiply by # contracts and 100
        # Leg 1
        prices_leg_1 = sign_leg_1 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_1, maturity_prices_leg_1.T.reshape(
                    1, maturity_prices_leg_1.shape[0]))))
        values_leg_1 = prices_leg_1 * contracts_leg_1 * 100

        # Leg 2
        prices_leg_2 = sign_leg_2 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_2, maturity_prices_leg_2.T.reshape(
                    1, maturity_prices_leg_2.shape[0]))))
        values_leg_2 = prices_leg_2 * contracts_leg_2 * 100

        # Leg 3
        prices_leg_3 = sign_leg_3 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_3, maturity_prices_leg_3.T.reshape(
                    1, maturity_prices_leg_3.shape[0]))))
        values_leg_3 = prices_leg_3 * contracts_leg_3 * 100

        # Leg 4
        prices_leg_4 = sign_leg_4 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_4, maturity_prices_leg_4.T.reshape(
                    1, maturity_prices_leg_4.shape[0]))))
        values_leg_4 = prices_leg_4 * contracts_leg_4 * 100

        # Leg 5
        prices_leg_5 = sign_leg_5 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_5, maturity_prices_leg_5.T.reshape(
                    1, maturity_prices_leg_5.shape[0]))))
        values_leg_5 = prices_leg_5 * contracts_leg_5 * 100

        # Calculate Costs
        cost_leg_1 = price_leg_1 * contracts_leg_1 * sign_leg_1 * 100
        cost_leg_2 = price_leg_2 * contracts_leg_2 * sign_leg_2 * 100
        cost_leg_3 = price_leg_3 * contracts_leg_3 * sign_leg_3 * 100
        cost_leg_4 = price_leg_4 * contracts_leg_4 * sign_leg_4 * 100
        cost_leg_5 = price_leg_5 * contracts_leg_5 * sign_leg_5 * 100
        entry_cost = cost_leg_1 + cost_leg_2 + cost_leg_3 + cost_leg_4 + cost_leg_5

        # Sum all PnL minus the total cost
        pnl = values_leg_1 + values_leg_2 + values_leg_3 + values_leg_4 + values_leg_5 - entry_cost

        # Create pnl dataframe
        df = pd.DataFrame(data=pnl.T, index=strike_prices, columns=labels)

        # Calculate purchased value per leg / 100 minus stock only values / num_shares
        option_spreads = values_leg_1/100 + values_leg_2/100 + values_leg_3/100 + values_leg_4/100 + values_leg_5/100

        # Make title for visualization
        title = '5 legs: ' + sub_leg_1 + ' - ' + sub_leg_2 + ' - ' + sub_leg_3 + ' - ' + sub_leg_4 + ' - ' + sub_leg_5

        # Visualize results
        self._show_results(spot_price=spot_price, pnl=pnl, df=df, option_spreads=option_spreads,
                           strike_prices=strike_prices, labels=labels, title=title, graph_type=graph_type,
                           graph_profile=graph_profile)

    def four_legs(self, spot_price, expiration_date,
                action_leg_1, contracts_leg_1, price_leg_1, option_leg_1, strike_leg_1, risk_leg_1, dividend_yield_leg_1,
                volatility_leg_1,

                action_leg_2, contracts_leg_2, price_leg_2, option_leg_2, strike_leg_2, risk_leg_2, dividend_yield_leg_2,
                volatility_leg_2,

                action_leg_3, contracts_leg_3, price_leg_3, option_leg_3, strike_leg_3, risk_leg_3, dividend_yield_leg_3,
                volatility_leg_3,

                action_leg_4, contracts_leg_4, price_leg_4, option_leg_4, strike_leg_4, risk_leg_4, dividend_yield_leg_4,
                volatility_leg_4,
                graph_type, graph_profile):

        """ Displays calculated option values for the 4 legs strategy.

        :param spot_price: (float) underlying stock price
        :param expiration_date: (str) expiration date
        :param action_leg_1: (str) whether the action is a buy or write for leg 1
        :param contracts_leg_1: (int) # of contracts to buy/write for leg 1
        :param price_leg_1: (float) ask price for leg 1
        :param option_leg_1: (str) 'put' or 'call' option type for leg 1
        :param strike_leg_1: (float) strike price for leg 1
        :param risk_leg_1: (float) risk-free interest rate for leg 1
        :param dividend_yield_leg_1: float) dividend yield for leg 1
        :param volatility_leg_1: (float) implied volatility for leg 1
        :param action_leg_2: (str) whether the action is a buy or write for leg 2
        :param contracts_leg_2: (int) # of contracts to buy/write for leg 2
        :param price_leg_2: (float) ask price for leg 2
        :param option_leg_2: (str) 'put' or 'call' option type for leg 2
        :param strike_leg_2: (float) strike price for leg 2
        :param risk_leg_2: (float) risk-free interest rate for leg 2
        :param dividend_yield_leg_2: float) dividend yield for leg 2
        :param volatility_leg_2: (float) implied volatility for leg 2
        :param action_leg_1: (str) whether the action is a buy or write for leg 1
        :param contracts_leg_1: (int) # of contracts to buy/write for leg 1
        :param price_leg_3: (float) ask price for leg 3
        :param option_leg_3: (str) 'put' or 'call' option type for leg 3
        :param strike_leg_3: (float) strike price for leg 3
        :param risk_leg_3: (float) risk-free interest rate for leg 3
        :param dividend_yield_leg_3: float) dividend yield for leg 3
        :param volatility_leg_3: (float) implied volatility for leg 3
        :param action_leg_4: (str) whether the action is a buy or write for leg 1
        :param contracts_leg_4: (int) # of contracts to buy/write for leg 1
        :param price_leg_4: (float) ask price for leg 4
        :param option_leg_4: (str) 'put' or 'call' option type for leg 4
        :param strike_leg_4: (float) strike price for leg 4
        :param risk_leg_4: (float) risk-free interest rate for leg 4
        :param dividend_yield_leg_4: float) dividend yield for leg 4
        :param volatility_leg_4: (float) implied volatility for leg 4
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param graph_profile: (str) graph profile such as 'pnl', 'risk' or 'option/spread'
        :return: annotated heatmap table and/or graph traces with calculated results
        """

        # Define auxiliary global variables
        global sign_leg_1, sign_leg_2, sign_leg_3, sign_leg_4, sub_leg_1, sub_leg_2, sub_leg_3, sub_leg_4

        # Calculate option prices with BSM options
        strike_prices, labels, dates_until_maturity, maturity_prices_leg_1, estimated_prices_leg_1, maturity_prices_leg_2, \
        estimated_prices_leg_2, maturity_prices_leg_3, estimated_prices_leg_3, maturity_prices_leg_4, \
        estimated_prices_leg_4 = self._get_option_prices(
            legs=4, S=spot_price, T=expiration_date,
            K_1=strike_leg_1, r_1=risk_leg_1, q_1=dividend_yield_leg_1, sigma_1=volatility_leg_1, option_type_1=option_leg_1,
            K_2=strike_leg_2, r_2=risk_leg_2, q_2=dividend_yield_leg_2, sigma_2=volatility_leg_2, option_type_2=option_leg_2,
            K_3=strike_leg_3, r_3=risk_leg_3, q_3=dividend_yield_leg_3, sigma_3=volatility_leg_3, option_type_3=option_leg_3,
            K_4=strike_leg_4, r_4=risk_leg_4, q_4=dividend_yield_leg_4, sigma_4=volatility_leg_4, option_type_4=option_leg_4)

        # Set title and direction sign as -1 if write and +1 if buy
        # Leg 1
        try:
            if action_leg_1 == 'buy':
                sign_leg_1 = 1
                sub_leg_1 = 'Long ' + str(option_leg_1)
            elif action_leg_1 == 'write':
                sign_leg_1 = -1
                sub_leg_1 = 'Short ' + str(option_leg_1)

        except AttributeError:
            print('Please try again.')

        # Leg 2
        try:
            if action_leg_2 == 'buy':
                sign_leg_2 = 1
                sub_leg_2 = 'Long ' + str(option_leg_2)
            elif action_leg_2 == 'write':
                sign_leg_2 = -1
                sub_leg_2 = 'Short ' + str(option_leg_2)
        except AttributeError:
            print('Please try again.')

        # Leg 3
        try:
            if action_leg_3 == 'buy':
                sign_leg_3 = 1
                sub_leg_3 = 'Long ' + str(option_leg_3)
            elif action_leg_3 == 'write':
                sign_leg_3 = -1
                sub_leg_3 = 'Short ' + str(option_leg_3)
        except AttributeError:
            print('Please try again.')

        # Leg 4
        try:
            if action_leg_4 == 'buy':
                sign_leg_4 = 1
                sub_leg_4 = 'Long ' + str(option_leg_4)
            elif action_leg_4 == 'write':
                sub_leg_4 = 'Short ' + str(option_leg_4)
                sign_leg_4 = -1
        except AttributeError:
            print('Please try again.')

        # Concatenate pnl arrays and multiply by # contracts and 100
        # Leg 1
        prices_leg_1 = sign_leg_1 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_1, maturity_prices_leg_1.T.reshape(
                    1, maturity_prices_leg_1.shape[0]))))
        values_leg_1 = prices_leg_1 * contracts_leg_1 * 100

        # Leg 2
        prices_leg_2 = sign_leg_2 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_2, maturity_prices_leg_2.T.reshape(
                    1, maturity_prices_leg_2.shape[0]))))
        values_leg_2 = prices_leg_2 * contracts_leg_2 * 100

        # Leg 3
        prices_leg_3 = sign_leg_3 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_3, maturity_prices_leg_3.T.reshape(
                    1, maturity_prices_leg_3.shape[0]))))
        values_leg_3 = prices_leg_3 * contracts_leg_3 * 100

        # Leg 4
        prices_leg_4 = sign_leg_4 * np.asarray(np.concatenate(
            (estimated_prices_leg_4, maturity_prices_leg_4.T.reshape(
                1, maturity_prices_leg_4.shape[0]))))
        values_leg_4 = prices_leg_4 * contracts_leg_4 * 100

        # Calculate Costs
        cost_leg_1 = price_leg_1 * contracts_leg_1 * sign_leg_1 * 100
        cost_leg_2 = price_leg_2 * contracts_leg_2 * sign_leg_2 * 100
        cost_leg_3 = price_leg_3 * contracts_leg_3 * sign_leg_3 * 100
        cost_leg_4 = price_leg_4 * contracts_leg_4 * sign_leg_4 * 100
        entry_cost = cost_leg_1 + cost_leg_2 + cost_leg_3 + cost_leg_4 

        # Sum all PnL minus the total cost
        pnl = values_leg_1 + values_leg_2 + values_leg_3 + values_leg_4 - entry_cost

        # Create pnl dataframe
        df = pd.DataFrame(data=pnl.T, index=strike_prices, columns=labels)

        # Calculate purchased value per leg / 100
        option_spreads = values_leg_1/100 + values_leg_2/100 + values_leg_3/100 + values_leg_4/100

        # Make title for visualization
        title = '4 legs: ' + sub_leg_1 + ' - ' + sub_leg_2 + ' - ' + sub_leg_3 + ' - ' + sub_leg_4 

        # Visualize results
        self._show_results(spot_price=spot_price, pnl=pnl, df=df, option_spreads=option_spreads,
                           strike_prices=strike_prices, labels=labels, title=title, graph_type=graph_type,
                           graph_profile=graph_profile)

    def three_legs(self, spot_price, expiration_date,
                action_leg_1, contracts_leg_1, price_leg_1, option_leg_1, strike_leg_1, risk_leg_1, dividend_yield_leg_1,
                volatility_leg_1,

                action_leg_2, contracts_leg_2, price_leg_2, option_leg_2, strike_leg_2, risk_leg_2, dividend_yield_leg_2,
                volatility_leg_2,

                action_leg_3, contracts_leg_3, price_leg_3, option_leg_3, strike_leg_3, risk_leg_3, dividend_yield_leg_3,
                volatility_leg_3,

                graph_type, graph_profile):
        """ Displays calculated option values for the 3 legs strategy.

        :param spot_price: (float) underlying stock price
        :param expiration_date: (str) expiration date
        :param action_leg_1: (str) whether the action is a buy or write for leg 1
        :param contracts_leg_1: (int) # of contracts to buy/write for leg 1
        :param price_leg_1: (float) ask price for leg 1
        :param option_leg_1: (str) 'put' or 'call' option type for leg 1
        :param strike_leg_1: (float) strike price for leg 1
        :param risk_leg_1: (float) risk-free interest rate for leg 1
        :param dividend_yield_leg_1: float) dividend yield for leg 1
        :param volatility_leg_1: (float) implied volatility for leg 1
        :param action_leg_2: (str) whether the action is a buy or write for leg 2
        :param contracts_leg_2: (int) # of contracts to buy/write for leg 2
        :param price_leg_2: (float) ask price for leg 2
        :param option_leg_2: (str) 'put' or 'call' option type for leg 2
        :param strike_leg_2: (float) strike price for leg 2
        :param risk_leg_2: (float) risk-free interest rate for leg 2
        :param dividend_yield_leg_2: float) dividend yield for leg 2
        :param volatility_leg_2: (float) implied volatility for leg 2
        :param action_leg_1: (str) whether the action is a buy or write for leg 1
        :param contracts_leg_1: (int) # of contracts to buy/write for leg 1
        :param price_leg_3: (float) ask price for leg 3
        :param option_leg_3: (str) 'put' or 'call' option type for leg 3
        :param strike_leg_3: (float) strike price for leg 3
        :param risk_leg_3: (float) risk-free interest rate for leg 3
        :param dividend_yield_leg_3: float) dividend yield for leg 3
        :param volatility_leg_3: (float) implied volatility for leg 3
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param graph_profile: (str) graph profile such as 'pnl', 'risk' or 'option/spread'
        :return: annotated heatmap table and/or graph traces with calculated results
        """

        # Define auxiliary global variables
        global sign_leg_1, sign_leg_2, sign_leg_3, sub_leg_1, sub_leg_2, sub_leg_3

        # Calculate option prices with BSM options
        strike_prices, labels, dates_until_maturity, maturity_prices_leg_1, estimated_prices_leg_1, maturity_prices_leg_2, \
        estimated_prices_leg_2, maturity_prices_leg_3, estimated_prices_leg_3= self._get_option_prices(
            legs=3, S=spot_price, T=expiration_date,
            K_1=strike_leg_1, r_1=risk_leg_1, q_1=dividend_yield_leg_1, sigma_1=volatility_leg_1, option_type_1=option_leg_1,
            K_2=strike_leg_2, r_2=risk_leg_2, q_2=dividend_yield_leg_2, sigma_2=volatility_leg_2, option_type_2=option_leg_2,
            K_3=strike_leg_3, r_3=risk_leg_3, q_3=dividend_yield_leg_3, sigma_3=volatility_leg_3, option_type_3=option_leg_3)

        # Set title and direction sign as -1 if write and +1 if buy
        # Leg 1
        try:
            if action_leg_1 == 'buy':
                sign_leg_1 = 1
                sub_leg_1 = 'Long ' + str(option_leg_1)
            elif action_leg_1 == 'write':
                sign_leg_1 = -1
                sub_leg_1 = 'Short ' + str(option_leg_1)

        except AttributeError:
            print('Please try again.')

        # Leg 2
        try:
            if action_leg_2 == 'buy':
                sign_leg_2 = 1
                sub_leg_2 = 'Long ' + str(option_leg_2)
            elif action_leg_2 == 'write':
                sign_leg_2 = -1
                sub_leg_2 = 'Short ' + str(option_leg_2)
        except AttributeError:
            print('Please try again.')

        # Leg 3
        try:
            if action_leg_3 == 'buy':
                sign_leg_3 = 1
                sub_leg_3 = 'Long ' + str(option_leg_3)
            elif action_leg_3 == 'write':
                sign_leg_3 = -1
                sub_leg_3 = 'Short ' + str(option_leg_3)
        except AttributeError:
            print('Please try again.')

        # Concatenate pnl arrays and multiply by # contracts and 100
        # Leg 1
        prices_leg_1 = sign_leg_1 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_1, maturity_prices_leg_1.T.reshape(
                    1, maturity_prices_leg_1.shape[0]))))
        values_leg_1 = prices_leg_1 * contracts_leg_1 * 100

        # Leg 2
        prices_leg_2 = sign_leg_2 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_2, maturity_prices_leg_2.T.reshape(
                    1, maturity_prices_leg_2.shape[0]))))
        values_leg_2 = prices_leg_2 * contracts_leg_2 * 100

        # Leg 3
        prices_leg_3 = sign_leg_3 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_3, maturity_prices_leg_3.T.reshape(
                    1, maturity_prices_leg_3.shape[0]))))
        values_leg_3 = prices_leg_3 * contracts_leg_3 * 100

        # Calculate Costs
        cost_leg_1 = price_leg_1 * contracts_leg_1 * sign_leg_1 * 100
        cost_leg_2 = price_leg_2 * contracts_leg_2 * sign_leg_2 * 100
        cost_leg_3 = price_leg_3 * contracts_leg_3 * sign_leg_3 * 100
        entry_cost = cost_leg_1 + cost_leg_2 + cost_leg_3 

        # Sum all PnL minus the total cost
        pnl = values_leg_1 + values_leg_2 + values_leg_3 - entry_cost

        # Create pnl dataframe
        df = pd.DataFrame(data=pnl.T, index=strike_prices, columns=labels)

        # Calculate purchased value per leg / 100
        option_spreads = values_leg_1/100 + values_leg_2/100 + values_leg_3/100

        # Make title for visualization
        title = '3 legs: ' + sub_leg_1 + ' - ' + sub_leg_2 + ' - ' + sub_leg_3

        # Visualize results
        self._show_results(spot_price=spot_price, pnl=pnl, df=df, option_spreads=option_spreads,
                           strike_prices=strike_prices, labels=labels, title=title, graph_type=graph_type,
                           graph_profile=graph_profile)

    def two_legs(self, spot_price, expiration_date,
                action_leg_1, contracts_leg_1, price_leg_1, option_leg_1, strike_leg_1, risk_leg_1, dividend_yield_leg_1,
                volatility_leg_1,

                action_leg_2, contracts_leg_2, price_leg_2, option_leg_2, strike_leg_2, risk_leg_2, dividend_yield_leg_2,
                volatility_leg_2,

                graph_type, graph_profile):
        """ Displays calculated option values for the 2 legs strategy.

        :param spot_price: (float) underlying stock price
        :param expiration_date: (str) expiration date
        :param action_leg_1: (str) whether the action is a buy or write for leg 1
        :param contracts_leg_1: (int) # of contracts to buy/write for leg 1
        :param price_leg_1: (float) ask price for leg 1
        :param option_leg_1: (str) 'put' or 'call' option type for leg 1
        :param strike_leg_1: (float) strike price for leg 1
        :param risk_leg_1: (float) risk-free interest rate for leg 1
        :param dividend_yield_leg_1: float) dividend yield for leg 1
        :param volatility_leg_1: (float) implied volatility for leg 1
        :param action_leg_2: (str) whether the action is a buy or write for leg 2
        :param contracts_leg_2: (int) # of contracts to buy/write for leg 2
        :param price_leg_2: (float) ask price for leg 2
        :param option_leg_2: (str) 'put' or 'call' option type for leg 2
        :param strike_leg_2: (float) strike price for leg 2
        :param risk_leg_2: (float) risk-free interest rate for leg 2
        :param dividend_yield_leg_2: float) dividend yield for leg 2
        :param volatility_leg_2: (float) implied volatility for leg 2
        :param graph_type: (str) graph type such as 'table', 'graph', or 'both'
        :param graph_profile: (str) graph profile such as 'pnl', 'risk' or 'option/spread'
        :return: annotated heatmap table and/or graph traces with calculated results
        """

        # Define auxiliary global variables
        global sign_leg_1, sign_leg_2, sub_leg_1, sub_leg_2

        # Calculate option prices with BSM options
        strike_prices, labels, dates_until_maturity, maturity_prices_leg_1, estimated_prices_leg_1, maturity_prices_leg_2, \
        estimated_prices_leg_2 = self._get_option_prices(
            legs=2, S=spot_price, T=expiration_date,
            K_1=strike_leg_1, r_1=risk_leg_1, q_1=dividend_yield_leg_1, sigma_1=volatility_leg_1, option_type_1=option_leg_1,
            K_2=strike_leg_2, r_2=risk_leg_2, q_2=dividend_yield_leg_2, sigma_2=volatility_leg_2, option_type_2=option_leg_2)

        # Set title and direction sign as -1 if write and +1 if buy
        # Leg 1
        try:
            if action_leg_1 == 'buy':
                sign_leg_1 = 1
                sub_leg_1 = 'Long ' + str(option_leg_1)
            elif action_leg_1 == 'write':
                sign_leg_1 = -1
                sub_leg_1 = 'Short ' + str(option_leg_1)

        except AttributeError:
            print('Please try again.')

        # Leg 2
        try:
            if action_leg_2 == 'buy':
                sign_leg_2 = 1
                sub_leg_2 = 'Long ' + str(option_leg_2)
            elif action_leg_2 == 'write':
                sign_leg_2 = -1
                sub_leg_2 = 'Short ' + str(option_leg_2)
        except AttributeError:
            print('Please try again.')

        # Concatenate pnl arrays and multiply by # contracts and 100
        # Leg 1
        prices_leg_1 = sign_leg_1 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_1, maturity_prices_leg_1.T.reshape(
                    1, maturity_prices_leg_1.shape[0]))))
        values_leg_1 = prices_leg_1 * contracts_leg_1 * 100

        # Leg 2
        prices_leg_2 = sign_leg_2 * np.asarray(
            np.concatenate(
                (estimated_prices_leg_2, maturity_prices_leg_2.T.reshape(
                    1, maturity_prices_leg_2.shape[0]))))
        values_leg_2 = prices_leg_2 * contracts_leg_2 * 100

        # Calculate Costs
        cost_leg_1 = price_leg_1 * contracts_leg_1 * sign_leg_1 * 100
        cost_leg_2 = price_leg_2 * contracts_leg_2 * sign_leg_2 * 100
        entry_cost = cost_leg_1 + cost_leg_2 

        # Sum all PnL minus the total cost
        pnl = values_leg_1 + values_leg_2 - entry_cost

        # Create pnl dataframe
        df = pd.DataFrame(data=pnl.T, index=strike_prices, columns=labels)

        # Calculate purchased value per leg / 100 minus stock only values / num_shares
        option_spreads = values_leg_1/100 + values_leg_2/100

        # Make title for visualization
        title = '2 legs: ' + sub_leg_1 + ' - ' + sub_leg_2

        # Visualize results
        self._show_results(spot_price=spot_price, pnl=pnl, df=df, option_spreads=option_spreads,
                           strike_prices=strike_prices, labels=labels, title=title, graph_type=graph_type,
                           graph_profile=graph_profile)


"""opt = Option()
opt.synthetic_put(
                num_shares=100,
                spot_price=2226.72,
                expiration_date='2021-04-09',
                action='buy',
                contracts=1,
                option_price=16.00,
                option_type='put',
                strike_price=2240,
                risk_free_rate=0.005,
                dividend_yield=0,
                volatility=0.2187,
                graph_type='graph',
                graph_profile='pnl'
            )

opt = Option()
opt.two_legs(
                spot_price=691.62,
                expiration_date='2021-04-09',
                action_leg_1='buy',
                contracts_leg_1=1,
                price_leg_1= 10.40,
                option_leg_1='call',
                strike_leg_1=700,
                risk_leg_1=0.005,
                dividend_yield_leg_1=0,
                volatility_leg_1=0.488653,
                action_leg_2='write',
                contracts_leg_2=1,
                price_leg_2=4.40,
                option_leg_2='put',
                strike_leg_2=720,
                risk_leg_2=0.005,
                dividend_yield_leg_2=0,
                volatility_leg_2=0.491155,
                graph_type='table',
                graph_profile='pnl'
            )


opt = Option()
opt.covered_call(
    spot_price=691.63,
    expiration_date='2021-04-09',
    num_shares=100,
    contracts=1,
    option_price=20.30,
    strike_price=680,
    risk_free_rate=0.005,
    dividend_yield=0,
    volatility=0.58271,
    graph_type='both',
    graph_profile='option/spread')

"""






















