import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt



import requests
import time
from datetime import datetime, timedelta, time
import json
import io
from PIL import Image
import os


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
#             return data_dictionary.update(data)
        else:
            print(f'Error: HTTP Status Code {response.status_code}')
            print(response.text)  # Print the response content for debugging

    except Exception as e:
        print(f'Error: {e}')


#--------------------------------------------------------------------------------------------
APITocken='Rth-0987u-wert-3456'
APPType='AIUSER'

# # Define the start and end date strings------------------------------------------------------
# start_date = datetime(2023, 7, 1, 0, 0)
# end_date = datetime(2023, 8, 31, 23, 59)

# Create a container for horizontal layout
col1, col2, col3 = st.columns([2, 2, 2])

# Date input widgets in the first column
with col1:
    start_date = st.date_input("Select Start Date", datetime(2023, 10, 1))  # Set to July 1, 2023
    end_date = st.date_input("Select End Date", datetime.now() + timedelta(days=1))  # Add one day to current date

# Time input widgets in the second column
with col2:
    start_time = st.time_input("Select Start Time", time(0, 0))  # Set to midnight (00:00)
    end_time = st.time_input("Select End Time", datetime.now().time())

# Sensor ID selection dropdown in the third column
with col3:
    sensor_id = st.selectbox("Select Sensor ID", ["ENE00960", "ENE00933", "ENE00950","ENE02516"])  # Add more sensor IDs as needed

# Combine the selected date and time into datetime objects using np.array
start_datetime = np.array(datetime.combine(start_date, start_time))
end_datetime = np.array(datetime.combine(end_date, end_time))
print(start_datetime)
print(end_datetime)
# Define a custom datetime format-----------------------------------------------------------
custom_format = "%d-%b-%Y %I:%M %p"

# @st.cache_data
def fetch_data_for_month():
    # Format the datetime objects using the custom format
    start_date_str = start_date.strftime(custom_format)
    end_date_str = end_date.strftime(custom_format)
    
    print(start_date_str)
    print(end_date_str)

    request_body =  {
    "SensorID":sensor_id,
     "FromDate":start_date_str,
     "ToDate":end_date_str,
     "DataInteval":1,
     "DataType":"P"
    }
    

    July_data = authenticate_and_request(APITocken, APPType, request_body)
    Sensor_Data_July = July_data['SearchDetail']
    if len(Sensor_Data_July) != 0:
        print(Sensor_Data_July[0])
        df_july_one = pd.DataFrame(Sensor_Data_July)
        df_july_one['DataDate'] = pd.to_datetime(df_july_one['DataDate'])
        df_july_two = df_july_one.loc[:, (df_july_one != 0).any(axis=0)]
        print(df_july_two.head())
        return df_july_two



# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
data = fetch_data_for_month()

