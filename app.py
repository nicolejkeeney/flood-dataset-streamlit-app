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
PLOT_HEIGHT = 500  # Balanced height that works for both desktop and mobile
PLOT_BG_COLOR = "white"
WATER_COLOR = "#E6F7FF"
GRID_COLOR = "lightgray"

# Widget defaults
DEFAULT_VARIABLE = "Economic Damages"
DEFAULT_REGION = "Admin1 (States/Provinces)"
DEFAULT_AGG_METRIC = "Mean"
DEFAULT_NUM_REGIONS = 15
MAX_NUM_REGIONS = 30

# Variable descriptions
VARIABLE_DESCRIPTIONS = {
    "Economic Damages": {
        "long_name": "Total economic damages adjusted to 2023 U.S dollar equivalent.",
    },
    "Population Affected": {
        "long_name": "Number of people injured, made homeless, or otherwise impacted by the flood.",
    },
    "Flooded Area": {
        "long_name": "Total inundated area derived from MODIS satellite imagery.",
    },
    "Flood Count": {
        "long_name": "Number of recorded floods.",
    },
    "Avg Precipitation (Flood)": {
        "long_name": "Average precipitation rate during floods.",
    },
    "Avg 75th Percentile Precipitation (Flood)": {
        "long_name": "Average of the top 25% of precipitation rates during floods. Indicates heavy rainfall.",
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
        text=title_text, x=0.5, xanchor="center", font=dict(size=26, color=HEADER_COLOR)
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
st.set_page_config(
    page_title="Global Flood Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)


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
    /* Mobile-specific improvements */
    @media (max-width: 768px) {
        /* Better spacing for mobile */
        .main .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 1rem !important;
        }

        /* Make title more readable */
        h1 {
            font-size: 1.5rem !important;
            line-height: 1.3 !important;
        }

        h2 {
            font-size: 1.2rem !important;
        }

        /* Better paragraph spacing */
        p {
            font-size: 0.95rem !important;
            line-height: 1.4 !important;
        }

        /* Make images responsive */
        img {
            max-width: 100% !important;
            height: auto !important;
        }
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Main content
st.title(f"Global Flood Analysis Dashboard")
st.markdown(
    "Explore a spatially and temporally disaggregated 21st century flood impact dataset (2000-2024)."
)
st.markdown(
    "Click through the tabs to find more information about the project and explore flood impacts and characteristics by region, time, and variable."
)

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

# Create navigation
view = st.selectbox(
    "Select View",
    ["Global Annual Trends", "Map View", "Top Regions", "Methods", "About"],
    label_visibility="collapsed"
)

# ========== MAP VIEW ==========
if view == "Map View":

    @st.fragment
    def map_fragment():
        """Independent map visualization with its own controls"""

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

            normalize  = st.selectbox(
                "Normalize Variable?",
                [True,False]
            )

            region = st.selectbox(
                "Geographic Level",
                ["Admin1 (States/Provinces)", "Country", "UN Subregion"],
                index=1,
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

            with st.spinner("Loading map (expect 10-15 second lag)..."):
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
                    autosize=True,
                    font=dict(color=HEADER_COLOR),
                    title=get_plot_title_config(f"{title} by {region}"),
                    margin={"r": 0, "t": 50, "l": 0, "b": 0},
                )

                st.plotly_chart(fig, use_container_width=True)

    map_fragment()

# ========== TOP REGIONS ==========
elif view == "Top Regions":

    @st.fragment
    def bar_fragment():
        """Independent bar chart with its own controls"""

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

            normalize  = st.selectbox(
                "Normalize Variable?",
                [True,False]
            ) 

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
                autosize=True,
                showlegend=False,
                yaxis={"categoryorder": "total ascending"},
                font=dict(color=HEADER_COLOR),
                plot_bgcolor=PLOT_BG_COLOR,
                paper_bgcolor=PLOT_BG_COLOR,
                title=get_plot_title_config(title),
                coloraxis_showscale=False,
                margin={"l": 10, "r": 10, "t": 50, "b": 10},
            )

            bar_fig.update_traces(
                hovertemplate="<b>%{y}</b><br>"
                + title
                + ": %{x:.2f}<extra></extra>"
            )

            st.plotly_chart(bar_fig, use_container_width=True)

    bar_fragment()

# ========== GLOBAL ANNUAL TRENDS ==========
elif view == "Global Annual Trends":

    @st.fragment
    def timeseries_fragment():
        """Independent timeseries with its own controls"""

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
                base_col, _ = var_map[variable]
                # COMMENTED OUT - normalization disabled, always use raw values
                # ts_col = (
                #     norm_col_name if (normalize and norm_col_name) else base_col
                # )
                ts_col = base_col  # Always use raw (non-normalized) column
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
                autosize=True,
                font=dict(color=HEADER_COLOR),
                plot_bgcolor=PLOT_BG_COLOR,
                paper_bgcolor=PLOT_BG_COLOR,
                showlegend=False,
                title=get_plot_title_config(ts_label),
                coloraxis_showscale=False,
                margin={"l": 10, "r": 10, "t": 50, "b": 10},
            )

            bar_fig.update_xaxes(showgrid=True, gridcolor=GRID_COLOR)
            bar_fig.update_yaxes(showgrid=True, gridcolor=GRID_COLOR)

            st.plotly_chart(bar_fig, use_container_width=True)

    timeseries_fragment()

# ========== METHODS ==========
elif view == "Methods":
    st.markdown("## Methods")

    st.markdown("### Summary")
    st.markdown(
        "This project involved a lengthy data processing pipeline with the end goal of creating a  global dataset of inland floods from 2000–2024 at the scale of subnational regions and months. Data processing involved substantial data preparation—cleaning, infilling missing values, and standardization—as well as regridding, reprojecting, merging, and slicing-and-dicing of several datasets of different flavors to arrive at the end product. All data wrangling was performed in Python and included simple tabular data cleaning and standarization, satellite data processing using Google Earth Engine's python API, and more computationally heavy geospatial processing run on Colorado State's trusty high-performance computing cluster, Cashew."
    )
    st.markdown("")
    st.markdown(
        "Both the **data processing code** and the **code for this app** are publicly available on GitHub:"
    )
    st.markdown(
        """
    - Data processing pipeline: [nicolejkeeney/emdat-modis-flood-dataset](https://github.com/nicolejkeeney/emdat-modis-flood-dataset)
    - This Streamlit app: [nicolejkeeney/flood-dataset-streamlit-app](https://github.com/nicolejkeeney/flood-dataset-streamlit-app)
    """
    )

    st.markdown("### Data Sources Overview")
    st.markdown(
        """
    - **EM-DAT disaster records**: International disaster database providing flood event records and reported impacts
    - **MODIS surface reflectance**: Satellite imagery (Terra/Aqua) for flood detection via Google Earth Engine Python API 
    - **MSWEP precipitation**: Bias-corrected product that combines satellite retrievals and reanalysis precipitation data, as well as gauge observations for data pre-2020
    - **GPW v4**: Gridded Population of the World for population-weighting
    - **GAUL 2015**: Global Administrative Unit Layers (admin level 1 boundaries)
    """
    )

    st.markdown("### Data Processing Pipeline")
    st.markdown("#### 1. Preprocess EM-DAT flood event catalog for geospatial analysis")
    st.markdown(
        """
    We analyze inland flood events from the EM-DAT disaster database, a standardized, international hazard dataset that includes event information for floods and other natural and anthropogenic hazards (Delforge et al., 2025). For an event to be included in the EM-DAT database, it must meet one of the following three criteria: ten or more deaths (including dead and missing), 100 or more people affected, and any call for international assistance or an emergency declaration. The dataset is provided in tabular format and includes numerous variables such as economic damages, the number of people affected, location information, and other relevant details for each hazard event. For our analysis, we subset the EM-DAT database to include all inland floods from 2000-2024. This subset consists of 4073 total events, of which 49.3% are classified as riverine floods, 17.3% as flash floods, and 33.4% as general floods. We focus on inland floods rather than coastal floods because the environmental drivers of the latter are more often oceanic (i.e. coastal surge) rather than atmospheric (i.e. precipitation).

    We consider two impact variables from the EM-DAT records: total damages in U.S. dollars adjusted for inflation and total number of affected people. In EM-DAT, total damages for events up until 2023 have already been adjusted to 2023 U.S dollar equivalent. We use the same adjustment procedure as EM-DAT to calculate 2023 equivalent damages for all events in 2024 based on the Organization for Economic Cooperation and Development (OECD) Consumer Price Index (Organisation for Economic Co-operation and Development, n.d.). Total affected people is defined as the combined number of people injured, made homeless, or otherwise impacted by the event. Notably, this number does not include fatalities, which are recorded in a separate field and excluded from our population-weighted impact estimates due to their comparatively low magnitude relative to the total number people affected.

    Given the nature of a human-compiled database and the complex realities of characterizing flood and impact data, the EM-DAT database has missing or incomplete data. We aim to maximize the total number of events in our analysis by infilling missing values for event dates and location when appropriate. If the flood start day is missing, we infill that value with the first day of the month (we apply this step for 278 events; 6.8% of total). Similarly, if the end date is missing, we infill that value with the last day of the month (applied for 268 events; 6.6% of total). If a flood is missing a start/end month or year, it is deemed too subjective for manual infilling and is dropped from our subset.

    We also address missing spatial information. EM-DAT provides location data through four fields: "Country," "River Basin," "Location" (narrative descriptions of affected places), and "Admin Units" (structured administrative codes and names). The "Admin Units" field maps directly to the 2015 Global Administrative Unit Layers (GAUL) dataset, which defines polygon boundaries for administrative regions worldwide at level 1 (states/provinces) and level 2 (counties/districts/municipalities) (Food and Agriculture Organization of the United Nations, 2015). While some event records contain level 2 location information (county/district/municipality level), many events only contain level 1 information. For this reason, we focus our analysis at the admin 1 (state/province) level. For most events, we use the "Admin Units" field to directly match flood events to affected level 1 regions, but 290 events (7.1% of total) lack this information. We manually infilled missing entries using the "Location" string (275 events) or news reports (15 events) when location strings were also absent. This infilling was particularly necessary for recent years, as many 2022-2023 events and all 2024 events lacked data in the "Admin Units" field. Some administrative regions underwent renaming or rezoning after 2015, when administrative regions in the GAUL dataset are defined. To address this, post-2015 flood events in renamed or rezoned regions were remapped to their 2015-equivalent boundaries for consistency. The infilled flood event catalog includes 4073 inland flood events across 2375 unique admin1 regions across 177 countries. A substantial subset of events in EM-DAT also contain empty fields for one or more flood impact variables. Missing flood impact information is addressed in a later step when we apply the panel regression analysis.

    Following initial data infilling steps, flood events are disaggregated into separate months and admin 1 regions using the location and date information. The goal of the disaggregation step is to produce a dataset with a consistent spatial (admin 1) and temporal (monthly) resolution, which is a requirement of fixed-effect panel regression methods. Disaggregated events are referred to hereafter as admin1-month events. During the event disaggregation process, each unique admin code is extracted from the "Admin Units" field, and second-level administrative regions are mapped to their corresponding first-level region using the GAUL database. Events are disaggregated so that each admin1-month event corresponds to a single month and a single administrative 1 region. For events that span multiple months, the start and end dates for each admin1-month event is adjusted to the portion of the event that falls within that month. For example, an event occurring within a single administrative 1 region with a start date of May 27 and an end date of June 2 would be split into two admin1-month events: the first spanning May 27-31 and the other spanning June 1-2. Similarly, events covering multiple regions are split so that each admin1-month event represents only one administrative 1 region. Each admin1-month event is then assigned a unique ID linking it to the corresponding month, administrative 1 code, and original event ID, as shown in the schematic below.
    """
    )

    # Hacky solution to get high res, centered image on the page
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image(
            "data/figs/event_disag_process_schematic.png",
            caption="Event disaggregation process",
            use_container_width=True,
        )

    st.markdown(
        "#### 2. Compute satellite-derived flood maps and flood-exposed population"
    )
    st.markdown(
        """
    Satellite imagery allows us to provide additional fine-scale flood information that is not available in human-reported event records. For each admin1-month event, we use MODIS satellite imagery to generate a high-resolution map of flooded pixels using a modified version of the inundated flood detection algorithm outlined in Tellman et al. (2021) and further detailed in their open source code repository (CloudToStreet, 2021). Here, we provide a summary of the algorithm, outline our modifications, and discuss its limitations. For more comprehensive details about the algorithm, we refer the reader to the Tellman manuscript.

    In brief, the algorithm works as follows. First, Google Earth Engine's (GEE) Python API  is used for retrieving surface reflectance imagery from NASA's MODIS sensors aboard the Terra (entire study duration) and Aqua (after July 2002) satellites. The water detection algorithm then utilizes the short-wave-infrared, near-infrared, and red bands from the surface reflectance data, along with fixed, empirically-derived threshold values, to classify each pixel as either water (1) or non-water (0). The water detection algorithm is applied across all 250m MODIS pixels within the flood event geometry, defined as the bounding box of the GAUL polygon of the corresponding admin 1 region. Dates covering the full admin1-month event duration plus a one-day buffer before and after the event are retrieved. This means that the number of days used in the detection algorithm is as short as 3 days for an event with a single day duration, or as long as 33 days for an event with 31-day (full month) duration, with the buffer days on either side. Detection never exceeds 33 days because admin1-month events are, by definition, limited to a maximum of one month.

    Our modified multi-day composite method uses a 3-day window centered on the retrieval date of the image. With two satellite overpasses per day, each single-day composite incorporates up to six observations. A pixel is classified as water if at least three of the six observations indicate water presence. Tellman et al. (2021) found that using a multiday composite reduced the rate of false positives. The algorithm then applies a terrain slope mask and permanent water mask to distinguish floodwater from permanent surface water and to further reduce false positives due to terrain or cloud shadows. The final flood map for a given admin1-month event combines all daily composites from the event into a single image, where a pixel is classified as inundated if it was identified as inundated on any day during the event.

    Population density data are sourced from NASA's Gridded Population of the World (GPW) dataset, which provides global estimates of population density at 1km resolution in 5-year intervals (Center For International Earth Science Information Network-CIESIN-Columbia University, 2018). We reproject this population density dataset to the finer spatial grid and projection (250m, EPSG:4326) of the satellite-derived flood maps using a bilinear reprojection method so the two datasets can be used together. Grid cell areas are then calculated with the Python package "xemsf" (Zhuang et al., 2025), and population counts are derived by multiplying population density by cell area. Finally, for each admin1-month event, we compute the total population within the flood zone by masking the population raster with the corresponding flood map and summing the population count of the flooded cells. For each admin1-month event, the population density raster corresponding to the closest preceding GPW release year is used—e.g., events occurring in 2003 use population data from the year 2000.
    """
    )

    st.markdown(
        "#### 3. Allocate EM-DAT flood impacts across disaggregated admin1-month flood events"
    )
    st.markdown(
        """
    To compare flood impacts on a consistent admin1-month scale, we distribute the impacts of floods that span multiple administrative regions and/or months across the corresponding admin1-month events. For most floods, we are able to compute population-weighted impacts to better capture the uneven distribution of impacts across different months and administrative regions. This process relies on three data sources: the satellite-derived flood maps for each admin1-month event, gridded global population density estimates, and the EM-DAT impact data.

    Three approaches are used to allocate impacts across admin1-month events for each flood, depending on the results of the satellite-derived flood maps:

    - **Case 1**: All admin1-month events have non-zero flood maps (i.e. flooded pixels were detected in every admin 1 region in every month). Population-weighted impacts are calculated by multiplying each event's fractional flooded population by the impact variables from that flood (approach #1). More specifically, fractional population is defined as the satellite-derived flooded population for that admin1-month event divided by the total satellite-derived flooded population across all admin1-month events for the flood.

    - **Case 2**: All events have either zero detected flooded pixels or the flood maps are unable to be generated due to internal GEE errors. In this case, the impact variables are divided equally across all admin1-month events (approach #2).

    - **Case 3**: Some admin1-month events have flooded pixels while others do not. Here, a hybrid approach is used in order to maintain information from the non-zero flood maps (approach #3). In this hybrid method, a small baseline fraction (5%) of the total impact is allocated equally among all events with zero flooded pixels (following approach #2), while the remaining 95% is distributed among events with detected flooding, weighted by their flooded population (following approach #1).

    Altogether, for 55% of floods we allocate impacts to admin1-events using approach #1, for 19% of events using approach #2, and 26% of events using approach #3.

    To account for differences in economic conditions, population density, and geographic area across admin1 regions and years, we normalize flood impacts to enable comparisons across regions. GDP-standardized economic damages are calculated as the damages divided by the admin1 region's yearly GDP, expressed as a percentage. The computation utilizes the mean GDP per capita for each year and admin1 region, which we extract from the global gridded yearly GDP per capita dataset at 5 arc-minute resolution from Kummu et al. (2025). Because the Kummu dataset is only available through 2022, we use the 2022 GDP values for events in 2023 and 2024. Similarly, the total people affected are expressed as a percentage of the total admin1 population (using GPW-derived population count), and total flooded area is expressed as a percentage of the total area of the admin1 region (using GAUL-derived areas).
    """
    )

    st.markdown(
        "#### 4. Extract monthly precipitation standardized anomalies at admin1-month level"
    )
    st.markdown(
        """
    Historical precipitation data enable us to add a climatological dimension to our flood dataset. For each admin1 region, we calculate the area-averaged daily mean and 75th percentile precipitation using the open-source Python package "exact_extract" (Baston, 2025). These calculations use daily 0.1° resolution data from GloH2O's Multi-Source Weighted-Ensemble Precipitation (MSWEP) dataset for 2000–2024 (Beck et al., 2019), a bias-corrected product that combines satellite retrievals and reanalysis precipitation data, as well as gauge observations for data pre-2020. For each of the precipitation variables, we compute the mean and standard deviation within each admin1 region across the 2000-2024 time period, and use these values to transform each monthly value into a standardized anomaly.
    """
    )

    st.markdown(
        "#### 5. Validation of satellite flood map detection and event disaggregation results"
    )
    st.markdown(
        """
    We compare our satellite-derived flooded population estimates to the total number of people affected during each event as reported in EM-DAT. This comparison allows us to evaluate how well satellite-based flooded population estimates reproduce reported flood impacts. The satellite-derived flooded population estimates (aggregated across all admin1-month events per flood) are positively correlated with the total number of people affected per flood as reported by EM-DAT (R² = 0.20, slope = 0.35, p < 0.001), indicating a statistically significant relationship between independent satellite-based exposure metrics and reported disaster impacts. The satellite-derived flooded population estimates are consistently lower than the EM-DAT total affected population, likely due to the following two factors. First, flood impacts extend far beyond the flood zone. People not directly located in inundated areas can still be impacted by floods due to destruction of key infrastructure like bridges, roads, or hospitals, or impeded access to food, water, or medicine. Second, the water detection algorithm likely underestimates the true extent of flooding, especially during short-duration flooding (as detailed below), which would correspondingly reduce the satellite-derived flooded population estimates.
    """
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(
            "data/figs/emdat_modis_regression.png",
            caption="Regression line on a log scale illustrating the relationship between the total number of people affected per flood and satellite-derived flooded population estimates. For each flood, flooded pixel estimates were generated for individual admin1-month events and then summed to provide a total value at the same flood-level scale of the EM-DAT reported impacts.",
            use_container_width=True,
        )
    st.markdown(
        """
    There are several limitations to the water detection algorithm that can result in misclassifications of pixels. Tellman et al. (2021) found that the water detection algorithm frequently underdetected flooded pixels for a number of reasons, including extreme cloud cover during the event, incorrect start and end dates reported in the event catalogue that don't actually encompass the full flood period, and challenges in detecting short-duration floods (such as flash floods) and urban flooding where flooded streets or channels may be much smaller than the MODIS 250m resolution. Using our modified water detection algorithm, 24% of the admin1-month events produce flood maps with no detected floodwater. Events with zero flooded pixels detected are predominantly short in duration, with a median of only 5 days (versus 13 days for events with detected flooded pixel maps), confirming the algorithm's limitations with detecting floodwaters for short duration events. Given these limitations, we anticipate that the flooded pixel counts for each event represent conservative estimates of the true flooded extent.
    """
    )

    col1, col2, col3 = st.columns([3, 4, 3])
    with col2:
        st.image(
            "data/figs/event_duration_flooded_pixels_violinplot.png",
            caption="Comparison of event duration for floods with and without successful flooded pixel detection, showing that events without detectable flooding are predominantly shorter in duration (note that, by definition, the maximum monthly flood duration is 30 or 31 days).",
            use_container_width=True,
        )

    st.markdown("### References")
    st.markdown(
        """
    Baston, D. (2025). exactextract. Retrieved from https://github.com/isciences/exactextract/releases/tag/v0.2.2

    Beck, H. E., Wood, E. F., Pan, M., Fisher, C. K., Miralles, D. G., Dijk, A. I. J. M. van, et al. (2019). MSWEP V2 Global 3-Hourly 0.1° Precipitation: Methodology and Quantitative Assessment. *Bulletin of the American Meteorological Society*, *100*(3), 473–500. https://doi.org/10.1175/BAMS-D-17-0138.1

    Center For International Earth Science Information Network-CIESIN-Columbia University. (2018). Gridded Population of the World, Version 4 (GPWv4): Population Count, Revision 11 (Version 4.11) [Data set]. Palisades, NY: NASA Socioeconomic Data and Applications Center (SEDAC). https://doi.org/10.7927/H4JW8BX5

    CloudToStreet. (2021). cloudtostreet/MODIS Global Flood Database (v1.0.0). Retrieved from https://github.com/cloudtostreet/MODIS_GlobalFloodDatabase/releases/tag/v1.0.0

    Delforge, D., Wathelet, V., Below, R., Sofia, C. L., Tonnelier, M., Van Loenhout, J. A. F., & Speybroeck, N. (2025). EM-DAT: the Emergency Events Database. *International Journal of Disaster Risk Reduction*, *124*, 105509. https://doi.org/10.1016/j.ijdrr.2025.105509

    Food and Agriculture Organization of the United Nations. (2015). Global Administrative Unit Layers (GAUL) 2015 [Data set]. FAO. Retrieved from https://data.apps.fao.org/catalog/dataset/global-administrative-unit-layers-gaul-2015

    Kummu, M., Kosonen, M., & Masoumzadeh Sayyar, S. (2025). Downscaled gridded global dataset for gross domestic product (GDP) per capita PPP over 1990–2022. *Scientific Data*, *12*(1), 178. https://doi.org/10.1038/s41597-025-04487-x

    Organisation for Economic Co-operation and Development. (n.d.). Inflation (CPI) [Data set]. OECD. Retrieved from https://www.oecd.org/en/data/indicators/inflation-cpi.html

    Tellman, B., Sullivan, J. A., Kuhn, C., Kettner, A. J., Doyle, C. S., Brakenridge, G. R., et al. (2021). Satellite imaging reveals increased proportion of population exposed to floods. *Nature*, *596*(7870), 80–86. https://doi.org/10.1038/s41586-021-03695-w

    Zhuang, J., Dussin, R., Huard, D., Bourgault, P., & Anderson Banihirwe. (2025, April 29). pangeo-data/xESMF: v0.8.10 (Version v0.8.10). Zenodo. https://doi.org/10.5281/ZENODO.4294774
    """
    )

# ========== ABOUT ==========
elif view == "About":
    st.markdown("## About This Project")

    st.markdown("### Summary")
    st.markdown(
        "This app is a visual representation of a master's project in the Department of Civil & Environmental Engineering at Colorado State University (2025), titled:\n"
        '"A Spatially and Temporally Disaggregated Twenty-First Century Global Flood Record for Flood Impact Analysis."'
    )

    # "Research Software Engineer @ [Eagle Rock Analytics](https://eaglerockanalytics.com/)  \n"
    st.markdown("### Author")
    st.markdown(
        "**Nicole Keeney**  \n"
        "[LinkedIn](https://www.linkedin.com/in/nicole-keeney/) | [GitHub](https://github.com/nicolejkeeney)  \n"
        "MS, Civil & Environmental Engineering (2025) @ Colorado State University"
    )

    st.markdown("### Abstract")
    st.markdown(
        "Given that floods are one of the most widespread and costly disasters, there is significant attention on understanding the hydrologic and socioeconomic drivers of these events. However, current research efforts are limited by a lack of detailed, comprehensive, and global-scale data on historical flood events and impacts. In this study, we combine flood damage records with climate reanalysis data and satellite-based flood detection to create a spatially and temporally disaggregated 21st century flood dataset. We start with 4073 inland floods from 2000-2024 contained in the EM-DAT international hazard database. We then disaggregate each event into sub-national administrative levels (e.g., states or provinces) and, for longer duration events, by calendar month to enable analysis at finer spatial and temporal scales. For each event, we derive flooded pixel maps from MODIS satellite imagery. By combining these high-resolution flood maps with gridded population density data, we calculate the number of people exposed to flooded areas in each state or province over time. Lastly, we use climate reanalysis data to extract historical precipitation data at the administrative region and month level in order to characterize the meteorological conditions of each flood. The result is a spatially and temporally consistent dataset of global flood characteristics and impacts to enable more granular impact analysis. In our exploratory analyses, we use the dataset to investigate how historical precipitation contributes to observed flood impacts—both in terms of people affected and economic damages—across different regions and through time. We find a statistically significant relationship between monthly extreme precipitation and flood impacts using a global-scale fixed-effects panel regression model. In future work, this model could serve as the basis for attributing flood impacts to underlying changes in the precipitation distribution."
    )
