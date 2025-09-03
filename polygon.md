# Polygon.io Options Data Implementation Guide

A comprehensive planning document for implementing a complete options data fetching system using Polygon.io's API, designed for production deployment with 100 symbols daily.

## Executive Summary

Polygon.io provides enterprise-grade options data through REST APIs and WebSocket streams, processing approximately 3 terabytes of options data daily from all 17 U.S. options exchanges via direct OPRA connections. **For 100 symbols daily, the recommended approach is the Options Advanced tier ($199/month) for production deployment**, providing real-time data access with unlimited API calls and 5+ years of historical data.

The implementation requires a multi-service architecture with intelligent caching, robust error handling, and proper database design to handle the high-volume, time-sensitive nature of options data. Expected implementation timeline is 6-8 weeks with proper resource allocation.

## Current Polygon.io Options API Capabilities

### Complete API Endpoints Inventory

Polygon.io offers five primary endpoint categories for options data access:

**Reference and Contract Data**
- `GET /v3/reference/options/contracts` - All active and expired options contracts with filtering by ticker, type, expiration, and strike
- `GET /v3/reference/options/exchanges` - Complete list of 17 U.S. options exchanges

**Market Data Snapshots**  
- `GET /v3/snapshot/options/{underlyingAsset}` - **Complete options chain snapshot** with Greeks, implied volatility, quotes, and trades (up to 250 contracts per request)
- `GET /v3/snapshot/options/{underlyingAsset}/{optionContract}` - Single contract snapshot with break-even calculations
- `GET /v3/snapshot` - Unified multi-asset snapshots for cross-market analysis

**Historical Trade and Quote Data**
- `GET /v3/trades/{optionsTicker}` - Tick-level trade data with nanosecond precision (up to 50,000 records per request)
- `GET /v3/quotes/{optionsTicker}` - Historical bid/ask quotes with exchange attribution

**Aggregate Data (OHLC)**
- `GET /v2/aggs/ticker/{optionsTicker}/range/{multiplier}/{timespan}/{from}/{to}` - Custom timespan aggregates with volume and VWAP
- `GET /v1/open-close/{optionsTicker}/{date}` - Daily ticker summaries

### Authentication and Rate Limits

**Authentication Methods:**
- API Key via query parameter: `?apiKey=YOUR_API_KEY`
- Authorization header: `Authorization: Bearer YOUR_API_KEY`

**Critical Rate Limits:**
- **Free Tier**: 5 API requests per minute (insufficient for production)
- **Paid Tiers**: Unlimited API requests with soft limit of 100 requests/second
- **WebSocket Connections**: Up to 3 concurrent connections plus data expansions

### Subscription Tiers for Options Data

| Tier | Monthly Cost | Rate Limits | Historical Data | Real-time Access | Best Use Case |
|------|-------------|-------------|-----------------|------------------|---------------|
| Basic (Free) | $0 | 5 calls/minute | 2 years, EOD only | No | Development only |
| Starter | $29 | Unlimited | 2 years | 15-min delayed | Strategy backtesting |
| Advanced | **$199** | Unlimited | 5+ years | **Real-time** | **Production (100 symbols)** |
| Business | $1,999 | Unlimited | 20+ years | Real-time + SLA | Enterprise applications |

**Key Insight**: We will start with Basic and we will need to sleep 20 seconds after every call in order to not hit the rate limit.  We will also only be able to popuplate the table with new data at EOD.

## Technical Implementation Requirements

### API Request Patterns for Options Chains

**Recommended Implementation Pattern:**
```python
from polygon import RESTClient
import asyncio
from concurrent.futures import ThreadPoolExecutor

class OptionsDataFetcher:
    def __init__(self, api_key: str, max_workers: int = 5):
        self.client = RESTClient(api_key)
        self.rate_limiter = RateLimiter(max_requests=90, time_window=1)
        self.max_workers = max_workers
    
    async def fetch_multiple_chains(self, tickers: List[str]) -> Dict[str, Any]:
        """Fetch options chains for multiple tickers with rate limiting"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._fetch_single_chain, ticker): ticker 
                for ticker in tickers
            }
            
            results = {}
            for future in as_completed(futures):
                ticker = futures[future]
                try:
                    results[ticker] = future.result()
                except Exception as e:
                    print(f"Error fetching {ticker}: {e}")
                    results[ticker] = None
                    
        return results
```

### Symbol Format and Validation

**Polygon.io Options Symbol Format**: `O:SYMBOL[CORRECTION]YYMMDDCPPPPPPPPP`

**Components:**
- **O:** - Required prefix for API endpoints
- **SYMBOL** - Underlying ticker (AAPL, SPY)
- **YYMMDD** - Expiration date (250117 = January 17, 2025)
- **C/P** - Call or Put
- **PPPPPPPPP** - Strike price × 1000 (00250000 = $250.00)

**Examples:**
- `O:AAPL250117C00250000` = AAPL January 17, 2025 $250 Call
- `O:SPY240315P00400000` = SPY March 15, 2024 $400 Put

### Pagination and Bulk Data Retrieval

**Automatic Pagination with Official SDK:**
```python
def fetch_all_historical_data(ticker: str, start_date: str, end_date: str):
    """Fetch complete historical dataset with automatic pagination"""
    client = RESTClient(api_key)
    all_data = []
    
    # SDK handles pagination automatically with list_aggs
    for agg in client.list_aggs(
        ticker=ticker,
        multiplier=1,
        timespan="minute",
        from_=start_date,
        to=end_date,
        limit=50000  # Maximum per request
    ):
        all_data.append(agg)
        
    return all_data
```

