"""

Script for building Streamlit app

"""

import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import plotly.express as px

# Input data filepaths
DATA_DIR = "./data/preprocessed/"
ADMIN1_FILEPATH = f"{DATA_DIR}app_admin1_aggregated.parquet"
COUNTRY_FILEPATH = f"{DATA_DIR}app_country_aggregated.parquet"
SUBREGION_FILEPATH = f"{DATA_DIR}app_subregion_aggregated.parquet"
ANNUAL_GLOBAL_FILEPATH = f"{DATA_DIR}app_annual_global_totals.parquet"
LAND_OUTLINE_FILEPATH = f"{DATA_DIR}app_land_outline.parquet"

# Global text colors
HEADER_COLOR = "#003D5C"

# Plot styling
PLOT_HEIGHT = 600
PLOT_BG_COLOR = "white"
WATER_COLOR = "#E6F7FF"
GRID_COLOR = "lightgray"

# Widget defaults
DEFAULT_VARIABLE = "Economic Damages"
DEFAULT_NORMALIZE = True
DEFAULT_REGION = "Admin1 (States/Provinces)"
DEFAULT_AGG_METRIC = "Mean"
DEFAULT_NUM_REGIONS = 15
MAX_NUM_REGIONS = 30

# Variable descriptions
VARIABLE_DESCRIPTIONS = {
    "Economic Damages": {
        "long_name": "Total economic damages adjusted to 2023 U.S dollar equivalent.",
        "norm_descrip": "Normalized by GDP",
    },
    "Population Affected": {
        "long_name": "Number of people injured, made homeless, or otherwise impacted by the flood.",
        "norm_descrip": "Normalized by total population",
    },
    "Flooded Area": {
        "long_name": "Total inundated area derived from MODIS satellite imagery.",
        "norm_descrip": "Normalized by total area",
    },
    "Flood Count": {"long_name": "Number of recorded floods.", "norm_descrip": ""},
    "Avg Precipitation (Flood)": {
        "long_name": "Average precipitation rate during floods.",
        "norm_descrip": "",
    },
    "Avg 75th Percentile Precipitation (Flood)": {
        "long_name": "Average of the top 25% of precipitation rates during floods. Indicates heavy rainfall.",
        "norm_descrip": "",
    },
}

# Variable-specific color palettes
COLOR_PALETTES = {
    "Flooded Area": [
        "#E3F2FD",
        "#90CAF9",
        "#42A5F5",
        "#1E88E5",
        "#1565C0",
        "#0D47A1",
    ],  # Blues
    "Economic Damages": [
        "#E8F5E9",
        "#81C784",
        "#66BB6A",
        "#4CAF50",
        "#388E3C",
        "#1B5E20",
    ],  # Greens
    "Population Affected": [
        "#F3E5F5",
        "#CE93D8",
        "#BA68C8",
        "#AB47BC",
        "#8E24AA",
        "#6A1B9A",
    ],  # Purples
    "Flood Count": [
        "#FFEBEE",
        "#EF9A9A",
        "#E57373",
        "#EF5350",
        "#E53935",
        "#C62828",
    ],  # Reds
    "Avg Precipitation (Flood)": [
        "#E3F2FD",
        "#90CAF9",
        "#42A5F5",
        "#1E88E5",
        "#1565C0",
        "#0D47A1",
    ],  # Blues (same as Flooded Area)
    "Avg 75th Percentile Precipitation (Flood)": [
        "#E3F2FD",
        "#90CAF9",
        "#42A5F5",
        "#1E88E5",
        "#1565C0",
        "#0D47A1",
    ],  # Blues (same as Flooded Area)
}


# Helper functions
def get_plot_title_config(title_text):
    """Create standardized title configuration for plots"""
    return dict(
        text=title_text, x=0.5, xanchor="center", font=dict(size=20, color=HEADER_COLOR)
    )


def generate_title(variable, agg_metric, normalize):
    """Generate appropriate title based on variable and normalization"""
    if variable == "Flood Count":
        return "Flood Event Count"

    # Precipitation variables don't use normalization
    precip_vars = [
        "Avg Precipitation (Flood)",
        "Avg 75th Percentile Precipitation (Flood)",
    ]
    if variable in precip_vars:
        return f"{agg_metric} {variable}"

    if normalize:
        norm_labels = {
            "Economic Damages": f"{agg_metric} Economic Damages (% of GDP)",
            "Population Affected": f"{agg_metric} Population Affected (% of Total)",
            "Flooded Area": f"{agg_metric} Flooded Area (% of Total Area)",
        }
        return norm_labels.get(variable, f"{agg_metric} {variable}")

    return f"{agg_metric} {variable}"


# Set title
st.set_page_config(page_title="Global Flood Analysis", layout="wide")


