import json
import requests

# ฟังก์ชันดึง schema จาก tables.json
def get_schema(db_id, tables_file='tables.json'):
    with open(tables_file, 'r') as f:
        tables = json.load(f)
    for db in tables:
        if db['db_id'] == db_id:
            schema = []
            # สร้าง mapping จาก table_index ไปยัง table_name
            for table_idx, table_name in enumerate(db['table_names']):
                # กรองคอลัมน์ที่ตรงกับ table_idx และไม่ใช่ [-1, "*"]
                columns = [col[1] for col in db['column_names'] if col[0] == table_idx]
                if columns:  # เพิ่มเฉพาะตารางที่มีคอลัมน์
                    schema.append(f"Table: {table_name}, Columns: {', '.join(columns)}")
            return '\n'.join(schema)
    return ""

# ฟังก์ชันเรียก Ollama API
def query_ollama(prompt):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "gemma3:12b",
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()['response'].strip()
    except Exception as e:
        print(f"Error: {e}")
        return ""

# อ่าน dev.json
with open('dev.json', 'r') as f:
    dev_data = json.load(f)

# สร้าง predicted_sql.txt
with open('predicted_sql.txt', 'w') as f:
    for i, item in enumerate(dev_data):
        question = item['question']
        db_id = item['db_id']
        schema = get_schema(db_id)
        prompt = f"""Given the following database schema:
{schema}
Translate this natural language question into a valid SQL query:
{question}
Output only the SQL query, no explanations or additional text."""
        sql = query_ollama(prompt)
        f.write(f"{sql}\n")
        print(f"Processed question {i+1}/{len(dev_data)}")

print("Generated predicted_sql.txt")