import requests

nanobot_default_tables = ["table", "column", "datatype"]


def export_cas_data(output_folder: str):
    print("INN export_cas_data")
    response = requests.get('http://localhost:3000/table.json?limit=20&shape=value_rows')
    print(response.status_code)
    print(response.text)
    # response.raise_for_status()
    #
    # table_records = response.json()
    # for table_rec in table_records:
    #     if table_rec["table"] not in table_rec["table"]:
    #         print(table_rec["table"])
    print("OUTTT")
