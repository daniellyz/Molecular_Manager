import sqlite3
import pandas as pd
import helper

cpds = sqlite3.connect('compounds.db')

cursor = cpds.cursor()

# Update database with exact mass

cursor.execute("SELECT compound_id, molecular_formula, computed_mass FROM compounds")
rows = cursor.fetchall()

for row in rows:
    row_id, mf, mass = row # The 'id' of the current row
    new_mass = helper.monoisotopic_mass(mf)
    if new_mass > 0:
        cursor.execute("UPDATE compounds SET computed_mass = ? WHERE compound_id = ?", (new_mass, row_id))
        cpds.commit()
    else:
        print('Failed to update')

cpds.close()

cpds = sqlite3.connect('compounds.db')
cursor = cpds.cursor()

# List all compounds

cursor.execute('select * from compounds')
rows = cursor.fetchall()
df = pd.DataFrame.from_records(rows, columns = ['cid', 'name', 'nf', 'type', 'nm'])

# Check measured compounds table max index

cursor.execute("DELETE FROM measured_compounds")
cpds.commit()

cursor.execute("DELETE FROM retention_time")
cpds.commit()

cursor.execute("SELECT measured_compound_id FROM measured_compounds")

tmp_id = cursor.fetchall()
if len(tmp_id) == 0:
    max_id = 999
else:
    max_id = max(tmp_id)

# Add one new measured compound into db
# Update retention time table ??
# Update compound table ??
# Update adduct table ??

measured = pd.read_excel('measured-compounds.xlsx')

for idx in measured.index:

    cid = int(measured['compound_id'][idx])
    #cpd = "Sulcotrion-D3"
    rt = float(measured['retention_time'][idx])
    rt_comment = str(measured['retention_time_comment'][idx])
    adduct_name = str(measured['adduct_name'][idx])

    rid = 'C' + str(cid) + ':RT' + str(rt)

    cursor.execute('SELECT adduct_id, mass_adjustment FROM adduct WHERE adduct_name = ?', (adduct_name,))
    aid, ajd = cursor.fetchone() # aid and mass difference obtained

    cursor.execute('SELECT measured_compound_id FROM measured_compounds WHERE compound_id = ? AND retention_time_id = ? AND adduct_id = ?', (cid, rid, aid))
    result = cursor.fetchone()

    if result is None:

        # No record found, insert the new record

        new_id = max_id + 1

        # Get neutral mass from compound table, add adduct adjustment

        cursor.execute('SELECT computed_mass FROM compounds WHERE compound_id = ?', (cid,))
        nm = cursor.fetchone()[0]
        new_mass = round(nm + ajd, 4)

        #  Get neutral formula from compound table, add adduct adjustment

        cursor.execute('SELECT molecular_formula FROM compounds WHERE compound_id = ?', (cid,))
        nf = cursor.fetchone()[0]
        mf = helper.ion_formula(nf, adduct_name)

        # Insert the new record (row of excel) into measured compounds:

        cursor.execute('INSERT INTO measured_compounds (measured_compound_id, compound_id, retention_time_id, adduct_id, measured_mass, molecular_formula) VALUES (?, ?, ?, ?, ?, ?)', (new_id, cid, rid, aid, new_mass, mf))
        cpds.commit()

        cursor.execute('SELECT * from measured_compounds where measured_compound_id = ?', (new_id,))
        result = cursor.fetchone()
        print(result)
        print("New record inserted.")

        max_id = new_id

        # Insert the new record (row of excel) into retention time table if it doesn't exist yet:

        cursor.execute('INSERT OR IGNORE INTO retention_time (retention_time_id, retention_time, comment) VALUES (?, ?, ?)', (rid, rt, rt_comment))
        cpds.commit()

    else:
    # Record already exists
        print("Record already exists with id:", result[0])

cpds.close()

# List all measured compounds

cpds = sqlite3.connect('compounds.db')

cursor = cpds.cursor()

cursor.execute('select * from measured_compounds')
rows = cursor.fetchall()
df = pd.DataFrame.from_records(rows, columns =['mid', 'cid', 'rid', 'aid', 'mm', 'mf'])

# Query measured compounds

type = "internal standard"
cursor.execute('select * from measured_compounds where compound_id in (select compound_id from compounds where compounds.type = ?)', (type,))
rows = cursor.fetchall()
df = pd.DataFrame.from_records(rows, columns =['mid', 'cid', 'rid', 'aid', 'mm', 'mf'])

# selection retention time (deviation allowed ???)

rt = 18
cursor.execute('select * from measured_compounds where retention_time_id in (select retention_time_id from retention_time where retention_time.retention_time = ?)', (rt, ))
rows = cursor.fetchall()
df = pd.DataFrame.from_records(rows, columns =['mid', 'cid', 'rid', 'aid', 'mm', 'mf'])

# selection ion type based on adducts

polarity = "positive"
cursor.execute('select * from measured_compounds where adduct_id in (select adduct_id from adduct where adduct.ion_mode = ?)', (polarity, ))
rows = cursor.fetchall()
df = pd.DataFrame.from_records(rows, columns =['mid', 'cid', 'rid', 'aid', 'mm', 'mf'])
