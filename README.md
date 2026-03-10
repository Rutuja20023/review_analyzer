# Amazon Review Sentiment Analyzer - Frontend

## Overview
Interactive web interface built with Streamlit for uploading and previewing Amazon review datasets.

---

## Features
- 📤 CSV file upload
- 📊 Data preview with adjustable row count
- 📈 Dataset statistics (total rows and columns)
- 🎨 Clean, user-friendly interface

---

## Installation

### Prerequisites
- Python 3.x
- pip

### Install Dependencies
```bash
pip install streamlit pandas
```

---

## Usage

### Run the Application
```bash
streamlit run demo_ui.py
```

The app will open in your browser at `http://localhost:8501`

---

## How to Use

1. **Upload CSV File**
   - Click "Browse files" button
   - Select your Amazon review CSV file
   - Supported format: `.csv`

2. **View Statistics**
   - Total rows in dataset
   - Total columns in dataset

3. **Preview Data**
   - Use slider to select number of rows (5-100)
   - View data in interactive table

---

## File Structure

```
frontend/
├── demo_ui.py           # Main Streamlit application
├── .streamlit/
│   └── config.toml      # Streamlit configuration
├── .gitignore
└── README.md
```

---

## Technologies Used
- **Streamlit**: Web framework for data apps
- **Pandas**: Data manipulation and analysis

---

## Screenshots

### Upload Interface
- File uploader with drag-and-drop support

### Data Preview
- Interactive table with adjustable row count
- Dataset statistics display

---

## Future Enhancements
- [ ] Sentiment analysis integration
- [ ] Data visualization (charts, graphs)
- [ ] Export analyzed results
- [ ] Filter and search functionality
- [ ] Real-time sentiment scoring

---

## Requirements
```
streamlit>=1.28.0
pandas>=2.0.0
```

---

## License
MIT License
