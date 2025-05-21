# UNDRSTND Analytics Frontend

A Streamlit-based frontend for the UNDRSTND analytics platform, providing a user-friendly interface for the scan_sources and competitor_analysis modules.

## Features

- **Source Scanner**: Analyze various sources and extract market forces
- **Competitor Analysis**: Perform in-depth analysis of competitors
- **User-friendly Interface**: Intuitive forms and visualizations
- **Persistent State**: Saves form data between sessions
- **Responsive Design**: Works on different screen sizes

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Node.js and npm (for optional development tools)

## Installation

1. Clone the repository (if not already done):
   ```bash
   git clone <repository-url>
   cd undrstnd
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   cd frontend
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the example environment file and update it with your settings:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file to set your configuration options.

## Running the Application

To start the Streamlit app, run:

```bash
streamlit run app.py
```

This will start the development server and open the application in your default web browser. If it doesn't open automatically, you can access it at `http://localhost:8501`.

## Project Structure

```
frontend/
├── app.py                 # Main Streamlit application
├── pages/                 # Individual pages
│   ├── 1_🔍_Source_Scanner.py
│   └── 2_🏢_Competitor_Analysis.py
├── utils/                 # Utility functions
│   └── analysis_utils.py
├── static/                # Static files (images, CSS, etc.)
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Development

### Adding New Pages

To add a new page to the application:

1. Create a new Python file in the `pages` directory.
2. The file name should start with a number followed by an underscore and the page name (e.g., `3_📈_Dashboard.py`).
3. The page will automatically appear in the sidebar navigation.

### Styling

Custom CSS can be added to the `static` directory and included in your pages using:

```python
with open("static/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
```

## Integration with Backend

The frontend is designed to work with the `scan_sources` and `competitor_analysis` modules. The integration points are defined in `utils/analysis_utils.py`.

### Environment Variables

- `API_BASE_URL`: Base URL for the backend API (if applicable)
- `DEBUG`: Set to `True` for development mode

## License

[Your License Here]

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
