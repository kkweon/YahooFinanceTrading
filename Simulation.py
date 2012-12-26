import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse as arg


parser = arg.ArgumentParser(description = "Market Simulator")
parser.add_argument("-c", "--cash", default = 10000, help = "Initial Cash\nDefault: 10,000", type = float)
parser.add_argument("-o", "--output", default = "values.csv", help = "Output File name\nDefault: values.csv", type = str)
parser.add_argument("-d", "--debug", default = False, help = "Verbose Mode = Debug", action = "store_true")
parser.add_argument("-t", "--type", default = "Adj Close", help = "Close = Actual Close, Adj Close = Adjusted Close, ...", type = str)
args = parser.parse_args()

#########################################################################################
# GLOBAL VARIABLES
#########################################################################################
DATA_SOURCE = "./YAHOO_DATA/"
DATA_TYPE = args.type
CASH = args.cash
OUTPUT = args.output
DEBUG = args.debug
#########################################################################################
# HELPER FUNCTIONS BEGINS
#########################################################################################
def cleanDateAndSort(dataframe):
	""" dataframe: date, action, symbol, share """
	new_frame = dataframe.sort_index(axis = 0)
	timestamp = set(new_frame.index)
	return new_frame, timestamp

def lookupSymbols(symbol_list, dates):
	''' source file (csv) => Date, Open, High, Low, Close, Volume, Adj Close '''
	super_df = dict() 
	for symbol in symbol_list:
		each_history_csv = pd.read_csv(DATA_SOURCE + symbol + ".csv", index_col = 0, header = 0, parse_dates = [0])
		selected = each_history_csv.ix[dates, DATA_TYPE]
		super_df[symbol] = selected.values	
	HIST_DB = pd.DataFrame(super_df, index = selected.index)
	HIST_DB = HIST_DB.fillna(0, method = 'ffill').fillna(0, method = 'backfill')
	return HIST_DB.sort_index(axis = 0)

def get_NYSE_dates(ts_list):
	''' ts_list => datetime.date '''
	beg_date = min(ts_list)
	end_date = max(ts_list)
	NYSE_Dates = np.loadtxt("NYSE_dates.txt", dtype = str)
	TS = list()
	for date in NYSE_Dates:
		TS.append(datetime.datetime.strptime(date, "%m/%d/%Y"))
		TS = [i for i in TS if i >= beg_date]
		TS = [i for i in TS if i <= end_date]
	return pd.DatetimeIndex(TS)
#########################################################################################
# HELPER FUNCTIONS ENDS
#########################################################################################

#########################################################################################
# CLASS DEFINITIONS
#########################################################################################
class Equity:
	def __init__(self, name, debug = False):
		''' Init: shares = 0 '''
		self.name = name
		self.share = 0
		self.debug = debug

	def __str__(self):
		return 'STOCK NAME: {:}\n CURRENT SHARE: {:d}\n'.format(self.name, self.share)


	def buy(self, date, share):
		'''Buy this equity
			date = dt.datetime(year, month, day, 16, 0, 0) '''
		global CASH
		price = self.get_price(date)
		CASH -= price * share
		self.share += share
		if self.debug:
			print '[BUY] {:}. SHARES: {:d}. PRICES: {:.2f}. CURRENT: {:d}. DATE: {:}'.format(self.name, share, price, self.share, date.strftime('%Y,%m,%d'))

	def sell(self, date, share):
		'''Sell this equity '''
		global CASH
		price = self.get_price(date)
		CASH += price * share
		self.share -= share
		if self.debug:
			print '[SELL] {:}. SHARES: {:d}. PRICES: {:.2f}. CURRENT: {:d}. DATE: {:}'.format(self.name, share, price, self.share, date.strftime('%Y,%m,%d'))

	def get_value(self, date):
		return self.share * self.get_price(date)

	def get_price(self, date):
		try:
			price = HIST.ix[date, self.name]
			return price
		except KeyError:
			return 0

	def get_name(self):
		return self.name

