import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import os as os
import numpy as np
import faiss
import traceback
from openai import OpenAI
import streamlit_shadcn_ui as shadcn

# ---------------------- CONFIG ----------------------
st.set_page_config(
    page_title="Belgium Business Intelligence Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------- OpenAI Client ----------------------
def get_openai_client():
    # 1) Try the [openai] section of Streamlit secrets
    if "openai" in st.secrets and "api_key" in st.secrets["openai"]:
        api_key = st.secrets["openai"]["api_key"]
    else:
        # 2) Fallback to the OPENAI_API_KEY env var
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        st.error("OpenAI API key not found. Please set it in Streamlit secrets or via the OPENAI_API_KEY env var.")
        st.stop()

    return OpenAI(api_key=api_key)

# ---------------------- SIDEBAR NAVIGATION ----------------------
st.sidebar.title("🇧🇪 Belgium Business Platform")

# Navigation options
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "📈 Growth Dashboard", "🤖 Competitor Finder Chatbot", "🔎 Company Explorer", "ℹ️ Link to the ChatGPT Chatbot"],
    key="page"
)

# ---------------------- NAVIGATION CALLBACKS ----------------------
def go_to_growth():
    st.session_state.page = "📈 Growth Dashboard"

def go_to_competitor():
    st.session_state.page = "🔍 Competitor Finder"

def go_to_explorer():
    st.session_state.page = "🔎 Company Explorer"

def go_to_chatbot():
    st.session_state.page = "ℹ️ Link to the ChatGPT Chatbot"

# ---------------------- LOAD DATA ----------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_FILE, delimiter=",", engine="python", on_bad_lines="skip")
        # Clean column names
        df.columns = df.columns.str.strip()
        return df
    except Exception:
        st.error("❌ Error loading the dataset:")
        st.text(traceback.format_exc())
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.stop()


