# invoice_bp.py

from flask import Blueprint, jsonify, request
from datetime import datetime
from . import db
from .items import Item
from datetime import datetime
from .items import StockTransaction 
from .party import PartyData

from .file import Invoice

invoice_bp = Blueprint('invoice', __name__)

# Mark as paid and unpaid 
@invoice_bp.route('/mark/<int:invoice_id>/mark_as_paid', methods=['POST'])
def mark_as_paid(invoice_id):
    try:
        invoice = Invoice.query.get_or_404(invoice_id)
        party = PartyData.query.get_or_404(invoice.party_id)

        if invoice.status == "Paid":
            # If the invoice was already marked as paid, we mark it as unpaid
            invoice.status = 'Unpaid'
            party.balance += int(invoice.total_amount)
        else:
            # If the invoice was unpaid, we mark it as paid
            invoice.status = 'Paid'
            party.balance -= int(invoice.total_amount)
        
        db.session.commit()

        return jsonify({'message': 'Invoice status and party balance updated successfully'}), 200
    except Exception as e:
        # Handle any errors that occur
        return jsonify({'error': str(e)}), 500
    
    db.session.commit()
    return jsonify({'message': 'Invoice marked as paid', 'invoice': invoice.id, 'status': invoice.status})

# Delete invoice 

@invoice_bp.route('/delete_invoice/<int:invoice_id>', methods=['DELETE'])
def delete_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    party = PartyData.query.get_or_404(invoice.party_id)
    
    if(invoice.status=="Unpaid"):
        party.balance -= int(invoice.total_amount)
    
    db.session.delete(invoice)
    db.session.commit()
    return jsonify({'message': 'Invoice deleted successfully', 'invoice_id': invoice_id})

# Fetch Alll invoice 

