from datetime import datetime
from app import create_app, db
from models.purchase_order import PurchaseOrder, PurchaseOrderItem

def add_po():
    """Adds a new purchase order by prompting for data."""
    print("Adding a new purchase order...")
    
    app = create_app()
    with app.app_context():
        try:
            po_number = input("Enter PO Number: ")
            
            existing_po = PurchaseOrder.query.filter_by(po_number=po_number).first()
            if existing_po:
                print(f"Purchase order {po_number} already exists. Aborting.")
                return

            po_date_str = input("Enter PO Date (YYYY-MM-DD): ")
            po_date = datetime.strptime(po_date_str, '%Y-%m-%d').date()
            vendor_name = input("Enter Vendor Name: ")
            vendor_code = input("Enter Vendor Code: ")
            shipped_to_name = input("Enter Shipped To Name: ")
            shipped_to_address = input("Enter Shipped To Address: ")
            bill_to_name = input("Enter Bill To Name: ")
            bill_to_address = input("Enter Bill To Address: ")
            total_tax_amount = float(input("Enter Total Tax Amount: "))
            grand_total = float(input("Enter Grand Total: "))

            po = PurchaseOrder(
                po_number=po_number,
                po_date=po_date,
                vendor_name=vendor_name,
                vendor_code=vendor_code,
                shipped_to_name=shipped_to_name,
                shipped_to_address=shipped_to_address,
                bill_to_name=bill_to_name,
                bill_to_address=bill_to_address,
                total_tax_amount=total_tax_amount,
                grand_total=grand_total
            )
            db.session.add(po)
            db.session.flush()

            while True:
                add_item = input('Do you want to add an item to this PO? (y/n): ').lower()
                if add_item != 'y':
                    break
                description = input("Enter item description: ")
                quantity = float(input("Enter quantity: "))
                rate = float(input("Enter rate: "))
                
                item = PurchaseOrderItem(
                    po_id=po.id,
                    description=description,
                    quantity=quantity,
                    rate=rate,
                    taxable_value = quantity * rate
                )
                db.session.add(item)

            db.session.commit()
            print(f"Successfully added purchase order {po_number}.")

        except Exception as e:
            db.session.rollback()
            print(f"An error occurred: {e}")

def show_pos():
    """Shows a list of all imported purchase orders."""
    print("Showing all purchase orders...")
    app = create_app()
    with app.app_context():
        pos = PurchaseOrder.query.all()
        if not pos:
            print("No purchase orders found.")
            return
        for po in pos:
            print(f"PO Number: {po.po_number}, Date: {po.po_date}, Vendor: {po.vendor_name}, Total: {po.grand_total}")

def show_po():
    """Shows the details of a specific purchase order."""
    po_number = input("Enter PO Number to show details: ")
    print(f"Showing details for purchase order {po_number}...")
    app = create_app()
    with app.app_context():
        po = PurchaseOrder.query.filter_by(po_number=po_number).first()
        if not po:
            print(f"Purchase order {po_number} not found.")
            return
        
        print(f"PO Number: {po.po_number}")
        print(f"PO Date: {po.po_date}")
        print(f"Vendor: {po.vendor_name} ({po.vendor_code})")
        print(f"Shipped To: {po.shipped_to_name}")
        print(f"  Address: {po.shipped_to_address}")
        print(f"Bill To: {po.bill_to_name}")
        print(f"  Address: {po.bill_to_address}")
        print(f"Total Tax: {po.total_tax_amount}")
        print(f"Grand Total: {po.grand_total}")
        print("--- Items ---")
        if po.items:
            for item in po.items:
                print(f"  - {item.description}")
                print(f"    Qty: {item.quantity}, Rate: {item.rate}, Subtotal: {item.taxable_value}")
        else:
            print("  No items for this PO.")

def main():
    """Main function to run the CLI menu."""
    while True:
        print("\n--- Purchase Order Management ---")
        print("1. Add a new purchase order")
        print("2. Show all purchase orders")
        print("3. Show a specific purchase order")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            add_po()
        elif choice == '2':
            show_pos()
        elif choice == '3':
            show_po()
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

if __name__ == '__main__':
    main()
