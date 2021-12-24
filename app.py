from flask import Flask, render_template
from forms import AddImage, RGFields

from MODELS.main_model_two import Image_Pre_Processing, Execute_OCR_RG

app = Flask(__name__)
app.config["SECRET_KEY"] = "mysecretkey"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add_image", methods=["GET", "POST"])
def add_image():

    form = AddImage()
    results = RGFields()

    if form.validate_on_submit():

        rg = form.rg.data
        dewarper = Image_Pre_Processing(blur_ksize=5, threshold_value=195, dilation_ksize=5, output_size=600)
        rg_reader = Execute_OCR_RG(dewarper)
        output_rg = rg_reader.execute_pipeline_ocr(rg)
        
        results.rg.data = output_rg["RG"]
        results.exped.data = output_rg["DATA_EXPED"]
        results.name.data = output_rg["NOME"]
        results.mother.data = output_rg["NOME_MAE"]
        results.father.data = output_rg["NOME_PAI"]
        results.bdate.data = output_rg["DATA_NASC"]
        results.cpf.data = output_rg["CPF"]
        results.city.data = output_rg["CIDADE_ORIGEM"]
        results.state.data = output_rg["UF_ORIGEM"]

        return render_template("data.html", form=results)

    return render_template("add.html", form=form)

@app.errorhandler(404)
def error404(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)



    