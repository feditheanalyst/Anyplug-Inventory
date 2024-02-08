import random
import json
import calendar
from datetime import datetime 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import streamlit as st
from streamlit_option_menu import option_menu
# from streamlit_gsheets import GSheetsConnection
# import gspread
import toml
# import pygsheets
import mysql.connector
import plotly.graph_objects as go
import plotly.express as px
# from st_supabase_connection import SupabaseConnection
# from supabase import create_client, Client
from prophet import Prophet 
from prophet.plot import plot_plotly, plot_components_plotly 
import sqlite3

#Header
pagetitle = "AnyPlug Gadget Inventory Management System"
currency = "₦"
lay_out = "centered"

# page configuration
st.set_page_config(page_title = pagetitle, layout = "wide")
st.title(pagetitle)

selected = option_menu(
    menu_title = None,
    options = ["Data Entry", "Analytics", "Forecast"],
    icons = ["pencil-fill", "bar-chart-fill", "graph-up"],
    orientation = "horizontal"
)

hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html = True)

# Initialize connection.
# supabase_conn = st.connection("supabase", type=SupabaseConnection)
# # Fetch data from Supabase (replace with your actual table name)
# data = supabase_conn.client.table("anyplug").select("*").execute()
# df = pd.DataFrame(data.data)  # Convert Supabase response to DataFrame

# Connect to SQLite database (create it if it doesn't exist)
conn = sqlite3.connect('anyplug.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS gadget (
        customer_id INTEGER PRIMARY KEY,
        customer_email TEXT,
        customer_phone INTEGER,
        product_name TEXT,
        product_description TEXT,
        initial_price INTEGER,
        amount_sold INTEGER,
        discount INTEGER,
        stock_quantity INTEGER,
        order_id INTEGER,
        order_date DATE,
        state TEXT,
        country TEXT,
        payment_method TEXT
    )
''')

if selected == "Data Entry":
    # File uploader
    uploaded_file = st.file_uploader('Upload a CSV file', type=['csv'])
    # Check if a file has been uploaded
    if uploaded_file is not None:
        # Read the dataset
        df = pd.read_csv(uploaded_file)
        #  Display the dataset
        st.subheader('Uploaded Dataset')
        st.write(df)
    else:
        st.info('Please upload a CSV file.')
    # Create two columns for layout
    col1, col2= st.columns(2)

    # Column 1: Customer information
    with col1:
        customer_id = st.text_input('CustomerId', value=str(random.randint(1000, 9999)))
        customer_email = st.text_input('CustomerEmail')
        customer_phone = st.text_input('CustomerPhoneNumber')
        product_name = st.text_input('ProductName')
        product_description = st.text_input('Description')
        state = st.text_input('State')
        payment_method_options = ['Credit Card', 'Debit Card', 'Cash', 'Bank Transfer']
        payment_method = st.selectbox('PaymentMethod', options=payment_method_options, index = None, placeholder= "Please select the payment method")

    with col2:   
        # Randomly generate OrderId
        order_id = st.text_input('OrderId', value=str(random.randint(1000, 9999)))
        initial_price = st.number_input('InitialPrice', step=1) 
        amount_sold = st.number_input('AmountSold', step=1)
        discount = st.number_input('Discount', step=1)
        stock_quantity = st.number_input('StockQuantity', step=1)
        country = st.text_input('Country')
        order_date = st.date_input('OrderDate')
    # submit button
    with st.form(key='my_form'):    
        submitted = st.form_submit_button("Save Data")

    if submitted:
        cursor.execute('''
            INSERT INTO gadget (
                customer_id, customer_email, customer_phone, product_name,
                product_description, state, payment_method, order_id,
                initial_price, amount_sold, discount, stock_quantity,
                country, order_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            int(customer_id), customer_email, customer_phone, product_name,
            product_description, state, payment_method, int(order_id),
            int(initial_price), int(amount_sold), int(discount),
            int(stock_quantity), country, str(order_date)
        ))

        # Commit changes and close connection
        conn.commit()
        # conn.close()
        st.write("Data Saved")

