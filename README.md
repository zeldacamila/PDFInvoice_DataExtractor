# PDFInvoice_DataExtractor
This is a Fast API builded to extract and collect data from pdf DIAN invoices

## Technologies Used

- [FastAPI](https://fastapi.tiangolo.com/)
- [pdfplumber](https://github.com/jsvine/pdfplumber)

## Environment Setup

1. Clone the repository:

```bash
git clone https://github.com/zeldacamila/PDFInvoice_DataExtractor.git
cd PDFInvoice_DataExtractor
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
uvicorn pdf-excelApp.main:app --host 0.0.0.0 --port 7860 --reload
```

## Usage
- Access http://localhost:7860/docs# in your browser to interact with the API endpoints.
