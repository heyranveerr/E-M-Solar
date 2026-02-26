from app import create_app, db
from models.project import SolarProject
from models.material import Material
from models.purchase_order import PurchaseOrder, PurchaseOrderItem
import pandas as pd
from datetime import date
import numpy as np # Import numpy for np.nan

def populate_data():
    app = create_app()
    with app.app_context():
        print("Populating data...")

        # 1. Create "Saatvik Agro" project
        project_name = "Saatvik Agro Products Morena, MP"
        project = SolarProject.query.filter_by(name=project_name).first()
        if not project:
            project = SolarProject(
                name=project_name,
                capacity_mw=1.3, # Placeholder
                budget=5000000.00, # Placeholder
                status="Planned", # Placeholder
                finance_supply_price=None, # To be updated by user input
                finance_service_price=None, # To be updated by user input
                finance_total_price=None # To be updated by user input
            )
            db.session.add(project)
            db.session.commit()
            print(f"Created project: {project.name}")
        else:
            print(f"Project '{project.name}' already exists. Skipping creation.")

        # 2. Add data from SOW-Rooftop Moraina-Saatvik Agro-R1-291125.csv for materials
        csv_file = r'D:\\Downloads extra\\EMSolar (2)\\EMSolar\\SOW-Rooftop Moraina-Saatvik Agro-R1-291125.csv'
        try:
            df = pd.read_csv(csv_file, header=6) 
            
            # Ensure column names are clean (remove leading/trailing spaces)
            df.columns = df.columns.str.strip()

            # Filter out rows with empty "Item Description"
            df = df[df['Item Description'].notna()]
            
            # Convert numerical columns, coercing errors to NaN
            for col in ['Total', 'Supply', 'Service', 'Rate', 'Amount']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            for index, row in df.iterrows():
                material = Material(
                    project_id=project.id,
                    name=row['Item Description'],
                    specification=row['Specification'] if 'Specification' in df.columns and pd.notna(row['Specification']) else None,
                    quantity=row['Total'] if 'Total' in df.columns and pd.notna(row['Total']) else 0.0,
                    uom=row['UOM'] if 'UOM' in df.columns and pd.notna(row['UOM']) else None,
                    make=row['MAKE'] if 'MAKE' in df.columns and pd.notna(row['MAKE']) else None,
                    supply=row['Supply'] if 'Supply' in df.columns and pd.notna(row['Supply']) else None,
                    service=row['Service'] if 'Service' in df.columns and pd.notna(row['Service']) else None,
                    rate=row['Rate'] if 'Rate' in df.columns and pd.notna(row['Rate']) else None,
                    amount=row['Amount'] if 'Amount' in df.columns and pd.notna(row['Amount']) else None
                )
                db.session.add(material)
            db.session.commit()
            print(f"Imported materials from CSV for project: {project.name}")
        except FileNotFoundError:
            print(f"Error: CSV file not found at {csv_file}. Skipping material import.")
        except KeyError as e:
            print(f"Error: Missing expected column in CSV file: {e}. Skipping material import.")
        except Exception as e:
            print(f"An unexpected error occurred during CSV import: {e}. Skipping material import: {e}")

        print("\nData population script finished. Please provide the following to complete the process:")
        print("1. Finance summary values (supply price, service price, total price) from 'BBU- Saatvik Agro.pdf'.")
        print("2. Details for the two Purchase Orders from '1000012147-PO-E&M.pdf' and '2000002451-PO-E&M.pdf'.")

if __name__ == "__main__":
    populate_data()
