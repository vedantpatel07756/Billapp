
from flask import Blueprint, request, jsonify, render_template


from . import db

from .file import PartyData,Invoice


party_bp = Blueprint('party', __name__)






# Party Data Retrive or Fetch  from database 



@party_bp.route('/partydata', methods=['GET'])
def get_party_data():
    party_data = PartyData.query.order_by(PartyData.id).all()  # Fetch data ordered by ID
    result = [
        {
            "id": data.id,
            "name": data.name,
            "contact_number": data.contact_number,
            "gst_number": data.gst_number,
            "pan_number": data.pan_number,
            "type": data.type,
            "balance": data.balance,
            "task": data.task
        } for data in party_data
    ]
    # print(result)
    return jsonify(result)

# Party Data Commited to database 


@party_bp.route('/create_party',methods=["POST","GET"])
def create_party():
    data = request.get_json()
    name = data['name']
    contact_number = data['contact_number']
    gst_number = data['gst_number']
    pan_number = data['pan_number']
    type = data['type']
    balance=data['balance']
    task=data['task']
    
    newParty=PartyData(name=str(name),
                       contact_number=str(contact_number),
                       gst_number=str(gst_number),
                       pan_number=str(pan_number),
                       type=str(type),
                       balance=balance,
                       task=str(task),
                       )
    
    db.session.add(newParty)
    db.session.commit()

    return jsonify({'message': 'Party created successfully'})


# Party Data Deleted with the help of there unique ID  

# @party_bp.route('/delete_party/<int:id>', methods=['DELETE'])
# def delete_party(id):
#     try:
#         # Step 2: Retrieve the record by its ID
#         party = PartyData.query.get(id)
        
#         if not party:
#             return jsonify({'error': 'Party not found'}), 404
        
#         # Step 3: Delete the record from the database
#         db.session.delete(party)
#         db.session.commit()
        
#         # Step 4: Return a success response
#         return jsonify({'message': 'Party deleted successfully'}), 200
#     except Exception as e:
#         # Handle any errors that occur
#         return jsonify({'error': str(e)}), 500


@party_bp.route('/delete_party/<int:id>', methods=['DELETE'])
def delete_party(id):
    try:
        # Step 2: Retrieve the PartyData record by its ID
        party = PartyData.query.get(id)
        
        if not party:
            return jsonify({'error': 'Party not found'}), 404

        # Step 3: Retrieve and delete all associated invoices
        invoices = Invoice.query.filter_by(party_id=id).all()
        for invoice in invoices:
            db.session.delete(invoice)
        
        # Step 4: Delete the PartyData record from the database
        db.session.delete(party)
        db.session.commit()
        
        # Step 5: Return a success response
        return jsonify({'message': 'Party and associated invoices deleted successfully'}), 200
    except Exception as e:
        # Handle any errors that occur
        return jsonify({'error': str(e)}), 500



# Update Party Data 

@party_bp.route('/update_party/<int:id>', methods=['GET', 'POST'])
def update_party(id):
    party = PartyData.query.get_or_404(id)
    if request.method == 'POST':
        data = request.get_json()
        party.name = data['name']
        party.contact_number = data['contact_number']
        party.gst_number = data['gst_number']
        party.pan_number = data['pan_number']
        party.type = data['type']
        party.balance = data['balance']
        party.task = data['task']
        try:
            db.session.commit()
            return jsonify({'message': 'Party updated successfully'})
        except Exception as e:
            return jsonify({'error': str(e)})
    else:
        return jsonify({'message': 'Get Message Call'})

