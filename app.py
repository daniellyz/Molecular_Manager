from flask import Flask, jsonify, request, g
import sqlite3
import helper

app = Flask(__name__)

# Path to the SQLite database
DATABASE = 'compounds.db'

# Function to connect to the database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Automatically close the connection to the database when the app context ends

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Function to query the database with any SQLite language
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    res = cur.fetchall()
    cur.close()
    return res

# Function to add one compound to compound table:
def insert_compound(cid, cpd_name, mf, type):

    cpds = get_db()
    cursor = cpds.cursor()

    # Calculate neutral mass:
    new_mass = helper.monoisotopic_mass(mf)

    # Insert the compound:
    if new_mass>0 and cpd_name!="":
        insert_cpd = f'INSERT INTO compounds ' \
                     f'(compound_id, compound_name, molecular_formula, type, computed_mass) ' \
                     f'VALUES (?, ?, ?, ?, ?)'
        cursor.execute(insert_cpd, [cid, cpd_name, mf, type, new_mass])
    cursor.close()
    cpds.commit()

# Function to add one measured compound:
def insert_measured_compound(new_id, cid, rid, aid, new_mass, mf):

    cpds = get_db()
    cursor = cpds.cursor()
    insert_mc = f'INSERT INTO measured_compounds ' \
                f'(measured_compound_id, compound_id, retention_time_id, adduct_id, measured_mass, molecular_formula)' \
                f'VALUES (?, ?, ?, ?, ?, ?)'
    cursor.execute(insert_mc, [new_id, cid, rid, aid, new_mass, mf])
    cursor.close()
    cpds.commit()

# # Function to add one retention time:
def insert_rt(rid, rt, rt_comment):

    cpds = get_db()
    cursor = cpds.cursor()

    insert_rt = f'INSERT OR IGNORE INTO retention_time ' \
            f'(retention_time_id, retention_time, comment) ' \
            f'VALUES (?, ?, ?)'
    cursor.execute(insert_rt, [rid, rt, rt_comment])
    cursor.close()
    cpds.commit()

# Route to get all compounds

@app.route('/compounds', methods=['GET'])
def get_compounds():
    res = query_db(f'SELECT * FROM compounds')
    # Transformation to dictionary for json format:
    compound_list = [{'Compound ID': x[0], 'Compound name': x[1], 'Neutral formula': x[2], 'Type': x[3], 'Neutral mass': x[4]} for x in res]
    return jsonify(compound_list)

# Route to get all measured compounds

@app.route('/measured_compounds', methods=['GET'])
def get_measured_compounds():
    res = query_db(f'SELECT * FROM measured_compounds')
    if not res:
        return jsonify({'Achtung': 'No measured compound'}), 404
    else:
        measured_compound_list = [{'Measured Compound ID': x[0], 'Compound ID': x[1], 'Retention Time ID': x[2], 'Adduct ID': x[3], 'Ion mass': x[4], 'Ion formula': x[5]} for x in res]
        return jsonify(measured_compound_list)

# Route to query measured compounds

