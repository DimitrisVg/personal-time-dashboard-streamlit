import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go

# Set the app configuration
st.set_page_config(
    page_title="Personal Time Dashboard",
    page_icon=":clock3:",
    layout="centered"
)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Yearly Overview", "Weekly Overview"])

# Year selector
selected_year = st.sidebar.selectbox("Select Year", [2024, 2025])

# Determine file path based on selected year
if selected_year == 2024:
    file_path = r'data\\2024\\2024_outlook_data.csv'
else:
    file_path = r'data\\2025\\2025_outlook_data.csv'

# Utility functions
def load_yearly_data(file_path):
    # Load dataset and preprocess
    data = pd.read_csv(file_path)
    data['Start Date'] = pd.to_datetime(data['Start Date'], format='%d/%m/%Y')
    data['End Date'] = pd.to_datetime(data['End Date'], format='%d/%m/%Y')
    data['Start Time'] = pd.to_datetime(data['Start Time'], format='%H:%M:%S').dt.time
    data['End Time'] = pd.to_datetime(data['End Time'], format='%H:%M:%S').dt.time

    # Handle duration calculation, including events spanning midnight
    def calculate_duration(row):
        start = datetime.datetime.combine(row['Start Date'], row['Start Time'])
        end = datetime.datetime.combine(row['End Date'], row['End Time'])
        if end < start:  # Handle overnight events
            end += datetime.timedelta(days=1)
        return (end - start).total_seconds() / 3600.0

    data['Duration'] = data.apply(calculate_duration, axis=1)
    return data

def load_weekly_data(file_path):
    # Placeholder for weekly data loading logic if needed
    return load_yearly_data(file_path)

# Define color scheme for categories
CATEGORY_COLORS = {
    "Ύπνος": "lightgrey",
    "<3": "mediumpurple",
    "Εργασία": "#b05a69",
    "Yellow category": "#f4e76a",
    "Purple category": "mediumpurple",
    "Χαζεύω": "black",
    "Σπίτι": "darkgrey",
    "Φίλοι": "orange",
    "Blyat": "blue",
    "Οικογένεια": "#5aca91",
    "Other": "#63d2d9",
    "Διάβασμα": "#d66871",
    "Erroneοus Tasks": "#e18563",
    "Break": "#ec6ab9",
    "Exercise": "red",
    "Λάμπρος": "blue"
}

# Yearly Overview Page
if page == "Yearly Overview":
    st.title(":clock3: Yearly Overview")
    st.write("Explore your yearly time data.")

    # Load data
    yearly_data = load_yearly_data(file_path)

    # Pie chart for categories
    st.header("Time Spent by Category")
    category_data = yearly_data.groupby('Categories')['Duration'].sum().dropna().reset_index()

    if not category_data.empty:
        fig = px.pie(
            category_data,
            names='Categories',
            values='Duration',
            title='Time Spent by Category',
            hole=0.4,
            color='Categories',
            color_discrete_map=CATEGORY_COLORS
        )
        st.plotly_chart(fig)

        # GitHub-style activity heatmap
        st.header("Activity Heatmap")
        selected_category = st.selectbox("Select a category to view activity:", category_data['Categories'].unique())

        filtered_data = yearly_data[yearly_data['Categories'] == selected_category]
        if not filtered_data.empty:
            # Generate a full calendar year for heatmap
            full_year = pd.date_range(start=f"{selected_year}-01-01", end=f"{selected_year}-12-31")
            heatmap_data = filtered_data.groupby(filtered_data['Start Date'].dt.date)['Duration'].sum().reindex(full_year, fill_value=0).reset_index()
            heatmap_data.columns = ['Date', 'Duration']
            heatmap_data['Week'] = heatmap_data['Date'].dt.isocalendar().week
            heatmap_data['Day of Week'] = heatmap_data['Date'].dt.dayofweek

            # Create a GitHub-style heatmap
            heatmap_fig = go.Figure(
                data=go.Heatmap(
                    z=heatmap_data['Duration'],
                    x=heatmap_data['Week'],
                    y=heatmap_data['Day of Week'],
                    colorscale='Viridis',
                    colorbar=dict(title="Hours Spent"),
                    xgap=2,  # Ensure square cells
                    ygap=2
                )
            )
            heatmap_fig.update_layout(
                title=f"Activity Heatmap for {selected_category}",
                xaxis_title="Week of Year",
                yaxis_title="Day of Week",
                yaxis=dict(
                    tickmode='array',
                    tickvals=list(range(7)),
                    ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                ),
                xaxis=dict(
                    scaleanchor="y",
                    scaleratio=1
                )
            )
            st.plotly_chart(heatmap_fig)
        else:
            st.write("No activity data available for the selected category.")
    else:
        st.write("No category data available.")

# Weekly Overview Page
elif page == "Weekly Overview":
    st.title(":clock3: Weekly Overview")
    st.write("Dive into your weekly time data.")

    # Load data
    weekly_data = load_weekly_data(file_path)

    # Select a specific week range
    st.header("Filter Weeks")
    start_week, end_week = st.slider(
        "Select week range:",
        1, 52, (1, 52),
        format="Week %d"
    )

    # Assuming dataset has a "Week" column or needs to be created
    weekly_data['Week'] = weekly_data['Start Date'].dt.isocalendar().week
    filtered_data = weekly_data[(weekly_data['Week'] >= start_week) & (weekly_data['Week'] <= end_week)]

    # Display bar chart
    st.header("Weekly Time Spent")
    weekly_summary = filtered_data.groupby('Week')['Duration'].sum().reset_index()

    if not weekly_summary.empty:
        fig = px.bar(
            weekly_summary,
            x='Week',
            y='Duration',
            title='Weekly Time Spent',
            labels={'Duration': 'Hours Spent'},
            color_discrete_sequence=['blue']  # Example default color for weekly bar chart
        )
        st.plotly_chart(fig)
    else:
        st.write("No data available for the selected weeks.")

    # Summary metrics
    total_hours = weekly_summary['Duration'].sum()
    avg_hours = weekly_summary['Duration'].mean()
    st.metric(label="Total Hours Spent", value=f"{total_hours:.2f} hours")
    st.metric(label="Average Hours per Week", value=f"{avg_hours:.2f} hours")