class Portfolio:
	def __init__(self, timespans, orders, symbols):
		''' Init with sorted orders dataframe and symbols is a list of unique symbols. '''
		self.ISO_ORDER = orders
		self.ISO_ORDER.index = [date.isoformat() for date in pd.DatetimeIndex(self.ISO_ORDER.index)]
		self.symbols = [Equity(i, DEBUG) for i in symbols]
		self.timespans = timespans
		self.df_to_report = []
		for time in timespans:
			self.execute(time)
		PORTFOLIO = pd.DataFrame(self.df_to_report, index = None, columns = ['Date', 'Value'])
		PORTFOLIO['Year'] = [i.year for i in PORTFOLIO['Date']]
		PORTFOLIO['Month'] = [i.month for i in PORTFOLIO['Date']]
		PORTFOLIO['Day'] = [i.day for i in PORTFOLIO['Date']]
		del PORTFOLIO['Date']
		PORTFOLIO['Value'] = PORTFOLIO['Value'].astype('int64')
		PORTFOLIO = PORTFOLIO.reindex_axis(['Year', 'Month', 'Day', 'Value'], axis = 1)
		PORTFOLIO.to_csv(OUTPUT, header = None, index = None)
		if DEBUG:
			PORTFOLIO = pd.DataFrame(self.df_to_report, index = None, columns = ['Date', 'Value'])
			PORTFOLIO.index = pd.DatetimeIndex(PORTFOLIO['Date'])
			del PORTFOLIO['Date']
			INNER = PORTFOLIO.join(orders, how = 'inner')
			if len(INNER) == len(orders):
				print "+{:-<46}+".format('')
				print "|{: ^47}|".format("VERIFIED")
				print "+{:-<46}+".format('')
			else:
				print "+{:-<46}+".format('')
				print "|{:^47}|".format("WARNING: DISCREPANCY FOUND")
				print "+{:-<46}+".format('')
				print "|{: ^49}|".format("<LENGTH DIFFERENCE>")
				print "|{: ^49}|".format("PORTFOLIO " + str(len(INNER)) +'- ORIGINAL '+ str(len(orders)))
				print "+{:-<46}+".format('')

	def execute(self, date):
		'''execute orders and return dataframe '''
		if date.isoformat() in list(self.ISO_ORDER.index):
			for i in range(len(self.ISO_ORDER.index)):
				if self.ISO_ORDER.index[i] == date.isoformat():
					SYMBOL = self.ISO_ORDER.ix[i, 'symbol']
					SHARES = self.ISO_ORDER.ix[i, 'share']
					ACTION = self.ISO_ORDER.ix[i, 'action']
					SYMBOL_POS = self.find_equity_by_name(SYMBOL)

					if ACTION == 'BUY' or ACTION == 'Buy' or ACTION == 'buy':
						self.symbols[SYMBOL_POS].buy(date, SHARES)

					else:
						self.symbols[SYMBOL_POS].sell(date, SHARES)

		fund_value = self.get_value(date)
		self.df_to_report.append([date, fund_value])

	def get_value(self, date):
		''' given date, get portfolio value '''
		global CASH
		equity_values = sum([i.get_value(date) for i in self.symbols])
		return (CASH + equity_values)

	def find_equity_by_name(self, name):
		''' return the index position of a equity from the given name '''
		equity_list = [i.get_name() for i in self.symbols]
		pos = np.nan
		for i in range(len(self.symbols)):
			if self.symbols[i].get_name() == name:
				pos = i 
				break
		return pos


if __name__ == "__main__":
	try:
		ORDERS = pd.read_csv('orders.csv', header = None, parse_dates = [0], index_col = 0,  names = [None, 'action', 'symbol', 'share'])
		ORDERS, order_timestamp = cleanDateAndSort(ORDERS)
		symbols = list(ORDERS['symbol'].unique())
		time_periods = get_NYSE_dates(order_timestamp)

		HIST = lookupSymbols(symbols, time_periods)
		My_portfolio = Portfolio(time_periods, ORDERS, symbols)
	except StopIteration:
		print "No Order was generated"

