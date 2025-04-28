
---

## Project Objectives

- Clean and normalize messy Excel input files
- Dynamically enforce data types for all fields
- Handle missing data (`NaN` vs `pd.NA`) correctly
- Extract and structure historical financial metrics separately
- Generate clean unique IDs for deals, contacts, and marketing participants
- Merge and link participants back to master contacts cleanly
- Prepare structured datasets ready for database ingestion

---

## Final Deliverables

- **deals_df** – Merged and cleaned deals table (business + consumer)
- **financial_data_df** – Separate table for historical EBITDA metrics - additional object
- **companies_df** – Master list of companies (PE firms + target companies)
- **contacts_df** – Cleaned list of contacts, properly typed, with Contact IDs
- **marketing_participants_df** – Marketing event attendees, linked to contacts

---

## Technologies Used

- Python 3.8+
- pandas
- numpy
- openpyxl
- re (regex for text cleaning)

---

## Key Features

- **Data Cleaning:** Automatic whitespace stripping, newline removal, smart null handling
- **Type Enforcement:** Batch type updates across columns with a simple dictionary
- **Historical Financial Extraction:** Clean split of EBITDA history into a dedicated table
- **ID Generation:** Auto-generate Deal_ID, Company_ID, Contact_ID, and Marketing_Participant_ID
- **Participant Matching:** Map marketing event participants back to master contacts using email

---

## Setup Instructions

1. Clone the repository or download the files
2. Install required packages:

   ```bash
   pip install pandas numpy openpyxl requests
3. Place raw Excel data inside a /data/ folder (optional)

4. Open pipeline.ipynb and run all cells
