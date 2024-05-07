from flask import Flask,render_template,request,redirect,url_for,flash,session, jsonify, send_file
from dbhelper import *
from datetime import date
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = '!@#$%%^'




#user/cart
@app.route("/user/cart/checkout", methods=['POST'])
def user_checkout():
    if 'user' in session:
        data = request.get_json()

        # Access the checkedItems and shipAddress from the JSON data
        checked_items = data.get('checkedItems', [])
        ship_address = data.get('shipAddress', '')
        valid = checkfields(ship_address.strip())
        if valid:
            if len(checked_items) > 0:
                # Perform actions with the data (e.g., update the database)
                for item in checked_items:
                    ic_id = item['id']
                    qty = item['quantity']
                    i_id = str(getIID(ic_id)[0]['i_id'])
                    datenow = str(date.today())
                    c_id = str(getCustomerId(session['user'])[0]['c_id'])
                    addrecord('Orders',o_date=datenow,ship_address=ship_address,c_id=c_id)
                    o_id = str(getOrderId(datenow,ship_address,c_id)[0]['o_id'])
                    addrecord('ItemsOrdered',o_id=o_id,i_id=i_id,qty=qty)
                    deleterecord('ItemsInCart',ic_id=ic_id)

                    # ... process item_id and quantity ...

                # Return a response (you can customize this based on your needs)
                flash("Item(s) Ordered Successfully")
                return jsonify({'success': True})
            else:
                flash("No item(s) Ordered")
                return jsonify({'success': False})
        else:
            flash("Error! Shipping Address Field is Important!")
            return jsonify({'success': False})

    elif 'admin' in session:
        return redirect(url_for("admin_customers"))

    else:
        flash("Login Properly!!!")
        return redirect(url_for("login"))

@app.route("/user/cart/deleteitemincart/<id>")
def user_deleteitemincart(id):
    if 'user' in session:
        ok:bool = deleterecord('ItemsInCart',ic_id=id)
        if ok:
            flash("Item Removed from Cart")
            return redirect(url_for("user_cart"))
        else:
            flash("Error Removing Item")
            return redirect(url_for("user_cart"))
    elif 'admin' in session:
        return redirect(url_for("admin_customers"))
    else:
        flash("Login Properly!!!")
        return redirect(url_for("login"))

@app.route("/user/cart")
def user_cart():
    if 'user' in session:
        head = ['Item Name','price','subtotal','quantity']
        c_id = str(getCustomerId(session['user'])[0]['c_id'])
        rows = getItemsInCart(c_id)
        return render_template("user_cart.html",title="user",header=head,cart=rows)
    elif 'admin' in session:
        return redirect(url_for("admin_customers"))
    else:
        flash("Login Properly!!!")
        return redirect(url_for("login"))


#user/orders
@app.route("/user/orders")
def user_orders():
    if 'user' in session:
        head = ['item name','price','quantity', 'total']
        c_id = str(getCustomerId(session['user'])[0]['c_id'])
        rows = getOrders(c_id)
        return render_template("user_orders.html",title="user",header=head,orderlist=rows)
    elif 'admin' in session:
        return redirect(url_for("admin_customers"))
    else:
        flash("Login Properly!!!")
        return redirect(url_for("login"))



#user/items
@app.route("/user/items/addtocart/<id>", methods = ['POST','GET'])
def user_addtocart(id):
    if 'user' in session:
        qty = request.form['tocartqty']
        valid = checkfields(qty)
        if valid:
            c_id = str(getCustomerId(session['user'])[0]['c_id'])
            i_id = id
            ok = addrecord('ItemsInCart',cart_id=c_id,i_id=id,qty=qty)
            if ok:
                flash("Item Added to Cart")
                return redirect(url_for("user_cart"))
            else:
                flash("Error!!!")
                return redirect(url_for("user_items"))
        else:
            flash("Error Adding to Cart! Quantity Field is Important!")
            return redirect(url_for("user_items"))
    elif 'admin' in session:
        return redirect(url_for("admin_customers"))
    else:
        flash("Login Properly!!!")
        return redirect(url_for("login"))

