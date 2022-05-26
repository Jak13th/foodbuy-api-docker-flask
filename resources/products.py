from urllib import response
from flask import request
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from services.open_food_fact import open_food_fact
from database.models import User, db, Product, Purchase
import requests
    
class ProductAPI(Resource):
    @jwt_required()
    def get(self, productId):
        product = Product.query.filter(Product.bar_code == productId).first()
        if not product:
            try:
                product_openff = requests.get(open_food_fact.url + "/api/v0/product/" + productId + ".json").json()
                product = {
                    "name": product_openff["product"]["generic_name_fr"],
                    "brand": product_openff["product"]["brands"],
                    "nutri_score": product_openff["product"]["nutriments"]["nutrition-score-fr"]
                }
                self.post(productId, product=product)
            except Exception as e:
                return {"Erreur" : "Produit introuvable"}

            return jsonify(product)
        
        else: 
            return jsonify({"name": product.name, "brand" : product.brand, "nutri_score" : product.nutri_score})

    def post(self, productId, product=None):
        
        # SI post a reçu un produit directement (aka si elle est appelée par le get au-dessus)
        if product:
            product_to_add = Product(
                name= product["name"],
                brand = product["brand"],
                nutri_score = product["nutri_score"],
                bar_code = productId
            )
        else:
            body = request.get_json()
            product_to_add = Product(
                name = body.get("name"),
                brand = body.get("brand"),
                nutri_score = body.get("nutri_score"),
                bar_code = productId
            )

        try:
            db.session.add(product_to_add)
            db.session.commit()
            return jsonify(product_to_add)
        except Exception as e:
            print(e)
            return {'error': 'Internal error : %s' % e}, 500


class ProductsAPI(Resource):
    @jwt_required()
    def get(self):
        Products = Product.query.all()
        return jsonify(Products)

class ProductsBuyAPI(Resource):
    @jwt_required()
    def post(self):
        body = request.get_json()
        user_id = get_jwt_identity()
        ProductBuy = Purchase(
            bar_code = body.get("bar_code"),
            price = body.get("price"),
            user_id = user_id
            )
        barCode = body.get('bar_code')
        existing_product = Product.query.filter(Product.bar_code==barCode).first()
        if existing_product:
            try:
                db.session.add(ProductBuy)
                db.session.commit()
                return jsonify(ProductBuy)
            except Exception as e:
                print(e)
                return {'error': 'Internal error : %s' % e}, 500
        else:
            ProductAdd = Product(
                bar_code=barCode,
                name=requests.get(f"https://world.openfoodfacts.org/api/v0/product/"+
                body.get("bar_code")+".json").json()["product"]["generic_name_fr"],
                brand=requests.get(f"https://world.openfoodfacts.org/api/v0/product/"+
                body.get("bar_code")+".json").json()["product"]["brands"],
                nutri_score=requests.get(f"https://world.openfoodfacts.org/api/v0/product/"+
                body.get("bar_code")+".json").json()["product"]["nutriments"]["nutrition-score-fr"]
            )
            try:
                db.session.add(ProductAdd)
                db.session.commit()
                db.session.add(ProductAdd)
                db.session.commit()
                return jsonify(ProductAdd)
            except Exception as e:
                print(e)
                return {'error': 'Internal error : %s' % e}, 500
