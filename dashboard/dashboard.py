"""Import libraries"""
import os
import pandas as pd
import streamlit as st
import altair as alt
import redshift_connector
import logging
from dotenv import load_dotenv


COLOUR_CARD = "#1f77b4"
COLOUR_CASH = "#B3E5FC"

st.markdown(
    """
    <style>
        .stApp {
            font-family: Arial, sans-serif;
            color: #333;
            background-color: #f8f9fa;
        }
        .stSidebar {
            background-color: #f1f3f5;
        }
        .stButton>button {
            background-color: #ADD8E6;
            color: white;
        }
        .stSidebar, .stTitle {
            padding: 10px;
            font-size: 16px;
        }
    </style>
    """, unsafe_allow_html=True
)


def get_redshift_connection():
    """Establish and return a connection to the Redshift database."""
    try:
        conn = redshift_connector.connect(
            host=os.environ["HOST"],
            port=int(os.environ.get("PORT", 5439)),
            user=os.environ["USERNAME"],
            password=os.environ["PASSWORD"],
            database=os.environ["DATABASE_NAME"]
        )
        conn.autocommit = True
        logging.info("Connected to Redshift.")
        return conn
    except Exception as e:
        logging.error("Error connecting to Redshift: %s", str(e))
        raise


def load_data_from_redshift():
    """Loads the data from redshift."""
    query = """
    SELECT 
        truck_id,
        payment_method_id,
        total,
        at AS timestamp
    FROM 
        ellie_bradley_schema.FACT_Transaction;
    """
    try:
        conn = get_redshift_connection()
        df = pd.read_sql(query, conn)
    finally:
        conn.close()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def home_page():
    """Page title and description."""
    st.title("T3 Food Trucks Dashboard")
    st.markdown(
        "### An interactive dashboard to explore T3’s transaction data and monitor truck performance.")


def render_sidebar_filters(df):
    """Renders the sidebar filters for the data."""
    st.sidebar.header("Filter Options")
    start_date = st.sidebar.date_input(
        "Start date", df['timestamp'].min().date())
    end_date = st.sidebar.date_input("End date", df['timestamp'].max().date())
    truck_filter = st.sidebar.multiselect(
        "Select trucks", df['truck_id'].unique())
    payment_filter = st.sidebar.radio(
        "Select payment type", ("All", "Card", "Cash"))
    return start_date, end_date, truck_filter, payment_filter


def apply_filters(df, start_date, end_date, truck_filter, payment_filter):
    """Apply filters to graphs."""
    filtered_data = df[(df['timestamp'].dt.date >= start_date)
                       & (df['timestamp'].dt.date <= end_date)]
    if truck_filter:
        filtered_data = filtered_data[filtered_data['truck_id'].isin(
            truck_filter)]
    if payment_filter != "All":
        payment_id = 1 if payment_filter == "Card" else 2
        filtered_data = filtered_data[filtered_data['payment_method_id'] == payment_id]
    return filtered_data


def plot_total_revenue_by_truck(filtered_data):
    """A bar chart of the total revenue for each truck."""
    st.subheader("Total Revenue by Truck")
    revenue_by_truck = filtered_data.groupby(
        'truck_id')['total'].sum().reset_index()
    chart = alt.Chart(revenue_by_truck).mark_bar(color=COLOUR_CARD).encode(
        x=alt.X('truck_id:O', title='Truck ID'),
        y=alt.Y('total:Q', title='Total Revenue (£)')
    )
    st.altair_chart(chart, use_container_width=True)


def plot_average_transaction_value(filtered_data):
    """A bar chart to show the average transaction value per truck."""
    st.subheader("Average Transaction Value by Truck")
    avg_transaction = filtered_data.groupby(
        'truck_id')['total'].mean().reset_index()
    chart = alt.Chart(avg_transaction).mark_bar(color=COLOUR_CARD).encode(
        x=alt.X('truck_id:O', title='Truck ID'),
        y=alt.Y('total:Q', title='Average Transaction Value (£)')
    )
    st.altair_chart(chart, use_container_width=True)


