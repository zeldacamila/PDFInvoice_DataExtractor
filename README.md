# PDF Invoices Data Extractor

Use PDFInvoice_DataExtractor API to extract data from a DIAN invoice.

---

## Technologies Used

- [FastAPI](https://fastapi.tiangolo.com/)
- [pdfplumber](https://github.com/jsvine/pdfplumber)

## Setup Instructions

1. Clone the repository:

```bash
git clone https://github.com/zeldacamila/PDFInvoice_DataExtractor.git
cd PDFInvoice_DataExtractor
```

2. Create a virtual enviroment (optional but recommended):

```bash
python -m venv venv
```

2. Activate the virtual env. For Windows use:

```bash
venv\Scripts\activate
```

For macOS and Linux, use:

```bash
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run your FastAPI application:

```bash
uvicorn pdf-excelApp.main:app --host 0.0.0.0 --port 7860 --reload
```

5. Access to the API:
   With your app running you can access it through your browser by navigating to http://localhost:7860.

---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