@invoice_bp.route('/getinvoices', methods=['GET'])
def get_invoices():
    try:
        invoices = Invoice.query.all()
        invoice_list = []
        for invoice in invoices:
            invoice_data = {
                'id': invoice.id,
                'party_id': invoice.party_id,
                'invoice_date': invoice.invoice_date,
                'total_amount': invoice.total_amount,
                'status': invoice.status,
                'item_id': invoice.item_id,
                'quantity': invoice.quantity,
                'unit_price': invoice.unit_price,
            }
            invoice_list.append(invoice_data)
        return jsonify(invoice_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400



# Fetch invoice According to party_id
    
@invoice_bp.route('/invoices/<int:party_id>', methods=['GET'])
def get_invoices_by_party_id(party_id):
    invoices = Invoice.query.filter_by(party_id=party_id).all()
    if not invoices:
        return jsonify({"message": "No invoices found for the given party ID"}), 404
    
    invoices_list = []
    for invoice in invoices:
        invoice_data = {
            "id": invoice.id,
            "party_id": invoice.party_id,
            "invoice_date": invoice.invoice_date,
            "total_amount": invoice.total_amount,
            "status": invoice.status,
            "item_id": invoice.item_id,
            "quantity": invoice.quantity,
            "unit_price": invoice.unit_price
        }
        invoices_list.append(invoice_data)
    
    return jsonify(invoices_list), 200


# Fetch invoice by invoice id 

@invoice_bp.route('/invoiceid/<int:invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    invoice = Invoice.query.get(invoice_id)
    if not invoice:
        return jsonify({"error": "Invoice not found"}), 404

    # Split the comma-separated fields into lists
    item_ids = invoice.item_id.split(',')
    quantities = invoice.quantity.split(',')
    unit_prices = invoice.unit_price.split(',')
    discountAmounts = invoice.discountAmount.split(',') if invoice.discountAmount else []
    discount_types = invoice.discount_type.split(',') if invoice.discount_type else []

    items_data = []
    for item_id, quantity, unit_price, discountAmount, discount_type in zip(
        item_ids, quantities, unit_prices, discountAmounts, discount_types):
        item = Item.query.get(int(item_id))
        item_value = str(int(quantity) * int(unit_price))
        if item:
            items_data.append({
                "id": item.id,
                "name": item.name,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_item_value": item_value,
                "discountAmount": discountAmount,  # Include discount amount
                "discount_type": discount_type ,
                 "unit":item.unit # Include discount type
            })

    invoice_data = {
        "id": invoice.id,
        "party_id": invoice.party_id,
        "invoice_date": invoice.invoice_date,
        "total_amount": invoice.total_amount,
        "status": invoice.status,
        "items": items_data,
        "bussinessName":invoice.bussinessName,
        "bussinessPhone":invoice.bussinessPhoneNo,
        "PaymentMode":invoice.PaymentMode
    }

    return jsonify(invoice_data)




# Post data to database invoice table 

@invoice_bp.route('/postinvoices', methods=['POST'])
def create_invoice():
    data = request.json
    print(data)
    try:
        item_details = data.get('item', [])
        item_ids = [item['item_id'] for item in item_details]
        quantities = [item['quantity'] for item in item_details]
        unit_prices = [item['unit_price'] for item in item_details]
        discounts = [item['discount'] for item in item_details]
        discount_types = [item['discount_type'] for item in item_details]  # Added for discount types

        # Create a new invoice object with item details including discounts and types
        new_invoice = Invoice(
            party_id=data['party_id'],
            invoice_date=data['invoice_date'],
            total_amount=data['total_amount'],
            status=data['status'],
            item_id=','.join(map(str, item_ids)),
            quantity=','.join(map(str, quantities)),
            unit_price=','.join(map(str, unit_prices)),
            discountAmount=','.join(map(str, discounts)),  # Store discounts directly in the invoice
            discount_type=','.join(map(str, discount_types)) , # Store discount types directly in the invoice
            bussinessName=data['bussinessName'],
            bussinessPhoneNo=data['bussinessPhone'],
            PaymentMode=data['paymentMode']
        )

        db.session.add(new_invoice)

        # Update party balance
        party_id = data['party_id']
        party = PartyData.query.get_or_404(party_id)
        party.balance = party.balance + int(data['total_amount'])  # Add total_amount to balance

        # Update item quantities and create stock transactions
        for item_id, quantity in zip(item_ids, quantities):
            item = Item.query.get(item_id)
            if item:
                # Ensure item quantity is sufficient
                if int(item.quantity) < int(quantity):
                    raise ValueError(f"Insufficient stock for item id {item_id}")

                # Adjust item quantity based on party type (Supplier or Customer)
                if party.type == "Supplier":
                    item.quantity = str(int(item.quantity) + int(quantity))
                    transaction_type = 'Add Stock'
                else:
                    item.quantity = str(int(item.quantity) - int(quantity))
                    transaction_type = 'Reduce Stock'

                # Create stock transaction
                stock_transaction = StockTransaction(
                    item_id=item_id,
                    transaction_type=transaction_type,
                    quantity=int(quantity),
                    date=data['invoice_date']
                )
                db.session.add(stock_transaction)
            else:
                raise ValueError(f"Item with id {item_id} not found")

        db.session.commit()

        return jsonify({'message': 'Invoice created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400








# # Post data to database invoice table 

# @invoice_bp.route('/postinvoices', methods=['POST'])
# def create_invoice():
#     data = request.json
#     try:
#         item_ids = [item['item_id'] for item in data['items']]
#         quantities = [item['quantity'] for item in data['items']]
#         unit_prices = [item['unit_price'] for item in data['items']]

#         # Create a new invoice object
#         new_invoice = Invoice(
#             party_id=data['party_id'],
#             invoice_date=data['invoice_date'],
#             total_amount=data['total_amount'],
#             status=data['status'],
#             item_id=','.join(map(str, item_ids)),
#             quantity=','.join(map(str, quantities)),
#             unit_price=','.join(map(str, unit_prices))
#         )

#         db.session.add(new_invoice)


#          # Update party balance
#         party_id = data['party_id']
#         party = PartyData.query.get_or_404(party_id)
#         party.balance = party.balance + int(data['total_amount'])  # Add total_amount to balance

#         # Update item quantities and create stock transactions
#         for item_id, quantity in zip(item_ids, quantities):
#             item = Item.query.get(item_id)
#             if item:
#                 # Ensure item quantity is sufficient
#                 if(party.type=="Customer"):
#                     if int(item.quantity) < int(quantity):
#                         raise ValueError(f"Insufficient stock for item id {item_id}")

#                 if (party.type=="Supplier") :
#                          # Reduce item quantity
#                     item.quantity =  str(int(item.quantity) + int(quantity))

#                     # Create stock transaction
#                     stock_transaction = StockTransaction(
#                         item_id=item_id,
#                         transaction_type='Add Stock',
#                         quantity=int(quantity),
#                         date=data['invoice_date']
#                     )
#                 else: 
#                     # Reduce item quantity
#                     item.quantity =  str(int(item.quantity) - int(quantity))

#                     # Create stock transaction
#                     stock_transaction = StockTransaction(
#                         item_id=item_id,
#                         transaction_type='Reduce Stock',
#                         quantity=int(quantity),
#                         date=data['invoice_date']
#                     )
#                 db.session.add(stock_transaction)
#             else:
#                 raise ValueError(f"Item with id {item_id} not found")

#         db.session.commit()

#         return jsonify({'message': 'Invoice created successfully'}), 201
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 400
