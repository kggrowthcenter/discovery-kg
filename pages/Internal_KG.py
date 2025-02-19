import pandas as pd
import streamlit as st
import plotly.express as px
from data_processing import finalize_data

# Mengatur judul halaman dan favicon
st.set_page_config(page_title='Internal KG')

# Menambahkan logo dan header ke sidebar dan halaman utama
st.logo('kognisi_logo.png')
col1, col2, col3 = st.columns([1, 12, 3])
with col2:
    st.markdown("<h2 style='text-align: center;'>KG EMPLOYEE TRAITS SUMMARY</h2>", unsafe_allow_html=True)
with col3:
    st.image('growth_center.png')

# Fungsi untuk memuat dan memproses data dengan caching
@st.cache_data
def load_and_process_data():
    # Mengambil dan memproses data
    df_discovery, df_sap, merged_df = finalize_data()
    merged_df['nik'] = merged_df['nik'].astype(str).str.replace(',', '', regex=False)
    merged_df['Customer ID'] = merged_df['Customer ID'].astype(str).str.replace(',', '', regex=False)
    merged_df["Test Date"] = pd.to_datetime(merged_df["Test Date"])
    merged_df["Register Date"] = pd.to_datetime(merged_df["Register Date"])
    return merged_df

# Memuat data dengan caching
merged_df = load_and_process_data()

# Memfilter data untuk pengguna internal
internal_df = merged_df[merged_df['status'] == 'Internal']

## Dropdown untuk memilih Bundle Name tanpa opsi "All"
bundle_names = internal_df['bundle_name'].dropna().unique()
selected_bundle = st.sidebar.selectbox("Select Bundle Name", bundle_names)

# Filter DataFrame berdasarkan Bundle Name
filtered_df = internal_df[internal_df['bundle_name'] == selected_bundle]

# Dropdown untuk Test Name berdasarkan Bundle Name yang dipilih
test_name_options = filtered_df['Test Name'].dropna().unique()
selected_test = st.sidebar.selectbox("Select Test Name", test_name_options)

# Filter DataFrame berdasarkan Test Name
filtered_df = filtered_df[filtered_df['Test Name'] == selected_test]

# Dropdown untuk Test Name berdasarkan Bundle Name yang dipilih
typology_options = filtered_df['typology'].dropna().unique()
selected_typology = st.sidebar.selectbox("Select Typology", typology_options)

# Filter DataFrame berdasarkan Test Name
filtered_df = filtered_df[filtered_df['typology'] == selected_typology]

# Multiselect untuk Unit tanpa pilihan default, pengguna memilih secara manual
unit_options = filtered_df['unit'].dropna().unique()
selected_units = st.sidebar.multiselect("Select Unit", unit_options)

# Filter DataFrame berdasarkan Unit yang dipilih (jika ada)
if selected_units:
    filtered_df = filtered_df[filtered_df['unit'].isin(selected_units)]

# Multiselect untuk Sub Unit tanpa pilihan default, pengguna memilih secara manual
subunit_options = filtered_df['subunit'].dropna().unique()
selected_subunits = st.sidebar.multiselect("Select Sub Unit", subunit_options)

# Filter DataFrame berdasarkan Sub Unit yang dipilih (jika ada)
if selected_subunits:
    filtered_df = filtered_df[filtered_df['subunit'].isin(selected_subunits)]

# Treemap untuk jumlah peserta tes per unit
treemap_data = filtered_df.groupby(['Test Name', 'unit']).size().reset_index(name='Unit Count')
fig3 = px.treemap(
    treemap_data, 
    title='Test Taker Per Unit', 
    path=["Test Name", "unit"], 
    values="Unit Count", 
    hover_data=["Unit Count"],
    color="unit"
)
fig3.update_traces(textinfo='label+value', hovertemplate='<b>%{label}</b><br>Active Learners : %{value}')
fig3.update_layout(width=400, height=650)
st.plotly_chart(fig3, use_container_width=True)

# Diagram lingkaran untuk distribusi typology
typology_counts = filtered_df['typology'].value_counts().reset_index()
typology_counts.columns = ['typology', 'User Count']
typology_counts = typology_counts.sort_values(by='User Count', ascending=False)
fig_typology = px.pie(
    typology_counts, 
    names='typology', 
    values='User Count', 
    title='Overall Results'
)
fig_typology.update_traces(
    hovertemplate='<b>%{label}</b><br>%{value}',
    textinfo='percent'
)
fig_typology.update_layout(
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig_typology, use_container_width=True)