@app.route("/user/items/order/<id>", methods = ['POST','GET'])
def user_orderitem(id):
    if 'user' in session:
        ship_address = request.form['ship_address'].strip()
        qty = request.form['qty']
        valid = checkfields(ship_address,qty)
        if valid:
            i_id = id
            datenow = str(date.today())
            c_id = str(getCustomerId(session['user'])[0]['c_id'])
            ok = addrecord('Orders',o_date=datenow,ship_address=ship_address,c_id=c_id)
            if ok:
                o_id = str(getOrderId(datenow,ship_address,c_id)[0]['o_id'])
                ok = addrecord('ItemsOrdered',o_id=o_id,i_id=i_id,qty=qty)
                if ok:
                    flash("Item Ordered Successfully")
                    return redirect(url_for("user_orders"))
                else:
                    flash("Error Ordering Item!")
                    return redirect(url_for("user_items"))
            else:
                flash("Error Ordering Item!")
                return redirect(url_for("user_items"))
        else:
            flash("Error Ordering Item! Shipping Address and Quantity Fields are Important!")
            return redirect(url_for("user_items"))
    elif 'admin' in session:
        return redirect(url_for("admin_customers"))
    else:
        flash("Login Properly!!!")
        return redirect(url_for("login"))


@app.route("/user/items/search", methods = ['POST','GET'])
def user_searchitem():
    if 'user' in session:
        if request.method == "POST":
            keyword = request.form['search'].strip()
            valid = checkfields(keyword)
            if valid:
                head = ['title','price']
                rows = searchlike('Items',title=keyword,price=keyword)
                return render_template("user_items.html",title="user",header=head,itemlist=rows,search=keyword)
            else:
                return redirect(url_for('user_items'))
        else:
            return redirect(url_for("user_items"))

    elif 'admin' in session:
        return redirect(url_for("admin_customers"))
    else:
        flash("Login Properly!!!")
        return redirect(url_for("login"))

@app.route("/user/items")
def user_items():
    if 'user' in session:
        head = ['Item Name','price']
        rows = getall('Items')
        return render_template("user_items.html",title="user",header=head,itemlist=rows,search=None)
    elif 'admin' in session:
        return redirect(url_for("admin_customers"))
    else:
        flash("Login Properly!!!")
        return redirect(url_for("login"))




#admin/items

@app.route("/admin/items/search", methods = ['POST','GET'])
def searchitem()->None:
    if 'admin' in session:
        if request.method == "POST":
            keyword = request.form['search'].strip()
            valid = checkfields(keyword)
            if valid:
                head = ['title','price']
                rows = searchlike('Items',title=keyword,price=keyword)
                return render_template("admin_items.html",title="admin",header=head,itemlist=rows,search=keyword)
            else:
                return redirect(url_for('admin_items'))
        else:
            return redirect(url_for("admin_items"))

    elif 'user' in session:
        return redirect(url_for("user_items"))
    else:
        flash("Login Properly!!!")
        return redirect(url_for("login"))

@app.route("/admin/updateitem/<id>", methods = ['POST','GET'])
def updateitem(id):
    if 'admin' in session:
        if request.method == "POST":
            title = request.form['title'].strip()
            price = request.form['price'].strip()
            valid = checkfields(title,price)
            if valid:
                ok = updaterecord('Items',i_id=id,title=title,price=price)
                if ok:
                    flash("Item Updated")
                    return redirect(url_for("admin_items"))
                else:
                    flash("Error Updating Item")
                    return redirect(url_for("admin_items"))
            else:
                flash("Error Updating Item! All Fields Are Important!")
                return redirect(url_for("admin_items"))
        else:
            return redirect(url_for("admin_items"))

    elif 'user' in session:
        return redirect(url_for("user_items"))
    else:
        flash("Login Properly!!!")
        return redirect(url_for("login"))

