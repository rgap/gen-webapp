import sqlite3

import Levenshtein
from flask import Flask, flash, render_template, request

app = Flask(__name__)
app.secret_key = "secret_delas"


@app.route("/")
def index():
    flash("Ingresa tu nombre de empresa")
    return render_template("index.html")


def get_db_connection():
    conn = sqlite3.connect("database/database.db")
    conn.row_factory = sqlite3.Row
    return conn


def calculate_similarity(consulta, empresas_nombres, substring_penalty=1):
    similarity_list = []

    for nombre in empresas_nombres:
        # cleanstrings
        nombre = nombre.replace(".", "")
        nombre = nombre.replace("SA", "")
        nombre = nombre.replace("S A", "")
        nombre = nombre.replace("SAC", "")
        nombre = nombre.replace("S A C", "")
        nombre = nombre.replace("SRL", "")
        nombre = nombre.replace("S R L", "")
        nombre = nombre.replace("EIRL", "")
        nombre = nombre.replace("E I R L", "")
        nombre = nombre.replace("SAA", "")
        nombre = nombre.replace("S A A", "")
        consulta = consulta.lower().strip()
        nombre = nombre.lower().strip()
        tmp_peso_nombre_existe = 0.25 if consulta in nombre else 0
        # compute distance
        distance = Levenshtein.distance(consulta, nombre)
        # Adjust the distance if query is a substring in target
        if consulta in nombre:
            distance -= len(consulta) * substring_penalty

        max_length = max(len(consulta), len(nombre))
        similarity = max(
            (1 - distance / max_length) * 100, 0
        )  # Limit similarity to a minimum of 0

        similarity_list.append(similarity)

    return similarity_list


@app.route("/consulta", methods=["POST", "GET"])
def consulta():
    nombre_consultado = str(request.form["nombre_input"])

    conn = get_db_connection()
    empresas = conn.execute("SELECT nombre FROM empresa").fetchall()
    empresas_nombres = [row["nombre"] for row in empresas]
    similaridades = calculate_similarity(nombre_consultado, empresas_nombres)
    empresa_nombre_similaridad = zip(empresas_nombres, similaridades)
    sorted_empresa_nombre_similaridad = sorted(
        empresa_nombre_similaridad, key=lambda x: x[1], reverse=True
    )
    top_empresa_nombre_similaridad = sorted_empresa_nombre_similaridad[:50]

    # print("nombre_consultado", nombre_consultado)
    # print('empresas_nombres', empresas_nombres)
    # print(similaridades)

    return render_template(
        "index.html",
        nombre_consultado=nombre_consultado,
        top_empresa_nombre_similaridad=top_empresa_nombre_similaridad,
    )


# if __name__ == "__main__":
#     app.run(port=8000, debug=True)