@app.route('/measured_compounds/query', methods=['GET'])
def query_measured_compounds():

    # http://127.0.0.1:5000/measured_compounds/query?query_params=RT&value=3
    # http://127.0.0.1:5000/measured_compounds/query?query_params=RT&value=-1
    # http://127.0.0.1:5000/measured_compounds?query_params=RT
    # http://127.0.0.1:5000/measured_compounds/query?query_params=type&value=internal standard
    # http://127.0.0.1:5000/measured_compounds/query?query_params=type&value=Unknown
    # http://127.0.0.1:5000/measured_compounds/query?query_params=polarity&value=negative

    ALLOWED_PARAMS = ['RT', 'type', 'polarity']

    query_params = request.args.get('query_params')
    value = request.args.get('value')

    if not query_db(f'SELECT * FROM measured_compounds'):
        return jsonify({'Achtung': 'No measured compound'}), 400

    if query_params not in ALLOWED_PARAMS:
        return jsonify({'error': 'Invalid query parameter, please use RT, type or polarity'}), 400

    if not value:
        return jsonify({'error': 'Please specify a value for the query'}), 400

    match query_params:
        case "RT":
            try:
                rt = round(float(value), 2)
            except ValueError:
                return jsonify({'Achtung': 'Retention time should be a number!'}), 400
            if rt <= 0:
                return jsonify({'Achtung': 'Retention time should be positive!'}), 400

            #query = f'SELECT * FROM measured_compounds ' \ # Another method
            #        f'WHERE measured_compounds.retention_time_id in ' \
            #        f'(SELECT retention_time_id FROM retention_time ' \
            #        f'WHERE retention_time.retention_time = ?)'

            query = f'SELECT M.*, R.retention_time ' \
                    f'FROM measured_compounds AS M ' \
                    f'JOIN retention_time AS R ' \
                    f'ON M.retention_time_id = R.retention_time_id ' \
                    f'WHERE R.retention_time = ?'

            res = query_db(query, [rt])
            res_list = [{'Measured Compound ID': x[0], 'Compound ID': x[1], 'Retention Time ID': x[2], 'Adduct ID': x[3],
                 'Ion mass': x[4], 'Ion formula': x[5], 'Retention time': x[6]} for x in res]

        case "type":

            type = value

            ALLOWED_TYPE = query_db(f'SELECT DISTINCT type FROM compounds')
            ALLOWED_TYPE = [x[0] for x in ALLOWED_TYPE if x[0]!= ""]
            ALLOWED_TYPE.append("Unknown")

            if type not in ALLOWED_TYPE:
                return jsonify({'Achtung': f'Invalid query value, please use ' + str(ALLOWED_TYPE)}), 400

            if type == "Unknown":
                type = ""

            query = f'SELECT M.*, C.type ' \
                    f'FROM measured_compounds AS M ' \
                    f'JOIN compounds AS C ' \
                    f'ON M.compound_id = C.compound_id ' \
                    f'WHERE C.type = ?'

            res = query_db(query, [type])
            res_list = [{'Measured Compound ID': x[0], 'Compound ID': x[1], 'Retention Time ID': x[2], 'Adduct ID': x[3],
                 'Ion mass': x[4], 'Ion formula': x[5], 'Type': x[6]} for x in res]

        case "polarity":
            polarity = value

            ALLOWED_POLARITY = ["positive", "negative"]
            if polarity not in ALLOWED_POLARITY:
                return jsonify({'Achtung': 'ion mode should be positive or negative!'}), 400

            query = f'SELECT M.*, A.ion_mode ' \
                    f'FROM measured_compounds AS M ' \
                    f'JOIN adduct AS A ' \
                    f'ON M.adduct_id = A.adduct_id ' \
                    f'WHERE A.ion_mode = ?'

            res = query_db(query, [polarity])
            res_list = [{'Measured Compound ID': x[0], 'Compound ID': x[1], 'Retention Time ID': x[2], 'Adduct ID': x[3],
                 'Ion mass': x[4], 'Ion formula': x[5], 'Polarity': x[6]} for x in res]

    if not res_list:
        return jsonify({'error': 'No measured compounds found for the given query'}), 404
    else:
        return jsonify(res_list)

# Route to add measured compound

@app.route('/measured_compounds/update', methods=['POST'])

