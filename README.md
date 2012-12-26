#YahooFinance
====================

1. python DataPull.py -p X -i Y
	* int X = integer yearly period.
			How many years of data from today
	* string Y = input file.
			Input File that contains symbols.
			Sample >> SP500.txt or NASDAQ_100.csv
	* It will automatically create YAHOO_DATA Folder

2. event_profiler.exe X Y
	* It will create orders.csv
	* string X = input file.
			Sample >> SP500.txt or NASDAQ_100.csv
	* float Y = event definition. Float.
			E.g.,> 5.0 it will create a order when price drop below $5.0 and sell after holding 5 days
3.	Simulation.py
	* it will read orders.csv and create a portfolio simulation and write to values.csv
4.	analyze.py
	* analyze values.csv, create graphs, and save results to /DATA_ANALYSIS/
