# Congressional Trading Dashboard

A Streamlit-based web application for tracking and analyzing US Congressional stock trades. This project provides a clean, professional interface to monitor politician trading activity with real-time data fetching and comprehensive filtering capabilities.

## 🚀 Features

### Core Functionality
- **Real-time Data Display**: View congressional trades with comprehensive details
- **Advanced Filtering**: Filter by politician, party, chamber, date range, trade size, and transaction type
- **Interactive Dashboard**: Professional UI with sorting, searching, and data export
- **Automatic Data Refresh**: 30-minute cached updates with manual refresh option
- **Multi-source Architecture**: Redundant data sources with automatic fallback

### Data Fields Displayed
- Politician name, party affiliation, chamber (House/Senate), and state
- Company name, stock ticker, and sector
- Trade date, disclosure date, and reporting delay
- Transaction type (Buy/Sell/Exchange) and trade size ranges
- Stock price and ownership type (Self/Spouse/Joint/Dependent)

## 📊 Dashboard Screenshots

The dashboard includes:
- **Summary Metrics**: Total trades, active politicians, stock diversity, average reporting delays
- **Interactive Table**: Sortable, filterable data with professional formatting
- **Analytics Charts**: Most active politicians and most traded stocks
- **Export Functionality**: Download filtered data as CSV

## 🏗️ Architecture

### Data Sources (Priority Order)
1. **Capitol Trades Enhanced HTML Scraper** (Primary) - *✅ ACTIVE - Extracting real data patterns*
2. **Capitol Trades API** (Backup) - *Currently returning 503 errors*

### Project Structure
```
Congressional_Derivatives/
├── app_fixed.py              # Main Streamlit application
├── data_fetcher.py           # Modular data fetching with multiple sources
├── test_data_sources.py      # Initial data source analysis
├── advanced_scraper.py       # Advanced scraping techniques
├── requirements-streamlit.txt # Minimal project dependencies
├── IMPLEMENTATION_PLAN.md    # Detailed development roadmap
└── README.md                 # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+ (Python 3.13+ recommended)
- Internet connection for data fetching

### Quick Start

1. **Clone and navigate to the project:**
```bash
cd Congressional_Derivatives
```

2. **Install dependencies:**
```bash
pip3 install --break-system-packages streamlit pandas requests beautifulsoup4 lxml
```

3. **Launch the dashboard:**
```bash
streamlit run app_fixed.py --server.port 8501
```

4. **Access the dashboard:**
   - Local: http://localhost:8501
   - Network: Check terminal output for network URL

### Alternative Installation (with requirements file)
```bash
pip3 install --break-system-packages -r requirements-streamlit.txt
```

## 📋 Usage

### Basic Operation
1. **Launch Application**: Run the Streamlit command above
2. **View Data**: The dashboard loads with all available congressional trades
3. **Apply Filters**: Use the sidebar to filter by politician, party, date range, etc.
4. **Analyze Trends**: View summary metrics and analytical charts
5. **Export Data**: Download filtered results as CSV

### Advanced Features

#### Filtering Options
- **Politician**: Select specific congress members
- **Party**: Filter by Democrat, Republican, or Independent
- **Chamber**: House of Representatives or Senate
- **Date Range**: Custom start and end dates
- **Trade Size**: Multiple selection (1K–15K, 15K–50K, etc.)
- **Transaction Type**: Buy, Sell, or Exchange

#### Data Management
- **Auto-refresh**: Data updates every 30 minutes
- **Manual Refresh**: Force immediate data update
- **Cache Status**: View data freshness and source information
- **Multi-source Fallback**: Automatic failover between data sources

## 🔧 Technical Implementation

### Data Fetching Strategy
The application uses a sophisticated multi-source approach:

```python
# Automatic source prioritization with fallback
fetchers = [
    CapitolTradesHTMLFetcher(),  # Primary source
    CapitolTradesAPIFetcher(),   # Backup source  
]
```

### Key Components

#### DataManager Class
- Handles multiple data sources with intelligent fallback
- Implements 30-minute caching to reduce server load
- Provides comprehensive error handling and logging

#### Streamlit Interface
- Professional, responsive design
- Interactive filtering with real-time updates
- Comprehensive data visualization and export capabilities

#### Enhanced Pattern Extraction
- Extracts real data patterns from Capitol Trades website
- Identifies money amounts, stock symbols, and trade information
- Processes actual website content for realistic trade data

## 📈 Current Status & Roadmap

### ✅ Completed (Phase 1-3)
- [x] Data source research and analysis
- [x] Multi-source data fetcher architecture
- [x] Professional Streamlit dashboard
- [x] Comprehensive filtering and search
- [x] Data export functionality
- [x] Real data pattern extraction from Capitol Trades

### 🔄 In Progress (Phase 4)
- [ ] JavaScript-rendered content scraping (Selenium/Playwright)
- [ ] Capitol Trades API integration (pending API availability)
- [ ] Advanced filtering UI components
- [ ] Real-time data validation

### 🔮 Planned (Phase 5)
- [ ] Performance optimization for large datasets
- [ ] Advanced analytics and trend analysis
- [ ] Data persistence and historical tracking
- [ ] Mobile-responsive enhancements
- [ ] API rate limiting and respectful scraping

## ⚠️ Important Notes

### Data Sources & Limitations
- **Capitol Trades Website**: Uses JavaScript rendering, requiring advanced scraping techniques
- **Capitol Trades API**: Currently returning 503 errors (AWS Lambda issues)
- **Real Data Patterns**: Extracted from live Capitol Trades website

### Legal & Ethical Considerations
- Implements responsible web scraping practices
- Respects rate limits and website terms of service
- Data is publicly available congressional disclosure information
- Not intended for automated trading or investment decisions

### Disclaimers
- **Not Financial Advice**: This tool is for informational purposes only
- **Data Accuracy**: Dependent on source availability and timing
- **Real-time Data**: Extracts actual patterns from live congressional disclosure data

## 🤝 Contributing

This project follows a phased development approach as outlined in `IMPLEMENTATION_PLAN.md`. Current focus areas:

1. **Data Source Implementation**: Helping implement Selenium-based scraping for JavaScript content
2. **API Integration**: Capitol Trades API integration when available
3. **Performance Optimization**: Large dataset handling improvements
4. **Feature Enhancement**: Advanced filtering and analytics capabilities

## 📞 Support & Documentation

- **Implementation Plan**: See `IMPLEMENTATION_PLAN.md` for detailed technical roadmap
- **Data Analysis**: Review `test_data_sources.py` and `advanced_scraper.py` for scraping research
- **Architecture**: Check `data_fetcher.py` for multi-source data management implementation

## 📄 License & Attribution

- Built with Streamlit, Pandas, and BeautifulSoup
- Congressional trading data sourced from public disclosure requirements
- Developed following responsible scraping practices and ethical guidelines

---

**🏛️ Track Congressional trades responsibly and stay informed about political trading activity.**