# ---------------------- HOME PAGE ----------------------
if page == "🏠 Home":
    st.title("🇧🇪 Belgium Business Intelligence Platform")
    st.markdown("This platform provides insights into high-growth Belgian companies, including their growth trends and potential competitors. Use the tools below to explore the data and gain valuable insights.")
    st.markdown("**Disclaimer:** The data is based on the latest available information and may not reflect real-time changes. Always verify with official sources.")
    st.markdown("This is made with ❤️ by Group A")
    
    # ─── Row 1 ───
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.subheader("📈 Growth Dashboard")
        st.write("Dive into comprehensive analysis of high-growth Belgian companies.")
        st.button(
            "Open Growth Dashboard",
            key="open_dashboard_btn",
            on_click=go_to_growth,
            type="primary",
        )
    with col2:
        st.subheader("🤖 Competitor Finder")
        st.write("Leverage AI to identify potential competitors based on your description.")
        st.button(
            "Open Competitor Finder",
            key="find_competitors_btn",
            on_click=go_to_competitor,
            type="primary",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── Row 2 ───
    col3, col4 = st.columns(2, gap="large")
    with col3:
        st.subheader("🔎 Company Explorer")
        st.write("Browse and filter high-growth firms by year, region, industry, and more.")
        st.button(
            "Open Company Explorer",
            key="open_explorer_btn",
            on_click=go_to_explorer,
            type="primary",
        )
    with col4:
        st.subheader("ℹ️ ChatGPT Chatbot")
        st.write("Ask the custom ChatGPT chatbot about any company, industry, or region.")
        st.button(
            "Open Chatbot",
            key="open_chatbot_btn",
            on_click=go_to_chatbot,
            type="primary",
        )
# ---------------------- Dashboard ----------------------

elif page == "📈 Growth Dashboard":
    st.title("📈 Belgium Company Growth Dashboard")
    st.sidebar.header("🔍 Dashboard Filters")

    # Inject CSS + smooth-scroll JS
    st.markdown("""
    <style>
      #chart-nav { display: grid; grid-template-columns: repeat(4,1fr); gap:1rem; }
      .nav-card {
        background: #1e1e2f; border-radius: 8px; padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.5);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
      }
      .nav-card:hover { transform: translateY(-3px); box-shadow: 0 4px 8px rgba(0,0,0,0.7); }
      .nav-card h2 { margin: 0 0 .25rem; font-size: 1.1rem; color: #fff; }
      .nav-card p  { margin: 0 0 .5rem; color: #aaa; font-size: .9rem; }
      .nav-card a  { color: #3caea3; text-decoration: none; font-weight: 600; }
      .nav-card a:hover { text-decoration: underline; }
    </style>
    <script>
      window.addEventListener('load', () => {
          document.querySelectorAll('a[href^="#section"]').forEach(a => {
              a.onclick = e => {
                  e.preventDefault();
                  const id = a.getAttribute('href').substring(1);
                  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
              };
          });
      });
    </script>
    """, unsafe_allow_html=True)

    # Navigation cards
    def nav_card(title, caption, anchor):
        st.markdown(f"""
        <div class="nav-card">  
            <h2>{title}</h2>
            <p>{caption}</p>
            <a href="#{anchor}">Go to Chart →</a>
        </div>
        """, unsafe_allow_html=True)

    # Top row of nav
    row1 = st.columns(4)
    cards1 = [
        ("📊 Key Metrics","Overview of total firms & KPIs.","section1"),
        ("🏙️ Top Cities & Region","Cities & Regions ranked by CHGF.","section2"),
        ("🏭 Top 10 Industries","Distribution & avg. growth.","section3"),
        ("🏢 Company Size","Employees-based size distribution.","section4"),
    ]
    for col, (t, c, a) in zip(row1, cards1):
        with col: nav_card(t, c, a)
    st.markdown("<br>", unsafe_allow_html=True)

    # Second row
    row2 = st.columns(2)
    cards2 = [
        ("📈 Growth Trend of CHGF Over Time","Avg. growth 2019–2023 and its count.","section5"),
        ("📅 Founding & Growth","Founding vs high-growth counts.","section6"),
    ]
    for col, (t, c, a) in zip(row2, cards2):
        with col: nav_card(t, c, a)
    st.divider()

    # Precompute fractional growth columns once
    years = [2019, 2020, 2021, 2022, 2023]
    for y in years:
        col     = f"Growth {y}"
        num_col = f"{col}_num"

        if col not in df.columns:
            df[num_col] = np.nan
            continue

        raw = df[col]

        # CASE 1: strings that contain an explicit "%" → strip & divide
        if raw.dtype == object and raw.str.contains('%').any():
            df[num_col] = (
                raw.astype(str)
                .str.replace(",", ".")
                .str.rstrip("%")
                .pipe(pd.to_numeric, errors="coerce")
                / 100
            )

        # CASE 2: everything else → already a fraction, just cast
        else:
            df[num_col] = pd.to_numeric(raw, errors="coerce").astype(float)

    # Ensure CHGF flags are numeric 0/1
    for y in years:
        fc = f"ConsistentHighGrowthFirm {y}"
        if fc in df.columns:
            df[fc] = (
                pd.to_numeric(df[fc], errors="coerce")
                  .fillna(0)
                  .astype(int)
            )

    # Common styling
    color_palette = px.colors.qualitative.Vivid
    theme_colors = {'primary': color_palette[0], 'secondary': color_palette[1]}
    layout_config = {
        'font_family': 'Arial, sans-serif',
        'font': {'color': 'white'},
        'title_font_size': 18,
        'title_font_color': 'white',
        'legend_title_font_color': 'white',
        'legend_font_color': 'white',
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'margin': dict(l=40, r=40, t=80, b=40)
    }

    # --- SECTION 1: Key Metrics ---
    st.markdown('<div id="section1"></div>', unsafe_allow_html=True)
    st.subheader("📊 Key Metrics")
    global_year    = st.sidebar.selectbox("Year", [2023, 2022, 2021, 2020, 2019])
    region_filter  = st.sidebar.multiselect("Region", df["Region"].dropna().unique())
    industry_filter= st.sidebar.multiselect("Industry", df["NACE Friendly Label"].dropna().unique())
    size_options   = ["All Sizes", "Small (<50)", "Medium (50-250)", "Large (>250)"]
    company_size   = st.sidebar.selectbox("Company Size", size_options)
    min_growth, max_growth = st.sidebar.slider("Growth Rate Range (%)", 0.0, 300.0, (0.0, 300.0))

    # Filter high-growth firms for the KPI snapshot
    flag_col    = f"ConsistentHighGrowthFirm {global_year}"
    filtered_df = df[df[flag_col] == 1].copy()
    if region_filter:
        filtered_df = filtered_df[filtered_df["Region"].isin(region_filter)]
    if industry_filter:
        filtered_df = filtered_df[filtered_df["NACE Friendly Label"].isin(industry_filter)]

    # Apply employee-size filter
    emp_col = f"Number of employees {global_year}"
    if emp_col in filtered_df and company_size != "All Sizes":
        filtered_df[emp_col] = pd.to_numeric(
            filtered_df[emp_col].replace("n.a.", np.nan),
            errors="coerce"
        )
        if company_size == "Small (<50)":
            filtered_df = filtered_df[filtered_df[emp_col] < 50]
        elif company_size == "Medium (50-250)":
            filtered_df = filtered_df[(filtered_df[emp_col] >= 50) & (filtered_df[emp_col] <= 250)]
        else:
            filtered_df = filtered_df[filtered_df[emp_col] > 250]

    orig_df = filtered_df.copy()

    # Growth-range filter
    growth_num_col = f"Growth {global_year}_num"
    filtered_df = filtered_df[
        (filtered_df[growth_num_col] >= min_growth/100) &
        (filtered_df[growth_num_col] <= max_growth/100)
    ]

    # --- KPI CARDS FIXED ---
    company_count  = len(orig_df)
    avg_growth     = orig_df[growth_num_col].mean() * 100     # single *100 → percent
    median_growth  = orig_df[growth_num_col].median() * 100  # single *100 → percent
    emp_series     = pd.to_numeric(orig_df[emp_col], errors="coerce")
    avg_employees  = int(np.nan_to_num(emp_series.mean(), nan=0))
    total_employees= int(np.nan_to_num(emp_series.sum(),  nan=0))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        shadcn.metric_card("Total Companies", f"{company_count:,}", f"In {global_year}")
    with c2:
        shadcn.metric_card(
            f"Avg. Growth ({global_year})",
            f"{avg_growth:.2f}%",
            f"Median: {median_growth:.2f}%"
        )
    with c3:
        shadcn.metric_card(
            f"Avg. Employees ({global_year})",
            f"{avg_employees:,}",
            "Per company"
        )
    with c4:
        shadcn.metric_card(
            f"Total Employment ({global_year})",
            f"{total_employees:,}",
            "Across firms"
        )

    # --- SECTION 2: Geographic Distribution ---
    st.markdown('<div id="section2"></div>', unsafe_allow_html=True)
    st.subheader("🗺️ Geographic Distribution")
    st.caption("See where high-growth firms are clustered—cities on the left, regions on the right—so you can spot geographic hotspots.")
    geo_tabs = st.tabs(["Cities","Regions"])

    with geo_tabs[0]:
        city_counts = filtered_df["City"].value_counts().head(20).reset_index()
        city_counts.columns = ["City","Company Count"]
        fig_cities = px.bar(
            city_counts, x="City", y="Company Count",
            color="Company Count", color_continuous_scale="Viridis",
            text_auto=True,
            title=f"Top 20 Cities ({global_year})"
        )
        fig_cities.update_layout(**layout_config)
        fig_cities.update_traces(textfont_color='white', marker_line_width=1, marker_line_color='#333', textposition='outside')
        st.plotly_chart(fig_cities, use_container_width=True)

    with geo_tabs[1]:
        region_counts = filtered_df["Region"].value_counts().reset_index()
        region_counts.columns = ["Region","Company Count"]
        fig_regions = px.pie(
            region_counts, names="Region", values="Company Count",
            color_discrete_sequence=px.colors.sequential.Viridis,
            hole=0.4, title=f"By Region ({global_year})"
        )
        fig_regions.update_layout(**layout_config)
        fig_regions.update_traces(textinfo='percent+label', textposition='inside', pull=[.05]*len(region_counts), textfont_color='white')
        st.plotly_chart(fig_regions, use_container_width=True)

    # --- SECTION 3: Industry Analysis & Avg Growth FIXED ---
    st.markdown('<div id="section3"></div>', unsafe_allow_html=True)
    st.subheader("🏭 Industry Analysis")
    st.caption("Distribution shows top 10 industries by firm count. Average Growth shows which sectors saw the fastest mean revenue increases in 2019–2023.")
    ind_tabs = st.tabs(["Distribution","Average Growth"])

    with ind_tabs[0]:
        ind_counts = (
            filtered_df["NACE Friendly Label"]
            .value_counts().head(10)
            .rename_axis("Industry")
            .reset_index(name="Company Count")
        )
        fig_ind = px.pie(
            ind_counts, names="Industry", values="Company Count",
            hole=0.3, color_discrete_sequence=px.colors.qualitative.Pastel,
            title=f"Top 10 Industries ({global_year})"
        )
        fig_ind.update_layout(**layout_config)
        fig_ind.update_traces(textinfo='percent+label', textposition='inside', pull=[.03]*10, textfont_color='white')
        st.plotly_chart(fig_ind, use_container_width=True)

    with ind_tabs[1]:
        # compute per-row avg growth % (2019–2023)
        growth_df = filtered_df.copy()
        for y in years:
            col = f"Growth {y}"
            if col in growth_df:
                growth_df[col] = (
                    growth_df[col].astype(str)
                                .str.replace(",",".")
                                .str.rstrip("%")
                                .pipe(pd.to_numeric,errors="coerce")/100
                )
            else:
                growth_df[col] = np.nan

        growth_df["Avg Growth (%)"] = growth_df[
            [f"Growth {y}" for y in years]
        ].mean(axis=1) * 100

        # average by top-10 industries
        top_inds = growth_df["NACE Friendly Label"].value_counts().head(10).index
        industry_avg_df = (
            growth_df[growth_df["NACE Friendly Label"].isin(top_inds)]
            .groupby("NACE Friendly Label")["Avg Growth (%)"].mean()
            .sort_values()
            .reset_index()
            .rename(columns={
                "NACE Friendly Label":"Industry",
                "Avg Growth (%)":"Average Growth Rate (%)"
            })
        )

        fig_ind_avg = px.bar(
            industry_avg_df,
            x="Industry",
            y="Average Growth Rate (%)",
            color="Average Growth Rate (%)",
            color_continuous_scale="Viridis",
            text_auto=".2f",
            title="Average Growth Rate of Top 10 Industries (2019–2023)"
        )
        fig_ind_avg.update_layout(
            yaxis_tickformat=".2f",
            **layout_config
        )
        fig_ind_avg.update_traces(textfont_color='white', marker_line_width=1, marker_line_color='#333', textposition='outside')
        st.plotly_chart(fig_ind_avg, use_container_width=True)

    # --- SECTION 4: Company Size Distribution ---
    st.markdown('<div id="section4"></div>', unsafe_allow_html=True)
    st.subheader("🏢 Company Size Distribution")
    st.caption("Breaks CHGF into buckets by employee count, highlighting whether small, mid-sized or large firms dominate the high-growth cohort.")
    try:
        size_df = filtered_df.copy()
        size_df["Employees_Numeric"] = pd.to_numeric(size_df[emp_col], errors="coerce")
        bins  = [0, 10, 50, 250, 1000, np.inf]
        labels= ["0-10", "11-50", "51-250", "251-1000", "1000+"]
        size_df["Size Category"] = pd.cut(size_df["Employees_Numeric"], bins=bins, labels=labels)
        size_counts = size_df["Size Category"].value_counts().sort_index().reset_index(name="Company Count")

        fig_size = px.bar(
            size_counts, x="Size Category", y="Company Count",
            color="Company Count", color_continuous_scale="Viridis",
            text_auto=True,
            title=f"Distribution of Company Sizes ({global_year})"
        )
        fig_size.update_layout(**layout_config)
        fig_size.update_traces(textfont_color='white', marker_line_width=1, marker_line_color='#333', textposition='outside')
        st.plotly_chart(fig_size, use_container_width=True)

    except Exception as e:
        st.error(f"Error in Company Size Distribution: {e}")

    # --- SECTION 5: Growth Trend Over Time (percent units) ---
    st.markdown('<div id="section5"></div>', unsafe_allow_html=True)
    st.subheader("📈 Growth Trend of CHGF Over Time")
    st.caption("Average Growth Rate plots the mean % change each year. The count tab shows how many firms met your growth criteria annually.")
    # build percent‐unit summary
    trend_df = pd.DataFrame({
        "Year": years,
        "Average Growth Rate (%)": [
            filtered_df[f"Growth {y}_num"].dropna().mean() * 100
            for y in years
        ]
    })
    count_df = pd.DataFrame({
        "Year": [str(y) for y in years],
        "Company Count": [
            filtered_df[f"Growth {y}_num"].notna().sum()
            for y in years
        ]
    })

    fg_tabs = st.tabs(["Average Growth Rate", "Consistent High-Growth Firms Count"])
    with fg_tabs[0]:
        try:
            fig_trend = px.bar(
                trend_df,
                x="Year", y="Average Growth Rate (%)",
                color="Average Growth Rate (%)",
                color_continuous_scale="Viridis",
                text_auto=".2f",
                title="Average Growth Rate of CHGF (2019–2023)"
            )
            fig_trend.update_layout(xaxis=dict(type="category"), **layout_config)
            fig_trend.update_traces(textfont_color="white", marker_line_width=1, marker_line_color="#333", textposition="outside")
            st.plotly_chart(fig_trend, use_container_width=True)
        except Exception as e:
            st.error(f"Error in Growth Trend Over Time: {e}")

    with fg_tabs[1]:
        try:
            fig_cnt = px.bar(
                count_df, x="Year", y="Company Count",
                color="Company Count", color_continuous_scale="Viridis",
                text_auto=True,
                title="High-Growth Firms per Year (2019–2023)"
            )
            fig_cnt.update_layout(**layout_config)
            fig_cnt.update_traces(textfont_color="white", marker_line_width=1, marker_line_color="#333", textposition="outside")
            st.plotly_chart(fig_cnt, use_container_width=True)
        except Exception as e:
            st.error(f"Error in High-Growth Firms per Year: {e}")

    # --- SECTION 6: Founding Timeline ---
    st.markdown('<div id="section6"></div>', unsafe_allow_html=True)
    st.subheader("📅 Founding Timeline")
    st.caption("Tracks when CHGF were founded by decade or year—helping you see whether new versus older firms are driving high growth.")
    
    try:
        timeline_df = filtered_df.dropna(subset=["Founded Year"]).copy()
        timeline_df["Founded Year"] = timeline_df["Founded Year"].astype(int)

        dt_tabs = st.tabs(["By Decade","By Year"])
        with dt_tabs[0]:
            decade_counts = (
                timeline_df["Founded Year"]
                .floordiv(10).mul(10)
                .value_counts().sort_index()
                .rename_axis("Decade").reset_index(name="Company Count")
            )
            decade_counts["Decade"] = decade_counts["Decade"].astype(str) + "s"
            fig_dec = px.bar(
                decade_counts, x="Decade", y="Company Count",
                color="Company Count", color_continuous_scale="Viridis",
                text_auto=True,
                title=f"Firms by Founding Decade ({global_year} cohort)"
            )
            fig_dec.update_layout(**layout_config)
            fig_dec.update_traces(textfont_color='white', marker_line_width=1, marker_line_color='#333', textposition='outside')
            st.plotly_chart(fig_dec, use_container_width=True)

        with dt_tabs[1]:
            year_counts = (
                timeline_df["Founded Year"]
                .value_counts().sort_index()
                .rename_axis("Year").reset_index(name="Company Count")
            )
            year_counts = year_counts[year_counts["Year"] >= 1990]
            fig_year = px.line(
                year_counts, x="Year", y="Company Count", markers=True,
                line_shape="spline", title="Firms Founded per Year (since 1990)"
            )
            fig_year.update_layout(**layout_config)
            fig_year.update_traces(textfont_color='white', marker=dict(size=8), line=dict(width=3, color=theme_colors['primary']))
            st.plotly_chart(fig_year, use_container_width=True)

    except Exception as e:
        st.error(f"Error in Founding Year: {e}")

# ---------------------- COMPETITOR FINDER ----------------------
elif page == "🤖 Competitor Finder Chatbot":
    st.title("RAG-Powered Competitor Intelligence")
    
    # Prepare for embeddings and search
    @st.cache_data
    def load_and_embed_data():
        try:
            st.sidebar.text("📥 Loading and preparing data...")
            df = pd.read_csv(DATA_FILE, sep=",", encoding="utf-8", on_bad_lines="skip")
            df.columns = df.columns.str.strip()
            
            # Keep only high growth firms with descriptions
            df = df[["Company name", "Description", "ConsistentHighGrowthFirm 2023", 
                    "Region", "City", "NACE Friendly Label", "Growth 2023"]]
            df = df[df["ConsistentHighGrowthFirm 2023"] == 1].dropna(subset=["Description"])
            df["combined"] = df["Company name"] + ": " + df["Description"]
            
            client = get_openai_client()
            
            def embed_batch(texts):
                st.sidebar.text(f"🧠 Embedding batch of {len(texts)} items")
                response = client.embeddings.create(input=texts, model=EMBED_MODEL)
                return [np.array(e.embedding, dtype="float32") for e in response.data]
            
            # Batch embedding
            embeddings = []
            batch_size = 50
            for i in range(0, len(df), batch_size):
                batch = df["combined"].iloc[i:i + batch_size].tolist()
                embeddings.extend(embed_batch(batch))
            
            df["embedding"] = embeddings
            
            # FAISS index
            dim = len(embeddings[0])
            index = faiss.IndexFlatL2(dim)
            index.add(np.vstack(embeddings))
            
            st.sidebar.text("✅ Data preparation complete")
            return df, index
        except Exception as e:
            st.sidebar.error(f"❌ Error preparing data: {e}")
            raise
    
    # Load data with progress
    with st.spinner("Loading RAG database..."):
        try:
            embedded_df, index = load_and_embed_data()
        except Exception as e:
            st.error(f"Failed to load data: {e}")
            st.stop()
    
    # Semantic search function
    def search_top_k_companies(query, k=5, region_filter=None, industry_filter=None):
        try:
            client = get_openai_client()
            response = client.embeddings.create(input=[query], model=EMBED_MODEL)
            query_embedding = np.array(response.data[0].embedding, dtype="float32")
            
            # Get more results than needed to apply filters
            search_k = min(k * 3, len(embedded_df))
            distances, indices = index.search(np.array([query_embedding]), search_k)
            
            results = embedded_df.iloc[indices[0]].copy()
            results["similarity_score"] = 1 - (distances[0] / distances[0].max())
            
            # Apply filters
            if region_filter:
                results = results[results["Region"].isin(region_filter)]
            if industry_filter:
                results = results[results["NACE Friendly Label"].isin(industry_filter)]
            
            # Return top k after filtering
            return results.head(k)
        except Exception as e:
            st.error(f"❌ Error during search: {e}")
            raise
    
    # GPT function for analysis
    def analyze_competitors(company_name, description, top_matches, analysis_type="competitive"):
        try:
            client = get_openai_client()
            matches_formatted = ""
            
            for i, (_, row) in enumerate(top_matches.iterrows(), 1):
                matches_formatted += f"""
                {i}. {row['Company name']}
                   Description: {row['Description']}
                   Industry: {row.get('NACE Friendly Label', 'N/A')}
                   Region: {row.get('Region', 'N/A')}
                   Growth 2023: {row.get('Growth 2023', 'N/A')}
                   Similarity Score: {row.get('similarity_score', 'N/A'):.2f}
                """
            
            if analysis_type == "competitive":
                prompt = f"""
                You are a business intelligence analyst. Your task is to identify and analyze relevant competitors for a given company.

                Company Name: {company_name}
                Description: {description}

                Here are potential high-growth firms from the database that could be competitors:
                {matches_formatted}

                Please provide a comprehensive competitive analysis including:
                1. Which firms are most likely direct competitors and why
                2. Which firms might be potential partners or represent adjacent markets
                3. Notable strengths and unique selling points of these companies
                4. Market positioning insights based on these companies
                5. Recommendations for competitive strategy
                
                Format your response with clear headers and bullet points for readability.
                """
            elif analysis_type == "market":
                prompt = f"""
                You are a market research analyst. Analyze the following high-growth companies in the same sector as:

                Company Name: {company_name}
                Description: {description}

                Here are high-growth firms in similar markets:
                {matches_formatted}

                Please provide a comprehensive market analysis including:
                1. Market trends and dynamics visible from these companies
                2. Common growth factors and strategies
                3. Market size and potential estimates
                4. Customer segments and needs being served
                5. Recommendations for market entry or expansion
                
                Format your response with clear headers and bullet points for readability.
                """
            elif analysis_type == "investment":
                prompt = f"""
                You are an investment analyst. Evaluate investment opportunities in the same sector as:

                Company Name: {company_name}
                Description: {description}

                Here are high-growth firms in similar markets:
                {matches_formatted}

                Please provide a comprehensive investment analysis including:
                1. Most promising companies for investment and why
                2. Risk factors in this sector
                3. Growth potential and metrics to watch
                4. Comparison to wider market trends
                5. Investment recommendation timeframe and strategy
                
                Format your response with clear headers and bullet points for readability.
                """
            
            response = client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a business intelligence analyst specializing in competitor analysis and market research."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"❌ Analysis error: {e}")
            raise
    
    # Dashboard UI
    st.subheader("🔎 Discover competitors and market insights")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        company_name = st.text_input("Enter your company name")
        company_description = st.text_area("Describe your company and its offerings", height=150)
    
    with col2:
        st.write("**Analysis Options**")
        
        # Region filter
        region_filter = st.multiselect(
            "Filter by Region (optional)",
            options=df["Region"].dropna().unique(),
            default=None
        )
        
        # Industry filter
        industry_filter = st.multiselect(
            "Filter by Industry (optional)",
            options=df["NACE Friendly Label"].dropna().unique(),
            default=None
        )
        
        # Number of results
        k_results = st.slider("Number of results", min_value=3, max_value=10, value=5)
        
        # Analysis type
        analysis_type = st.selectbox(
            "Select Analysis Type",
            options=["Competitive Analysis", "Market Trends", "Investment Potential"],
            index=0
        )
        
        # Map to backend values
        analysis_map = {
            "Competitive Analysis": "competitive",
            "Market Trends": "market",
            "Investment Potential": "investment"
        }
    
    # Button to trigger search
    if st.button("Find & Analyze", type="primary"):
        if not company_name or not company_description:
            st.warning("Please enter both company name and description")
        else:
            with st.spinner("🔍 Finding relevant companies and analyzing..."):
                try:
                    # Prepare query
                    query = f"{company_name}: {company_description}"
                    
                    # Perform search
                    top_matches = search_top_k_companies(
                        query, 
                        k=k_results, 
                        region_filter=region_filter if region_filter else None,
                        industry_filter=industry_filter if industry_filter else None
                    )
                    
                    # Get analysis
                    analysis = analyze_competitors(
                        company_name, 
                        company_description, 
                        top_matches,
                        analysis_type=analysis_map[analysis_type]
                    )
                    
                    # Display results
                    st.subheader(f"Top {len(top_matches)} Similar Companies")
                    
                    # Use tabs to show different views
                    company_tabs = st.tabs(["Table View", "Card View"])
                    
                    with company_tabs[0]:
                        # Table view with similarity scores
                        display_df = top_matches[["Company name", "Region", "NACE Friendly Label", "similarity_score"]]
                        display_df.columns = ["Company", "Region", "Industry", "Similarity Score"]
                        display_df["Similarity Score"] = display_df["Similarity Score"].apply(lambda x: f"{x:.2f}")
                        st.dataframe(display_df, use_container_width=True)
                    
                    with company_tabs[1]:
                        # Card view with more details
                        for i, (_, row) in enumerate(top_matches.iterrows()):
                            with st.container():
                                with shadcn.card(key=f"company_card_{i}"):
                                    st.subheader(row["Company name"])
                                    st.markdown(f"""
                                    **Description:** {row["Description"][:200]}... 
                                    
                                    **Industry:** {row.get("NACE Friendly Label", "N/A")}  
                                    **Region:** {row.get("Region", "N/A")}  
                                    **City:** {row.get("City", "N/A")}  
                                    **Growth 2023:** {row.get("Growth 2023", "N/A")}  
                                    **Similarity Score:** {row.get("similarity_score", 0):.2f}
                                    """)
                                    st.write("🏢")
                                            
                    # Display analysis
                    st.subheader(f"📊 {analysis_type}")
                    st.markdown(analysis)
                    
                    # Add download options
                    with st.expander("Export Results"):
                        # Prepare CSV for download
                        csv = top_matches.to_csv(index=False)
                        st.download_button(
                            label="Download results as CSV",
                            data=csv,
                            file_name=f"{company_name}_competitors.csv",
                            mime="text/csv"
                        )
                        
                        # Prepare PDF report (just a placeholder, actual PDF generation would require additional libraries)
                        st.download_button(
                            label="Download analysis report (PDF)",
                            data=analysis.encode(),
                            file_name=f"{company_name}_{analysis_type.lower().replace(' ', '_')}.txt",
                            mime="text/plain",
                            help="Note: Currently downloads as text. PDF functionality requires additional setup."
                        )
                
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    st.error(traceback.format_exc())

# ---------------------- COMPANY EXPLORER ----------------------
elif page == "🔎 Company Explorer":
    st.title("🔎 Company Explorer")

    df_explorer = load_data()
    if df_explorer.empty:
        st.stop()

    # — Precompute fractional growth columns for explorer —
    available_years = [2019, 2020, 2021, 2022, 2023]
    for y in available_years:
        col     = f"Growth {y}"
        num_col = f"{col}_num"

        if col not in df_explorer.columns:
            df_explorer[num_col] = np.nan
            continue

        raw = df_explorer[col]

        # Case A: strings containing “%” → strip & divide
        if raw.dtype == object and raw.astype(str).str.contains("%").any():
            df_explorer[num_col] = (
                raw.astype(str)
                   .str.replace(",", ".")
                   .str.rstrip("%")
                   .pipe(pd.to_numeric, errors="coerce")
                   / 100
            )
        # Case B: already a fraction → just cast
        else:
            df_explorer[num_col] = pd.to_numeric(raw, errors="coerce").astype(float)


    # ------------------- Year Selector -------------------
    st.subheader("📂 Select Year and Search Companies")

    available_years = [2019, 2020, 2021, 2022, 2023]
    selected_year = st.selectbox("📅 Select Cohort Year", available_years, index=4)

    # Filter based on selected year's 'ConsistentHighGrowthFirm' flag
    growth_flag_col = f"ConsistentHighGrowthFirm {selected_year}"
    if growth_flag_col not in df_explorer.columns:
        st.error(f"❌ No high growth firm data available for {selected_year}.")
        st.stop()

    # Convert growth flag to numeric
    df_explorer[growth_flag_col] = pd.to_numeric(df_explorer[growth_flag_col], errors='coerce')
    df_explorer = df_explorer[df_explorer[growth_flag_col] == 1].copy()

    # ------------------- Filters and Search -------------------
    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

    with col1:
        search_term = st.text_input("🔍 Search by Name or Description")

    with col2:
        region_filter = st.multiselect("🌍 Region", sorted(df_explorer["Region"].dropna().unique()))

    with col3:
        city_filter = st.multiselect("🏙️ City", sorted(df_explorer["City"].dropna().unique()))

    with col4:
        industry_filter = st.multiselect("🏭 Industry", sorted(df_explorer["NACE Friendly Label"].dropna().unique()))

    # ------------------- Apply Filters -------------------
    filtered_df = df_explorer.copy()

    if search_term:
        filtered_df = filtered_df[
            filtered_df["Company name"].str.contains(search_term, case=False, na=False) |
            filtered_df["Description"].str.contains(search_term, case=False, na=False)
        ]

    if region_filter:
        filtered_df = filtered_df[filtered_df["Region"].isin(region_filter)]

    if city_filter:
        filtered_df = filtered_df[filtered_df["City"].isin(city_filter)]

    if industry_filter:
        filtered_df = filtered_df[filtered_df["NACE Friendly Label"].isin(industry_filter)]

    # ------------------- Show Results -------------------
    st.subheader(f"📋 Showing {len(filtered_df)} matching companies for {selected_year}")

    if filtered_df.empty:
        st.info("No companies match the current search and filters.")
    else:
        for idx, row in filtered_df.iterrows():
            with st.expander(f"🔹 {row['Company name']} ({row.get('City', 'N/A')}, {row.get('Region', 'N/A')})"):
                st.markdown(f"**Industry:** {row.get('NACE Friendly Label', 'N/A')}")
                st.markdown(f"**Founded Year:** {row.get('Founded Year', 'N/A')}")
                # show Growth as a properly formatted percent
                num_col = f"Growth {selected_year}_num"
                gr = row.get(num_col)
                if pd.notna(gr):
                    st.markdown(f"**Growth {selected_year}:** {gr * 100:.2f}%")
                else:
                    st.markdown(f"**Growth {selected_year}:** {row.get(f'Growth {selected_year}', 'N/A')}")
                st.markdown(f"**Employees {selected_year}:** {row.get(f'Number of employees {selected_year}', 'N/A')}")
                st.markdown(f"**Description:** {row.get('Description', 'N/A')}")
  

# ---------------------- ABOUT PAGE ----------------------
elif page == "ℹ️ Link to the ChatGPT Chatbot":
    st.title("ℹ️ Link to the ChatGPT Chatbot")
    st.markdown("""
    [Click here to access the ChatGPT Chatbot](https://chatgpt.com/g/g-680e4c3e58288191971c5f8ef1ee0c40)
    
    """)
    st.markdown("""
    This chatbot is powered by OpenAI's GPT-3.5 and is designed to assist you in finding high-growth firms and analyzing their competitive landscape.
    You can ask questions about specific companies, industries, or regions, and the chatbot will provide insights based on the data available in this dashboard.
    If you have any questions or feedback, feel free to reach out to us!
                
                """)
