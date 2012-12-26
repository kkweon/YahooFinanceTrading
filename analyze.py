import argparse as arg
import numpy as np
import pandas as pd
import datetime as dt
import os
import matplotlib.dates as dates
from pylab import *

############################################################
#				GLOBAL DECLARATION BEGINS HERE
############################################################
parser = arg.ArgumentParser(description = 'Analyze the portfolio comparing with Benchmark')
parser.add_argument('-b', "--benchmark", type = str, default = "SPY", help = "BENCHMARK; DEFAULT: SPY")
parser.add_argument("-i", "--input", type = str, default = "values.csv", help = "Input CSV; DEFAULT: values.csv")
parser.add_argument("-t", "--type", type = str, default = "Adj Close", choices = ['Close', 'Adj Close', 'Volume'], help = "PRICE TYPE: DEFAULT: Adj Close")
parser.add_argument('-o', "--output", type = str, default = 'performance.png', help = "PNG Image file, default: Performance.png")
parser.add_argument('-d', '--debug', default = False, action = "store_true", help = "DEBUG MODE")
parser.add_argument('-f', '--fontsize', type = str, default = 'larger', choices = ['small', 'medium', 'xx-large', 'x-large', 'large', 'larger', 'smaller'], help = "FONT SIZE")
args = parser.parse_args()

############################################################
#						OPTION	
############################################################
INPUT = args.input
BENCHMARK = args.benchmark
DATA_SOURCE = "./YAHOO_DATA/"
PRICE_TYPE = args.type # actual_close, volume, close, etc.
FONT_SIZE = args.fontsize # for plotting
OUTPUT = args.output
OUTPUT2 = "scatter_plot.png"
OUTPUT_FOLDER = "./DATA_ANALYSIS/"
DPI = 300
if not os.access(OUTPUT_FOLDER, os.F_OK):
		os.makedirs(OUTPUT_FOLDER)
DEBUG = args.debug
############################################################
#					OPTION	END
############################################################

print "INPUT> {:}".format(INPUT)
print "OUTPUT> {:}".format(OUTPUT)
print "BENCHMARK> {:}".format(BENCHMARK)
print "FONT SIZE> {:}".format(FONT_SIZE)

############################################################
#				GLOBAL DECLARATION ENDS HERE
############################################################

############################################################
#						HELPER FUNCTIONS 
############################################################
def rstyle(ax): 
    """Styles an axes to appear like ggplot2
    Must be called after all plot and axis manipulation operations have been carried out (needs to know final tick spacing)
    """
    #set the style of the major and minor grid lines, filled blocks
    ax.grid(True, 'major', color='w', linestyle='-', linewidth=1.4)
    ax.grid(True, 'minor', color='0.92', linestyle='-', linewidth=0.7)
    ax.patch.set_facecolor('0.85')
    ax.set_axisbelow(True)
    
    #set minor tick spacing to 1/2 of the major ticks
    ax.xaxis.set_minor_locator(MultipleLocator( (plt.xticks()[0][1]-plt.xticks()[0][0]) / 2.0 ))
    ax.yaxis.set_minor_locator(MultipleLocator( (plt.yticks()[0][1]-plt.yticks()[0][0]) / 2.0 ))
    
    #remove axis border
    for child in ax.get_children():
        if isinstance(child, matplotlib.spines.Spine):
            child.set_alpha(0)
       
    #restyle the tick lines
    for line in ax.get_xticklines() + ax.get_yticklines():
        line.set_markersize(5)
        line.set_color("gray")
        line.set_markeredgewidth(1.4)
    
    #remove the minor tick lines    
    for line in ax.xaxis.get_ticklines(minor=True) + ax.yaxis.get_ticklines(minor=True):
        line.set_markersize(0)
    
    #only show bottom left ticks, pointing out of axis
    rcParams['xtick.direction'] = 'out'
    rcParams['ytick.direction'] = 'out'
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    
    
    if ax.legend_ <> None:
        lg = ax.legend_
        lg.get_frame().set_linewidth(0)
        lg.get_frame().set_alpha(0.5)
        
def get_date_index(dataframe):
	''' Dataframe must have Year, Month, Day, Value Columns '''
	dataframe.index = [dt.datetime(dataframe['Year'][i], dataframe['Month'][i], dataframe['Day'][i]) for i in range(len(dataframe))]
	del dataframe['Year'], dataframe['Month'], dataframe['Day']
	dataframe['Value'] = dataframe['Value'].astype('float64')
	return dataframe.copy() 

def normalize(dataframe, cash = 1):
	''' return a normalized dataframe and multiply by cash (initial investment) '''
	for column in dataframe.columns:
		dataframe[column] = [float(dataframe[column][i]) / float(dataframe[column][0]) * float(cash) for i in range(len(dataframe))]
	return dataframe.copy()

def combine_DF(dataframe1, dataframe2, p_type):
	''' combine two dataframes '''
	for column in dataframe2.columns:
		if column == p_type:
			dataframe1[column] = dataframe2[column]
	return dataframe1.copy()

