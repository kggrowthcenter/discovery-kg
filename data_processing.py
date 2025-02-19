import streamlit as st
import pandas as pd
from fetch_data import fetch_data_discovery, fetch_data_sap

@st.cache_data
def fetch_discovery_data():
    # Fetch data from Discovery
    df_discovery = fetch_data_discovery()
    return df_discovery

@st.cache_data
def fetch_sap_data():
    # Fetch SAP data with selected columns
    selected_columns = ['name_sap', 'email', 'nik', 'unit', 'subunit', 'admin_hr', 'layer', 'generation', 'gender', 'division', 'department']
    df_sap = fetch_data_sap(selected_columns)
    df_sap = clean_sap_data(df_sap)
    return df_sap

def clean_sap_data(df_sap):
    df_sap['email'] = df_sap['email'].str.strip().str.lower()
    df_sap['nik'] = df_sap['nik'].astype(str).str.zfill(6)
    return df_sap

@st.cache_data
def finalize_data():
    # Fetch and clean data from Discovery and SAP
    df_discovery = fetch_discovery_data()
    df_sap = fetch_sap_data()

    # Clean Discovery email
    df_discovery['email'] = df_discovery['email'].str.strip().str.lower()

    if 'Register Date' in df_discovery.columns:
        df_discovery['Register Date'] = pd.to_datetime(df_discovery['Register Date'], errors='coerce').dt.date
        df_discovery = df_discovery.dropna(subset=['Register Date'])
        
    # Convert Test Date to timestamp and extract date
    if 'Test Date' in df_discovery.columns:
        df_discovery['Test Date'] = pd.to_datetime(df_discovery['Test Date'], errors='coerce').dt.date
        df_discovery = df_discovery.dropna(subset=['Test Date'])

    # Merge Discovery data with SAP data based on email
    merged_df = pd.merge(df_discovery, df_sap, on='email', how='left', indicator=True)
    merged_df['status'] = merged_df['_merge'].apply(lambda x: 'Internal' if x == 'both' else 'External')
    merged_df.drop(columns=['_merge'], inplace=True)

    return df_discovery, df_sap, merged_df
