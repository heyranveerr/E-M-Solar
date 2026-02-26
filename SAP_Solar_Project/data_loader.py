import pandas as pd
from app import create_app, db
from models.project import SolarProject
from models.material import Material
from models.finance import FinanceTransaction

def load_sow_data(file_path):
    """
    Reads and cleans the 'SOW' sheet from the Excel file and loads it into the database.
    """
    app = create_app()
    with app.app_context():
        try:
            # Manually define column headers
            columns = [
                'S_No', 'Item_Description', 'Specification', 'Qty_Process_P',
                'Qty_FMG_1', 'Qty_Storage', 'Total', 'UOM', 'MAKE',
                'Supply', 'Service', 'Rate', 'Amount'
            ]

            # Read the 'SOW' sheet, skipping the first 7 rows and using the manually defined columns
            df = pd.read_csv(file_path, sheet_name='SOW', header=None, skiprows=8, names=columns)

            # Drop rows that are entirely empty
            df = df.dropna(how='all')

            # Forward-fill section headers in 'S_No' column
            df['S_No'] = df['S_No'].fillna(method='ffill')

            # Remove rows that are just section headers (where 'Item_Description' is null)
            df = df[df['Item_Description'].notna()]
            
            # Create a project
            project = SolarProject.query.first()
            if not project:
                project = SolarProject(name='Saatvik Agro', capacity_mw=1.0, budget=1000000, status='In Progress')
                db.session.add(project)
                db.session.commit()

            # Iterate over the dataframe and create Material and FinanceTransaction objects
            for index, row in df.iterrows():
                material = Material(
                    project_id=project.id,
                    name=row['Item_Description'],
                    specification=row['Specification'],
                    quantity=row['Total'],
                    uom=row['UOM'],
                    make=row['MAKE'],
                    supply=row['Supply'],
                    service=row['Service'],
                    rate=row['Rate'],
                    amount=row['Amount']
                )
                db.session.add(material)
                db.session.commit()

                if row['Amount']:
                    finance_transaction = FinanceTransaction(
                        project_id=project.id,
                        material_id=material.id,
                        expense=row['Amount'],
                        description=row['Item_Description']
                    )
                    db.session.add(finance_transaction)
                    db.session.commit()
            
            print("Data loaded successfully.")

        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    load_sow_data('SOW-Rooftop Moraina-Saatvik Agro-R1-291125.csv')

