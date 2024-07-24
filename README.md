# Alfred AI - README

## Overview
Alfred AI is a secure, feature-rich tool designed to assist users with document processing and analysis. It prioritizes privacy by avoiding the sharing of your data with third-party companies like Google or OpenAI. The application uses a variety of Python libraries and tools, such as Streamlit, spaCy, TextBlob, and pdfplumber, to provide comprehensive functionalities including general chat, PDF analysis, and more.

## Features
1. **General Chat**: Interact with Alfred AI, a helpful assistant, to ask questions and receive responses in various tones.
2. **PDF Analysis**: Upload PDF files to extract text, identify named entities, analyze sentiment, and more.
3. **Settings**: Customize the response tone and configure API settings.

## Installation

### Prerequisites
- Python 3.7 or higher
- Necessary Python packages

### Setup

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd alfred-ai
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Download the spaCy model:
    ```bash
    python -m spacy download en_core_web_sm
    ```

## Usage

### Running Locally
To start the application, run:
```bash
streamlit run app.py
```

### Accessing Online
You can also use the app directly online at [Alfred AI](https://alfredai.streamlit.app).

### Main Pages
- **Welcome**: Enter your name and API URL to start using Alfred AI.
- **General Chat**: Engage in conversations with Alfred AI.
- **PDF Analysis**: Upload and analyze PDF files.
- **Settings**: Adjust response tone and API settings.

## Key Components

### 1. `Conversation` Class
Handles interactions with the backend API, managing messages and response tones.

### 2. PDF Functions
- `extract_text_from_pdf(file)`: Extracts text from uploaded PDF files.
- `extract_entities(text)`: Extracts named entities using spaCy.
- `analyze_sentiment(text)`: Analyzes sentiment using TextBlob.

### 3. Utility Functions
- `clean_text(text)`: Cleans and formats text.
- `format_entities_for_display(entities)`: Formats extracted entities for display.
- `apply_color_map(df)`: Applies a color map to entities based on type.
- `get_table_download_link(df)`: Generates a download link for extracted data.
- `export_conversation()`: Exports conversation history.

## Error Handling
The application includes robust error handling for common issues such as network errors, timeouts, and missing models.

## Contributing
1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Submit a pull request.

## License
This project is licensed under the MIT License - see the [The MIT License](https://opensource.org/license/mit) file for details.

## Acknowledgments
Special thanks to the developers and communities of the libraries used in this project, including Streamlit, spaCy, TextBlob, and pdfplumber.

## Contact
For any inquiries or issues, please contact [abhiabhishektiwari1106@gmail.com](mailto:abhiabhishektiwari1106@gmail.com).

---

By prioritizing privacy and providing comprehensive document analysis features, Alfred AI aims to be your go-to tool for secure and efficient document management. Enjoy exploring the capabilities of Alfred AI!
