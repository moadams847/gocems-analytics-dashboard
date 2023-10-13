import streamlit as st
from PIL import Image
import rpy2.robjects as robjects
import os
# path = os.path.dirname(__file__)
# print(path)

# Check for R installation
try:
    # Set R working directory
    # robjects.r('setwd(path)')

    # Load R libraries
    robjects.r('library(ggplot2)')
    robjects.r('library(openair)')
    robjects.r('library(tidyverse)')

    # Read data
    robjects.r('df <- read.csv("New_df_ENE00967.csv")')
    
    # Convert date to POSIXct
    robjects.r('df_one <- df %>% mutate(date = as.POSIXct(date, format = "%d/%m/%Y %H:%M"))')
    
    # Generate plot
    robjects.r('my_plot <- calendarPlot(df_one, pollutant = "PM2_5", year = 2023, annotate = "date")')
    
    # Save plot to PNG
    robjects.r('png("image_two.jpg", width = 800, height = 600)')
    robjects.r('print(my_plot)')
    robjects.r('dev.off()')  # Close the PNG device

    # Load the generated image
    image = Image.open('image_two.png')
    st.image(image, caption='Calplot')

# except robjects.rinterface.RRuntimeError as e:
#     st.error(f"An R error occurred: {str(e)}")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.warning("Please ensure that R and the required libraries are properly installed and configured.")
