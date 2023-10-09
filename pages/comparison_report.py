import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
from datetime import datetime, timedelta
import json

# st.title('GOCEMS Air Quality Dashboard')

def authenticate_and_request(APITocken, APPType, request_body):
    # API endpoint URL (replace with the actual API endpoint)
    api_url = 'https://echt.seelive.io/API/DataAI/API_GetSensorData'

    # Construct headers with authentication tokens
    headers = {
        'Authorization': f'Bearer {APITocken}',
        'APITocken': APITocken,
        'APPType': APPType
    }

    try:
        # Send POST request to the API with request body
        response = requests.post(api_url, headers=headers, json=request_body)

        # Check for successful response (status code 200)
        if response.status_code == 200:
            data = response.json()  # Assuming the API returns JSON data
            print('API Response:')
            return (data)
        else:
            print(f'Error: HTTP Status Code {response.status_code}')
            print(response.text)  # Print the response content for debugging

    except Exception as e:
        print(f'Error: {e}')

#--------------------------------------------------------------------------------------------
APITocken='Rth-0987u-wert-3456'
APPType='AIUSER'

# Create a container for horizontal layout
col1, col2, col3 = st.columns([2, 2, 2])

# Date input widgets in the first column
with col1:
    yesterday = datetime.now() - timedelta(days=1)
    start_date = st.date_input("Select Start Date", value=yesterday)
    end_date = st.date_input("Select End Date", value=datetime.now())

# Time input widgets in the second column
with col2:
    start_time = st.time_input("Select Start Time", value=yesterday.time())
    end_time = st.time_input("Select End Time", value=datetime.now().time())

# Sensor ID selection dropdown in the third column
with col3:
    sensor_id = st.selectbox("Select Sensor ID", ["ENE00960", "ENE00933", "ENE00950"])  # Add more sensor IDs as needed
# Add a sensor selection dropdown to compare with the current sensor
    selected_sensor_to_compare = st.selectbox("Select Sensor to Compare", ["None", "ENE00933", "ENE00950"])  # Add more sensors as needed

# Combine the selected date and time into datetime objects using np.array
start_datetime = np.array(datetime.combine(start_date, start_time))
end_datetime = np.array(datetime.combine(end_date, end_time))
print(start_datetime)
print(end_datetime)
# Define a custom datetime format-----------------------------------------------------------
custom_format = "%d-%b-%Y %I:%M %p"

# @st.cache_data
def fetch_data_for_month(sensor_id):
    # Format the datetime objects using the custom format
    start_date_str = start_date.strftime(custom_format)
    end_date_str = end_date.strftime(custom_format)
    
    print(start_date_str)
    print(end_date_str)

    request_body =  {
    "SensorID": sensor_id,  # Use the selected sensor ID
     "FromDate":start_date_str,
     "ToDate":end_date_str,
     "DataInteval":1,
     "DataType":"R"
    }
    
    July_data = authenticate_and_request(APITocken, APPType, request_body)
    Sensor_Data_July = July_data['SearchDetail']
    if len(Sensor_Data_July) != 0:
        # print(Sensor_Data_July[0])
        df_july_one = pd.DataFrame(Sensor_Data_July)
        df_july_one['DataDate'] = pd.to_datetime(df_july_one['DataDate'])
        df_july_two = df_july_one.loc[:, (df_july_one != 0).any(axis=0)]
        # print(df_july_two.head())
        return df_july_two

# Fetch data for the selected sensor
data_current_sensor = fetch_data_for_month(sensor_id)
# print(data_current_sensor.head(1))

# Fetch data for the selected sensor to compare (if selected)
data_to_compare_sensor = None
if selected_sensor_to_compare != "None" and selected_sensor_to_compare != sensor_id:
    data_to_compare_sensor = fetch_data_for_month(selected_sensor_to_compare)

if data_to_compare_sensor is not None and data_current_sensor is not None:
    # Data is not None, it may be a DataFrame
    
    if not data_to_compare_sensor.empty and not data_current_sensor.empty:
        # print("DataFrame is not empty")
        # print(data_current_sensor.head(2))
        # print(data_to_compare_sensor.head(2))

        # Set seconds to zero
        data_current_sensor['DataDate'] = data_current_sensor['DataDate'].apply(lambda dt: dt.replace(second=0))
        data_to_compare_sensor['DataDate'] = data_to_compare_sensor['DataDate'].apply(lambda dt: dt.replace(second=0))
        
       # Prefix df based on DeviceID
        prefix_one = data_current_sensor['DeviceID'].iloc[0]
        prefix_two = data_to_compare_sensor['DeviceID'].iloc[0]

        data_current_sensor = data_current_sensor.add_prefix(f'{prefix_one}_')
        print(data_current_sensor)

        data_to_compare_sensor = data_to_compare_sensor.add_prefix(f'{prefix_two}_')
        print(data_to_compare_sensor)

        # Merge dataframes based on DataDate
        merged_df = pd.merge(data_current_sensor, data_to_compare_sensor, left_on=f'{prefix_one}_DataDate', right_on=f'{prefix_two}_DataDate', how='inner')  
        print(merged_df.head(1))
        # st.write(merged_df.head(1))

        
        # Plot the merged data
        custom_format_graph = "%d-%b-%Y"
        fig = px.line(merged_df, x=f'{prefix_one}_DataDate', y=[f'{prefix_one}_PM2_5', f'{prefix_two}_PM2_5'], title=f'PM2.5 line plot for sensors {prefix_one} and {prefix_two} from {start_date.strftime(custom_format_graph)} to {end_date.strftime(custom_format_graph)}')

        fig.update_xaxes(title_text='Date and Time')
        fig.update_yaxes(title_text='PM2.5 Concentration')

        # Display the combined time series plot in Streamlit
        st.plotly_chart(fig)

    else:
        # DataFrame is empty, perform actions for the empty case
        print("DataFrame is empty")
        
else:
    # Data is None or the same sensor is selected, perform actions for the None case
    if selected_sensor_to_compare == sensor_id:
        st.subheader('Please choose a different sensor to compare')
    else:
        st.subheader('Choose the sensors you wish to compare')




