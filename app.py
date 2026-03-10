import streamlit as st
import pandas as pd
import sqlite3
import time
import plotly.express as px
import plotly.graph_objects as go
from scoring_engine import calculate_product_score
from email_utils import send_report_email, validate_email
import os
from multiprocessing import Pool, cpu_count
import numpy as np

# Page config
st.set_page_config(
    page_title="Amazon Review Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #FF9900 0%, #FF6B00 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .stAlert {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

DB_NAME = "amazon_reviews.db"

# Header
st.markdown('<p class="main-header">Amazon Review Sentiment Analyzer</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### Navigation")
    page = st.radio("", ["Upload & Process", "View Analytics", "Help"])
    
    st.markdown("---")
    st.markdown("### Settings")
    show_debug = st.checkbox("Show Debug Info", value=False)
    
    st.markdown("---")
    # Clear database button
    if st.button("Clear Database", help="Delete all stored data"):
        try:
            import os
            if os.path.exists(DB_NAME):
                os.remove(DB_NAME)
                st.success("Database cleared successfully")
                st.rerun()
            else:
                st.info("No database to clear")
        except Exception as e:
            st.error(f"Error: {e}")
    
    st.markdown("---")
    st.markdown("### Quick Stats")
    try:
        conn = sqlite3.connect(DB_NAME)
        count = pd.read_sql_query("SELECT COUNT(*) as count FROM reviews", conn).iloc[0]['count']
        st.metric("Total Reviews", f"{count:,}")
        conn.close()
    except:
        st.info("No data yet")

# ==================== PAGE 1: UPLOAD & PROCESS ====================
if page == "Upload & Process":
    
    st.markdown("## Step 1: Upload Your Data")
    
    # Option to choose upload method
    upload_method = st.radio(
        "Choose upload method:",
        ["Upload File (< 20GB)", "Load from Disk (Large Files)"],
        horizontal=True
    )
    
    df = None
    
    if upload_method == "Upload File (< 20GB)":
        uploaded_file = st.file_uploader(
            "Drop your CSV file here or click to browse",
            type=["csv"],
            help="Upload Amazon review dataset in CSV format"
        )
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file, low_memory=False)
    
    else:
        file_path = st.text_input(
            "Enter full file path:",
            placeholder="E:\\data\\reviews.csv",
            help="Enter the complete path to your CSV file"
        )
        
        if file_path and st.button("Load File"):
            try:
                with st.spinner('Loading large file...'):
                    df = pd.read_csv(file_path, low_memory=False)
                st.success(f"File loaded successfully")
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
    if df is not None:
        # Success message
        st.success(f"File uploaded successfully - {len(df):,} records found")
        
        # Data preview
        with st.expander("Preview Data (First 10 rows)", expanded=True):
            st.dataframe(df.head(10), use_container_width=True)
        
        # Column info
        with st.expander("Available Columns"):
            col_info = pd.DataFrame({
                'Column Name': df.columns,
                'Data Type': df.dtypes.values,
                'Non-Null': df.count().values,
                'Sample Value': [str(df[col].iloc[0])[:50] + "..." if len(str(df[col].iloc[0])) > 50 else str(df[col].iloc[0]) for col in df.columns]
            })
            st.dataframe(col_info, use_container_width=True)
        
        st.markdown("---")
        st.markdown("## Step 2: Configure Columns")
        
        # Auto-detect review column
        def auto_detect_review_column(df):
            """Auto-detect which column likely contains review text"""
            possible_names = ['reviewText', 'review_text', 'text', 'verified_reviews', 
                            'reviews.text', 'body', 'content', 'summary', 'review', 
                            'reviewContent', 'review_content', 'comment', 'comments']
            
            # First try exact matches
            for col in df.columns:
                if col in possible_names:
                    return col
            
            # Then try partial matches
            for col in df.columns:
                col_lower = col.lower()
                if any(name.lower() in col_lower for name in ['review', 'text', 'content', 'comment']):
                    # Check if it has actual text (not just IDs)
                    sample = str(df[col].iloc[0])
                    if len(sample) > 30 and ' ' in sample:  # Has spaces = likely text
                        return col
            
            return df.columns[0]  # Fallback to first column
        
        # Auto-detect rating column
        def auto_detect_rating_column(df):
            """Auto-detect which column likely contains ratings"""
            possible_names = ['rating', 'ratings', 'star', 'stars', 'score']
            
            for col in df.columns:
                if col.lower() in possible_names:
                    return col
            
            return 'None'
        
        # Get auto-detected columns
        detected_review_col = auto_detect_review_column(df)
        detected_rating_col = auto_detect_rating_column(df)
        
        # Show auto-detection result
        st.info(f"Auto-detected: Review column = '{detected_review_col}', Rating column = '{detected_rating_col}'")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Review Text Column")
            review_column = st.selectbox(
                "Which column contains the review text?",
                options=df.columns.tolist(),
                index=df.columns.tolist().index(detected_review_col),
                help="Select the column with customer reviews/comments"
            )
            
            # Show sample
            sample_text = str(df[review_column].iloc[0])
            if len(sample_text) > 0:
                st.success(f"Sample: {sample_text[:200]}...")
            else:
                st.error("Warning: This column appears to be empty!")
        
        with col2:
            st.markdown("### Rating Column (Optional)")
            rating_options = ['None'] + df.columns.tolist()
            default_rating_idx = rating_options.index(detected_rating_col) if detected_rating_col in rating_options else 0
            
            rating_column = st.selectbox(
                "Which column contains ratings?",
                options=rating_options,
                index=default_rating_idx,
                help="Select the column with star ratings (1-5)"
            )
            
            if rating_column != 'None':
                sample_rating = df[rating_column].iloc[0]
                st.info(f"Sample rating: {sample_rating}")
        
        st.markdown("---")
        st.markdown("## Step 3: Run Analysis")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        
        with col_btn2:
            if st.button("Analyze Reviews & Store Results", type="primary", use_container_width=True):
                
                # Validation
                if len(str(df[review_column].iloc[0])) == 0:
                    st.error("The selected review column is empty. Please select a different column.")
                else:
                    with st.spinner('Processing reviews...'):
                        start_time = time.time()
                        
                        # Get data
                        reviews = df[review_column].values
                        ratings = df[rating_column].values if rating_column != 'None' else [None] * len(df)
                        
                        # Progress tracking
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        total_rows = len(df)
                        
                        scores = []
                        categories = []
                        
                        # Use simple processing for small datasets (< 50k rows)
                        if total_rows < 50000:
                            for i in range(total_rows):
                                review = reviews[i]
                                rating = ratings[i]
                                
                                if pd.notna(review):
                                    review = str(review)
                                else:
                                    review = ""
                                
                                score, category = calculate_product_score(review, None, rating)
                                scores.append(score)
                                categories.append(category)
                                
                                # Update progress every 100 rows
                                if i % 100 == 0:
                                    progress = (i + 1) / total_rows
                                    progress_bar.progress(progress)
                                    status_text.text(f"Processing: {i + 1:,} / {total_rows:,} reviews ({progress*100:.1f}%)")
                        
                        # Use multiprocessing for large datasets (>= 50k rows)
                        else:
                            def process_row(args):
                                review, rating = args
                                if pd.notna(review):
                                    review = str(review)
                                else:
                                    review = ""
                                return calculate_product_score(review, None, rating)
                            
                            data = list(zip(reviews, ratings))
                            batch_size = 10000
                            num_workers = max(1, cpu_count() - 1)
                            
                            for i in range(0, len(data), batch_size):
                                batch = data[i:i+batch_size]
                                
                                with Pool(num_workers) as pool:
                                    results = pool.map(process_row, batch)
                                
                                batch_scores = [r[0] for r in results]
                                batch_categories = [r[1] for r in results]
                                
                                scores.extend(batch_scores)
                                categories.extend(batch_categories)
                                
                                # Update progress
                                progress = min((i + batch_size) / total_rows, 1.0)
                                progress_bar.progress(progress)
                                status_text.text(f"Processing: {min(i + batch_size, total_rows):,} / {total_rows:,} reviews ({progress*100:.1f}%)")
                        
                        progress_bar.progress(1.0)
                        status_text.text(f"Completed - Processed {total_rows:,} reviews")
                        
                        # Add to dataframe
                        df["score"] = scores
                        df["category"] = categories
                        
                        # Store in database with batch insertion
                        conn = sqlite3.connect(DB_NAME)
                        df.to_sql("reviews", conn, if_exists="replace", index=False, chunksize=5000)
                        
                        # Create indexes
                        conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON reviews(category)")
                        conn.execute("CREATE INDEX IF NOT EXISTS idx_score ON reviews(score)")
                        
                        conn.commit()
                        conn.close()
                        
                        end_time = time.time()
                        
                        # Success metrics
                        st.success("Analysis Complete")
                        
                        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                        
                        with col_m1:
                            st.metric("Processing Time", f"{end_time - start_time:.2f}s")
                        with col_m2:
                            st.metric("Total Processed", f"{len(df):,}")
                        with col_m3:
                            avg_score = sum(scores) / len(scores)
                            st.metric("Average Score", f"{avg_score:.2f}")
                        with col_m4:
                            positive = sum(1 for s in scores if s > 0)
                            st.metric("Positive Rate", f"{positive/len(scores)*100:.1f}%")
                        
                        st.info("Navigate to 'View Analytics' to see detailed insights")

# ==================== PAGE 2: VIEW ANALYTICS ====================
elif page == "View Analytics":
    
    try:
        conn = sqlite3.connect(DB_NAME)
        df_db = pd.read_sql_query("SELECT * FROM reviews", conn)
        conn.close()
        
        if len(df_db) == 0:
            st.warning("No data found. Please upload and process data first.")
        else:
            # Overview metrics
            st.markdown("## Overview Dashboard")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total Reviews", f"{len(df_db):,}")
            with col2:
                avg_score = df_db['score'].mean()
                st.metric("Average Score", f"{avg_score:.2f}")
            with col3:
                positive_pct = (df_db['score'] > 0).sum() / len(df_db) * 100
                st.metric("Positive", f"{positive_pct:.1f}%")
            with col4:
                negative_pct = (df_db['score'] < 0).sum() / len(df_db) * 100
                st.metric("Negative", f"{negative_pct:.1f}%")
            with col5:
                neutral_pct = (df_db['score'] == 0).sum() / len(df_db) * 100
                st.metric("Neutral", f"{neutral_pct:.1f}%")
            
            st.markdown("---")
            
            # Charts
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown("### Category Distribution")
                category_counts = df_db['category'].value_counts()
                fig1 = px.pie(
                    values=category_counts.values,
                    names=category_counts.index,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col_chart2:
                st.markdown("### Score Distribution")
                fig2 = px.histogram(
                    df_db,
                    x='score',
                    nbins=30,
                    color_discrete_sequence=['#FF9900']
                )
                fig2.update_layout(showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)
            
            st.markdown("---")
            
            # Top/Bottom reviews
            col_top, col_bottom = st.columns(2)
            
            with col_top:
                st.markdown("### Top 5 Best Reviews")
                top_df = df_db.nlargest(5, 'score')[['score', 'category']]
                
                # Add review text if exists
                review_cols = [c for c in df_db.columns if 'review' in c.lower() or 'text' in c.lower() or 'content' in c.lower()]
                if review_cols:
                    top_df['preview'] = df_db.nlargest(5, 'score')[review_cols[0]].str[:100] + "..."
                
                st.dataframe(top_df, use_container_width=True)
            
            with col_bottom:
                st.markdown("### Bottom 5 Worst Reviews")
                bottom_df = df_db.nsmallest(5, 'score')[['score', 'category']]
                
                if review_cols:
                    bottom_df['preview'] = df_db.nsmallest(5, 'score')[review_cols[0]].str[:100] + "..."
                
                st.dataframe(bottom_df, use_container_width=True)
            
            st.markdown("---")
            
            # Detailed table with filters
            st.markdown("### Detailed Data Explorer")
            
            col_f1, col_f2 = st.columns(2)
            
            with col_f1:
                selected_categories = st.multiselect(
                    "Filter by Category",
                    options=df_db['category'].unique(),
                    default=df_db['category'].unique()
                )
            
            with col_f2:
                min_score = int(df_db['score'].min())
                max_score = int(df_db['score'].max())
                
                if min_score < max_score:
                    score_range = st.slider(
                        "Filter by Score",
                        min_score,
                        max_score,
                        (min_score, max_score)
                    )
                else:
                    score_range = (min_score, max_score)
                    st.info(f"All scores are {min_score}")
            
            # Apply filters
            filtered_df = df_db[
                (df_db['category'].isin(selected_categories)) &
                (df_db['score'] >= score_range[0]) &
                (df_db['score'] <= score_range[1])
            ]
            
            st.write(f"Showing **{len(filtered_df):,}** of **{len(df_db):,}** reviews")
            
            # Column selector
            display_cols = st.multiselect(
                "Select columns to display",
                options=df_db.columns.tolist(),
                default=['score', 'category']
            )
            
            if display_cols:
                st.dataframe(filtered_df[display_cols], use_container_width=True, height=400)
            
            # Download
            st.markdown("---")
            st.markdown("### Download or Email Report")
            
            col_d1, col_d2 = st.columns(2)
            
            with col_d1:
                st.markdown("#### Download")
                csv = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download CSV Report",
                    data=csv,
                    file_name="amazon_reviews_report.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col_d2:
                st.markdown("#### Send via Email")
                recipient_email = st.text_input(
                    "Recipient Email",
                    placeholder="example@email.com",
                    key="email_input"
                )
                
                if st.button("Send Report", type="primary", use_container_width=True):
                    if not validate_email(recipient_email):
                        st.error("Invalid email address")
                    else:
                        with st.spinner("Sending email..."):
                            try:
                                # Save charts as images
                                chart1_path = "category_chart.png"
                                chart2_path = "score_chart.png"
                                
                                # Check if kaleido is installed (required for plotly image export)
                                try:
                                    import kaleido
                                    fig1.write_image(chart1_path, width=800, height=600)
                                    fig2.write_image(chart2_path, width=800, height=600)
                                except ImportError:
                                    st.error("⚠️ Please install kaleido: pip install kaleido")
                                    st.stop()
                                
                                success, message = send_report_email(
                                    recipient_email=recipient_email,
                                    csv_data=csv,
                                    chart1_path=chart1_path,
                                    chart2_path=chart2_path
                                )
                                
                                if success:
                                    st.success(f"✅ Report sent successfully to {recipient_email}")
                                    st.info("📬 Check your spam/junk folder if you don't see it in inbox")
                                else:
                                    st.error(f"❌ Error: {message}")
                                    
                                # Clean up image files
                                try:
                                    if os.path.exists(chart1_path):
                                        os.remove(chart1_path)
                                    if os.path.exists(chart2_path):
                                        os.remove(chart2_path)
                                except:
                                    pass
                                    
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please upload and process data first in the 'Upload & Process' tab")

# ==================== PAGE 3: HELP ====================
else:
    st.markdown("## How to Use This Tool")
    
    st.markdown("""
    ### Step-by-Step Guide
    
    #### 1. Upload Your Data
    - Go to **Upload & Process** tab
    - Click to upload your CSV file
    - The file should contain customer reviews
    
    #### 2. Configure Columns
    - Select which column contains the **review text**
    - Optionally select the **rating column** (1-5 stars)
    - Check the sample to verify correct selection
    
    #### 3. Run Analysis
    - Click **"Analyze Reviews & Store Results"**
    - Wait for processing to complete
    - View quick statistics
    
    #### 4. View Analytics
    - Go to **View Analytics** tab
    - Explore charts, metrics, and insights
    - Filter and download results
    
    ---
    
    ### Scoring System
    
    Reviews are scored based on:
    - **Positive words**: good, excellent, best, quality (+2 points each)
    - **Negative words**: bad, poor, worst, terrible (-2 points each)
    - **Intensifiers**: very, extremely (doubles the score)
    - **Negations**: not, never (reverses the sentiment)
    - **Star ratings**: 4-5 stars (+2), 1-2 stars (-2)
    
    ### Categories
    
    - **Highly Recommended**: Score ≥ 10
    - **Recommended**: Score 5-9
    - **Average**: Score 0-4
    - **Below Average**: Score -1 to -5
    - **Not Recommended**: Score < -5
    
    ---
    
    ### Tips
    
    - Ensure your CSV has a column with actual review text
    - Larger datasets take longer to process
    - Enable "Show Debug Info" in sidebar to troubleshoot
    - Download filtered results for further analysis
    - **Email Feature**: Install kaleido package to enable email reports with charts
    """)