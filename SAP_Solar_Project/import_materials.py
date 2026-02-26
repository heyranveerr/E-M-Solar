import csv
import os
import sys
sys.path.append('.')

from app import create_app
from extensions import db
from models.material import Material

app = create_app()

def import_materials_from_csv(csv_file_path, project_id=1):
    with app.app_context():
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            # Skip header rows until data
            for row in reader:
                if row[0] == 'S.No.':
                    next(reader)  # Skip the Qty labels row
                    break
            for row in reader:
                if row[0].isdigit():
                    s_no = row[0]
                    name = row[1]
                    specification = row[2]
                    qty_process_p = row[3]
                    qty_fmg1 = row[4]
                    qty_storage = row[5]
                    total_qty = row[6]
                    uom = row[7]
                    make = row[8]
                    supply = row[9]
                    service = row[10]
                    rate = row[11]
                    amount = row[12]

                    material = Material(
                        project_id=project_id,
                        name=name,
                        specification=specification,
                        qty_process_p=qty_process_p,
                        qty_fmg1=qty_fmg1,
                        qty_storage=qty_storage,
                        total_qty=total_qty,
                        uom=uom,
                        make=make,
                        supply=supply,
                        service=service,
                        rate=rate,
                        amount=amount
                    )
                    db.session.add(material)
            db.session.commit()
            print("Materials imported successfully!")

if __name__ == '__main__':
    csv_file = 'EMSolar/SOW-Rooftop Moraina-Saatvik Agro-R1-291125.csv'
    import_materials_from_csv(csv_file)