def pretty_print(total_return, standard_deviation, sharpe_ratios, save_log = "Summary.txt"):
	''' first row: my_data, second row: benchmark '''
	summary_file = open(OUTPUT_FOLDER + save_log, "w")
	print '{:*<50}'.format('')
	print '{:^50}'.format('SUMMARY')
	summary_file.write("SUMMARY\n")
	print '{:*<50}'.format('')
	print '{:<50}'.format('\t\t\tMY PORTFOLIO\tBENCHMARK')
	print '{:*<50}'.format('')
	print "[SHARPE RATIO]\t\t  {: .3f}	{: .3f}".format(sharpe_ratios[0], sharpe_ratios[1])
	summary_file.write("[SHARPE RATIO]\t\t  {: .3f}	{: .3f}\n".format(sharpe_ratios[0], sharpe_ratios[1]))
	print "[TOTAL RETURN]\t\t  {: .2%}	{: .2%}".format(total_return[0], total_return[1])
	summary_file.write("[TOTAL RETURN]\t\t  {: .2%}	{: .2%}\n".format(total_return[0], total_return[1]))
	print "[STD OF DAILY RETURN]\t  {: .3f}	{: .3f}".format(standard_deviation[0], standard_deviation[1])
	summary_file.write("[STD OF DAILY RETURN]\t  {: .3f}	{: .3f}\n".format(standard_deviation[0], standard_deviation[1]))
	print '{:*<50}'.format('')
	summary_file.close()
	
############################################################
#						HELPER ENDS 
############################################################

# MAIN BEGINS #
MY_PORTFOLIO = pd.read_csv(INPUT, header = None, names = ['Year', 'Month', 'Day', 'Value']) 
MY_PORTFOLIO = get_date_index(MY_PORTFOLIO)

# READ BENCHMARK
BENCHMARK_DATA = pd.read_csv(DATA_SOURCE + BENCHMARK + ".csv", header = 0, index_col = 0, parse_dates = [0])
if DEBUG:
	print BENCHMARK_DATA

# COMBINE MY PORTFOLIO + BENCHMARK_DATA and NORMALIZE
NEW_DATA = combine_DF(MY_PORTFOLIO, BENCHMARK_DATA, PRICE_TYPE)
NORMALIZED_DATA = normalize(NEW_DATA, MY_PORTFOLIO['Value'][0])
if DEBUG:
	print NEW_DATA

# Calculate Daily Returns, its means, and its STD
# first row = MY_PORTFOLIO, second row = BENCHMARK
DAILY_RET = NEW_DATA.pct_change()
MEAN_DAILY_RET = DAILY_RET.mean()
if DEBUG:
	print "MEAN", MEAN_DAILY_RET
STD = DAILY_RET.std()
if DEBUG:
	print "STD", STD
SHARPE_R = MEAN_DAILY_RET / STD * float(len(NEW_DATA)) ** 0.5
if DEBUG:
	print "SHARPE RATIO", SHARPE_R
TOTAL_RETURN = NEW_DATA.ix[-1] / NEW_DATA.ix[0] - 1
if DEBUG:
	print "TOTAL RETURN", TOTAL_RETURN
# CALCULATION ENDS ABOVE 

# PRINT OUTPUT
pretty_print(TOTAL_RETURN, STD, SHARPE_R)

# PLOTTING BEGINS
fig = figure()
ax = fig.add_subplot(111) 
NORMALIZED_DATA.plot(style = '-', ax = ax, rot = 30, grid = True)
ax.axhline(y = NORMALIZED_DATA.ix[0, 'Value'], color = 'r', ls = '--')
fill_between(NORMALIZED_DATA.index, NORMALIZED_DATA.ix[0, 'Value'], NORMALIZED_DATA['Value'].values, where = NORMALIZED_DATA['Value'].values < NORMALIZED_DATA.ix[0, 'Value'], color = "red", alpha = 0.3)
fill_between(NORMALIZED_DATA.index, NORMALIZED_DATA[PRICE_TYPE].values, NORMALIZED_DATA['Value'].values, where = NORMALIZED_DATA['Value'].values > NORMALIZED_DATA[PRICE_TYPE].values, color = "yellow", alpha = 0.3)
legend(['MY PORTFOLIO', BENCHMARK], loc = 0)
ylabel('USD, $', fontsize = FONT_SIZE)
xlabel('Daily', fontsize = FONT_SIZE)
title('Normalized Prices', fontsize = FONT_SIZE)
fig.autofmt_xdate()
rstyle(ax)
savefig(OUTPUT_FOLDER + OUTPUT, dpi = DPI)
print "FILE SAVED {:=<20}> [{:}]".format('', OUTPUT)



clf()
ax = fig.add_subplot(111)
scatter(NORMALIZED_DATA[PRICE_TYPE], NORMALIZED_DATA['Value'], s = 40, c = "blue", marker = "*", linewidth = 0)
xlabel(BENCHMARK + " PRICE", fontsize = FONT_SIZE)
grid()
ylabel("My Portfolio", fontsize = FONT_SIZE)
title("Scatter Plot: My portfolio vs " + BENCHMARK, fontsize = FONT_SIZE)
rstyle(ax)
savefig(OUTPUT_FOLDER + OUTPUT2, dpi = DPI)
