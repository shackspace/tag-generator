from flask import Flask, render_template, request, abort, send_file, redirect
import json
app = Flask(__name__)

#app.config["SERVER_NAME"] = "127.0.0.1:8080"
DB_FILE="db/db.json"

# in-memory database

def save_db():
  with open(DB_FILE,"w+") as persistence:
    json.dump(db,persistence)
    print "db saved"
    return db

def load_db():
  try:
    persistence = open(DB_FILE)
    return json.load(persistence)
    print "db loaded"
  except:
    print "cannot read db, trying to create it first"
    return save_db()

@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/publish", methods=["POST"])
def publish():
    try:
        handle = request.form["handle"]
        email = request.form["email"]
        text = request.form["freetext"]
    except:
        abort(500)

    db.append({"handle": handle, "email": email, "text": text,})
    save_db()
    return redirect("/details/%d" % (len(db)-1))


@app.route("/qr/<int:ident>")
def gen_qr(ident=None):
    if ident is None: abort(500)
    data = {}
    try: data = db[ident]
    except: abort(404)

    import qrcode
    import os.path

    qrpath = "qr/%s.png" % (ident)
    if not os.path.isfile(qrpath):  #skip if qrcode has already been written
        qr = qrcode.QRCode(version=5, error_correction=qrcode.constants.ERROR_CORRECT_Q, box_size=30, border=0)
        qr.add_data("%s" % (data["email"]))
        qr.make(fit=True)
        img = qr.make_image()
        img.save(qrpath)
        generate_cute_qr(qrpath, data)

    assert (os.path.isfile(qrpath))
    f = open(qrpath)
    return send_file(f, mimetype="image/png")


@app.route("/details/<int:ident>")
def details_for(ident=None):
    """
    returns details for box or project
    """
    if ident is None: abort(500)

    data = {}
    try: data = db[ident]
    except: print "%d not found" % (ident)
    return render_template("tag.html", host=request.host, app=app, ident=ident, data=data)


@app.route("/details/<int:ident>/json")
def json_for(ident=None):
    import json

    if ident is None: abort(500)

    data = {}
    try: data = db[ident]
    except: abort(404)
    return json.dumps(data)


def generate_cute_qr(qrpath, data):
    from PIL import Image, ImageDraw, ImageFont

    handletext = data["handle"]
    emailtext = "Email: %s" % data["email"]
    freitext = "%s" % data["text"]


    im = Image.open("../resources/A4_300dpi_generic_tag.png")
    qr = Image.open(qrpath)
    qr = qr.resize((896, 896), Image.BICUBIC)

    textFontsize = 200
    textFont = ImageFont.truetype("../resources/Vera.ttf", textFontsize)
    offsetX = 444  #offset for the shackspace logo on the leftside
    draw = ImageDraw.Draw(im)

    draw.text((offsetX, 400), handletext, font=textFont, fill="#000000")
    draw.text((offsetX, 800), emailtext,  font=textFont, fill="#000000")
    draw.text((offsetX, 1200), freitext,   font=textFont, fill="#000000")

    #QR-Code
    im.paste(qr, (2392, 300))
    del draw
    im.save(qrpath, "PNG")

if __name__ == "__main__":
    #url_for('static', filename='index.js')
    #url_for('static', filename='jquery-1.7.2.min.js')
    app.debug = True
    #system("rm qr/*")
    db = []
    db = load_db()
    app.run(host="0.0.0.0", port=8080)