# Read in data - will load appropriate file based on region selection
@st.cache_data
def load_regional_data(region):
    """Load pre-aggregated data with geometries based on region selection"""
    if region == "Admin1 (States/Provinces)":
        return gpd.read_parquet(ADMIN1_FILEPATH)
    elif region == "Country":
        return gpd.read_parquet(COUNTRY_FILEPATH)
    else:  # UN Subregion
        return gpd.read_parquet(SUBREGION_FILEPATH)


@st.cache_data
def load_annual_data():
    """Load annual global totals for timeseries"""
    return pd.read_parquet(ANNUAL_GLOBAL_FILEPATH)


@st.cache_data
def load_land_outline():
    """Load land outline for continent borders"""
    return gpd.read_parquet(LAND_OUTLINE_FILEPATH)


# Apply styling
st.markdown(
    """
    <style>
    /* Tabs - Full width tab style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background-color: transparent;
        width: 100%;
        display: flex;
    }

    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.2rem;
        font-weight: 600;
        background-color: #f0f2f6;
        border-radius: 0px;
        padding: 16px 24px;
        border: none;
        border-bottom: 3px solid transparent;
        flex: 1;
    }

    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: white;
        border-bottom: 3px solid;
    }

    .stTabs [data-baseweb="tab-list"] button:hover {
        background-color: #e8eaed;
    }

    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Main content
st.title(f"Global Flood Analysis Dashboard")

# Helper mappings
var_map = {
    "Economic Damages": ("damages", "damages_norm"),
    "Population Affected": ("pop_affected", "pop_affected_norm"),
    "Flooded Area": ("flooded_area", "flooded_area_norm"),
    "Flood Count": (None, None),
    "Avg Precipitation (Flood)": ("avg_precip", None),
    "Avg 75th Percentile Precipitation (Flood)": ("extreme_precip_75", None),
}

region_id_map = {
    "Admin1 (States/Provinces)": "adm1_code",
    "Country": "ISO",
    "UN Subregion": "UN Subregion",
}

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["Map View", "Top Regions", "Annual Totals (Global)", "About"]
)

# ========== MAP TAB ==========
with tab1:

    @st.fragment
    def map_fragment():
        """Independent map visualization with its own controls"""

        # Controls in a vertical column
        with st.container():
            col1, col2 = st.columns([1, 4])

            with col1:
                variable = st.selectbox(
                    "Variable",
                    [
                        "Economic Damages",
                        "Population Affected",
                        "Flooded Area",
                        "Flood Count",
                        "Avg Precipitation (Flood)",
                        "Avg 75th Percentile Precipitation (Flood)",
                    ],
                    index=0,
                    key="map_variable",
                )
                st.caption(VARIABLE_DESCRIPTIONS[variable]["long_name"])

                precip_vars = [
                    "Avg Precipitation (Flood)",
                    "Avg 75th Percentile Precipitation (Flood)",
                ]
                if variable not in ["Flood Count"] + precip_vars:
                    normalize = st.checkbox(
                        "Normalize", value=True, key="map_normalize"
                    )
                    if VARIABLE_DESCRIPTIONS[variable]["norm_descrip"]:
                        st.caption(VARIABLE_DESCRIPTIONS[variable]["norm_descrip"])
                else:
                    normalize = False

                region = st.selectbox(
                    "Geographic Level",
                    ["Admin1 (States/Provinces)", "Country", "UN Subregion"],
                    index=0,
                    key="map_region",
                )

                agg_metric = st.selectbox(
                    "Statistic",
                    ["Mean", "Median", "Max", "Sum"],
                    index=0,
                    key="map_agg",
                )

            with col2:
                # Load data
                geo_data = load_regional_data(region)

                # Build column name
                if variable == "Flood Count":
                    value_col = "flood_count"
                else:
                    base_col, norm_col = var_map[variable]
                    base_name = norm_col if (normalize and norm_col) else base_col
                    value_col = f"{base_name}_{agg_metric.lower()}"

                title = generate_title(variable, agg_metric, normalize)
                current_colors = COLOR_PALETTES[variable]

                # Determine location and name columns
                location_col = region_id_map[region]
                if region == "Admin1 (States/Provinces)":
                    name_col = "Admin1 (States/Provinces)"
                elif region == "Country":
                    name_col = "Country"
                else:
                    name_col = "UN Subregion"

                with st.spinner("Loading map (expect 10-15 second lag for Admin1)..."):
                    # Load country boundaries
                    country_borders = gpd.read_parquet(COUNTRY_FILEPATH)

                    # Create map
                    fig = px.choropleth_mapbox(
                        geo_data,
                        geojson=geo_data.geometry,
                        locations=geo_data.index,
                        color=value_col,
                        color_continuous_scale=current_colors,
                        mapbox_style="white-bg",
                        center={"lat": 20, "lon": 0},
                        zoom=0.8,
                        opacity=1.0,
                    )

                    fig.update_traces(marker_line_width=0.2, marker_line_color="white")

                    # Add hover
                    if name_col in geo_data.columns:
                        customdata = np.column_stack(
                            [
                                geo_data[name_col],
                                geo_data[location_col],
                                geo_data[value_col],
                            ]
                        )
                        hover_template = "<b>%{customdata[0]}</b><br>Code: %{customdata[1]}<br>Value: %{customdata[2]:.2f}<extra></extra>"
                        fig.update_traces(
                            customdata=customdata, hovertemplate=hover_template
                        )

                    # Add country borders
                    country_trace = px.choropleth_mapbox(
                        country_borders,
                        geojson=country_borders.geometry,
                        locations=country_borders.index,
                        color_discrete_sequence=["rgba(0,0,0,0)"],
                        mapbox_style="white-bg",
                    ).data[0]

                    country_trace.marker.line.width = 0.5
                    country_trace.marker.line.color = "#A9A9A9"
                    country_trace.showlegend = False
                    country_trace.hoverinfo = "skip"
                    country_trace.hovertemplate = None

                    fig.add_trace(country_trace)

                    fig.update_layout(
                        height=PLOT_HEIGHT,
                        font=dict(color=HEADER_COLOR),
                        title=get_plot_title_config(f"{title} by {region}"),
                        margin={"r": 0, "t": 50, "l": 0, "b": 0},
                    )

                    st.plotly_chart(fig, width="stretch")

    map_fragment()

# ========== BAR CHART TAB ==========
with tab2:

    @st.fragment
    def bar_fragment():
        """Independent bar chart with its own controls"""

        # Controls in a vertical column
        with st.container():
            col1, col2 = st.columns([1, 4])

            with col1:
                variable = st.selectbox(
                    "Variable",
                    [
                        "Economic Damages",
                        "Population Affected",
                        "Flooded Area",
                        "Flood Count",
                        "Avg Precipitation (Flood)",
                        "Avg 75th Percentile Precipitation (Flood)",
                    ],
                    index=0,
                    key="bar_variable",
                )
                st.caption(VARIABLE_DESCRIPTIONS[variable]["long_name"])

                precip_vars = [
                    "Avg Precipitation (Flood)",
                    "Avg 75th Percentile Precipitation (Flood)",
                ]
                if variable not in ["Flood Count"] + precip_vars:
                    normalize = st.checkbox(
                        "Normalize", value=True, key="bar_normalize"
                    )
                    if VARIABLE_DESCRIPTIONS[variable]["norm_descrip"]:
                        st.caption(VARIABLE_DESCRIPTIONS[variable]["norm_descrip"])
                else:
                    normalize = False

                region = st.selectbox(
                    "Geographic Level",
                    ["Admin1 (States/Provinces)", "Country", "UN Subregion"],
                    index=0,
                    key="bar_region",
                )

                agg_metric = st.selectbox(
                    "Statistic",
                    ["Mean", "Median", "Max", "Sum"],
                    index=0,
                    key="bar_agg",
                )

                max_regions = 15 if region == "UN Subregion" else 30
                num_regions = st.slider(
                    "Number of regions",
                    min_value=5,
                    max_value=max_regions,
                    value=15,
                    step=1,
                    key="bar_num",
                )

            with col2:
                # Load data
                geo_data = load_regional_data(region)

                # Build column name
                if variable == "Flood Count":
                    value_col = "flood_count"
                else:
                    base_col, norm_col = var_map[variable]
                    base_name = norm_col if (normalize and norm_col) else base_col
                    value_col = f"{base_name}_{agg_metric.lower()}"

                title = generate_title(variable, agg_metric, normalize)
                current_colors = COLOR_PALETTES[variable]

                # Determine display names
                if region == "Admin1 (States/Provinces)":
                    if (
                        "Admin1 (States/Provinces)" in geo_data.columns
                        and "Country" in geo_data.columns
                    ):
                        geo_data_copy = geo_data.copy()
                        geo_data_copy["Display Name"] = (
                            geo_data_copy["Admin1 (States/Provinces)"].astype(str)
                            + ", "
                            + geo_data_copy["Country"].astype(str)
                        )
                        display_col = "Display Name"
                        top_n = (
                            geo_data_copy[[display_col, value_col]]
                            .nlargest(num_regions, value_col)
                            .copy()
                        )
                    else:
                        display_col = region_id_map[region]
                        top_n = (
                            geo_data[[display_col, value_col]]
                            .nlargest(num_regions, value_col)
                            .copy()
                        )
                elif region == "Country":
                    display_col = (
                        "Country"
                        if "Country" in geo_data.columns
                        else region_id_map[region]
                    )
                    top_n = (
                        geo_data[[display_col, value_col]]
                        .nlargest(num_regions, value_col)
                        .copy()
                    )
                else:
                    display_col = (
                        "UN Subregion"
                        if "UN Subregion" in geo_data.columns
                        else region_id_map[region]
                    )
                    top_n = (
                        geo_data[[display_col, value_col]]
                        .nlargest(num_regions, value_col)
                        .copy()
                    )

                top_n.columns = ["Region", title]
                top_n = top_n.reset_index(drop=True)
                top_n.index = top_n.index + 1

                # Create bar chart
                bar_fig = px.bar(
                    top_n,
                    x=title,
                    y="Region",
                    orientation="h",
                    color=title,
                    color_continuous_scale=current_colors,
                    labels={title: title, "Region": ""},
                )

                bar_fig.update_layout(
                    height=PLOT_HEIGHT,
                    showlegend=False,
                    yaxis={"categoryorder": "total ascending"},
                    font=dict(color=HEADER_COLOR),
                    plot_bgcolor=PLOT_BG_COLOR,
                    paper_bgcolor=PLOT_BG_COLOR,
                    title=get_plot_title_config(title),
                    coloraxis_showscale=False,
                )

                bar_fig.update_traces(
                    hovertemplate="<b>%{y}</b><br>"
                    + title
                    + ": %{x:.2f}<extra></extra>"
                )

                st.plotly_chart(bar_fig, width="stretch")

    bar_fragment()

# ========== TIMESERIES TAB ==========
with tab3:

    @st.fragment
    def timeseries_fragment():
        """Independent timeseries with its own controls"""

        # Controls in a vertical column
        with st.container():
            col1, col2 = st.columns([1, 4])

            with col1:
                variable = st.selectbox(
                    "Variable",
                    [
                        "Economic Damages",
                        "Population Affected",
                        "Flooded Area",
                        "Flood Count",
                    ],
                    index=0,
                    key="ts_variable",
                )
                st.caption(VARIABLE_DESCRIPTIONS[variable]["long_name"])

                # Always use raw (non-normalized) values for timeseries
                normalize = False

            with col2:
                # Load data
                annual_data = load_annual_data()

                # Select column
                if variable == "Flood Count":
                    ts_col = "flood_count"
                    ts_label = f"Total {variable} by Year"
                else:
                    base_col, norm_col_name = var_map[variable]
                    ts_col = (
                        norm_col_name if (normalize and norm_col_name) else base_col
                    )
                    ts_label = f"Total {variable} by Year"

                current_colors = COLOR_PALETTES[variable]

                # Create bar chart
                bar_fig = px.bar(
                    annual_data,
                    x="year",
                    y=ts_col,
                    labels={"year": "Year", ts_col: ts_label},
                    color=ts_col,
                    color_continuous_scale=current_colors,
                )

                bar_fig.update_layout(
                    height=PLOT_HEIGHT,
                    font=dict(color=HEADER_COLOR),
                    plot_bgcolor=PLOT_BG_COLOR,
                    paper_bgcolor=PLOT_BG_COLOR,
                    showlegend=False,
                    title=get_plot_title_config(f"{ts_label} Over Time"),
                    coloraxis_showscale=False,
                )

                bar_fig.update_xaxes(showgrid=True, gridcolor=GRID_COLOR)
                bar_fig.update_yaxes(showgrid=True, gridcolor=GRID_COLOR)

                st.plotly_chart(bar_fig, width="stretch")

    timeseries_fragment()

# ========== ABOUT TAB ==========
with tab4:
    st.subheader("About This Project")
    st.markdown("Master's Thesis, Colorado State University, 2025")

    st.markdown("### Data Sources")
    st.markdown(
        """
    This application visualizes flood event data derived from multiple sources:
    - **EM-DAT International Disaster Database**: Disaster impact metrics including economic damages, population affected, and event records
    - **MODIS Surface Reflectance Imagery**: Satellite-derived flood extent and duration data
    - **Other geospatial and demographic datasets**
    """
    )

    st.markdown("### Author")
    st.markdown(
        """
        <div style="margin-top: 10px;">
            <div>Nicole Keeney</div>
            <div style="margin-top: 10px;">
                <a href="https://linkedin.com/in/nicole-keeney" target="_blank" style="text-decoration: none; margin-right: 10px;">
                    <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="20" height="20" style="vertical-align: middle;">
                </a>
                <a href="https://github.com/nicolejkeeney" target="_blank" style="text-decoration: none;">
                    <img src="https://cdn-icons-png.flaticon.com/512/25/25231.png" width="20" height="20" style="vertical-align: middle;">
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
