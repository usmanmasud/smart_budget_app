# Smart Budget App 💰

A beginner-friendly budget tracking application built with Python and Streamlit that helps you manage your expenses with multi-currency support.

## Features ✨

- **Add Expenses**: Track your daily expenses with categories
- **Currency Conversion**: Convert your budget and expenses to different currencies
- **Visual Analytics**: See your spending patterns with charts
- **Budget Alerts**: Get warnings when you exceed your budget
- **Data Persistence**: All data is stored locally in SQLite database

## What You'll Learn 📚

This project demonstrates:
- **Web App Development** with Streamlit
- **Database Operations** with SQLite
- **API Integration** for currency conversion
- **Data Visualization** with charts
- **File Structure** organization

## Installation & Setup 🚀

### Prerequisites
- Python 3.7 or higher
- Internet connection (for currency conversion)

### Step 1: Clone or Download
Download this project to your computer.

### Step 2: Install Dependencies
Open terminal/command prompt in the project folder and run:
```bash
pip install -r requirements.txt
```

### Step 3: Run the App
```bash
streamlit run app.py
```

The app will open in your web browser at `http://localhost:8501`

## How to Use 📖

### Adding Expenses
1. Select the date of your expense
2. Enter the amount spent
3. Choose a category (Food, Transport, Rent, Bills, Other)
4. Add an optional note
5. Click "Add Expense"

### Currency Conversion
1. Select your preferred currency from the dropdown
2. Your budget and expenses will automatically convert
3. Rates are fetched in real-time from a free API

### Budget Tracking
1. Set your monthly budget in the "Budget Alert" section
2. The app will warn you if you exceed your budget
3. View spending summaries and charts

## Project Structure 📁

```
smart_budget_app/
├── app.py              # Main application file
├── utils.py            # Currency conversion utilities
├── database.db         # SQLite database (created automatically)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Code Explanation 🔍

### app.py
- **Database Setup**: Creates SQLite table for expenses
- **User Interface**: Streamlit components for input/output
- **Data Processing**: Handles expense calculations and summaries
- **Currency Integration**: Converts amounts using exchange rates

### utils.py
- **API Functions**: Fetches currency exchange rates
- **Conversion Logic**: Converts amounts between currencies
- **Error Handling**: Manages API failures gracefully

## API Used 🌐

This app uses the **ExchangeRate-API** (free tier):
- No API key required for basic usage
- Updates exchange rates daily
- Supports 160+ currencies
- Fallback to USD if API fails

## Customization Ideas 💡

**Beginner Level:**
- Add more expense categories
- Change the app colors/theme
- Add more chart types

**Intermediate Level:**
- Add expense editing/deletion
- Create monthly/yearly reports
- Add expense search functionality

**Advanced Level:**
- Add user authentication
- Create expense predictions
- Add receipt photo uploads

## Troubleshooting 🔧

**App won't start?**
- Check if Python is installed: `python --version`
- Install requirements: `pip install -r requirements.txt`

**Currency conversion not working?**
- Check internet connection
- App will use USD as fallback

**Database errors?**
- Delete `database.db` file and restart the app

## Learning Resources 📚

- [Streamlit Documentation](https://docs.streamlit.io/)
- [SQLite Tutorial](https://www.sqlitetutorial.net/)
- [Python Requests Library](https://requests.readthedocs.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## Contributing 🤝

This is a learning project! Feel free to:
- Add new features
- Fix bugs
- Improve documentation
- Share your improvements

## License 📄

This project is open source and available under the MIT License.

---

**Happy Budgeting! 🎉**

*Built with ❤️ for learning Python web development*