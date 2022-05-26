from flask import request
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from sqlalchemy import desc
from services.open_food_fact import open_food_fact
from database.models import db, Product, Purchase, User

import json

from sqlalchemy.orm import load_only

import requests


class RankingUsersAPI(Resource):
    @jwt_required()
    def get(self):
        
        purchases = db.session.query(User.full_name, db.func.sum(Purchase.price)).join(Purchase).group_by(User.id).order_by(db.func.sum(Purchase.price).desc()).all()

        keys = ["Full Name", "total_sum"]
        
        return jsonify([dict(zip(keys, tup)) for tup in purchases])

class RankingProductsAPI(Resource):
    @jwt_required()
    def get(self):
        products = db.session.query(Purchase.bar_code, db.func.count(Purchase.bar_code))\
            .group_by(Purchase.bar_code).order_by(db.func.count(Purchase.bar_code).desc()).all()
        
        keys = ["transactions", "name"]
        products_by_transactions = []
        print(products)
        for bar_code, transactions in products:
            product = Product.query.filter(Product.bar_code == bar_code).first()
            print(product)
            if product:
                products_by_transactions.append(dict(zip(keys,(transactions, product.name))))
            

        return jsonify(products_by_transactions)