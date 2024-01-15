import random
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import streamlit as st
from streamlit_option_menu import option_menu
import mysql.connector
import plotly.graph_objects as go
import plotly.express as px
import calendar
from datetime import datetime
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
from prophet import Prophet 
from prophet.plot import plot_plotly, plot_components_plotly

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


# @st.cache_data
# def get_session_state():
#     return {"data_entries": []}
# # Get or create the session state
# state = get_session_state()

# MySQL database connection configuration
# mydb = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': 'feditheanalyst_20',
#     'database': 'plug'
# }

# # Create a MySQL connection
# connection = mysql.connector.connect(**mydb)
# cursor = connection.cursor()


# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()
conn = st.connection("supabase",type=SupabaseConnection)

# Perform query.
rows = conn.query("*", table="plug", ttl="10m").execute()


if selected == "Data Entry":
    # File uploader
    # uploaded_file = st.file_uploader('Upload a CSV file', type=['csv'])

    # # Check if a file has been uploaded
    # if uploaded_file is not None:
    #     # Read the dataset
    #     df = pd.read_csv(uploaded_file)

    #     # Display the dataset
    #     st.subheader('Uploaded Dataset')
    #     st.write(df)
    # else:
    #     st.info('Please upload a CSV file.')

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
        # Collect data from form fields
        customer_id = st.session_state.customer_id  # Access from session state
        customer_email = st.session_state.customer_email
        customer_phone = st.session_state.customer_phone
        product_name = st.session_state.product_name
        product_description = st.session_state.product_description
        initial_price = st.session_state.initial_price
        amount_sold = st.session_state.amount_sold
        discount = st.session_state.discount
        stock_quantity = st.session_state.stock_quantity
        order_id = st.session_state.order_id
        order_date = st.session_state.order_date
        state = st.session_state.state
        country = st.session_state.country
        payment_method =st.session_state.payment_method

    data = {
        "customer_id" : customer_id,
        "customer_email": customer_email,
        "customer_phone": customer_phone,
        "product_name": product_name,
        "product_description": product_description,
        "initial_price": initial_price,
        "amount_sold": amount_sold,
        "discount": discount,
        "stock_quantity": stock_quantity,
        "order_id": order_id,
        "order_date": order_date,
        "state": state,
        "country": country,
        "payment_method":payment_method
    }
        # sql = "insert into dataass(customer_id, customer_email, customer_phone, product_name, product_description, initial_price, amount_sold, discount, stock_quantity, order_id, order_date, state, country, payment_method) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        # val = (customer_id, customer_email, customer_phone, product_name, product_description, initial_price, amount_sold, discount, stock_quantity, order_id, order_date, state, country, payment_method)
        # cursor.execute(sql, val)
        # connection.commit()
        # st.success("Data Saved")
    try:
        supabase.table("plug").insert(data).execute()
        st.success("Data Saved")
    except Exception as e:
        st.error("Error saving data:", e)

elif selected == "Analytics":
    # Retrieve data from Supabase using the connection
    result = conn.query("select * from plug").execute()

    # Convert the result to a Pandas DataFrame
    df1 = pd.DataFrame(result.data, columns=result.columns)

    # Convert 'order_date' to datetime type (if applicable)
    if 'order_date' in df1.columns:
        df1['order_date'] = pd.to_datetime(df1['order_date'])

    # cursor.execute("select * from dataass")
    # result = cursor.fetchall()

    # # Convert the data to a pandas DataFrame
    # df1 = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
    
    # # Convert 'order_date' to datetime type
    # df1['order_date'] = pd.to_datetime(df1['order_date'])

    # # Store the data in session state
    # state["data_entries"] = df1

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
    fig1 = px.bar(top_5_states, x='state', y='amount_sold', title='Product Sales Analysis',
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
                # text='amount_sold', # Display the value on top of each bar
                # color='amount_sold', # Color by Amount for positive/negative differentiation
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
    # Retrieve data from Supabase using the connection
    result = conn.query("select * from plug").execute()

    # Convert the result to a Pandas DataFrame
    df1 = pd.DataFrame(result.data, columns=result.columns)

    # Convert 'order_date' to datetime type (if applicable)
    if 'order_date' in df1.columns:
        df1['order_date'] = pd.to_datetime(df1['order_date'])
    # cursor.execute("select * from dataass")
    # result = cursor.fetchall()

    # # Convert the data to a pandas DataFrame
    # df1 = pd.DataFrame(result, columns=[i[0] for i in cursor.description])

    # # Store the data in session state
    # state["data_entries"] = df1

    df2 = df1[["order_date", "amount_sold"]]

    df2.columns = ["ds", "y"]

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
