from flask import Flask, render_template, request, flash
import Levenshtein
import sqlite3


app = Flask(__name__)
app.secret_key = "secret_delas"

@app.route("/")
def index():
	flash("Ingresa tu nombre de empresa")
	return render_template("index.html")


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def calculate_similarity(consulta, empresas_nombres):
    similarity_list = []
    
    for nombre in empresas_nombres:
        distance = Levenshtein.distance(consulta, nombre)
        similarity = 100 - (distance / max(len(consulta), len(nombre))) * 100
        similarity_list.append(similarity)
    
    return similarity_list


@app.route("/consulta", methods=['POST', 'GET'])
def consulta():

	nombre_consultado = str(request.form['nombre_input'])

	conn = get_db_connection()
	empresas = conn.execute("SELECT nombre FROM empresa").fetchall()
	empresas_nombres = [row['nombre'].lower() for row in empresas]
	similaridades = calculate_similarity(nombre_consultado, empresas_nombres)
	empresa_nombre_similaridad = zip(empresas_nombres, similaridades)

	print('nombre_consultado', nombre_consultado)
	# print('empresas_nombres', empresas_nombres)
	# print(similaridades)
	
	return render_template("index.html", nombre_consultado=nombre_consultado, empresa_nombre_similaridad=empresa_nombre_similaridad)


if __name__ == "__main__":
    app.run(port=8000, debug=True)

