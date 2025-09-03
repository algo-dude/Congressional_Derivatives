#!/usr/bin/env python3
"""
Congressional Trading Dashboard - Streamlit App (Fixed Version)
Clean implementation using the modular data fetcher
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from data_fetcher import get_congressional_data, get_cache_info


# Page configuration
st.set_page_config(
    page_title="Congressional Trading Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def display_summary_metrics(df):
    """Display key summary metrics"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        recent_trades = len(df[df['disclosure_date'] >= cutoff_date])
        st.metric(
            label="Total Trades",
            value=len(df),
            delta=f"+{recent_trades} this month"
        )
    
    with col2:
        unique_politicians = df['politician_name'].nunique()
        st.metric(
            label="Active Politicians",
            value=unique_politicians
        )
    
    with col3:
        unique_stocks = df['ticker'].nunique()
        st.metric(
            label="Different Stocks",
            value=unique_stocks
        )
    
    with col4:
        if len(df) > 0:
            avg_delay = df['reporting_delay'].mean()
            st.metric(
                label="Avg Reporting Delay",
                value=f"{avg_delay:.0f} days"
            )
        else:
            st.metric(
                label="Avg Reporting Delay",
                value="N/A"
            )


def create_filters(df):
    """Create sidebar filters"""
    st.sidebar.header("🔍 Filter Trades")
    
    if df.empty:
        st.sidebar.warning("No data available for filtering")
        return {}
    
    # Politician filter
    politicians = ["All"] + sorted(df['politician_name'].unique().tolist())
    selected_politician = st.sidebar.selectbox("Select Politician", politicians)
    
    # Party filter
    parties = ["All"] + sorted(df['party'].unique().tolist())
    selected_party = st.sidebar.selectbox("Select Party", parties)
    
    # Chamber filter
    chambers = ["All"] + sorted(df['chamber'].unique().tolist())
    selected_chamber = st.sidebar.selectbox("Select Chamber", chambers)
    
    # Transaction type filter
    transaction_types = ["All"] + sorted(df['transaction_type'].unique().tolist())
    selected_transaction = st.sidebar.selectbox("Select Transaction Type", transaction_types)
    
    # Date range filter
    st.sidebar.subheader("Date Range")
    try:
        min_date = datetime.strptime(df['trade_date'].min(), '%Y-%m-%d').date()
        max_date = datetime.strptime(df['trade_date'].max(), '%Y-%m-%d').date()
        
        start_date = st.sidebar.date_input("From", min_date, min_value=min_date, max_value=max_date)
        end_date = st.sidebar.date_input("To", max_date, min_value=min_date, max_value=max_date)
    except:
        start_date = datetime.now().date()
        end_date = datetime.now().date()
    
    # Trade size filter
    trade_sizes = sorted(df['trade_size'].unique().tolist())
    selected_trade_sizes = st.sidebar.multiselect("Select Trade Sizes", trade_sizes, default=trade_sizes)
    
    return {
        'politician': selected_politician,
        'party': selected_party,
        'chamber': selected_chamber,
        'transaction': selected_transaction,
        'start_date': start_date,
        'end_date': end_date,
        'trade_sizes': selected_trade_sizes
    }


def apply_filters(df, filters):
    """Apply filters to the dataframe"""
    if df.empty or not filters:
        return df
    
    filtered_df = df.copy()
    
    if filters.get('politician', 'All') != "All":
        filtered_df = filtered_df[filtered_df['politician_name'] == filters['politician']]
    
    if filters.get('party', 'All') != "All":
        filtered_df = filtered_df[filtered_df['party'] == filters['party']]
    
    if filters.get('chamber', 'All') != "All":
        filtered_df = filtered_df[filtered_df['chamber'] == filters['chamber']]
    
    if filters.get('transaction', 'All') != "All":
        filtered_df = filtered_df[filtered_df['transaction_type'] == filters['transaction']]
    
    # Date filter
    if 'start_date' in filters and 'end_date' in filters:
        filtered_df = filtered_df[
            (pd.to_datetime(filtered_df['trade_date']).dt.date >= filters['start_date']) &
            (pd.to_datetime(filtered_df['trade_date']).dt.date <= filters['end_date'])
        ]
    
    # Trade size filter
    if filters.get('trade_sizes'):
        filtered_df = filtered_df[filtered_df['trade_size'].isin(filters['trade_sizes'])]
    
    return filtered_df


