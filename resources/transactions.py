from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from services.open_food_fact import open_food_fact
from database.models import db, Purchase, User, Product
import requests 

import boto3
import csv  


class TransactionsAPI(Resource):
    @jwt_required()
    def get(self):
        s3 = boto3.client("s3") # boto3 utilise les credentials par défaut en variable d'env
        obj = s3.get_object(Bucket="website-transactions-groupe-5", Key="transactions.csv")
        data = obj['Body'].read().decode('utf-8').splitlines()
        records = csv.reader(data)
        
        headers = next(records)
        
        sent_products = []

        for row in records:
            user = User.query.filter(User.email == row[2]).first()
            if user:
                print("l'utilisateur existe")
                purchase_params = {
                "bar_code": row[0],
                "price" : row[1],
                "user_id" : get_jwt_identity()
                }
                
                sent_products.append(purchase_params)
                
                product_purchase = Purchase(**purchase_params)
                existing_product = Product.query.filter(Product.bar_code==purchase_params["bar_code"]).first()

                if not existing_product:
                    print('Le produit n\'est pas dans la DB')
                    product_openff = requests.get(open_food_fact.url + "/api/v0/product/" + purchase_params["bar_code"] + ".json").json()
                    product = {
                        "bar_code": purchase_params["bar_code"],
                        "name": product_openff["product"]["generic_name_fr"],
                        "brand": product_openff["product"]["brands"],
                        "nutri_score": product_openff["product"]["nutriments"]["nutrition-score-fr"]
                    }
                    ProductAdd = Product(**product)
                    try:
                        db.session.add(ProductAdd)
                        db.session.commit()
                        print("Produit ajouté à la DB")
                    except Exception as e:
                        print(e)
                        return {'error': 'Internal error : %s' % e}, 500
                    
                
                # Maintenant que le produit est ajouté dans la DB s'il n'y était pas déjà, on ajoute l'élément Purchase    
                try:
                    db.session.add(product_purchase)
                    db.session.commit()
                except Exception as e:
                    print(e)
                    return {'error': 'Internal error : %s' % e}, 500
            
            
        return jsonify(sent_products)