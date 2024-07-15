from . import db
from datetime import datetime

class PartyData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    gst_number = db.Column(db.String(15), nullable=False)
    pan_number = db.Column(db.String(10), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    balance=db.Column(db.Integer(),nullable=False)
    task=db.Column(db.String(50),nullable=False)

    
# class Invoice(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     party_id = db.Column(db.Integer, db.ForeignKey('party_data.id'), nullable=False)
#     invoice_date = db.Column(db.String,  nullable=False)
#     total_amount = db.Column(db.String, nullable=False)
#     status = db.Column(db.String(20), nullable=False)  # 'Paid' or 'Unpaid'
    
#     # Embedded Invoice Item fields
#     item_id = db.Column(db.String, nullable=False)
#     quantity = db.Column(db.String, nullable=False)
#     unit_price = db.Column(db.String, nullable=False)

#     #discount
#     discountAmount =db.Column(db.String,nullable=True)

#     def __repr__(self):
#         return (f"Invoice(id={self.id}, party_id={self.party_id}, invoice_date={self.invoice_date}, "
#                 f"total_amount={self.total_amount}, status={self.status}, item_id={self.item_id}, "
#                 f"quantity={self.quantity}, unit_price={self.unit_price})")
    
class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    party_id = db.Column(db.Integer, db.ForeignKey('party_data.id'), nullable=False)
    invoice_date = db.Column(db.String, nullable=False)
    total_amount = db.Column(db.String, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'Paid' or 'Unpaid'

    # Embedded Invoice Item fields
    item_id = db.Column(db.String, nullable=False)
    quantity = db.Column(db.String, nullable=False)
    unit_price = db.Column(db.String, nullable=False)
    discountAmount = db.Column(db.String, nullable=True)  # New column for discount amount
    discount_type = db.Column(db.String,nullable=True)
    bussinessName = db.Column(db.String,nullable=True)
    bussinessPhoneNo = db.Column(db.String,nullable=True)
    PaymentMode = db.Column(db.String,nullable=True)

    def __repr__(self):
        return (f"Invoice(id={self.id}, party_id={self.party_id}, invoice_date={self.invoice_date}, "
                f"total_amount={self.total_amount}, status={self.status}, item_id={self.item_id}, "
                f"quantity={self.quantity}, unit_price={self.unit_price}, discountAmount={self.discountAmount})")
    

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.String(80), nullable=False,)  # Change to Integer for numerical operations
    sales_price = db.Column(db.String(80), nullable=False)
    purchase_price = db.Column(db.String(80), nullable=False)
    stock_transactions = db.relationship('StockTransaction', backref='item', lazy=True)
    unit = db.Column(db.String(80),nullable=True)

    def __repr__(self):
        return f"Item(id={self.id}, name={self.name}, quantity={self.quantity}, sales_price={self.sales_price}, purchase_price={self.purchase_price})"


class StockTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'Add' or 'Reduce'
    quantity = db.Column(db.String, nullable=False)
    date = db.Column(db.String(25),nullable=True)

    def __repr__(self):
        return f"StockTransaction(id={self.id}, item_id={self.item_id}, transaction_type={self.transaction_type}, quantity={self.quantity}, date={self.date})"
    

# New Table Added 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'