def main():
    """Main Streamlit application"""
    
    # Header
    st.title("🏛️ Congressional Trading Dashboard")
    st.markdown("### Track US Politician Stock Trades")
    
    # Load data
    with st.spinner("Loading congressional trade data..."):
        df, data_source = get_congressional_data()
        cache_info = get_cache_info()
    
    # Display data source and status
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"**Data Source**: {data_source}")
    with col2:
        if cache_info.get('last_updated'):
            st.markdown(f"**Last Updated**: {cache_info['last_updated']}")
    with col3:
        if st.button("🔄 Refresh Data"):
            df, data_source = get_congressional_data(force_refresh=True)
            st.rerun()
    
    # Check if we have data
    if df.empty:
        st.error("No congressional trading data available. Please check your data sources.")
        st.markdown("### Troubleshooting")
        st.markdown("""
        1. **Capitol Trades Website**: May be using JavaScript rendering
        2. **Capitol Trades API**: Currently returning 503 errors
        
        Please check the data fetcher configuration or contact support.
        """)
        return
    
    # Create filters
    filters = create_filters(df)
    
    # Apply filters
    filtered_df = apply_filters(df, filters)
    
    # Display summary metrics
    st.subheader("📊 Summary Metrics")
    display_summary_metrics(filtered_df)
    
    st.markdown("---")
    
    # Main data table
    st.subheader("📋 Congressional Trades")
    
    if len(filtered_df) > 0:
        # Display count
        st.markdown(f"**Showing {len(filtered_df):,} of {len(df):,} total trades**")
        
        # Configure display columns and formatting
        display_columns = [
            'politician_name', 'party', 'chamber', 'state',
            'company', 'ticker', 'sector', 'transaction_type',
            'trade_size', 'price', 'trade_date', 'disclosure_date',
            'reporting_delay', 'owner'
        ]
        
        # Column configuration for better display
        column_config = {
            'politician_name': st.column_config.TextColumn('Politician', width="medium"),
            'party': st.column_config.TextColumn('Party', width="small"),
            'chamber': st.column_config.TextColumn('Chamber', width="small"),
            'state': st.column_config.TextColumn('State', width="small"),
            'company': st.column_config.TextColumn('Company', width="large"),
            'ticker': st.column_config.TextColumn('Ticker', width="small"),
            'sector': st.column_config.TextColumn('Sector', width="medium"),
            'transaction_type': st.column_config.TextColumn('Type', width="small"),
            'trade_size': st.column_config.TextColumn('Trade Size', width="small"),
            'price': st.column_config.TextColumn('Price', width="small"),
            'trade_date': st.column_config.DateColumn('Trade Date', width="medium"),
            'disclosure_date': st.column_config.DateColumn('Disclosure Date', width="medium"),
            'reporting_delay': st.column_config.NumberColumn('Delay (days)', width="small"),
            'owner': st.column_config.TextColumn('Owner', width="small"),
        }
        
        # Display the dataframe with better formatting
        st.dataframe(
            filtered_df[display_columns],
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Download button
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv_data,
            file_name=f"congressional_trades_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
        
    else:
        st.warning("No trades found matching your current filters. Try adjusting your selection.")
    
    # Additional analysis (if we have data)
    if len(filtered_df) > 0:
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔝 Most Active Politicians")
            politician_counts = filtered_df['politician_name'].value_counts().head(10)
            if len(politician_counts) > 0:
                st.bar_chart(politician_counts)
            else:
                st.info("No politician data to display")
        
        with col2:
            st.subheader("📈 Most Traded Stocks")
            stock_counts = filtered_df['ticker'].value_counts().head(10)
            if len(stock_counts) > 0:
                st.bar_chart(stock_counts)
            else:
                st.info("No stock data to display")
        
        # Party breakdown
        st.subheader("🎯 Trade Distribution by Party")
        party_breakdown = filtered_df['party'].value_counts()
        if len(party_breakdown) > 0:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.bar_chart(party_breakdown)
            with col2:
                st.dataframe(party_breakdown.reset_index().rename(columns={'index': 'Party', 'party': 'Trades'}))
    
    # Cache status
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Cache Status")
    if cache_info:
        for key, value in cache_info.items():
            if key != 'last_updated':  # Already shown in header
                st.sidebar.text(f"{key.replace('_', ' ').title()}: {value}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **🔧 Technical Details**  
    - **Data Sources**: Capitol Trades HTML scraper and API  
    - **Update Frequency**: Every 30 minutes (cached)  
    - **Architecture**: Modular with automatic fallback between sources  
    
    **⚠️ Important Disclaimers**  
    - This tool is for informational and educational purposes only  
    - Not financial or investment advice  
    - Data accuracy depends on source availability and disclosure timing
    """)


if __name__ == "__main__":
    main()