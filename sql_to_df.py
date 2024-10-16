import psycopg2
import pandas as pd

# Redshift connection parameters
host = "razor-workgroup.815361800176.eu-central-1.redshift-serverless.amazonaws.com"
port = "5439"  # default Redshift port
dbname = "dev"
user = "adriana.mejia@razor-group.com"
password = "P@$$phr@se8"

# SQL query to be migrated
sql_query = """
select .........
"""

try:
    # Connect to Redshift
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password
    )
    
    # Execute query and load the result into a DataFrame
    df = pd.read_sql_query(sql_query, conn)

    # Display the DataFrame
    print(df)

except Exception as e:
    print(f"Error: {e}")

finally:
    if 'conn' in locals() and conn:
        conn.close()

