import pandas as pd
import numpy as np
import openpyxl
import re

#-----------------------BASIC CLEANING FUNCS------------------------------------------

def cleanse_column_names(df):
    '''Clean column names to remove whitespaces/new lines.'''
    df.columns = df.columns.str.strip().str.replace('\n', '', regex=True)
    return df

def modernize_nans(df):
    '''Standardize nans to pd.NA.'''
    df = df.replace(['N/A', 'NA', 'None', '-', '', np.nan, None], pd.NA)
    return df

def update_data_types(df, dtype_dict):
    '''Handles quicker changes to data types.'''
    for col, dtype in dtype_dict.items():
        df[col] = df[col].astype(dtype)
    
    return df

def date_parsing(x):
    '''Handles inaccurate Excel date types, some in text style.'''
    if pd.isna(x):
        return pd.NaT
    
    x = str(x).strip()

    try:
        return pd.to_datetime(x)
    except:
        try:
            return pd.to_datetime(x, format = '%b-%y')
        except:
            return pd.NaT

def clean_dash_text(text):
    '''Clean any dash text, usually present in excel fields, make cleaner with commas.'''
    if pd.isna(text):
        return text

    text = str(text).strip()

    # Remove leading dash and any spaces after it
    text = re.sub(r'^-\s*', '', text)

    # Replace dashes between words with commas
    text = re.sub(r'\s*-\s*', ', ', text)

    # Final cleanup
    text = text.strip()

    return text

def clean_phone(phone):
    '''Clean phone number for standardization.'''
    if pd.isna(phone):
        return pd.NA
    return re.sub(r'\D', '', str(phone))

#--------------FINANCIAL DATAFRAME HANDLING-------------------------------------------

def clean_numeric_value(value):
    '''Cleans numeric value correctly handling real numbers and parentheses-wrapped strings.'''
    if pd.isna(value):
        return pd.NA

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value).strip()

    # Check if the value is wrapped in parentheses
    is_negative = False
    if value.startswith('(') and value.endswith(')'):
        is_negative = True
        value = value[1:-1]  # Strip parentheses

    # Remove anything non-numeric except .
    value = re.sub(r'[^\d\.]', '', value)

    if not value:  # Empty after cleaning
        return pd.NA

    try:
        numeric_value = float(value)
        if is_negative:
            numeric_value = -numeric_value
        return numeric_value
    except Exception as e:
        print(f"Error cleaning value {value}: {e}")
        return pd.NA


def extract_text_content(value):
    '''Remove text content in fields.'''
    if pd.isna(value):
        return ''
    
    value = str(value)
    value = re.sub(r'[\d\.\(\)]', '', value)
    text = re.findall(r'[A-Za-z]+', value)

    return ' '.join(text) if text else ''

def find_target_column(text):
    '''Parse through text to look for possible relocation of fields.'''
    text = text.lower()
    if 'ltm' in text:
        return 'LTM EBITDA'
    if 'ttm' in text:
        return 'LTM Revenue'
    return None

def is_cad_currency(text):
    '''Allow for processing of CAD values.'''
    if pd.isna(text):
        return False
    text = str(text).lower()
    return 'cad' in text or 'c$' in text

def process_financial_dataframe(df, columns_to_check, cad_to_usd_rate=0.73):
    '''Process financial columns in dataframes to standardize currency, clean text in columns, and ensure proper location of field.'''
    if 'Notes' not in df.columns:
        df['Notes'] = pd.NA

    audit_log = []  # Keep track of what we change

    for idx, row in df.iterrows():
        for col in columns_to_check:
            value = row[col]
            if pd.isna(value):
                continue

            original_value = value
            str_val = str(value)

            # Try to extract text (like LTM, CAD, etc.)
            extracted_text = extract_text_content(str_val)
            is_cad = is_cad_currency(str_val)
            numeric_value = clean_numeric_value(value)

            # If CAD, convert to USD
            if is_cad and pd.notna(numeric_value):
                numeric_value *= cad_to_usd_rate

            # Replace the value with cleaned number
            df.at[idx, col] = numeric_value

            # Build up notes if needed
            notes = []
            if extracted_text:
                notes.append(f"{col}: {extracted_text}")
            if is_cad:
                notes.append("originally stored as CAD")

            if notes:
                current_notes = df.at[idx, 'Notes']
                new_notes = '; '.join(notes)
                if pd.isna(current_notes):
                    df.at[idx, 'Notes'] = new_notes
                else:
                    df.at[idx, 'Notes'] = str(current_notes) + "; " + new_notes

            # Move value if needed (LTM EBITDA, etc.)
            target_col = find_target_column(extracted_text)
            if target_col:
                if target_col not in df.columns:
                    df[target_col] = pd.NA
                df.at[idx, target_col] = numeric_value

            # Log the change
            audit_log.append({
                'Row Index': idx,
                'Column Name': col,
                'Old Value': original_value,
                'New Value': numeric_value,
                'Notes Added': new_notes if notes else None,
                'Migrated To Column': target_col
            })

    audit_df = pd.DataFrame(audit_log)

    return df, audit_df