if data is not None:
    id_sensor_from_df = data['DeviceID'][0]

        # Create a download button to download the displayed data as CSV
    # st.write(data)

    # Exclude 'DeviceID' from aggregation
    data.drop(columns='DeviceID', inplace=True)
    print(data.columns)

      # Set 'Timestamp' as the index
    data.set_index('DataDate', inplace=True)
    # Resample the data by minute
    
    
    def resample_and_aggregate(data, resample_freq, aggregation_func):
        """
        Resample a DataFrame by a specified frequency and perform aggregation using a given function.
        
        Parameters:
            - data: DataFrame
                The input DataFrame to be resampled and aggregated.
            - resample_freq: str
                The resampling frequency (e.g., 'H' for hourly, 'D' for daily).
            - aggregation_func: str
                The aggregation function to apply ('mean', 'max', or 'min').

        Returns:
            - resampled_df: DataFrame
                The resampled and aggregated DataFrame.
        """
        if aggregation_func == 'mean':
            resampled_df = data.resample(resample_freq).mean()
        elif aggregation_func == 'max':
            resampled_df = data.resample(resample_freq).max()
        elif aggregation_func == 'min':
            resampled_df = data.resample(resample_freq).min()
        else:
            raise ValueError("Invalid aggregation function. Choose 'mean', 'max', or 'min'.")

        return resampled_df


    # Specify the aggregation function ('mean', 'max', or 'min')
    # Select aggregation function
    aggregation_func = st.selectbox("Select Aggregation Function", ['mean', 'max', 'min'])

    # Resample and aggregate the DataFrame
    result_df = resample_and_aggregate(data, 'H', aggregation_func)
    print(result_df)


    # resampled_df = data.resample('H').mean()
    cleaned_data = result_df.dropna()

    # resampled_df.reset_index(inplace=True)
    print(cleaned_data.head())

    st.subheader(f'Sensor {id_sensor_from_df} Hourly {aggregation_func} Aggregation')
    st.write(cleaned_data)
    data_load_state.text('Loading data...done!')



    # hourly evolution----------------------------------------------------
   
    # Extract the day of the week and hour
    # cleaned_data.reset_index(inplace=True)

    cleaned_data['DayOfWeek'] = cleaned_data.iloc[:, 0].index.to_series().dt.day_name()
    cleaned_data['Hour'] = cleaned_data.iloc[:, 0].index.to_series().dt.hour
    print(cleaned_data)

    # Create a new list excluding 'Hour' and 'DayOfWeek'

    column_list =cleaned_data.columns

    new_column_list = [item for item in column_list if item not in ('Hour', 'DayOfWeek')]

    selected_column = st.selectbox(f"Select a Column", new_column_list)
    print(selected_column)

    sns.set_style('darkgrid')

    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    # Create a single row with multiple columns for subplots with reduced horizontal gaps
    fig, axes = plt.subplots(1, len(days), figsize=(15, 5), sharey=True, sharex=True)

    # Plot PM2.5 vs. Hours and PM10 vs. Hours for each day using Seaborn with legends
    for i, day in enumerate(days):
        day_resampled_df = cleaned_data[cleaned_data['DayOfWeek'] == day]
        ax = axes[i]

        sns.lineplot(data=cleaned_data, x='Hour', y=selected_column, label=f'{selected_column}', ax=ax, errorbar=None)
    #     sns.lineplot(data=day_resampled_df, x='Hour', y='PM10', marker='o', label='PM10', ax=ax)

        ax.set_title(f'{day}')
        ax.set_xlabel('Hour')
        ax.set_ylabel('Concentration')
        ax.legend()  # Add a legend to the subplot
        
    # Set a single title for the entire plot
    fig.suptitle(f'Hourly evolution of {id_sensor_from_df}_{selected_column} during the week')

    # Adjust horizontal gap between subplots
    plt.subplots_adjust(wspace=0.05)  # You can adjust the value as needed

    fig = plt.savefig(f'Hourly evolution of {id_sensor_from_df}_{selected_column} during the week.png', dpi=150)  # You can replace the file name as needed

    st.subheader(f'Hourly evolution of {selected_column} during the week')
    
   # Display the saved image
    image = Image.open(f"Hourly evolution of {id_sensor_from_df}_{selected_column} during the week.png")

    # Convert the image to a supported format (e.g., PNG)
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="png")
    image_data = image_bytes.getvalue()

    # Create a download button for the image
    st.download_button("Download graph", image_data, f"Hourly evolution of {id_sensor_from_df}_{selected_column} during the week.png", key="download_image")
    
    st.image(image)

    # Delete the PNG file if the action is successful
    path = os.path.dirname(__file__)
    print(path)
    if os.path.exists(f"{path}\Hourly evolution of {id_sensor_from_df}_{selected_column} during the week.png"):
        os.remove(f"{path}\Hourly evolution of {id_sensor_from_df}_{selected_column} during the week.png")
        print("File deleted.")
    


    # You can adjust spacing between subplots by adding markdown text or other Streamlit elements
    st.markdown("##")


else:
    st.write('Specify a suitable date range')
    # Handle the case where data is None
    # id_sensor_from_df = None  # Or perform other appropriate actions









