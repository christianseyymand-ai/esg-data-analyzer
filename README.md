# ESG Data Analyzer

Python-based ESG data analysis tool for processing Excel sustainability data, validating ESG inputs, and generating reporting-ready outputs for dashboards, internal reporting, and executive communication.

This project demonstrates how ESG teams can use Python and AI-assisted workflows to transform raw sustainability data into structured insights.

---

## Project Summary

ESG teams often collect sustainability data through spreadsheets from different departments, facilities, suppliers, or business units.

This project simulates an ESG data analysis workflow where raw data is collected through an Excel template, processed with Python, and transformed into structured outputs for reporting and decision-making.

The project includes:

- ESG data collection template
- Python-based data processing script
- Automated data validation and analysis
- Reporting-ready output files
- AI-assisted executive summary generation
- Case study documentation

---

## Business Challenge

Sustainability and ESG teams often face challenges such as:

- Fragmented ESG data
- Manual spreadsheet work
- Inconsistent formats
- Missing or incomplete values
- Difficulty preparing reporting-ready outputs
- Time-consuming executive summary preparation
- Limited automation in ESG reporting workflows

This project shows how Python can help make ESG data workflows more structured, repeatable, and scalable.

---

## Solution Built

I developed a Python-based ESG data analyzer that:

- Reads ESG data from an Excel collection template
- Cleans and processes the dataset
- Validates missing or inconsistent values
- Calculates key ESG and sustainability indicators
- Structures outputs for reporting and dashboard use
- Generates files in the `outputs/` folder
- Uses an AI-assisted workflow to support executive-level ESG analysis

---

## Repository Structure

```text
esg-data-analyzer/
├── README.md
├── analizar_v3.py
├── requirements.txt
├── .env.example
├── data/
│   └── ESG_Data_Collection_Template.xlsx
├── outputs/
│   └── .gitkeep
└── case-study/
    └── ESG_Analyzer_CaseStudy.pdf
```

---

## Main Script

The main script is:

```text
analizar_v3.py
```

The script processes the Excel template and generates output files inside:

```text
outputs/
```

---

## Input File

The project uses the following Excel input template:

```text
data/ESG_Data_Collection_Template.xlsx
```

The template is designed to collect ESG and sustainability-related data in a structured way.

Example data categories may include:

- Energy consumption
- Water consumption
- Waste generation
- Emissions-related activity data
- Workforce and social indicators
- Governance or compliance indicators

---

## Outputs

The script generates reporting-ready outputs in the `outputs/` folder.

These outputs may include:

- Cleaned ESG dataset
- Summary tables
- ESG indicator analysis
- Executive-style ESG summary
- Reporting-ready files for dashboards or internal review

---

## Tools Used

- Python
- pandas
- openpyxl
- Anthropic API
- Excel
- ESG data analysis
- Sustainability reporting workflows

---

## Environment Variables

This project uses an API key for AI-assisted analysis.

Create a local `.env` file based on `.env.example`:

```env
ANTHROPIC_API_KEY=your_api_key_here
```

Do not upload your real `.env` file to GitHub.

---

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## How to Run

Run the main script:

```bash
python analizar_v3.py
```

Generated files will be saved in:

```text
outputs/
```

---

## Case Study

A case study PDF is included in:

```text
case-study/ESG_Analyzer_CaseStudy.pdf
```

The case study explains the project context, workflow, outputs, and business value.

---

## Skills Demonstrated

This project demonstrates skills relevant to ESG, sustainability, and data roles:

- ESG data analysis
- Python automation
- Excel-based data workflows
- Sustainability reporting support
- ESG data validation
- Reporting-ready output generation
- AI-assisted analysis
- Executive-level ESG communication
- Workflow documentation

---

## Use Case

This project is relevant for ESG and sustainability teams that need to:

- Automate manual ESG data workflows
- Process Excel-based sustainability data
- Improve reporting consistency
- Generate structured outputs for dashboards
- Support internal ESG reporting
- Create executive summaries from sustainability data

---

## About the Project

This is a simulated portfolio project created to demonstrate ESG data automation, Python workflow design, and sustainability reporting support.

The data is sample/synthetic and does not represent any real company or client.

---

## Author

**Christian Seymand**  
ESG & Carbon Data Analyst

I help ESG teams build carbon inventories, dashboards, and reporting workflows.

Portfolio: [christianseymand.crd.co](https://christianseymand.crd.co/)  
LinkedIn: [linkedin.com/in/christian-seymand-934244137](https://linkedin.com/in/christian-seymand-934244137/)
