import urllib
import urllib2
import datetime
import os
from Tkinter import Tk
from tkSimpleDialog import askstring
import tkFileDialog
import argparse as arg

################### GLOBAL VARIABLES ###################
CURRENT_TIME = datetime.datetime.now()
TOTAL_COUNT = 0
ERROR_COUNT = 0
########################################################
################### ARGUMENTS PARSER ###################
################### IGNORE THIS ########################
parser = arg.ArgumentParser(description="Read SYMBOLS from .txt (DATA_SOURCE: YAHOO FINANCE)\n Set Optional Ending dates and adjust using by yearly period")
parser.add_argument("-y", "--year", type = int, default = CURRENT_TIME.year, help = "Ending Year" )
parser.add_argument("-m", "--month", type = int, default = CURRENT_TIME.month, help = "Ending Month")
parser.add_argument("-d", "--day", type = int, default = CURRENT_TIME.day, help = "Ending Day")
parser.add_argument("-i", "--input", type=str, default="DATAPULL_SYMBOL.txt", help="Text File that contains Symbols")
parser.add_argument("-b", "--benchmark", type = str, default = "SPY", help = "Benchmark[default: SPY]")
parser.add_argument("-t", "--tradingperiod", type=str, default="d", choices=["d", "w", "m"], help="Trading Period: w - weekly\nd - daily[default]\nm - monthly")
parser.add_argument("-p", "--yearly_period", type=int, default=1, help="Yearly Period.\nInteger, i years data from today\n (e.g, i == 1 => 1 year from today [default])")
parser.add_argument("-tk","--tkinter", default = False, action = "store_true", help = "Run as Tk mode")
args = parser.parse_args()
########################################################



########################################## OPTIONS #######################################
YEARLY_PERIOD = args.yearly_period
ENDING_DATES = [args.month, args.day, args.year]
STARTING_DATES = list(ENDING_DATES)
STARTING_DATES[2] = ENDING_DATES[2] - YEARLY_PERIOD
TRADING_PERIOD = args.tradingperiod # w: weekly, d: daily, m: monthly
DATA_PATH = "./YAHOO_DATA/" # Default folder to save
INPUT_FILE = args.input  # it will read symbols from this Text File
if args.tkinter:
	root = Tk()
	root.withdraw()
	INPUT_FILE = tkFileDialog.askopenfile(mode = "r", title = "Open a symbol txt File", filetypes = [("*.txt", "txt"), ("All", "*.*")])
	TRADING_PERIOD = int(askstring("Trading Period", "Enter trading years from today e.g 1"))
BENCH_MK = args.benchmark
##########################################################################################

def readSymbols(file, TK_MODE = False):
	''' read any file and return a list of symbols '''
	symbol_list = list()
	if not TK_MODE:
		file_to_read = open(file, "r")
	else:
		file_to_read = INPUT_FILE
	symbol_list = [symbol[:-1].replace(' ', '') if symbol.find("\n") != -1 else symbol.replace(' ','') for symbol in file_to_read.readlines()]
	symbol_list = filter(None, symbol_list)
	symbol_list.append(BENCH_MK)
	return symbol_list

def getPrices(symbolList, startingPeriod, endingPeriod, period_option = TRADING_PERIOD):
	for symbol in symbolList:
		getPrice(symbol, startingPeriod[0], startingPeriod[1], startingPeriod[2], ENDING_DATES[0], ENDING_DATES[1], ENDING_DATES[2], period_option)
	if ERROR_COUNT > 0:
		print "{:d} ERRORS WERE FOUND OUT OF {:d}".format(ERROR_COUNT, TOTAL_COUNT)
	else:
		print "SUCCESS! EVERY SYMBOL IS UPDATED OUT OF {:d}".format(TOTAL_COUNT)


def getPrice(symbol, init_month, init_day, init_year, end_month, end_day, end_year, t_period):
	""" Get Price Default: One Year from Current Time w/ Daily Ticks """
	global TOTAL_COUNT, ERROR_COUNT

	if not os.access(DATA_PATH, os.F_OK):
		os.makedirs(DATA_PATH)

	try:
		TOTAL_COUNT += 1
		if symbol[0] == "$": # Correct Index.
			symbol = symbol[1:]

		params = urllib.urlencode ({'a':init_month - 1, 'b':init_day, 'c':init_year, 'd':end_month - 1, 'e':end_day, 'f':end_year, 'g':t_period, 's':str(symbol), 'ignore':".csv"})
		DATA = urllib2.urlopen("http://ichart.finance.yahoo.com/table.csv?%s" % params)
		output = open(DATA_PATH + symbol + ".csv", "w")
		for line in DATA:
			output.write(line)
		output.close()
	except urllib2.URLError:
		print "SYMBOL: {:} is not found".format(symbol)
		ERROR_COUNT += 1


if __name__ == "__main__":
	symbols = readSymbols(INPUT_FILE, args.tkinter)
	getPrices(symbols, STARTING_DATES, ENDING_DATES)