# Diagram batang bertumpuk untuk hasil per unit
typology_counts = filtered_df.groupby(['unit', 'typology']).size().reset_index(name='User Count')
unit_total_counts = typology_counts.groupby('unit')['User Count'].sum().reset_index()
unit_total_counts = unit_total_counts.sort_values(by='User Count', ascending=False)
sorted_units = unit_total_counts['unit']

fig_stacked = px.bar(
    typology_counts,
    x='unit',
    y='User Count',
    color='typology',
    title='Result Per Unit',
    labels={'User Count': 'Active Learners'},  # Label diubah menjadi "Active Learners"
    text='User Count',
    height=400
)
fig_stacked.update_layout(
    barmode='stack',
    xaxis_title='Unit',
    yaxis_title='Active Learners',  # Judul sumbu y diubah
    xaxis_categoryorder='array',
    xaxis_categoryarray=sorted_units,
    yaxis=dict(tickformat=',', title='Active Learners')
)
fig_stacked.update_traces(texttemplate='%{text:.0f}')
st.plotly_chart(fig_stacked, use_container_width=True)

# Diagram batang bertumpuk untuk gender
gender_counts = filtered_df.groupby(['gender', 'typology']).size().reset_index(name='User Count')
gender_total_counts = gender_counts.groupby('gender')['User Count'].sum().reset_index()
gender_total_counts = gender_total_counts.sort_values(by='User Count', ascending=False)
sorted_genders = gender_total_counts['gender']

fig_gender = px.bar(
    gender_counts,
    x='gender',
    y='User Count',
    color='typology',
    title='Result Per Gender',
    labels={'User Count': 'Active Learners'},  # Label diubah menjadi "Active Learners"
    text='User Count',
    height=400
)
fig_gender.update_layout(
    barmode='stack',
    xaxis_title='Gender',
    yaxis_title='Active Learners',  # Judul sumbu y diubah
    xaxis_categoryorder='array',
    xaxis_categoryarray=sorted_genders,
    yaxis=dict(tickformat=',', title='Active Learners')
)
fig_gender.update_traces(texttemplate='%{text:.0f}')
st.plotly_chart(fig_gender, use_container_width=True)

# Diagram batang bertumpuk untuk generasi
generation_counts = filtered_df.groupby(['generation', 'typology']).size().reset_index(name='User Count')
generation_total_counts = generation_counts.groupby('generation')['User Count'].sum().reset_index()
generation_total_counts = generation_total_counts.sort_values(by='User Count', ascending=False)
sorted_generations = generation_total_counts['generation']

fig_generation = px.bar(
    generation_counts,
    x='generation',
    y='User Count',
    color='typology',
    title='Result Per Generation',
    labels={'User Count': 'Active Learners'},  # Label diubah menjadi "Active Learners"
    text='User Count',
    height=400
)
fig_generation.update_layout(
    barmode='stack',
    xaxis_title='Generation',
    yaxis_title='Active Learners',  # Judul sumbu y diubah
    xaxis_categoryorder='array',
    xaxis_categoryarray=sorted_generations,
    yaxis=dict(tickformat=',', title='Active Learners')
)
fig_generation.update_traces(texttemplate='%{text:.0f}')
st.plotly_chart(fig_generation, use_container_width=True)

# Diagram batang bertumpuk untuk layer
layer_counts = filtered_df.groupby(['layer', 'typology']).size().reset_index(name='User Count')
layer_total_counts = layer_counts.groupby('layer')['User Count'].sum().reset_index()
layer_total_counts = layer_total_counts.sort_values(by='User Count', ascending=False)
sorted_layers = layer_total_counts['layer']

fig_layer = px.bar(
    layer_counts,
    x='layer',
    y='User Count',
    color='typology',
    title='Result Per Layer',
    labels={'User Count': 'Active Learners'},  # Label diubah menjadi "Active Learners"
    text='User Count',
    height=400
)
fig_layer.update_layout(
    barmode='stack',
    xaxis_title='Layer',
    yaxis_title='Active Learners',  # Judul sumbu y diubah
    xaxis_categoryorder='array',
    xaxis_categoryarray=sorted_layers,
    yaxis=dict(tickformat=',', title='Active Learners')
)
fig_layer.update_traces(texttemplate='%{text:.0f}')
st.plotly_chart(fig_layer, use_container_width=True)

# Display the raw data
st.header('Raw Data', divider='gray')

# Display data
with st.expander("Demography Active Learners"):
    st.dataframe(filtered_df)
