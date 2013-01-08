#include <iostream>
#include <algorithm>
#include <exception>
#include <fstream>
#include <vector>
#include <sstream>
#include <cstdlib>
using namespace std;

string delSpaces(string &str) {
   str.erase(std::remove(str.begin(), str.end(), ' '), str.end());
   return str;
}

template <class T>
void print_vector(T vec) {
	size_t sz = vec.size();
	for (int i = 0; i < sz; i++)
		cout << vec[i] << endl;
}

int find_a_letter(string str, char letter, int pos = 1) {
	int found = 0;
	while (pos > 0) {
		found = str.find(letter, found + 1);
		pos--;
	}
	return found;
}

class Equity {
	private:
		string name;
		vector<float> prices;
		vector<string> dates;
		string file_path;
	public:
		Equity(string str) {
			name = str;
			file_path = "./YAHOO_DATA/" + name + ".csv";
		}
		void open_and_save();
		vector<float> get_prices() {
			return prices;
		} 
		vector<string> get_dates() {
			return dates;
		} 

		string get_name() {
			return name;
		}
};

float string_to_float(string str) {
	float number;
	istringstream is(str);
	is >> number;
	return number;
}

void Equity::open_and_save() {
	// option(int) {0:actual_close, 1:close}
	// open filename and saves to prices and dates vectors.
	string print;
	ifstream csv_file(file_path.c_str(), ifstream::in);
	int line = 0;
	int pos_beg, pos_end, pos_date;
	if(csv_file.is_open()) {
		while(csv_file.good()) {
			getline(csv_file, print);
			if (line > 0) {
				pos_beg = find_a_letter(print, ',', 4);
				pos_end = find_a_letter(print, ',', 5);
				pos_date = print.find(',');
				if (pos_beg != string::npos && pos_end != string::npos && pos_date != string::npos) {
					dates.push_back(print.substr(0, pos_date));
					prices.push_back(string_to_float(print.substr(pos_beg+1, pos_end - pos_beg - 1).c_str()));
				}
			}
			line++;
		}
		csv_file.close();
	}
	else {
		cout << "Failed to open a file: " << file_path << endl;	
	}
}

void event_profiler_main(const vector<string> vec, string output, const float event_def) {
	int vs = vec.size();
	string name;
	vector<float> price;
	vector<string> date;
	ofstream of(output.c_str());
	if(of.is_open()) {
			for(int i = 0; i < vs; i++) {
					Equity sym(vec[i]);
					sym.open_and_save();
					price = sym.get_prices();
					date = sym.get_dates();
					name = sym.get_name();
					size_t sz = price.size();		
					for(int j = 1; j < sz; j++) {
						if (price[j - 1] < event_def && price[j] >= event_def) {
							cout << "EVENT FOUND: " << name << " DATES: " << date[j-1] << endl;
							of << date[j - 1] << ",Buy," << name << ",100\n";
							if (j - 6 >= 0) {
								of << date[j - 6] << ",Sell," << name << ",100\n";
							}
							else {
								cerr << "ENDING DATE EVENT! " << endl;
								of << date[0] << ",Sell," << name << ",100\n";
							}
						}
					}
				}
			of.close();
		}
	}


int main(int argc, char* argv[]) {

	bool argvs_flag = false;
	int pos;
	string line;
	vector<string> tickers;
	ifstream sym_list;
	string FILENAME;
	float eventDefinition;
	if (argc == 2) {
		FILENAME = argv[1];	
	}
	else if (argc == 3) {
		FILENAME = argv[1];
		eventDefinition = atof(argv[2]);
		argvs_flag = true;
	}
	else {
		cout << "FILENAME: ";
		cin >> FILENAME;
	}
	if (!argvs_flag) {
		cout << "Event Definition: ";
		cin >> eventDefinition;
	}
	sym_list.open(FILENAME.c_str());
	if(sym_list.is_open()) {
		while(sym_list.good()) {
			getline(sym_list, line);
			pos = line.find("\n");
			if(pos != string::npos)
				line = line.replace(14, 2, "");
			line = delSpaces(line);
			if (line.size() != 0)
				tickers.push_back(line);
		}
		sym_list.close();
		event_profiler_main(tickers, "orders.csv", eventDefinition);
	}
	return 0;
}