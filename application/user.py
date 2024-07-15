from flask import Blueprint, request, jsonify
from . import db,socketio
from datetime import datetime
from .file import User



user_bp = Blueprint('user', __name__)


# Create User 

@user_bp.route('/employe/create_user', methods=['POST'])
def create_user():
    data = request.get_json()

    new_user = User(
        name=data['name'],
        gender=data['gender'],
        phone_number=data['phone_number'],
        email=data['email'],
        password=data['password']
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully!"}), 201


# how Users 

@user_bp.route('/employe/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = []
    for user in users:
        if(user.email=="adminSST@gmail.com" or user.email=="vedantpatel07756@gmail.com"):
            continue

        user_data = {
            'id': user.id,
            'name': user.name,
            'gender': user.gender,
            'phone_number': user.phone_number,
            'email': user.email,
            'password':user.password,
        }
        user_list.append(user_data)
    return jsonify(user_list)

# # Delete View 
# @user_bp.route('/users/<int:id>', methods=['DELETE'])
# def delete_user(id):
#     user = User.query.get(id)
#     if user:
#         db.session.delete(user)
#         db.session.commit()
#         return jsonify({'message': 'User deleted successfully'}), 200
#     else:
#         return jsonify({'message': 'User not found'}), 404

# Delete User 
@user_bp.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if user:
        user_id = user.id  # store user_id before deleting
        db.session.delete(user)
        db.session.commit()
        socketio.emit('account_deleted',{'user_id': user_id}, namespace='/')
        print("Socket Connection Deleted Account pass")
        return jsonify({'message': 'User deleted successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404



@user_bp.route('/checkdelete',methods=['GET'])
def check():
    socketio.emit('check', namespace='/')
    print("Socket Connection Deleted Account pass")
    return 'checked'

# Login View 
    
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and user.password == password:
        user_data = {
            'id': user.id,
            'name': user.name,
            'gender': user.gender,
            'phone_number': user.phone_number,
            'email': user.email
        }
        return jsonify(user_data), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401