from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL


app= Flask(__name__)
app.secret_key="flash message"

#config files
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='root'
app.config['MYSQL_DB']='inventory'

mysql=MySQL(app)
flag=True


#Index Page
@app.route('/')
def Index():
    try:
        cur=mysql.connection.cursor()
        cur.execute("SELECT *FROM product")
        data=cur.fetchall()
        cur.execute("SELECT *FROM location")
        data2 = cur.fetchall()
        cur.execute("SELECT *FROM productmovement")
        data3 = cur.fetchall()

        cur.close()
        return render_template('index.html', product=data,location=data2, promove=data3)
    except:
        flash("Unexpected Error")



#Adding a new Product
@app.route('/insert',methods = ['POST'])
def insert():
    try:
        if request.method == "POST":
            flash("Product added successfully")
            product = request.form['product']
            quantity = request.form['quantity']
            warehouse = request.form['warehouse']

            cur =mysql.connection.cursor()
            cur.execute("INSERT INTO product (product, quantity, warehouse) VALUES(%s,%s,%s)", (product,quantity,warehouse))
            mysql.connection.commit()
    except:
        mysql.connection.rollback()
        flash("wrong input")
    finally:
        return redirect(url_for('Index'))

#Updating a new product
@app.route('/update', methods= ['POST','GET'])
def update():
    try:
        if request.method=='POST':
            id=request.form['id']
            product = request.form['product']
            quantity = request.form['quantity']
            warehouse = request.form['warehouse']
            cur =mysql.connection.cursor()
            cur.execute("""
                            UPDATE product 
                            SET product=%s, quantity=%s, warehouse=%s
                            WHERE product_id=%s
                            """, (product,quantity,warehouse,id))
            flash("Data Updated")
            mysql.connection.commit()
    except:
        mysql.connection.rollback()
        flash("wrong input")
    finally:
        return redirect(url_for('Index'))

#Updating the Location
@app.route('/updateL', methods= ['POST','GET'])
def updateL():
    try:
        if request.method=='POST':
            id=request.form['id']
            location = request.form['location']
            cur =mysql.connection.cursor()
            cur.execute("""
                            UPDATE location 
                            SET location=%s
                            WHERE location_id=%s
                            """, (location,id))
            flash("Location Updated")
            mysql.connection.commit()
    except:
        mysql.connection.rollback()
        flash("wrong input")
    finally:
        return redirect(url_for('Index'))


#deleting a Product
@app.route('/delete/<string:id_data>', methods=['POST','GET'])
def delete(id_data):
    try:
        flash("Data Deleted Successfully")
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM product WHERE product_id=%s",(id_data))
        mysql.connection.commit()
    except:
        mysql.connection.rollback()
        flash("wrong input")
    finally:
        return redirect(url_for('Index'))

#Adding a New Location
@app.route('/insertL',methods = ['POST'])
def insertL():
    try:
        if request.method == "POST":
            flash("Location added successfully")
            location = request.form['location']
            cur =mysql.connection.cursor()
            cur.execute("INSERT INTO location (location) VALUES(%s)", [location])

            mysql.connection.commit()

    except :
        mysql.connection.rollback()
        flash("wrong input")
    finally:
        return redirect(url_for('Index'))

#Moving Product into a Location
def into(tolocation,product,quantity):
    try:
        cur = mysql.connection.cursor()

        cur.execute("""SELECT * FROM product
                        WHERE product=%s and warehouse=%s""", (product,tolocation))
        d = cur.fetchone()
        global flag
        flag=True
        if d is None:
            cur.execute("INSERT INTO product ( product, quantity, warehouse) VALUES(%s,%s,%s)",(product,quantity, tolocation))
        else:
            q = int(d[2]) + int(quantity)

            cur.execute("""UPDATE product 
                                       SET quantity=%s
                                       WHERE product=%s and warehouse=%s
                                       """, (q, product,tolocation))

        mysql.connection.commit()
        return
    except:
        mysql.connection.rollback()
        flash("wrong input")

#Moving Product out of a Location
def out(product,quantity,fromlocation,tolocation=0):
    try:
        cur = mysql.connection.cursor()

        cur.execute("""SELECT * FROM product
                        WHERE product=%s and warehouse=%s""", (product,fromlocation))
        d = cur.fetchone()
        if d is None:
             flash("No such product exist")
             global flag
             flag = False
             return redirect(url_for('Index'))

        else:
            q = int(d[2])
            if q<int(quantity) :
                flash("Product Transaction Stock Exceeds Current Stock")

                flag = False
                return redirect(url_for('Index'))
            elif q>=int(quantity) :
                q=q-int(quantity)

                flag = True
                cur.execute("""UPDATE product 
                        SET quantity=%s
                        WHERE product=%s and warehouse=%s
                        """, (q, product,fromlocation))
            if tolocation != 0:
                    into(tolocation,product,quantity)
        mysql.connection.commit()
        return
    except:
        mysql.connection.rollback()
        flash("wrong input")





#Product Movement
@app.route('/movement', methods= ['POST','GET'])
def movement():
    try:
        if request.method == "POST":

            fromlocation = request.form['fromlocation']
            tolocation = request.form['tolocation']
            product = request.form['product']
            quantity = request.form['quantity']


            if not fromlocation and not tolocation :
                flash("Invalid Entry: Transaction Failed")
                return redirect(url_for('Index'))
            elif not fromlocation :
                into(tolocation,product,quantity)

            elif not tolocation :
                out(product,quantity,fromlocation)

            else:
                out(product, quantity, fromlocation, tolocation)

            cur = mysql.connection.cursor()
            global flag

            if flag:
                cur.execute("INSERT INTO productmovement (fromlocation,tolocation,product,quantity) VALUES(%s,%s,%s,%s)", (fromlocation,tolocation,product,quantity))
                flash("Product Moved Successfully")

            mysql.connection.commit()
    except:
        mysql.connection.rollback()
        flash("wrong input")
    finally:
        return redirect(url_for('Index'))


if __name__=="__main__":
    app.run(debug=False)