import pandas as pd
import streamlit as st
import altair as alt
from data_processing import finalize_data

def run(navigate_to):
    # Add logo at the top of the sidebar
    st.sidebar.image('kognisi_logo.png')

    # Header for "Test Result"
    st.markdown("<h2 style='text-align: center;'>Test Result</h2>", unsafe_allow_html=True)

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 3, 1])
    with col3:
        if st.button("Back to Main"):
            navigate_to("main")

    # Dashboard guide
    st.markdown("#### Panduan Dashboard\nFilter Test Results mengikuti filter di halaman Demography")

    # Retrieve data
    df_discovery, df_sap, merged_df = finalize_data()

    # Ensure 'nik' and 'Customer ID' are strings
    merged_df['nik'] = merged_df['nik'].astype(str).str.replace(',', '', regex=False)
    merged_df['Customer ID'] = merged_df['Customer ID'].astype(str).str.replace(',', '', regex=False)

    # Convert date columns
    merged_df["Test Date"] = pd.to_datetime(merged_df["Test Date"])
    merged_df["Register Date"] = pd.to_datetime(merged_df["Register Date"])

    # Date filters
    startDate_test, endDate_test = merged_df["Test Date"].min(), merged_df["Test Date"].max()
    startDate_register, endDate_register = merged_df["Register Date"].min(), merged_df["Register Date"].max()

    # Input date for Test Date
    col1, col2 = st.columns(2)
    with col1:
        date1 = st.date_input("Start Date (Test Date)", startDate_test)
    with col2:
        date2 = st.date_input("End Date (Test Date)", endDate_test)

    # Input date for Register Date
    col3, col4 = st.columns(2)
    with col3:
        date3 = st.date_input("Start Date (Register Date)", startDate_register)
    with col4:
        date4 = st.date_input("End Date (Register Date)", endDate_register)

    # Filter data based on selected dates
    df_test_filtered = merged_df[
        (merged_df["Test Date"] >= pd.to_datetime(date1)) & (merged_df["Test Date"] <= pd.to_datetime(date2))
    ]
    df_register_filtered = merged_df[
        (merged_df["Register Date"] >= pd.to_datetime(date3)) & (merged_df["Register Date"] <= pd.to_datetime(date4))
    ]
    df_filtered = df_test_filtered[
        (df_test_filtered["Register Date"] >= pd.to_datetime(date3)) & 
        (df_test_filtered["Register Date"] <= pd.to_datetime(date4))
    ]

    # Sidebar filters
    st.sidebar.header("Filter Options")
    name_input = st.sidebar.text_input("Filter by Name", "")

    filters = {
        'nik': st.sidebar.selectbox("Filter NIK", ["All"] + list(merged_df['nik'].dropna().unique())),
        'gender': st.sidebar.selectbox("Filter Gender", ["All"] + list(merged_df['gender'].dropna().unique())),
        'unit': st.sidebar.selectbox("Filter Unit", ["All"] + list(merged_df['unit'].dropna().unique())),
        'Last Education': st.sidebar.selectbox("Filter Last Education", ["All"] + list(merged_df['Last Education'].dropna().unique())),
        'Province': st.sidebar.selectbox("Filter Province", ["All"] + list(merged_df['Province'].dropna().unique())),
        'generation': st.sidebar.selectbox("Filter Generation", ["All"] + list(merged_df['generation'].dropna().unique())),
        'layer': st.sidebar.selectbox("Filter Layer", ["All"] + list(merged_df['layer'].dropna().unique())),
        'status': st.sidebar.selectbox("Filter Status", ["All", "Internal", "External"])
    }

    # Apply filters based on sidebar input
    if name_input:
        df_filtered = df_filtered[df_filtered["name"].str.contains(name_input, case=False, na=False)]

    for key, value in filters.items():
        if value != "All":
            df_filtered = df_filtered[df_filtered[key] == value]

    # Calculate total registered users
    total_registered_users = df_filtered['Customer ID'].nunique()
    internal_users = df_filtered[df_filtered['status'] == 'Internal']['Customer ID'].nunique()
    external_users = df_filtered[df_filtered['status'] == 'External']['Customer ID'].nunique()

    # Display active user counts
    st.markdown("<h3>ACTIVE USER</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<p style='font-size: 20px; text-align: center;'><strong>Overall: <span style='color: red;'>{total_registered_users:,}</span></strong></p>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<p style='font-size: 20px; text-align: center;'><strong>Internal User: <span style='color: red;'>{internal_users:,}</span></strong></p>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<p style='font-size: 20px; text-align: center;'><strong>External User: <span style='color: red;'>{external_users:,}</span></strong></p>", unsafe_allow_html=True)

    # Active learners by bundle
    bundle_names = ['GI', 'LEAN', 'ELITE', 'Genuine', 'Astaka']

    # Create filtered dataframe for active learners
    if 'bundle_name' in df_filtered.columns:
        df_active_learners = df_filtered.groupby(['Customer ID', 'Test Date', 'bundle_name']).size().reset_index(name='test_count')

        # Count active learners per bundle
        bundle_counts = {bundle: df_active_learners[df_active_learners['bundle_name'] == bundle]['Customer ID'].nunique() for bundle in bundle_names}

        # Display active learners counts
        st.markdown("<h3>ACTIVE LEARNERS</h3>", unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns(5)

        for i, bundle in enumerate(bundle_names):
            with eval(f'col{i + 1}'):
                st.markdown(f"<p style='font-size: 20px; text-align: center;'><strong>{bundle}: <span style='color: red;'>{bundle_counts[bundle]:,}</span></strong></p>", unsafe_allow_html=True)
                
        # Active learners data for Bundle GI
        gi_active_learners = df_filtered[df_filtered['bundle_name'] == 'GI']

        # Get highest scores
        highest_scores = gi_active_learners.loc[gi_active_learners.groupby(['email', 'Test Date', 'Test Name'])['total_score'].idxmax()]
        gi_active_learners_data = highest_scores[['name', 'email', 'Customer ID', 'bundle_name', 'Test Date', 'Test Name', 'total_score', 'final_result']]

        # Stacked bar chart for Growth Inventory
        st.subheader("Growth Inventory")
        gi_filtered = df_filtered[df_filtered['bundle_name'] == 'GI']
        gi_distribution = gi_filtered.groupby(['Test Name', 'typology']).agg({'Customer ID': 'nunique'}).reset_index()
        gi_distribution.columns = ['Test Name', 'typology', 'Active Users']

        # Calculate percentages
        total_active_users_per_test = gi_distribution.groupby('Test Name')['Active Users'].transform('sum')
        gi_distribution['Percentage'] = (gi_distribution['Active Users'] / total_active_users_per_test * 100).round(2)

        # Plot chart
        chart = alt.Chart(gi_distribution).mark_bar().encode(
            x='Test Name',
            y='Active Users',
            color='typology',
            tooltip=[
                alt.Tooltip('Test Name:N', title='Test Name'),
                alt.Tooltip('typology:N', title='Typology'),
                alt.Tooltip('Active Users:Q', title='Active Learners'),
                alt.Tooltip('Percentage:Q', title='Percentage', format='.1f')  # Format percentage with one decimal place
            ]
        ).properties(
            width=600,
            height=400
        ).configure_mark(
            opacity=0.8
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            fontSize=16
        )

        st.altair_chart(chart, use_container_width=True)

        # Data download for Growth Inventory
        with st.expander("Data Growth Inventory"):
            st.write(gi_distribution.style.background_gradient(cmap="Oranges"))
            csv = gi_distribution.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv, file_name="Growth_Inventory.csv", mime="text/csv", help='Click here to download the data as a CSV file')

        # Repeat for LEAN
        lean_active_learners = df_filtered[df_filtered['bundle_name'] == 'LEAN']

        # Get highest scores for LEAN
        highest_scores_lean = lean_active_learners.loc[lean_active_learners.groupby(['email', 'Test Date', 'Test Name'])['total_score'].idxmax()]
        lean_active_learners_data = highest_scores_lean[['name', 'email', 'Customer ID', 'bundle_name', 'Test Date', 'Test Name', 'total_score', 'final_result']]

        # Stacked bar chart for LEAN
        st.subheader("LEAN")
        lean_filtered = df_filtered[df_filtered['bundle_name'] == 'LEAN']
        lean_distribution = lean_filtered.groupby(['Test Name', 'typology']).agg({'Customer ID': 'nunique'}).reset_index()
        lean_distribution.columns = ['Test Name', 'typology', 'Active Users']

        # Calculate percentages for LEAN
        total_active_users_per_test_lean = lean_distribution.groupby('Test Name')['Active Users'].transform('sum')
        lean_distribution['Percentage'] = (lean_distribution['Active Users'] / total_active_users_per_test_lean * 100).round(2)

        # Plot chart for LEAN
        chart_lean = alt.Chart(lean_distribution).mark_bar().encode(
            x='Test Name',
            y='Active Users',
            color='typology',
            tooltip=[
                alt.Tooltip('Test Name:N', title='Test Name'),
                alt.Tooltip('typology:N', title='Typology'),
                alt.Tooltip('Active Users:Q', title='Active Learners'),
                alt.Tooltip('Percentage:Q', title='Percentage', format='.1f')  # Format percentage with one decimal place
            ]
        ).properties(
            width=600,
            height=400
        ).configure_mark(
            opacity=0.8
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            fontSize=16
        )

        st.altair_chart(chart_lean, use_container_width=True)

        # Data download for LEAN
        with st.expander("Data LEAN"):
            st.write(lean_distribution.style.background_gradient(cmap="Oranges"))
            csv_lean = lean_distribution.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv_lean, file_name="LEAN.csv", mime="text/csv", help='Click here to download the data as a CSV file')

        # Display final result distribution
        st.subheader("FINAL RESULT LEAN")
        lean_active_learners = df_filtered[df_filtered['bundle_name'] == 'LEAN']

        # Get highest scores for LEAN
        highest_scores_lean = lean_active_learners.loc[lean_active_learners.groupby(['email', 'Test Date', 'Test Name'])['total_score'].idxmax()]
        lean_active_learners_data = highest_scores_lean[['name', 'email', 'Customer ID', 'bundle_name', 'Test Date', 'Test Name', 'total_score', 'final_result']]
        
        # Get unique combinations of Customer ID and Test Date
        unique_combinations = lean_active_learners_data[['Customer ID', 'Test Date']].drop_duplicates()

        # Merge back to get final_result
        unique_results = unique_combinations.merge(lean_active_learners_data[['Customer ID', 'Test Date', 'final_result']],
                                                   on=['Customer ID', 'Test Date'], 
                                                   how='left').drop_duplicates()

        # Aggregate final_result for pie chart
        final_result_counts = unique_results['final_result'].value_counts().reset_index()
        final_result_counts.columns = ['Final Result', 'Count']

        # Calculate percentage
        final_result_counts['Percentage'] = (final_result_counts['Count'] / final_result_counts['Count'].sum()) * 100

        # Plot pie chart for final results
        pie_chart = alt.Chart(final_result_counts).mark_arc().encode(
            theta='Count:Q',
            color='Final Result:N',
            tooltip=[
                alt.Tooltip('Final Result:N', title='Final Result'),
                alt.Tooltip('Count:Q', title='Active Learners'),
                alt.Tooltip('Percentage:Q', title='Percentage', format='.1f')  # Format percentage with one decimal place
            ]
        ).properties(
            width=400,
            height=400
        )

        st.altair_chart(pie_chart, use_container_width=True)

        # Expander for final result data
        with st.expander("View Final Result Data"):
            st.write(final_result_counts.style.background_gradient(cmap="Oranges"))
            csv_final = final_result_counts.to_csv(index=False).encode('utf-8')  # Convert to CSV
            st.download_button(
                label="Download Final Result Data", 
                data=csv_final, 
                file_name="Final_Results_LEAN.csv", 
                mime="text/csv",
                help='Click here to download the final result data as a CSV file'
        )

        # Repeat for ELITE
        elite_active_learners = df_filtered[df_filtered['bundle_name'] == 'ELITE']

        # Get highest scores for ELITE
        highest_scores_elite = elite_active_learners.loc[elite_active_learners.groupby(['email', 'Test Date', 'Test Name'])['total_score'].idxmax()]
        elite_active_learners_data = highest_scores_elite[['name', 'email', 'Customer ID', 'bundle_name', 'Test Date', 'Test Name', 'total_score', 'final_result']]

        # Stacked bar chart for ELITE
        st.subheader("ELITE")
        elite_filtered = df_filtered[df_filtered['bundle_name'] == 'ELITE']
        elite_distribution = elite_filtered.groupby(['Test Name', 'typology']).agg({'Customer ID': 'nunique'}).reset_index()
        elite_distribution.columns = ['Test Name', 'typology', 'Active Users']

        # Calculate percentages for ELITE
        total_active_users_per_test_elite = elite_distribution.groupby('Test Name')['Active Users'].transform('sum')
        elite_distribution['Percentage'] = (elite_distribution['Active Users'] / total_active_users_per_test_elite * 100).round(2)

        # Plot chart for ELITE
        chart_elite = alt.Chart(elite_distribution).mark_bar().encode(
            x='Test Name',
            y='Active Users',
            color='typology',
            tooltip=[
                alt.Tooltip('Test Name:N', title='Test Name'),
                alt.Tooltip('typology:N', title='Typology'),
                alt.Tooltip('Active Users:Q', title='Active Learners'),
                alt.Tooltip('Percentage:Q', title='Percentage', format='.1f')  # Format percentage with one decimal place
            ]
        ).properties(
            width=600,
            height=400
        ).configure_mark(
            opacity=0.8
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            fontSize=16
        )

        st.altair_chart(chart_elite, use_container_width=True)

        # Data download for ELITE
        with st.expander("Data ELITE"):
            st.write(elite_distribution.style.background_gradient(cmap="Oranges"))
            csv_elite = elite_distribution.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv_elite, file_name="ELITE.csv", mime="text/csv", help='Click here to download the data as a CSV file')

        # Display final result distribution
        st.subheader("FINAL RESULT ELITE")
        elite_active_learners = df_filtered[df_filtered['bundle_name'] == 'ELITE']

        # Get highest scores for ELITE
        highest_scores_elite = elite_active_learners.loc[elite_active_learners.groupby(['email', 'Test Date', 'Test Name'])['total_score'].idxmax()]
        elite_active_learners_data = highest_scores_elite[['name', 'email', 'Customer ID', 'bundle_name', 'Test Date', 'Test Name', 'total_score', 'final_result']]
        
        # Get unique combinations of Customer ID and Test Date
        unique_combinations = elite_active_learners_data[['Customer ID', 'Test Date']].drop_duplicates()

        # Merge back to get final_result
        unique_results = unique_combinations.merge(elite_active_learners_data[['Customer ID', 'Test Date', 'final_result']],
                                                   on=['Customer ID', 'Test Date'], 
                                                   how='left').drop_duplicates()

        # Aggregate final_result for pie chart
        final_result_counts = unique_results['final_result'].value_counts().reset_index()
        final_result_counts.columns = ['Final Result', 'Count']

        # Calculate percentage
        final_result_counts['Percentage'] = (final_result_counts['Count'] / final_result_counts['Count'].sum()) * 100

        # Plot pie chart for final results
        pie_chart = alt.Chart(final_result_counts).mark_arc().encode(
            theta='Count:Q',
            color='Final Result:N',
            tooltip=[
                alt.Tooltip('Final Result:N', title='Final Result'),
                alt.Tooltip('Count:Q', title='Active Learners'),
                alt.Tooltip('Percentage:Q', title='Percentage', format='.1f')  # Format percentage with one decimal place
            ]
        ).properties(
            width=400,
            height=400
        )

        st.altair_chart(pie_chart, use_container_width=True)

        # Expander for final result data
        with st.expander("View Final Result Data"):
            st.write(final_result_counts.style.background_gradient(cmap="Oranges"))
            csv_final = final_result_counts.to_csv(index=False).encode('utf-8')  # Convert to CSV
            st.download_button(
                label="Download Final Result Data", 
                data=csv_final, 
                file_name="Final_Results_ELITE.csv", 
                mime="text/csv",
                help='Click here to download the final result data as a CSV file'
        )
            
        st.subheader("Genuine")
        # Filter DataFrame untuk bundle_name yang spesifik
        genuine_filtered = df_filtered[df_filtered['bundle_name'] == 'Genuine']

        # Get highest scores
        highest_scores = genuine_filtered.loc[genuine_filtered.groupby(['email', 'Test Date', 'Test Name'])['total_score'].idxmax()]
        genuine_active_learners_data = highest_scores[['name', 'email', 'Customer ID', 'bundle_name', 'Test Date', 'Test Name', 'total_score', 'final_result']]

        # Add a rank column from 1 to 9 based on total_score for each Customer ID and Test Date
        genuine_active_learners_data['rank'] = genuine_active_learners_data.groupby(['Customer ID', 'Test Date'])['total_score'].rank(ascending=False, method='first').astype(int)

        # Filter ranks from 1 to 9
        genuine_active_learners_data = genuine_active_learners_data[genuine_active_learners_data['rank'] <= 9]

        # Create a select box for rank selection with a unique key
        genuine_rank = st.selectbox("Select Top for Genuine", options=list(range(1, 10)), key='genuine_rank_select')

        # Filter data based on the selected rank
        filtered_rank_data = genuine_active_learners_data[genuine_active_learners_data['rank'] == genuine_rank]

        # Count the number of unique users for each test name at the selected rank
        user_count_by_test = filtered_rank_data.groupby('Test Name')['Customer ID'].nunique().reset_index()
        user_count_by_test.columns = ['Test Name', 'Total Active Users']

        # Display the results
        st.write(f"Genuine Top {genuine_rank}")
        st.dataframe(user_count_by_test)

        st.subheader("Astaka")
        # Filter DataFrame untuk bundle_name yang spesifik
        astaka_filtered = df_filtered[df_filtered['bundle_name'] == 'Astaka']

        # Get highest scores
        highest_scores = astaka_filtered.loc[astaka_filtered.groupby(['email', 'Test Date', 'Test Name'])['total_score'].idxmax()]
        astaka_active_learners_data = highest_scores[['name', 'email', 'Customer ID', 'bundle_name', 'Test Date', 'Test Name', 'total_score', 'final_result']]

        # Add a rank column from 1 to 6 based on total_score for each Customer ID and Test Date
        astaka_active_learners_data['rank'] = astaka_active_learners_data.groupby(['Customer ID', 'Test Date'])['total_score'].rank(ascending=False, method='first').astype(int)

        # Filter ranks from 1 to 6
        astaka_active_learners_data = astaka_active_learners_data[astaka_active_learners_data['rank'] <= 6]

        # Create a select box for rank selection with a unique key
        astaka_rank = st.selectbox("Select Top for Astaka", options=list(range(1, 7)), key='astaka_rank_select')

        # Filter data based on the selected rank
        filtered_rank_data = astaka_active_learners_data[astaka_active_learners_data['rank'] == astaka_rank]

        # Count the number of unique users for each test name at the selected rank
        user_count_by_test = filtered_rank_data.groupby('Test Name')['Customer ID'].nunique().reset_index()
        user_count_by_test.columns = ['Test Name', 'Total Active Users']

        # Display the results
        st.write(f"Astaka Top {astaka_rank}")
        st.dataframe(user_count_by_test)
