# ESG Data Analyzer

A Python-based ESG and GHG inventory analyzer that calculates Scope 1, Scope 2, and selected Scope 3 emissions for companies in Latin America.

This project demonstrates how Python and AI can support carbon accounting workflows, emissions data processing, and ESG reporting.

---

## Overview

Many companies collect sustainability data across different departments, suppliers, and formats. This makes it difficult to calculate emissions consistently, identify hotspots, and generate reporting-ready outputs.

The ESG Data Analyzer automates a simplified GHG inventory workflow. It calculates emissions across Scope 1, Scope 2, and selected Scope 3 categories, then generates structured outputs that can be used for ESG analysis and reporting.

The project is designed as a portfolio case study for ESG data analysis, carbon accounting, and sustainability reporting roles.

---

## What this project does

The analyzer processes company-level sustainability data and generates:

- Scope 1 emissions from fuel consumption
- Scope 2 emissions from electricity consumption
- Scope 3 emissions from selected categories
- A complete GHG inventory in CSV format
- An AI-assisted ESG report with insights, reduction opportunities, and methodological limitations

---

## Scope coverage

This project follows a simplified GHG Protocol-style structure.

### Scope 1

Direct emissions from fuel combustion.

Examples:

- Diesel
- Gasoline
- Natural gas
- LPG

### Scope 2

Indirect emissions from purchased electricity.

The project uses country-level grid emission factors for selected Latin American countries.

### Scope 3

Selected Scope 3 categories are included:

- Category 1: Purchased goods and services
- Category 4: Upstream transportation and distribution
- Category 6: Business travel
- Category 7: Employee commuting

---

## Project structure

```text
esg-data-analyzer/
  case-study/
    project-summary.md
  data/
  outputs/
    ghg_inventory_complete.csv
    esg_report_ai_assisted.txt
  .env.example
  README.md
  ghg_inventory_analyzer.py
  requirements.txt

Tech stack
Python
Pandas
Anthropic API
python-dotenv
CSV reporting
Files
ghg_inventory_analyzer.py

Main Python script. It calculates emissions, creates a GHG inventory, and optionally generates an AI-assisted ESG report.

requirements.txt

Project dependencies.

.env.example

Example environment variable file for API key configuration.

outputs/ghg_inventory_complete.csv

Generated GHG inventory output.

outputs/esg_report_ai_assisted.txt

Generated AI-assisted ESG report.

case-study/project-summary.md

Project case study and portfolio explanation.

data/

Folder for sample input datasets or supporting ESG data.

How to run
1. Install dependencies
pip install -r requirements.txt

If needed, on Windows:

py -m pip install -r requirements.txt
2. Run without AI reporting

This mode generates the GHG inventory CSV without requiring an API key.

python ghg_inventory_analyzer.py --no-ai

On Windows:

py ghg_inventory_analyzer.py --no-ai
3. Run with AI-assisted ESG reporting

To generate the AI-assisted ESG report, create a .env file in the project root.

Use .env.example as a template:

ANTHROPIC_API_KEY=your_api_key_here

Then run:

python ghg_inventory_analyzer.py

On Windows:

py ghg_inventory_analyzer.py
Outputs

The script generates files inside the outputs/ folder.

outputs/ghg_inventory_complete.csv
outputs/esg_report_ai_assisted.txt

The CSV output contains company-level emissions results, including Scope 1, Scope 2, Scope 3 categories, total emissions, and Scope 3 percentage.

The text report provides an AI-assisted ESG analysis, including rankings, emissions hotspots, reduction opportunities, and methodological limitations.

Methodology

This project uses a simplified carbon accounting methodology inspired by the GHG Protocol Corporate Standard.

Scope 1 methodology

Scope 1 emissions are calculated from fuel consumption using fuel-specific emission factors.

Scope 1 emissions = fuel consumption x emission factor
Scope 2 methodology

Scope 2 emissions are calculated from electricity consumption using country-level grid emission factors.

Scope 2 emissions = electricity consumption x grid emission factor
Scope 3 methodology

Scope 3 emissions are calculated using simplified activity-based and spend-based methods.

Included categories:

Category 1: Purchased goods and services
Category 4: Upstream transportation and distribution
Category 6: Business travel
Category 7: Employee commuting
Important note on emission factors

The emission factors used in this project are simplified and intended for portfolio, learning, and demonstration purposes.

For real-world corporate reporting, emission factors should be validated against official and up-to-date sources such as:

GHG Protocol
IPCC
IEA
DEFRA / UK Government conversion factors
National grid emission factor databases
Supplier-specific data where available
Example use case

A sustainability or ESG team needs to quickly estimate emissions across multiple companies or business units.

The team has data related to:

Electricity consumption
Fuel consumption
Supplier spend
Freight activity
Business travel
Employee commuting

This tool converts that data into a structured emissions inventory and generates a draft ESG analysis report.

Skills demonstrated
ESG data analysis
Carbon accounting
GHG inventory development
Scope 1, 2 and 3 emissions modeling
Python automation
Data transformation with Pandas
AI-assisted sustainability reporting
Reporting-ready data outputs
Sustainability analytics for Latin American companies
Environmental data storytelling
Limitations

This project is a simplified portfolio model and does not replace a full corporate GHG inventory.

Main limitations include:

Emission factors are simplified
Supplier-specific Scope 3 data is not included
Market-based Scope 2 calculations are not included
Uncertainty analysis is not included
Scope 3 coverage is limited to selected categories
The model uses sample company data for demonstration purposes
The AI-generated report should be reviewed before any real-world reporting use
Future improvements

Potential improvements include:

Add external CSV input support
Add Power BI dashboard integration
Add year-over-year emissions comparison
Add emissions intensity by revenue and employee
Add market-based and location-based Scope 2 reporting
Add more Scope 3 categories
Add supplier-level emissions data
Add uncertainty ranges
Add automated charts and visual summaries
Add automated PDF report generation
Portfolio relevance

This project is relevant for roles such as:

ESG Data Analyst
Sustainability Analyst
Carbon Accounting Analyst
ESG Reporting Analyst
Climate Data Analyst
Sustainability Consultant
ESG Data & Reporting Consultant

It shows the ability to connect sustainability knowledge, data analysis, automation, and reporting into one practical workflow.

Author

Created by Christian Seymand as part of an ESG Data Analyst / Carbon Accounting portfolio.

Portfolio: christianseymand.crd.co
  