def plot_revenue_trends(filtered_data):
    """A line graph to show the revenue trends by date."""
    st.subheader("Revenue Trends by Date")
    revenue_trends = filtered_data.groupby(
        [filtered_data['timestamp'].dt.date, 'truck_id'])['total'].sum().reset_index()
    revenue_trends.columns = ['date', 'truck_id', 'total_revenue']
    chart = alt.Chart(revenue_trends).mark_line(color=COLOUR_CARD).encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('total_revenue:Q', title='Total Revenue'),
        tooltip=['date:T', 'total_revenue:Q', 'truck_id:N']
    ).properties(width=600, height=400)
    st.altair_chart(chart, use_container_width=True)


def plot_transaction_volume_by_hour(filtered_data):
    """A bar chart to show the peak transaction times. """
    st.subheader("Peak Transaction Times")
    filtered_data['hour'] = filtered_data['timestamp'].dt.hour
    transactions_by_hour = filtered_data.groupby(
        'hour').size().reset_index(name='count')
    chart = alt.Chart(transactions_by_hour).mark_line(color=COLOUR_CARD).encode(
        x=alt.X('hour:O', title='Hour of Day'),
        y=alt.Y('count:Q', title='Transaction Volume')
    )
    st.altair_chart(chart, use_container_width=True)


def plot_payment_method_distribution(filtered_data):
    """Create a pie chart of cash vs card payment options."""
    st.subheader("Payment Method Distribution")
    payment_dist = filtered_data['payment_method_id'].value_counts(
        normalize=True).reset_index()
    payment_dist.columns = ['payment_method', 'proportion']
    payment_dist['payment_method'] = payment_dist['payment_method'].replace({
                                                                            1: 'Card', 2: 'Cash'})

    pie_chart = alt.Chart(payment_dist).mark_arc(innerRadius=50).encode(
        theta=alt.Theta('proportion:Q', title=""),
        color=alt.Color('payment_method:N', scale=alt.Scale(
            domain=['Card', 'Cash'], range=[COLOUR_CARD, COLOUR_CASH]), legend=None),
        tooltip=['payment_method', alt.Tooltip('proportion:Q', format=".2%")]
    ).properties(width=300, height=300)
    st.altair_chart(pie_chart, use_container_width=True)


def plot_card_cash_count(filtered_data):
    """Create a bar chart of cash vs card payment options."""
    st.subheader("Count of Card vs Cash Transactions")
    payment_count = filtered_data['payment_method_id'].value_counts(
    ).reset_index()
    payment_count.columns = ['payment_method', 'count']
    payment_count['payment_method'] = payment_count['payment_method'].replace({
                                                                              1: 'Card', 2: 'Cash'})

    bar_chart = alt.Chart(payment_count).mark_bar().encode(
        x=alt.X('payment_method:N', title='Payment Method'),
        y=alt.Y('count:Q', title='Transaction Count'),
        color=alt.Color('payment_method:N', scale=alt.Scale(
            domain=['Card', 'Cash'], range=[COLOUR_CARD, COLOUR_CASH])),
        tooltip=['payment_method', 'count']
    ).properties(width=300, height=300)
    st.altair_chart(bar_chart, use_container_width=True)


def main():
    """Main function for the dashboard."""
    truck_data = load_data_from_redshift()
    home_page()
    start_date, end_date, truck_filter, payment_filter = render_sidebar_filters(
        truck_data)
    filtered_data = apply_filters(
        truck_data, start_date, end_date, truck_filter, payment_filter)

    plot_total_revenue_by_truck(filtered_data)
    plot_average_transaction_value(filtered_data)
    plot_revenue_trends(filtered_data)
    plot_transaction_volume_by_hour(filtered_data)
    plot_payment_method_distribution(filtered_data)
    plot_card_cash_count(filtered_data)


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.WARNING)
    load_dotenv()
    main()
