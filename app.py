import streamlit as st
import pandas as pd
import io

def process_rncp_file(uploaded_file):
    # Read the uploaded file based on its extension
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension == 'csv':
        df = pd.read_csv(uploaded_file)
    elif file_extension in ['xls', 'xlsx']:
        try:
            # Try to read with sheet name 'Onglet 3 - référentiel NPEC'
            df = pd.read_excel(uploaded_file, sheet_name='Onglet 3 - référentiel NPEC')
        except:
            try:
                # If specific sheet not found, use first sheet
                df = pd.read_excel(uploaded_file)
                st.warning("Sheet 'Onglet 3 - référentiel NPEC' not found. Using first sheet.")
            except Exception as e:
                st.error(f"Error reading Excel file: {str(e)}")
                return None
    else:
        st.error("File format not supported. Please upload a CSV or Excel file.")
        return None
    
    # Skip initial description rows if they exist
    if df.iloc[0:2].isna().any(axis=1).all():
        df = df.iloc[2:].reset_index(drop=True)
    
    # Use first row as header if current headers are unnamed
    if df.columns.str.contains('Unnamed').any():
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)
    
    # Check if 'RNCP' column exists
    if 'RNCP' not in df.columns:
        st.error("The file must contain a column named 'RNCP'")
        return None
    
    # Split RNCP codes and expand rows
    df['RNCP'] = df['RNCP'].str.split('/')
    df = df.explode('RNCP')
    
    return df

def main():
    st.title("RNCP Code Processor")
    
    st.write("""
    This app processes files containing RNCP codes. It will:
    1. Skip initial description rows if present
    2. Handle correct column headers
    3. Split multiple RNCP codes separated by '/'
    4. Create separate rows for each RNCP code while maintaining other information
    """)
    
    uploaded_file = st.file_uploader("Upload your file (CSV or Excel)", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file is not None:
        df = process_rncp_file(uploaded_file)
        
        if df is not None:
            st.write("Preview of processed data:")
            st.dataframe(df.head())
            
            # CSV download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download processed file (CSV)",
                data=csv,
                file_name="processed_rncp.csv",
                mime="text/csv"
            )
            
            # Display statistics
            st.subheader("File Statistics")
            st.write(f"Number of processed rows: {len(df)}")
            st.write(f"Number of unique RNCP codes: {df['RNCP'].nunique()}")

if __name__ == '__main__':
    main()