### Error Handling and Rate Limit Management

**Production-Ready Error Handler:**
```python
class PolygonErrorHandler:
    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        
    def retry_with_backoff(self, func: Callable, *args, **kwargs) -> Optional[Any]:
        """Retry with exponential backoff for rate limits and server errors"""
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limited
                    wait_time = self._parse_rate_limit_headers(e.response)
                    time.sleep(wait_time or (self.backoff_factor * (2 ** attempt)))
                    
                elif e.response.status_code in [500, 502, 503, 504]:
                    # Server errors - retry with backoff
                    time.sleep(self.backoff_factor * (2 ** attempt))
                else:
                    # Client errors - don't retry
                    raise
```

### Intelligent Caching Strategy

**Market-Hours-Aware Caching:**
```python
class SmartOptionsCache:
    def get_cache_ttl(self, data_type: str, timestamp: datetime = None) -> int:
        """Dynamic TTL based on market conditions and data type"""
        is_market_open = self._is_market_open(timestamp or datetime.now())
        
        ttl_mapping = {
            "real_time_quotes": 30 if is_market_open else 3600,     # 30s/1h
            "options_chain": 60 if is_market_open else 1800,       # 1m/30m  
            "historical_data": 86400,                              # 24h
            "greeks": 300 if is_market_open else 1800,            # 5m/30m
        }
        
        return ttl_mapping.get(data_type, 3600)
```

## Options Data Structure and Fields

### Complete Options Data Schema

**Core Contract Details:**
```json
{
  "ticker": "O:AAPL250117C00250000",
  "underlying_ticker": "AAPL",
  "contract_type": "call|put",
  "exercise_style": "american|european",
  "expiration_date": "2025-01-17",
  "strike_price": 250.00,
  "shares_per_contract": 100
}
```

**Market Data and Analytics:**
```json
{
  "break_even_price": 252.06,
  "implied_volatility": 0.24132,
  "open_interest": 5823,
  "fmv": 2.15,
  
  "greeks": {
    "delta": 0.0998,
    "gamma": 0.0036,
    "theta": -0.0071,
    "vega": 0.3535
  },
  
  "day": {
    "open": 1.98,
    "high": 1.98, 
    "low": 1.95,
    "close": 1.95,
    "volume": 3,
    "vwap": 1.96
  }
}
```

**Real-time Quote Structure:**
```json
{
  "last_quote": {
    "bid": 1.90,
    "bid_size": 200,
    "ask": 2.22,
    "ask_size": 627,
    "midpoint": 2.06,
    "bid_exchange": 4,
    "ask_exchange": 4,
    "last_updated": 1675183059055012000
  }
}
```

### Historical Data Coverage

**Data Availability:**
- **Trades**: Historical data back to 2016 (8+ years)
- **Quotes**: Historical data back to 2022 (3+ years)
- **Aggregates**: 10+ years of OHLC data
- **Timestamps**: Unix nanosecond precision (UTC)
- **Volume**: ~3 terabytes processed daily across all exchanges

## Implementation Architecture Planning

### Recommended System Architecture

**Core Microservices Design:**

1. **Data Ingestion Service**
   - Handles all Polygon.io API connections
   - Manages rate limiting and error handling
   - WebSocket connections for real-time streams

2. **Data Processing Service**  
   - Calculates derived metrics and Greeks
   - Validates data quality and completeness
   - Handles corporate actions and adjustments

3. **Data Storage Service**
   - Time-series database for market data
   - Reference data management
   - Historical data archival

4. **API Gateway Service**
   - Exposes data to client applications
   - Authentication and authorization
   - Request routing and load balancing

5. **Notification Service**
   - Real-time alerts and updates
   - WebSocket connections to clients
   - Event-driven notifications

### Database Schema Recommendations

**Core Options Contracts Table:**
```sql
CREATE TABLE options_contracts (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(50) NOT NULL UNIQUE,
    underlying_ticker VARCHAR(20) NOT NULL,
    contract_type VARCHAR(4) NOT NULL,
    expiration_date DATE NOT NULL,
    strike_price DECIMAL(12,6) NOT NULL,
    shares_per_contract INTEGER DEFAULT 100,
    
    INDEX idx_underlying_exp (underlying_ticker, expiration_date),
    INDEX idx_strike_type (strike_price, contract_type)
);
```

**Time-Series Market Data Table:**
```sql
CREATE TABLE options_market_data (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(50) NOT NULL,
    timestamp_ns BIGINT NOT NULL,
    
    -- Pricing and Greeks
    implied_volatility DECIMAL(12,10),
    delta DECIMAL(12,10),
    gamma DECIMAL(12,10), 
    theta DECIMAL(12,10),
    vega DECIMAL(12,10),
    
    -- OHLCV Data
    open_price DECIMAL(12,6),
    high_price DECIMAL(12,6),
    low_price DECIMAL(12,6),
    close_price DECIMAL(12,6),
    volume INTEGER,
    
    INDEX idx_ticker_timestamp (ticker, timestamp_ns)
);
```



**Technical Excellence:**
- Implement comprehensive error handling with circuit breaker patterns
- Use intelligent caching to minimize API calls and improve performance
- Design for horizontal scalability from day one
- Maintain high code quality with proper testing coverage