elif selected == "Analytics":
    # Read data from SQLite database
    cursor.execute('SELECT * FROM gadget')
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df1 = pd.DataFrame(data, columns=columns)
    # Convert 'order_date' to datetime type (if applicable)
    if 'order_date' in df1.columns:
        df1['order_date'] = pd.to_datetime(df1['order_date'])

    # Create side-by-side layout for month and year slicers
    col1, col2 = st.columns(2)
    # Create a month slicer
    months = ['All', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    with col1:
        selected_month = st.selectbox('Select Month', months, index=0)

    # Create a year slicer
    years = ['All'] + list(df1['order_date'].dt.year.unique())
    with col2:
        selected_year = st.selectbox('Select Year', years, index=0)
 
    # Filter the DataFrame based on user selection
    if selected_month != 'All':
        month_index = months.index(selected_month)
        df1 = df1[df1['order_date'].dt.month == month_index]
    if selected_year != 'All':
        df1 = df1[df1['order_date'].dt.year == selected_year]

    # KPI's
    TotalSales = df1["amount_sold"].sum()
    TotalDiscount = df1["discount"].sum()
    AverageSales = int(df1["amount_sold"].sum())
    TotalStock = df1["stock_quantity"].sum()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sales", f"{currency}{TotalSales}")
    col2.metric("Total Stock", f"{currency}{TotalStock}")
    col3.metric("Average Sales", f"{currency}{AverageSales}")
    col4.metric("Total Discount", f"{currency}{TotalDiscount}")

    # --------------first chart-----------------
    # Sort the DataFrame by 'amount_sold' in descending order
    df2 = df1.sort_values(by='amount_sold', ascending=False)

    # Select the top 5 products
    top_5_products = df2.iloc[:5, :]  # Get the first 5 rows

    # Plotting the barchart
    fig = px.bar(top_5_products, x='product_name', y='amount_sold', title='Product Sales Analysis',
             labels={'amount_sold': 'Total Amount Sold'},
             color='product_name',  # Add color for each product if needed
             height=500)
    # Update layout for better readability
    fig.update_layout(xaxis_title='Product Name', yaxis_title='Total Amount Sold')


    # --------------second chart-----------------
    # Select the top 5 states
    top_5_states = df2.iloc[:5, :]  # Get the first 5 rows
    # Plotting the barchart
    fig1 = px.bar(top_5_states, x='state', y='amount_sold', title='Sales Analysis Across States',
             labels={'amount_sold': 'Total Amount Sold'},
             color='state',
             height=500)
    # Update layout for better readability
    fig1.update_layout(xaxis_title='Product Name', yaxis_title='Total Amount Sold')


    # --------------third chart-----------------
    # Group data by date, calculating total sales and total discount
    grouped_data = df1.groupby('order_date')[['amount_sold', 'discount']].sum()
    # Create a line chart with two lines, one for each metric
    fig2 = px.line(
        grouped_data,
        x=grouped_data.index,
        y=['amount_sold', 'discount'],  # Include both metrics
        title='Total Sales and Discounts Over Time'
    )
    # Update layout for clarity
    fig2.update_layout(
        xaxis_title='Date',
        yaxis_title='Amount (Naira)',  # Generic label for both metrics
        legend_title='Metric'  # Add a legend for clarity
    )

    # --------------fourth chart-----------------
    # Calculate cumulative sum for the waterfall chart
    df1['CumulativeAmount'] = df1['amount_sold'].cumsum()

    # Create a waterfall chart using a bar chart and cumulative values
    fig3 = px.bar(df1, x='payment_method', y='amount_sold', title='Sales by Payment Method',
                color_continuous_scale=['red', 'green'] # Customize the color scale
                )

    # Update layout for better readability
    fig3.update_layout(yaxis_title='Sales Amount', barmode='relative', showlegend=False)


    col1, col2 = st.columns(2)
    col1.plotly_chart(fig, use_container_width = True)
    col2.plotly_chart(fig1, use_container_width = True)
    col1.plotly_chart(fig2, use_container_width = True)
    col2.plotly_chart(fig3, use_container_width = True)

if selected == "Forecast":
    # fetch data
    # Read data from SQLite database
    cursor.execute('SELECT * FROM gadget')
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df1 = pd.DataFrame(data, columns=columns)

    # Convert 'order_date' to datetime type (if applicable)
    if 'order_date' in df1.columns:
        df1['order_date'] = pd.to_datetime(df1['order_date'])

    df2 = df1[["order_date", "amount_sold"]]

    df2.columns = ["ds", "y"]
    df2.dropna(inplace = True) 
    model = Prophet()
    model.fit(df2)

    future_days = st.number_input("Enter number of days to predict:", min_value=1, value=30)
    future_dates = model.make_future_dataframe(periods=future_days)

    forecast = model.predict(future_dates)

    # Create Plotly figure
    fig = px.line(forecast, x='ds', y='yhat')
    fig.update_layout(  # Customize layout (optional)
        title="Sales Prediction",
        xaxis_title="Date",
        yaxis_title="Predicted Sales"
    )

    # Create a separate trace for actual data points
    fig.add_trace(
        go.Scatter(
            x=df2['ds'],  # Use the original data for actual points
            y=df2['y'],
            mode='markers',  # Display as markers
            name='Actual Data'
        )
    )

    # Display the figure using st.plotly_chart
    st.plotly_chart(fig, use_container_width=True)

    # Summarize current sales range (in Naira, integers, with commas for thousands)
    current_sales_range = (df2['y'].min(), df2['y'].max())
    current_sales_range_naira_int = tuple(format(int(value), ',') for value in current_sales_range)
    st.write("**Current Sales Range:**")
    st.write(f"- The current sales range is between **₦{current_sales_range_naira_int[0]}** and **₦{current_sales_range_naira_int[1]}**.")

    # Summarize predicted sales range (in Naira, integers, with commas for thousands)
    predicted_sales_range = (forecast['yhat'].min(), forecast['yhat'].max())
    predicted_sales_range_naira_int = tuple(format(int(value), ',') for value in predicted_sales_range)
    st.write("**Predictions:**")
    st.write(f"- Following the current trend, sales are forecast to be between **₦{predicted_sales_range_naira_int[0]}** and **₦{predicted_sales_range_naira_int[1]}** in the next {future_days} days.")
