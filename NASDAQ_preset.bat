REM PRESET EVENT_DEF 50
event_profiler.exe NASDAQ_100.csv
python Simulation.py --cash 500
python analyze.py