# Code Golf Version
The ECM1400 Coursework written using the fewest bytes possible. **Not intended to be marked**.
## Constraints
There must exist three files named `main.py`, `covid_data_handler.py` and `news_data_handling.py`. Each containing the functions in the specification, with the given parameter names. 

Testing, logging, configuration files and documentation is not included.
## Solution
### Overall - 2532 bytes, 15 lines
- **main.py** - 987 bytes/chars, 5 lines
- **covid_data_handler.py** - 919 bytes/chars, 5 lines
- **news_data_handling.py** - 626 bytes/chars, 5 lines
## Dependencies
- Python 3.9+
- Flask 2.0.2+
- requests 2.26.0+
- uk_covid19 1.2.2+
## Usage
- Copy the repository to a folder.
- Generate a [newsapi.org](https://newsapi.org/) key from [here](https://newsapi.org/register).
- Replace `"[API_KEY_HERE]"` in `news_data_handling.py` with your API key.
- Navigate to the folder in Command Prompt.
- Install the required dependencies.
- Ensure Python 3.9+ is used.
- Run `python main.py`.
- Open a web browser and navigate to [127.0.0.1:5000/](http://127.0.0.1:5000/)
## Explanation
An explanation of the tricks used to shorten the code is found in [explanation.md](explanation.md).