def update_measured_compounds():

    # "Allowed" input values:

    ALLOWED_CID = query_db(f'SELECT compound_id FROM compounds')
    ALLOWED_CID = [x[0] for x in ALLOWED_CID]
    ALLOWED_RT_ID = query_db(f'SELECT retention_time_id FROM retention_time')
    ALLOWED_ADDUCT_NAME = query_db(f'SELECT adduct_name FROM adduct')
    ALLOWED_ADDUCT_NAME = [x[0] for x in ALLOWED_ADDUCT_NAME]
    ALLOWED_ADMIN_USER = "Admin"
    ALLOWED_ADMIN_PW = 1111

    # Check the highest id in measured compound table:

    res = query_db("SELECT measured_compound_id FROM measured_compounds")
    max_id = 999 if not res else max(res)[0]

    # Retrieve data from input json:

    new_measured_compound = request.get_json()
    cid = int(new_measured_compound.get('compound_id'))
    cpd_name = str(new_measured_compound.get('compound_name'))
    rt = new_measured_compound.get('retention_time')
    rt_comment = str(new_measured_compound.get('retention_time_comment'))
    adduct_name = str(new_measured_compound.get('adduct_name'))
    user = str(new_measured_compound.get('user')) # user to upgrade compound
    pw = int(new_measured_compound.get('password')) # password to update compound
    type = str(new_measured_compound.get('type')) # type of compound to update compound
    mf = str(new_measured_compound.get('molecular_formula')) # molecular formula to update compound

    # If the compound does not exist in the compound database, consider update compound table if user has admin right:

    if cid not in ALLOWED_CID:
        if pw != ALLOWED_ADMIN_PW or user != ALLOWED_ADMIN_USER:
            return jsonify({"Achtung": "Compound does not exist with id: " + str(cid) + ". You need admin right to add compound."}), 400
        else:
            if not type or not mf or not cpd_name:
                return jsonify({"Achtung": "Please specify compound type, name and molecular formula! "}), 400
            else:
                insert_compound(cid, cpd_name, mf, type)
                ALLOWED_CID = query_db(f'SELECT compound_id FROM compounds')
                ALLOWED_CID = [x[0] for x in ALLOWED_CID]
                if cid not in ALLOWED_CID:
                    return jsonify({"Error": "Compound update failed. "}), 400

    # If the adduct exists in the database, retrieve adjustment for ion mass:

    if adduct_name not in ALLOWED_ADDUCT_NAME:
        return jsonify({"Achtung": "Adduct name does not exist: " + str(adduct_name)}), 400
    else:
        res = query_db(f'SELECT adduct_id, mass_adjustment FROM adduct WHERE adduct_name = ?', [adduct_name])
        aid, ajd = res[0]

    # Check retention time input and if the retention time table needs to be updated

    try:
        rt = round(float(rt), 2)
        if rt <= 0:
            return jsonify({'Achtung': 'Retention time should be positive!'}), 400
        rid = 'C' + str(cid) + ':RT' + str(rt)  # retention time index, linked to compound
        if rid not in ALLOWED_RT_ID:
            insert_rt(rid, rt, rt_comment)
    except ValueError:
        return jsonify({'Achtung': 'Retention time should be a number!'}), 400

    # Check if the newly measured compound already exists in the database (avoid duplicated measured compound entry):

    res = query_db(f'SELECT measured_compound_id FROM measured_compounds WHERE compound_id = ? AND retention_time_id = ? AND adduct_id = ?', [cid, rid, aid])
    existing_id = res  # searching if the new compound already exists in the database

    # Insert and display the new record:

    if not existing_id:

        new_id = max_id + 1 # the index increments by 1 to the newest existing item in the db

        # Get neutral mass from compound table, add adduct adjustment to get ion mass:

        res = query_db(f'SELECT computed_mass FROM compounds WHERE compound_id = ?', [cid])
        new_mass = round(res[0][0] + ajd, 4)

        #  Get neutral formula from compound table, add adduct adjustment to get ion formula:

        res = query_db('SELECT molecular_formula FROM compounds WHERE compound_id = ?', [cid])
        mf = helper.ion_formula(res[0][0], adduct_name)

        # Insert the new record into measured compounds:

        insert_measured_compound(new_id, cid, rid, aid, new_mass, mf)

        res = query_db(f'SELECT * from measured_compounds where measured_compound_id = ?', [new_id])
        res_list = [{'Added': "", 'Measured Compound ID': x[0], 'Compound ID': x[1], 'Retention Time ID': x[2], 'Adduct ID': x[3],
                 'Ion mass': x[4], 'Ion formula': x[5]} for x in res]
        return jsonify(res_list)
        #max_id = new_id
    else:
        return jsonify({"Achtung": "Measured compound already exists with id: " + str(existing_id[0][0])}), 400

# Route to delete all measured compound >1604 (delete all newly added compounds during demo)

@app.route('/measured_compounds/delete', methods=['DELETE'])
def delete_added_measured_compounds():

    initial_db_max_id = 1604
    res = query_db("SELECT measured_compound_id FROM measured_compounds")
    idx_to_delete = [x[0] for x in res if x[0] > initial_db_max_id]

    if len(idx_to_delete) > 0:
        placeholders = ','.join(['?'] * len(idx_to_delete))
        cpds = get_db()
        cursor = cpds.cursor()
        cursor.execute(f'DELETE FROM measured_compounds WHERE measured_compound_id IN ({placeholders})', idx_to_delete)
        rows_deleted = cursor.rowcount
        cpds.commit()
        cpds.close()
        return jsonify({'Message': f'{rows_deleted} items deleted successfully'}), 200

    else:
        return jsonify({'Achtung': 'No items deleted.'}), 400

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)