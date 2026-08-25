from flask import Flask, jsonify, request
from database import get_connection

app = Flask(__name__)


@app.route('/api/test_bd')
def test_bd():
    connection = get_connection()

    if connection:
        connection.close()
        return jsonify({
            'message': 'Connexion à la base de données réussie'
        })

    return jsonify({
        'message': 'Échec de connexion à la base de données'
    }), 500

 
@app.route("/api/inscription", methods=["POST"])
def creer_inscription():

    donnees = request.get_json()
    #pour verifier que c est vraiment du JSON qui a ete envoye
    if not donnees:
        return jsonify({
            "message": "Aucune donnée JSON reçue"
        }),400
    champs_obligatoires = [
        "nom",
        "prenom",
        "date_naissance",
        "email",
        "mot_de_passe",
        "telephone",
        "nom_parent",
        "telephone_parent",
        "inscrit_par_parent",
        "id_filiere",
        "lycee_origine",
        "serie_bac",
        "mention_bac",
        "annee_bac"
    ]
    champs_manquants = []
    for champ in champs_obligatoires:
        if champ not in donnees:
            champs_manquants.append(champ)

    if champs_manquants:
        return jsonify({
            "message": "Champs manquants",
            "champs": champs_manquants
        }), 400
    #pour verifier que l'id_filiere existe dans la table filiere
    sql_filiere = """
        SELECT id_filiere
        FROM filiere
        WHERE id_filiere = %s
    """
    cursor.execute(sql_filiere, (donnees["id_filiere"],))

    filiere = cursor.fetchone()

    if not filiere:
        return jsonify({
            "message": "La filière spécifiée n'existe pas"
        }), 400

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # =========================
        # 1. CREER LE PARCOURS
        # =========================

        sql_parcours = """
            INSERT INTO parcours
            (
                lycee_origine,
                serie_bac,
                mention_bac,
                annee_bac
            )
            VALUES (%s, %s, %s, %s)
        """

        valeurs_parcours = (
            donnees["lycee_origine"],
            donnees["serie_bac"],
            donnees["mention_bac"],
            donnees["annee_bac"]
        )

        cursor.execute(sql_parcours, valeurs_parcours)

        # Récupérer l'ID du parcours créé pour mettre dans la table etudiant
        id_parcours = cursor.lastrowid


        # =========================
        # 2. CREER L'ETUDIANT
        # =========================

        sql_etudiant = """
            INSERT INTO etudiant
            (
                nom,
                prenom,
                date_naissance,
                email,
                mot_de_passe,
                telephone,
                nom_parent,
                telephone_parent,
                inscrit_par_parent,
                id_filiere,
                id_parcours
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        valeurs_etudiant = (
            donnees["nom"],
            donnees["prenom"],
            donnees["date_naissance"],
            donnees["email"],
            donnees["mot_de_passe"],
            donnees["telephone"],
            donnees["nom_parent"],
            donnees["telephone_parent"],
            donnees["inscrit_par_parent"],
            donnees["id_filiere"],
            id_parcours
        )

        cursor.execute(sql_etudiant, valeurs_etudiant)


        # =========================
        # 3. VALIDER LA TRANSACTION
        # =========================

        connection.commit()

        return jsonify({
            "message": "Inscription enregistrée avec succès",
            "id_parcours": id_parcours
        }), 201


    except Exception as e:

        # =========================
        # 4. ANNULER EN CAS D'ERREUR
        # =========================

        connection.rollback()

        return jsonify({
            "message": "Erreur lors de l'inscription",
            "erreur": str(e)
        }), 500


    finally:

        # =========================
        # 5. FERMER LA CONNEXION
        # =========================

        cursor.close()
        connection.close()

@app.route("/api/cycle", methods=["GET"])
def get_cycle():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        sql = """
            SELECT * FROM cycle
        """
        cursor.execute(sql)
        cycles = cursor.fetchall()

        return jsonify(cycles), 200
    except Exception as e:
        return jsonify({"message": "Erreur lors de la récupération des cycles", "erreur": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route("/api/cycles/<int:id_cycle>/filieres", methods=["GET"])
def get_filieres(id_cycle):

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        sql = """
            SELECT id_filiere, nom_filiere
            FROM filiere
            WHERE id_cycle = %s
        """

        cursor.execute(sql, (id_cycle,))

        filieres = cursor.fetchall()

        return jsonify(filieres), 200

    except Exception as e:

        return jsonify({
            "message": "Erreur lors de la récupération des filières",
            "erreur": str(e)
        }), 500

    finally:

        cursor.close()
        connection.close()


if __name__ == '__main__':
    app.run(debug=True)