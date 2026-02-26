import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import os

def generate_report():
    """
    Generates a bar chart of project costs and saves it as a PNG file.
    """
    try:
        # Get the absolute path to the database file
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database.db'))
        
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        
        # Read data from the finance_transaction table into a pandas DataFrame
        df = pd.read_sql('SELECT * FROM finance_transaction', conn)
        
        # Group by project_id and sum the expenses
        project_costs = df.groupby('project_id')['expense'].sum()
        
        # Create a bar chart
        project_costs.plot(kind='bar')
        plt.title("Project Cost Analysis")
        plt.xlabel("Project ID")
        plt.ylabel("Total Expense")
        
        # Save the chart to a file
        reports_dir = os.path.dirname(__file__)
        plt.savefig(os.path.join(reports_dir, 'project_cost_analysis.png'))
        
        print("Report generated successfully: project_cost_analysis.png")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    generate_report()
