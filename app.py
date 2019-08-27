import datetime
import os

from flask import Flask, render_template, redirect, url_for
from forms import ItemForm
from models import Items
from database import db_session

app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']

@app.route("/", methods=('GET', 'POST'))
def add_item():
    form = ItemForm()
    if form.validate_on_submit():
        item = Items(name=form.name.data, quantity=form.quantity.data, description=form.description.data, date_added=datetime.datetime.now())
        db_session.add(item)
        db_session.commit()
        print("item: {}".format(item))
        print("form.name.data: {}".format(form.name.data))
        print("form.quantity.data: {}".format(form.quantity.data))
        print("form.description.data: {}".format(form.description.data))
        print("datetime.datetime.now(): {}".format(datetime.datetime.now()))

        print("\n--\n")

        print("success url: {}".format(url_for('success')))
        print("xsuccess url: {}".format(url_for('success', _external=True)))
        print("redirect url: {}".format(str(redirect(url_for('success')))))
        return redirect(url_for('success'))

    print("rendering template index.html...")
    return render_template('index.html', form=form)

@app.route("/success")
def success():
    results = "Item successfully added to database! </br>"
 
    results = results + "Currently listed items: </br> </br>"
    qry = db_session.query(Items)
    all_items = qry.all()
    for cur_item in all_items:
        results = results + str(cur_item)

    print(results)
    #print('success results: {}'.format(str(results)))
    #print('last result: {}'.format(results[-1]))
    #for res in results:
    #    print('Items result:')
    #    print('    id:          {}'.format(res.id))
    #    print('    name:        {}'.format(res.name))
    #    print('    quantity:    {}'.format(res.quantity))
    #    print('    description: {}'.format(res.description))
    #    print('    date_added:  {}'.format(res.date_added))

    return str(results)
  

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
