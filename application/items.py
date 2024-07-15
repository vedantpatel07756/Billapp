from flask import Blueprint, request, jsonify
from . import db
from datetime import datetime
from .file import Item,StockTransaction

items_bp = Blueprint('items', __name__)



# add item Data 
@items_bp.route('/items/add_item', methods=['POST'])
def add_item():
    data = request.get_json()
    new_item = Item(
        name=str(data['name']),
        quantity=data['quantity'],
        sales_price=data['sales_price'],
        purchase_price=data['purchase_price'],
        unit=data['unit']
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({'message': 'Item added successfully'})

# Fetch item Data 

@items_bp.route('/items/get_item', methods=['GET'])
def get_all_items():
    items = Item.query.all()
    items_list = []
    for item in items:
        item_data = {
            'id': item.id,
            'name': item.name,
            'quantity': str(item.quantity),
            'sales_price': str(item.sales_price),
            'purchase_price': str(item.purchase_price),
            'unit':item.unit,
        }
        items_list.append(item_data)
    return jsonify(items_list)


# update item data 

@items_bp.route('/items/updateitem/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    try:
        # Fetch the item to update
        item = Item.query.get(item_id)

        if not item:
            return jsonify({'message': 'Item not found'}), 404

        # Get updated data from request body (ensure proper content type)
        data = request.get_json()

        # Validate and sanitize input (consider using a schema library like Marshmallow)
        if not data or not all(field in data for field in ['name', 'sales_price', 'purchase_price']):
            return jsonify({'message': 'Missing required fields'}), 400

        # Update item attributes with proper type conversions
        item.name = data['name']
        item.sales_price = data['sales_price'] # Assuming float for sales_price
        item.purchase_price = data['purchase_price']  # Assuming float for purchase_price
        item.unit=str(data['unit']) 

        # Commit changes to the database
        db.session.commit()

        return jsonify({'message': 'Item updated successfully'}), 200
    except Exception as e:
        # Handle potential exceptions (e.g., database errors, validation errors)
        print(f"An error occurred: {e}")
        return jsonify({'message': 'Error updating item'}), 500


# Delete the item with all the stock data with it
@items_bp.route('/items/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
  try:
    item = Item.query.get(item_id)

    if not item:
      return jsonify({'message': 'Item not found'}), 404

    # Delete all related stock transactions
    StockTransaction.query.filter_by(item_id=item_id).delete()
    db.session.commit()

    # Delete the item
    db.session.delete(item)
    db.session.commit()

    return jsonify({'message': 'Item deleted successfully'}), 200
  except Exception as e:
    # Handle potential exceptions (e.g., database errors)
    print(f"An error occurred: {e}")
    return jsonify({'message': 'Error deleting item'}), 500



# Relational Functioning With items and stock Transaction 

@items_bp.route('/api/add_stock_transaction', methods=['POST'])
def add_stock_transaction():
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data provided'}), 400

    try:
        item_id = data['item_id']
        transaction_type = data['transaction_type']
        quantity_str = data['quantity']
        date=data['date']
        print(quantity_str)
        # Convert quantity from string to integer
        try:
            quantity = int(quantity_str)
        except ValueError:
            return jsonify({'message': 'Invalid quantity format'}), 400

        # Validate input
        if transaction_type not in ['Add Stock', 'Reduce Stock']:
            return jsonify({'message': 'Invalid transaction_type'}), 400
        
        # Create a new StockTransaction object
        new_transaction = StockTransaction(item_id=item_id, transaction_type=transaction_type, quantity=quantity_str, date=date)
        
        # Update item quantity based on transaction type
        item = Item.query.get(item_id)
        # item.quantity=quantity
        if transaction_type == 'Add Stock':
            item.quantity = str(int(item.quantity) + quantity)  # Update and convert to string
        elif transaction_type == 'Reduce Stock':
            item.quantity = str(int(item.quantity) - quantity)  # Update and convert to string

        # Commit changes to the database
        db.session.add(new_transaction)
        db.session.commit()

        return jsonify({'message': 'Stock transaction added successfully'}), 201
    
    except KeyError as e:
        return jsonify({'message': f'Missing required field: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500



# Fetch that Stocj Transaction ID Using ITem ID 
    

@items_bp.route('/stock/<int:item_id>', methods=['GET'])
def get_stock_data(item_id):
    transactions = StockTransaction.query.filter_by(item_id=item_id).all()
    if not transactions:
        return jsonify({"error": "No transactions found for this item"}), 404


    return jsonify({
        "item_id": item_id,
        "transactions": [
            {
                "id": transaction.id,
                "transaction_type": transaction.transaction_type,
                "quantity": transaction.quantity,
                "date": transaction.date
            } for transaction in transactions
        ]
    })