@app.route("/admin/deleteitem/<id>")
def deleteitem(id)->None:
    if 'admin' in session:
        ok:bool = deleterecord('Items',i_id=id)
        if ok:
            flash("Item Deleted")
            return redirect(url_for("admin_items"))
    elif 'user' in session:
        return redirect(url_for("user_items"))
    else:
        flash("Login Properly!!!")
        return redirect(url_for("login"))

@app.route("/admin/additem", methods = ['POST','GET'])
def additem():
    if 'admin' in session:
        if request.method == "POST":
            title = request.form['title'].strip()
            price = request.form['price'].strip()
            price = str(round(float(price),2))
            valid = checkfields(title,price)
            if valid:
                ok = addrecord('Items',title=title,price=price)
                if ok:
                    flash("New Item Added")
                    return redirect(url_for("admin_items"))
                else:
                    flash("Error Adding Item")
                    return redirect(url_for("admin_items"))
            else:
                flash("Error Adding Item! All Fields Are Important!")
                return redirect(url_for("admin_items"))
        else:
            return redirect(url_for("admin_items"))

    elif 'user' in session:
        return redirect(url_for("user_items"))
    else:
        flash("Login Properly!!!")
        return redirect(url_for("login"))
		
@app.route('/generateCustomer')
def generateCustomerRoute():
    generateCustomer('Customer')
    return send_file('CustomerList.csv', as_attachment=True)

@app.route('/generateSales')
def generateSalesRoute():
    generateSales()
    return send_file('CustomerOrderItemReport.csv', as_attachment=True)

	
@app.route("/admin/items")
def admin_items():
    if 'admin' in session:
        head = ['item name','price','actions']
        rows = getall('Items')
        return render_template("admin_items.html",title="admin",header=head,itemlist=rows,search=None)
    elif 'user' in session:
        return redirect(url_for("user_items"))
    else:
        flash("Login Properly!!!")
        return redirect(url_for("login"))



#admin/customers

@app.route("/admin/customers/search", methods = ['POST','GET'])
def searchcustomer()->None:
    if 'admin' in session:
        if request.method == "POST":
            keyword = request.form['search'].strip()
            valid = checkfields(keyword)
            if valid:
                head = ['customer name','email','address','username','password']
                rows = searchlike('Customer',c_name=keyword,c_email=keyword,c_address=keyword,username=keyword,password=keyword)
                return render_template("admin_customers.html",title="admin",header=head,customerlist=rows,search=keyword)
            else:
                return redirect(url_for('admin_customers'))
        else:
            return redirect(url_for("admin_customers"))
    elif 'user' in session:
        return redirect(url_for("user_items"))
    else:
        flash("Login Properly!!!")
        return redirect(url_for("login"))

@app.route("/admin/deletecustomer/<id>")
def deletecustomer(id)->None:
    if 'admin' in session:
        ok:bool = deleterecord('Customer',c_id=id)
        if ok:
            flash("Customer Deleted")
            return redirect(url_for("admin_customers"))
    elif 'user' in session:
        return redirect(url_for("user_items"))
    else:
        flash("Login Properly!!!")
        return redirect(url_for("login"))

@app.route("/admin/updatecustomer/<id>", methods = ['POST','GET'])
def updatecustomer(id):
    if 'admin' in session:
        if request.method == "POST": 
            name = request.form['name'].strip()
            email = request.form['email'].strip()
            address = request.form['address'].strip()
            username = request.form['username'].strip()
            password = request.form['password'].strip()
            valid = checkfields(name,email,address,username,password)
            if valid:
                ok = updaterecord('Customer',c_id=id,c_name=name,c_email=email,c_address=address,username=username,password=password)
                if ok:
                    flash("Customer Updated")
                    return redirect(url_for("admin_customers"))
                else:
                    flash("Error Updating Customer")
                    return redirect(url_for("admin_customers"))
            else:
                flash("Error Updating Customer! All Fields Are Important!")
                return redirect(url_for("admin_customers"))
        else:
            redirect(url_for("admin_customers"))

    elif 'user' in session:
        return redirect(url_for("user_items"))
    else:
        flash("Login Properly!!!")
        return redirect(url_for("login"))

