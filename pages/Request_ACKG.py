import pandas as pd
import streamlit as st
from data_processing import finalize_data

# Set page configuration
st.set_page_config(page_title='Request_ACKG')

# Add logo and header to sidebar and main page
st.sidebar.image('kognisi_logo.png')
col1, col2, col3 = st.columns([1, 12, 3])
with col2:
    st.markdown("<h2 style='text-align: center;'>REQUEST ACKG</h2>", unsafe_allow_html=True)
with col3:
    st.image('growth_center.png')

@st.cache_data
def load_and_process_data():
    # Fetch and process data
    df_discovery, df_sap, merged_df = finalize_data()
    merged_df['nik'] = merged_df['nik'].astype(str).str.replace(',', '', regex=False)
    merged_df['Customer ID'] = merged_df['Customer ID'].astype(str).str.replace(',', '', regex=False)
    merged_df["Test Date"] = pd.to_datetime(merged_df["Test Date"], errors='coerce')  # Convert and handle errors
    merged_df["Register Date"] = pd.to_datetime(merged_df["Register Date"], errors='coerce')  # Convert and handle errors
    return merged_df

# Load and process data
merged_df = load_and_process_data()

# Sidebar filter for email & phone search
email_search = st.sidebar.text_input('Search Email')
phone_search = st.sidebar.text_input('Search Phone')

# Sidebar filter for Test Date range
start_date = st.sidebar.date_input('Start Date', value=pd.to_datetime('2023-01-01'))
end_date = st.sidebar.date_input('End Date', value=pd.to_datetime('today'))

# Filter the DataFrame based on email and phone search inputs
filtered_df = merged_df
if email_search:
    filtered_df = filtered_df[filtered_df['email'].str.contains(email_search, case=False, na=False)]
if phone_search:
    filtered_df = filtered_df[filtered_df['phone'].str.contains(phone_search, case=False, na=False)]

# Filter based on Test Date range if 'Test Date' column exists
if 'Test Date' in filtered_df.columns:
    filtered_df = filtered_df[(filtered_df['Test Date'] >= pd.to_datetime(start_date)) & (filtered_df['Test Date'] <= pd.to_datetime(end_date))]
else:
    st.warning("'Test Date' column is not available in the data.")

# Pivot table for bundle GI
gi_df = filtered_df[filtered_df['bundle_name'] == 'GI'][['email', 'phone', 'Test Name', 'typology']].drop_duplicates()
gi_pivot = gi_df.pivot_table(index=['email', 'phone'], columns='Test Name', values='typology', aggfunc='first').reset_index()

# Add persona column if 'name' exists
if 'name' in filtered_df.columns:
    gi_persona_df = filtered_df[filtered_df['bundle_name'] == 'GI'][['email', 'phone', 'name', 'final_result']].drop_duplicates()
    gi_pivot = pd.merge(gi_pivot, gi_persona_df, on=['email', 'phone'], how='left').rename(columns={'final_result': 'persona'})
else:
    gi_persona_df = filtered_df[filtered_df['bundle_name'] == 'GI'][['email', 'phone', 'final_result']].drop_duplicates()
    gi_pivot = pd.merge(gi_pivot, gi_persona_df, on=['email', 'phone'], how='left').rename(columns={'final_result': 'persona'})

# Rename columns for GI bundle
gi_pivot = gi_pivot.rename(columns={
    'Mindset': 'mindset',
    'Creativity Style': 'creativity_style',
    'Humility': 'humility',
    'Grit': 'grit',
    'Curiosity': 'curiosity',
    'Meaning Making': 'meaning_making',
    'Purpose in Life': 'purpose_in_life'
})

# Pivot table for bundle LEAN
lean_df = filtered_df[filtered_df['bundle_name'] == 'LEAN'][['email', 'phone', 'Test Name', 'typology', 'final_result']].drop_duplicates()
lean_pivot = lean_df.pivot_table(index=['email', 'phone'], columns='Test Name', values='typology', aggfunc='first').reset_index()

# Add 'Overall LEAN' column from final_result
lean_overall_df = lean_df[['email', 'phone', 'final_result']].drop_duplicates()
lean_pivot = pd.merge(lean_pivot, lean_overall_df, on=['email', 'phone'], how='left').rename(columns={'final_result': 'Overall LEAN'})

# Rename columns for LEAN bundle
lean_pivot = lean_pivot.rename(columns={
    'Intellectual Curiosity': 'Intellectual Curiosity',
    'Unconventional Thinking': 'Unconventional Thinking',
    'Cognitive Flexibility': 'Cognitive Flexibility',
    'Open-Mindedness': 'Open-Mindedness',
    'Social Astuteness': 'Social Astuteness',
    'Social Flexibility': 'Social Flexibility',
    'Personal Learner': 'Personal Learner',
    'Self-Reflection': 'Self-Reflection',
    'Self - Regulation': 'Self-Regulation'
})

# Pivot table for bundle ELITE
elite_df = filtered_df[filtered_df['bundle_name'] == 'ELITE'][['email', 'phone', 'Test Name', 'typology', 'final_result']].drop_duplicates()
elite_pivot = elite_df.pivot_table(index=['email', 'phone'], columns='Test Name', values='typology', aggfunc='first').reset_index()

# Add 'Overall ELITE' column from final_result
elite_overall_df = elite_df[['email', 'phone', 'final_result']].drop_duplicates()
elite_pivot = pd.merge(elite_pivot, elite_overall_df, on=['email', 'phone'], how='left').rename(columns={'final_result': 'Overall ELITE'})

# Rename columns for ELITE bundle
elite_pivot = elite_pivot.rename(columns={
    'Self-Awareness': 'Self-Awareness',
    'Self-Regulation': 'Self - Regulation',
    'Motivation': 'Motivation',
    'Empathy': 'Empathy',
    'Social skills': 'Social skills'
})

# Merge all data (GI, LEAN, ELITE)
combined_df = gi_pivot.copy()  # Start with GI pivot
combined_df = pd.merge(combined_df, lean_pivot, on=['email', 'phone'], how='left')  # Merge with LEAN
combined_df = pd.merge(combined_df, elite_pivot, on=['email', 'phone'], how='left')  # Merge with ELITE

# Select relevant columns for display, including 'Astaka Top' columns
columns_to_display = ['name', 'email', 'phone', 'persona',
                      'mindset', 'creativity_style', 'humility', 'grit', 'curiosity', 'meaning_making', 'purpose_in_life',
                      'Overall LEAN', 'Intellectual Curiosity', 'Unconventional Thinking', 'Cognitive Flexibility',
                      'Open-Mindedness', 'Social Astuteness', 'Social Flexibility', 'Personal Learner',
                      'Self-Reflection', 'Self - Regulation', 'Overall ELITE', 'Self-Awareness', 'Motivation', 'Empathy', 'Social skills']

# Display the DataFrame with the selected columns
st.dataframe(combined_df[columns_to_display])

st.dataframe(filtered_df)
