# Amazon Review Sentiment Analyzer

## Overview
Professional web application built with Streamlit for comprehensive Amazon review sentiment analysis. Features enterprise-grade UI, advanced sentiment scoring, and automated reporting capabilities.

---

## Features

### Core Analysis
- 📤 **File Upload**: Support for CSV files up to 20GB or unlimited size via disk path
- 🤖 **Auto-Detection**: Intelligent column detection for review text and ratings
- ⚡ **High Performance**: Multiprocessing for datasets ≥50k rows
- 📊 **Smart Scoring**: Advanced sentiment analysis with negation, intensifiers, and context awareness
- 🎯 **5-Category Classification**: Highly Recommended, Recommended, Average, Below Average, Not Recommended

### Professional Interface
- 🎨 **Enterprise UI**: Professional gradient design with Amazon branding
- 📈 **Interactive Charts**: Plotly-powered pie charts and histograms
- 🔍 **Data Explorer**: Advanced filtering and column selection
- 📱 **Responsive Design**: Optimized for desktop and mobile

### Export & Sharing
- 💾 **Download Reports**: Export filtered results as CSV
- 📧 **Email Integration**: Send reports with charts via SendGrid API
- 📊 **Chart Export**: Automatic PNG generation for email attachments
- 🔒 **Secure**: Environment variable configuration for API keys

### Database & Performance
- 🗄️ **SQLite Storage**: Persistent data storage with indexing
- ⚡ **Optimized Queries**: B-tree indexes for fast filtering
- 📊 **Real-time Stats**: Live metrics in sidebar
- 🧹 **Data Management**: Easy database clearing functionality

---

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Required Packages
```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.0.0
sqlite3 (built-in)
multiprocessing (built-in)
sendgrid>=6.0.0
kaleido>=0.2.1
```

---

## Usage

### Run the Application
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Environment Setup (Optional)
For email functionality, set environment variables:
```bash
export SENDGRID_API_KEY="your-sendgrid-api-key"
export SENDER_EMAIL="your-verified-email@domain.com"
```

---

## How to Use

### 1. Upload & Process
- **Upload Method 1**: Drag & drop CSV files (up to 20GB)
- **Upload Method 2**: Enter disk path for unlimited file sizes
- **Auto-Detection**: System automatically identifies review and rating columns
- **Column Configuration**: Manual override for column selection
- **Processing**: Click "Analyze Reviews & Store Results" to start

### 2. View Analytics
- **Overview Dashboard**: Key metrics and statistics
- **Interactive Charts**: Category distribution pie chart and score histogram
- **Top/Bottom Reviews**: Best and worst performing reviews
- **Data Explorer**: Advanced filtering by category and score range
- **Column Selection**: Choose which data columns to display

### 3. Export & Share
- **Download**: Export filtered results as CSV
- **Email Reports**: Send analysis with charts to any email address
- **Chart Attachments**: Automatic PNG generation for visual reports

### 4. Help & Documentation
- **Scoring System**: Detailed explanation of sentiment calculation
- **Categories**: Understanding the 5-tier classification system
- **Tips**: Best practices for optimal results

---

## File Structure

```
amazon-review-analyzer/
├── app.py                   # Main Streamlit application
├── scoring_engine.py        # Sentiment analysis engine
├── email_utils.py          # SendGrid email integration
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .streamlit/
│   └── config.toml        # Streamlit configuration
├── .gitignore
└── README.md
```

---

## Technologies Used
- **Streamlit**: Modern web framework for data applications
- **Pandas**: Advanced data manipulation and analysis
- **Plotly**: Interactive data visualization
- **SQLite**: Lightweight database with indexing
- **SendGrid**: Professional email delivery service
- **Multiprocessing**: Parallel processing for large datasets
- **Kaleido**: Static image export for charts

---

## Sentiment Scoring Algorithm

### Advanced Features
- **Lexicon-Based Analysis**: Positive/negative word detection
- **Negation Handling**: "not good" correctly identified as negative
- **Intensifier Support**: "very excellent" gets higher positive score
- **CAPS Emphasis**: "AMAZING" receives bonus points
- **Star Rating Integration**: 1-5 star ratings influence final score
- **Context Awareness**: Sophisticated text preprocessing

### Score Categories
- **Highly Recommended**: Score ≥ 10 (Exceptional reviews)
- **Recommended**: Score 5-9 (Good reviews)
- **Average**: Score 0-4 (Neutral reviews)
- **Below Average**: Score -1 to -5 (Poor reviews)
- **Not Recommended**: Score < -5 (Very poor reviews)

---

## Performance Features

### Scalability
- **Small Datasets** (<50k rows): Simple processing for speed
- **Large Datasets** (≥50k rows): Multiprocessing with CPU optimization
- **Batch Processing**: 10k row batches for memory efficiency
- **Progress Tracking**: Real-time progress bars and status updates

### Database Optimization
- **Indexed Storage**: B-tree indexes on category, rating, and score
- **Batch Insertion**: 5k row chunks for optimal performance
- **Query Optimization**: Fast filtering and aggregation

---

## Email & Export Features

### Download Options
- **CSV Export**: Complete dataset or filtered results
- **Custom Filtering**: By category, score range, and columns
- **Instant Download**: Browser-based file download

### Email Integration
- **SendGrid API**: Professional email delivery
- **Chart Attachments**: Automatic PNG generation
- **Report Package**: CSV + 2 chart images per email
- **Email Validation**: Built-in format checking
- **Delivery Confirmation**: Success/error status reporting

---

## License
MIT License
