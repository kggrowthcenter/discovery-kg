import pandas as pd
import streamlit as st
import altair as alt
from data_processing import finalize_data

def run(navigate_to):
    # Menambahkan logo di atas sidebar
    st.sidebar.image('kognisi_logo.png')

    # Menambahkan header "Demography" di tengah
    st.markdown("<h2 style='text-align: center;'>Demography</h2>", unsafe_allow_html=True)

    # Menambahkan keterangan Panduan dashboard di bagian atas
    st.markdown("""
    #### Panduan Dashboard
    - **Register Date** adalah waktu user mendaftar.
    - **Test Date** adalah tanggal user selesai mengerjakan test.
    """)

    # Tombol navigasi untuk Test Results
    col1, col2, col3 = st.columns([1, 4, 1])
    with col3:
        if st.button("Test Results"):
            navigate_to("results")

    # Mengambil data dari data_processing
    df_discovery, df_sap, merged_df = finalize_data()

    # Membersihkan dan mengonversi kolom
    merged_df['nik'] = merged_df['nik'].astype(str).str.replace(',', '')
    merged_df['Customer ID'] = merged_df['Customer ID'].astype(str).str.replace(',', '')
    merged_df["Test Date"] = pd.to_datetime(merged_df["Test Date"])
    merged_df["Register Date"] = pd.to_datetime(merged_df["Register Date"])

    # Menyiapkan filter tanggal
    startDate_test, endDate_test = merged_df["Test Date"].min(), merged_df["Test Date"].max()
    startDate_register, endDate_register = merged_df["Register Date"].min(), merged_df["Register Date"].max()

    # Input tanggal untuk filter
    col1, col2 = st.columns(2)
    with col1:
        date1 = st.date_input("Start Date (Test Date)", startDate_test)
    with col2:
        date2 = st.date_input("End Date (Test Date)", endDate_test)

    col3, col4 = st.columns(2)
    with col3:
        date3 = st.date_input("Start Date (Register Date)", startDate_register)
    with col4:
        date4 = st.date_input("End Date (Register Date)", endDate_register)

    # Memfilter data berdasarkan tanggal
    df_test_filtered = merged_df[(merged_df["Test Date"] >= pd.to_datetime(date1)) & (merged_df["Test Date"] <= pd.to_datetime(date2))]
    df_register_filtered = merged_df[(merged_df["Register Date"] >= pd.to_datetime(date3)) & (merged_df["Register Date"] <= pd.to_datetime(date4))]
    df_filtered = df_test_filtered[(df_test_filtered["Register Date"] >= pd.to_datetime(date3)) & (df_test_filtered["Register Date"] <= pd.to_datetime(date4))]

    # Menambahkan catatan
    st.markdown("""
    #### Notes
    - **Test Date** mempengaruhi semua chart kecuali Total Registered User dan grafik Registered User.
    - **Register Date** mempengaruhi semua chart.
    """)

    # Sidebar filters
    st.sidebar.header("Filter Options")
    name_input = st.sidebar.text_input("Filter by Name", "")

    filters = {
        'nik': st.sidebar.multiselect("Filter NIK", list(merged_df['nik'].dropna().unique()), default=[]),
        'gender': st.sidebar.multiselect("Filter Gender", list(merged_df['gender'].dropna().unique()), default=[]),
        'unit': st.sidebar.multiselect("Filter Unit", list(merged_df['unit'].dropna().unique()), default=[]),
        'Last Education': st.sidebar.multiselect("Filter Last Education", list(merged_df['Last Education'].dropna().unique()), default=[]),
        'Company': st.sidebar.multiselect("Filter Company", list(merged_df['Company'].dropna().unique()), default=[]),
        'Province': st.sidebar.multiselect("Filter Province", list(merged_df['Province'].dropna().unique()), default=[]),
        'generation': st.sidebar.multiselect("Filter Generation", list(merged_df['generation'].dropna().unique()), default=[]),
        'layer': st.sidebar.multiselect("Filter Layer", list(merged_df['layer'].dropna().unique()), default=[]),
        'status': st.sidebar.multiselect("Filter Status", ["Internal", "External"], default=[])
    }
    
    # Apply filters based on sidebar input
    if name_input:
        df_filtered = df_filtered[df_filtered["name"].str.contains(name_input, case=False, na=False)]

    for key, value in filters.items():
        if value:  # If the filter has selections, apply it
            df_filtered = df_filtered[df_filtered[key].isin(value)]

    # Menghitung jumlah pengguna
    total_registered_users = df_register_filtered['Customer ID'].nunique()
    total_active_users = df_filtered['Customer ID'].nunique()
    total_internal_users = df_filtered[df_filtered['status'] == 'Internal']['Customer ID'].nunique()
    total_external_users = df_filtered[df_filtered['status'] == 'External']['Customer ID'].nunique()

    # Menampilkan informasi "DISCOVERY USER"
    st.markdown("<h3>DISCOVERY USER</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<p style='font-size: 20px; text-align: center;'><strong>Overall: <span style='color: red;'>{total_active_users:,}</span></strong></p>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<p style='font-size: 20px; text-align: center;'><strong>Internal User: <span style='color: red;'>{total_internal_users:,}</span></strong></p>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<p style='font-size: 20px; text-align: center;'><strong>External User: <span style='color: red;'>{total_external_users:,}</span></strong></p>", unsafe_allow_html=True)

    # Menampilkan tabel berdasarkan dropdown
    st.subheader("Select Table to Display")
    table_option = st.selectbox("Choose a table to display:", ["Last Education","Company", "University", "Location", "Unit"])

    # Memetakan opsi dropdown ke kolom dataframe
    table_dict = {
        "Last Education": 'Last Education',
        "Company" : 'Company',
        "University": 'Institution',
        "Location": 'Province',
        "Unit": 'unit'
    }

    # Menyiapkan tabel breakdown
    breakdown_column = table_dict[table_option]
    internal_breakdown = df_filtered[df_filtered['status'] == 'Internal'].groupby(breakdown_column)['Customer ID'].nunique().reset_index()
    internal_breakdown.columns = [breakdown_column, 'Internal Count']
    external_breakdown = df_filtered[df_filtered['status'] == 'External'].groupby(breakdown_column)['Customer ID'].nunique().reset_index()
    external_breakdown.columns = [breakdown_column, 'External Count']
    breakdown_table = pd.merge(internal_breakdown, external_breakdown, on=breakdown_column, how='outer').fillna(0)
    st.write(f"### Breakdown by {table_option}")
    st.dataframe(breakdown_table)

    # Pie chart untuk distribusi gender
    gender_breakdown = df_filtered.groupby(['gender', 'status'])['Customer ID'].nunique().reset_index()
    gender_summary = gender_breakdown.groupby('gender')['Customer ID'].sum().reset_index()
    gender_summary.columns = ['Gender', 'Count']
    pie_chart = alt.Chart(gender_summary).mark_arc().encode(
        theta=alt.Theta(field="Count", type="quantitative"),
        color=alt.Color(field="Gender", type="nominal"),
        tooltip=[alt.Tooltip('Gender', title='Gender'), alt.Tooltip('Count', title='Count')]
    ).properties(title='Gender Distribution')
    st.altair_chart(pie_chart, use_container_width=True)
    
    # Count unique active learners by test date
    active_learners_counts = (df_filtered
                              .groupby('Register Date')
                              .agg(active_learners=('Customer ID', 'nunique'))
                              .reset_index())

    # Create a line chart for active learners
    st.subheader("Registered Users Over Time")
    line_chart = alt.Chart(active_learners_counts).mark_line(
        stroke='steelblue',  # Change the line color
        strokeWidth=2  # Increase line width for better visibility
    ).encode(
        x=alt.X('Register Date:T', title='Register Date', 
                axis=alt.Axis(format='%Y-%m-%d', labelAngle=-45)),  # Tilt x-axis labels
        y=alt.Y('active_learners:Q', axis=alt.Axis(titleColor='black')),
        tooltip=[
            alt.Tooltip('Register Date:T', title='Register Date', format='%Y-%m-%d'), 
            alt.Tooltip('active_learners:Q', title='Active Learners')
        ]
    ).properties(
        width=600,
        height=400
    )

    # Display the chart
    st.altair_chart(line_chart, use_container_width=True)

    # Tombol untuk menampilkan data tabel Registered Users
    if st.button("Show Data Table for Registered Users"):
        st.write(active_learners_counts)

    # Grafik garis untuk Active Users
    # Count unique active learners by test date
    active_learner_counts = (df_filtered
                              .groupby('Test Date')
                              .agg(active_learner=('Customer ID', 'nunique'))
                              .reset_index())
    
    # Create a line chart for active learners
    st.subheader("Active User Over Time")
    chart_line = alt.Chart(active_learner_counts).mark_line(
        stroke='steelblue',  # Change the line color
        strokeWidth=2  # Increase line width for better visibility
    ).encode(
        x=alt.X('Test Date:T', title='Test Date', 
                axis=alt.Axis(format='%Y-%m-%d', labelAngle=-45)),  # Tilt x-axis labels
        y=alt.Y('active_learner:Q', axis=alt.Axis(titleColor='black')),
        tooltip=[
            alt.Tooltip('Test Date:T', title='Test Date', format='%Y-%m-%d'), 
            alt.Tooltip('active_learner:Q', title='Active Learner')
        ]
    ).properties(
        width=600,
        height=400
    )

    # Display the chart
    st.altair_chart(chart_line, use_container_width=True)
    
    # Tombol untuk menampilkan data tabel Active Users
    if st.button("Show Data Table for Active Users"):
        st.write(active_learner_counts)

   # Grafik bar charts untuk generation
    st.subheader("Generation Distribution")
    generation_distribution = df_filtered.groupby('generation')['Customer ID'].nunique().reset_index(name='Generation User')
    generation_distribution.columns = ['Generation', 'Count']
    generation_bar_chart = alt.Chart(generation_distribution).mark_bar().encode(
        x=alt.X('Generation:O', title='Generation'),
        y=alt.Y('Count:Q', title='Users'),
        color=alt.Color('Generation:O', title='Generation'),
        tooltip=['Generation', 'Count']
    ).properties(width=800, height=300)
    st.altair_chart(generation_bar_chart, use_container_width=True)
