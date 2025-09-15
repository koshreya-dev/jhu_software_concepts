"""
Refreshes the existing applicant dataset with new scraped data. 
Reads temporary JSON files produced by the scraper and LLM pipeline. 
Cleans up formatting issues and merges new rows into the database. 
"""
import os
import psycopg_pool
import json

# Use the 'DATABASE_URL' environment variable to connect to the database.
pool = psycopg_pool.ConnectionPool(os.environ['DATABASE_URL'], min_size= 0, max_size= 80)

# Use dataset that is created from running update_data.py
jsonl_file_path = r'C:\Users\Shreya\jhu_software_concepts\module_3\temp_new_rows_llm.json'
table_name = 'applicants'

#Get a connection from the pool.
conn = pool.getconn()

with conn.cursor() as cur:
  # Open json file with data
  with open(jsonl_file_path, 'r', encoding='utf-8') as f:
                # Read the entire file content
                file_content = f.read()
                # Wrap the content in a JSON array and parse it
                data_from_json = json.loads(f'[{file_content.replace("}\n{", "},{")}]')
  # Re-order data                            
  data_from_json.reverse()
  
  # Empty list to populate                 
  data_to_insert = []
  
  # Iterate through json and get respective fields
  for json_data in data_from_json:
    record = (          
        json_data.get('program'),
        json_data.get('comments'),
        json_data.get('date_added'),
        json_data.get('url'),
        json_data.get('status'),
        json_data.get('term'),
        json_data.get('US/International'),
        json_data.get('GPA'),
        json_data.get('GRE'),
        json_data.get('GRE V'),
        json_data.get('GRE AW'),
        json_data.get('Degree'),
        json_data.get('llm-generated-program'),
        json_data.get('llm-generated-university')
    )
    data_to_insert.append(record)

  # Insert data
  columns = [
      'program', 'comments', 'date_added', 'url', 'status', 'term',
      'us_or_international', 'gpa', 'gre', 'gre_v', 'gre_aw', 'degree', 
      'llm_generated_program', 'llm_generated_university'
  ]
  
  # Insert using executemany from 3rd version of psycopg
  cur.executemany(
    f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
    data_to_insert
  )
  print(f"Successfully inserted {len(data_to_insert)} records into {table_name}")
  
  # Commit the changes to the database
  conn.commit()

# Close the connection
pool.putconn(conn)
conn.close()
print("Script finished and pool closed.")
