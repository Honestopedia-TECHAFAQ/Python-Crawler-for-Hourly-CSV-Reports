import requests
import pandas as pd
import streamlit as st
import datetime
import time
import os
def load_config():
    config = {}
    with open("config.txt", "r") as file:
        for line in file:
            key, value = line.strip().split("=")
            config[key.strip()] = value.strip()
    return config

def log_activity(message):
    with open("activity_log.txt", "a") as log_file:
        log_file.write(f"{datetime.datetime.now()}: {message}\n")
def login(url, username, password):
    try:
        response = requests.post(url, data={"username": username, "password": password})
        response.raise_for_status()
        token = response.json().get("token")
        log_activity("Successfully logged in and retrieved token.")
        return token
    except Exception as e:
        log_activity(f"Login failed: {str(e)}")
        st.error("Login failed. Check the configuration or try again.")
        return None
def fetch_report(api_url, token, queue_list, start_date, end_date):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"queues": queue_list, "start_date": start_date, "end_date": end_date}
    try:
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json().get("data")
        log_activity("Successfully fetched report data.")
        return data
    except Exception as e:
        log_activity(f"Failed to fetch report data: {str(e)}")
        st.error("Failed to fetch report data.")
        return None
def export_to_csv(data, file_path):
    try:
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        log_activity(f"Report exported to {file_path}")
        st.success(f"Report saved at {file_path}")
    except Exception as e:
        log_activity(f"Failed to export CSV: {str(e)}")
        st.error("Failed to save report. Check file path or data format.")
def run_crawler():
    config = load_config()
    token = login(config["login_url"], config["username"], config["password"])
    
    if not token:
        return 
    start_date = config["start_date"]
    end_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    queue_list = config["queue_list"].split(",")
    data = fetch_report(config["api_url"], token, queue_list, start_date, end_date)
    
    if data:
        export_to_csv(data, config["export_path"])
st.title("Automated User Activity Crawler")
st.write("This tool logs into your platform, retrieves user activity, and exports a CSV report every hour.")

if st.button("Run Crawler Now"):
    run_crawler()
    st.write("Crawler executed. Check logs for details.")
while True:
    run_crawler()
    time.sleep(3600)  