@app.route("/admin/addcustomer", methods = ['POST','GET'])
def addcustomer():
    if 'admin' in session:
        if request.method == "POST":
            name = request.form['name'].strip()
            email = request.form['email'].strip()
            address = request.form['address'].strip()
            password = request.form['password'].strip()
            valid = checkfields(name,email,address,password)
            if valid:
                ok = addrecord('Customer',c_name=name,email=email,c_address=address,password=password)
                if ok:
                    c_id = str(getCustomerId(email)[0]['c_id'])
                    cart = addrecord('Cart',cart_id=c_id)
                    flash("New Customer Added")
                    return redirect(url_for("admin_customers"))
                else:
                    flash("Error Adding Customer")
                    return redirect(url_for("admin_customers"))
            else:
                flash("Error Adding Customer! All Fields Are Important!")
                return redirect(url_for("admin_customers"))
        else:
            redirect(url_for("admin_customers"))
    elif 'user' in session:
        return redirect(url_for("user_items"))
    else:
        flash("Login Properly!!!")
        return redirect(url_for("login"))
		
		

		
@app.route("/admin/customers")
def admin_customers():
    if 'admin' in session:
        head = ['customer name','email','address']
        rows = getall('Customer')
        return render_template("admin_customers.html",title="admin",header=head,customerlist=rows,search=None)
    elif 'user' in session:
        return redirect(url_for("user_items"))
    else:
        flash("Login Properly!!!")
        return redirect(url_for("login"))


#login and register module

@app.route("/",methods=['GET','POST'])
@app.route("/login",methods=['GET','POST'])
def login()->None:
    if "admin" in session:
        return redirect(url_for("admin_customers"))
    elif "user" in session:
        return redirect(url_for("user_items"))
    else:
        if request.method == "POST":
            email:str = request.form['email']
            password:str = request.form['password']
            user:list = userlogin('Admin',a_email=email,password=password)
            if len(user) > 0:
                session['admin'] = email
                return redirect(url_for("admin_customers"))
            else:
                user:list = userlogin('Customer',email=email,password=password)
                if len(user) > 0:
                    session['user'] = email
                    return redirect(url_for("user_items"))
                else:
                    flash("Invalid User!!!")
                    return redirect(url_for("login"))
        else:
            return render_template("login.html",title="login")

@app.route("/register",methods=['GET','POST'])
def register()->None:
    if 'admin' in session:
        return redirect(url_for("admin_customers"))
    elif 'user' in session:
        return redirect(url_for("user_items"))
    else:
        if request.method == "POST":
            name:str = request.form['name'].strip()
            email:str = request.form['email'].strip()
            address:str = request.form['address'].strip()
            password:str = request.form['password'].strip()
            valid = checkfields(name,email,address,password)
            if valid:
                ok:bool = addrecord('Customer',c_name=name,email=email,c_address=address,password=password)
                if ok:
                    c_id = str(getCustomerId(email)[0]['c_id'])
                    cart = addrecord('Cart',cart_id=c_id)
                    flash("You are now Registered")
                    return redirect(url_for("login"))
                else:
                    flash("Error Creating Account!")
                    return redirect(url_for("register"))
            else:
                flash("Error Creating Account! All Fields Are Important!")
                return redirect(url_for("register"))
        else:
            return render_template("register.html",title="register")


#admin/logout

@app.route("/admin/logout")
def admin_logout()->None:
    if 'user' in session:
        return redirect(url_for("user_items"))
    elif 'admin' in session:
        session.pop("admin")
        flash("You are logged out.")
        return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))


#user/logout

@app.route("/user/logout")
def user_logout()->None:
    if 'admin' in session:
        return redirect(url_for("admin_customers"))
    elif 'user' in session:
        session.pop("user")
        flash("You are logged out.")
        return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)