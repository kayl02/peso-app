from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)
app.secret_key = 'peso_secret_key'

import os

DB_CONFIG = {
    'host': os.environ.get('MYSQLHOST', 'localhost'),
    'user': os.environ.get('MYSQLUSER', 'root'),
    'password': os.environ.get('MYSQLPASSWORD', ''),
    'database': os.environ.get('MYSQLDATABASE', 'peso_db'),
    'port': int(os.environ.get('MYSQLPORT', 3306))
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def generate_applicant_id(cursor):
    cursor.execute("SELECT Applicant_ID FROM Applicant ORDER BY Applicant_ID DESC LIMIT 1")
    last = cursor.fetchone()
    if not last:
        return 'AP001'
    last_id = last[0]  # e.g. AP007
    num = int(last_id[2:]) + 1
    return f'AP{num:03}'

def generate_skill_cd(cursor):
    cursor.execute("SELECT SkillCD FROM Skills_Acquired ORDER BY SkillCD DESC LIMIT 1")
    last = cursor.fetchone()
    if not last:
        return 'SK001'
    last_id = last[0]
    num = int(last_id[2:]) + 1
    return f'SK{num:03}'

# ─────────────────────────────────────────
# HOME / DASHBOARD
# ─────────────────────────────────────────
@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM Applicant")
    total = cursor.fetchone()['total']

    cursor.execute("""
        SELECT Employment_Status, COUNT(*) AS Total
        FROM Employment
        GROUP BY Employment_Status
        ORDER BY Total DESC
    """)
    emp_stats = cursor.fetchall()

    cursor.execute("SELECT * FROM Applicant ORDER BY Applicant_ID DESC LIMIT 5")
    recent = cursor.fetchall()

    cursor.close(); db.close()
    return render_template('index.html', total=total, emp_stats=emp_stats, recent=recent)

# ─────────────────────────────────────────
# LIST ALL APPLICANTS
# ─────────────────────────────────────────
@app.route('/applicants')
def applicants():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.Applicant_ID, a.Name, a.Mobile_No, a.Civil_Status,
               e.Employment_Status, emp.Employer_Name
        FROM Applicant a
        LEFT JOIN Employment e ON a.Applicant_ID = e.Applicant_ID
        LEFT JOIN Employer emp ON e.Employer_ID = emp.Employer_ID
    """)
    rows = cursor.fetchall()
    cursor.close(); db.close()
    return render_template('applicants.html', applicants=rows)

# ─────────────────────────────────────────
# VIEW SINGLE APPLICANT
# ─────────────────────────────────────────
@app.route('/applicant/<id>')
def view_applicant(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Applicant WHERE Applicant_ID = %s", (id,))
    applicant = cursor.fetchone()
    if not applicant:
        flash('Applicant not found.', 'error')
        return redirect(url_for('applicants'))

    cursor.execute("SELECT * FROM Educational_Background WHERE Applicant_ID = %s", (id,))
    education = cursor.fetchall()

    cursor.execute("SELECT * FROM Language_Spoken WHERE Applicant_ID = %s", (id,))
    languages = cursor.fetchall()

    cursor.execute("""
        SELECT t.*, s.Skills FROM Training_Certificates t
        JOIN Skills_Acquired s ON t.SkillCD = s.SkillCD
        WHERE t.Applicant_ID = %s
    """, (id,))
    trainings = cursor.fetchall()

    cursor.execute("SELECT * FROM Credentials WHERE Applicant_ID = %s", (id,))
    credentials = cursor.fetchall()

    cursor.execute("""
        SELECT e.*, emp.Employer_Name, emp.Employer_Address, emp.Business_Nature
        FROM Employment e JOIN Employer emp ON e.Employer_ID = emp.Employer_ID
        WHERE e.Applicant_ID = %s
    """, (id,))
    employment = cursor.fetchone()

    cursor.execute("SELECT * FROM Overseas_Filipino WHERE Applicant_ID = %s", (id,))
    overseas = cursor.fetchone()

    cursor.close(); db.close()
    return render_template('view_applicant.html',
        applicant=applicant, education=education, languages=languages,
        trainings=trainings, credentials=credentials,
        employment=employment, overseas=overseas)

# ─────────────────────────────────────────
# ADD NEW APPLICANT (FORM)
# ─────────────────────────────────────────
@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        try:
            f = request.form

            # Auto-generate Applicant ID
            applicant_id = generate_applicant_id(cursor)

            # INSERT applicant
            cursor.execute("""
                INSERT INTO Applicant
                (Applicant_ID, Name, Address, Birthdate, Place_Birth, Age, Sex,
                 Height, Weight, Religion, Civil_Status, Landline_No, Mobile_No, Email_Address)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                applicant_id, f['name'], f['address'], f['birthdate'],
                f['place_birth'], f['age'], f['sex'],
                f.get('height') or None, f.get('weight') or None,
                f.get('religion') or None, f['civil_status'],
                f.get('landline') or None, f['mobile'], f.get('email') or None
            ))

            # Employer
            cursor.execute("""
                INSERT INTO Employer (Employer_Name, Employer_Address, Business_Nature)
                VALUES (%s,%s,%s)
            """, (f['employer_name'], f['employer_address'], f.get('business_nature') or None))
            employer_id = cursor.lastrowid

            # Employment
            cursor.execute("""
                INSERT INTO Employment
                (Applicant_ID, Employment_Status, Position_LastEmployer, Current_Position, Employer_ID)
                VALUES (%s,%s,%s,%s,%s)
            """, (applicant_id, f['employment_status'],
                  f.get('position_last') or None, f['current_position'], employer_id))

            # Education rows
            for level in ['Elementary', 'High School', 'College']:
                key = level.lower().replace(' ', '_')
                school = f.get(f'school_{key}')
                if school:
                    cursor.execute("""
                        INSERT INTO Educational_Background
                        (Educ_Level, Applicant_ID, School_Name, HighestLevelComp, Year_Graduated)
                        VALUES (%s,%s,%s,%s,%s)
                    """, (level, applicant_id, school,
                          f.get(f'course_{key}', ''), f.get(f'year_{key}', 1970)))

            # Languages
            for lang in f.getlist('languages'):
                if lang.strip():
                    cursor.execute("""
                        INSERT INTO Language_Spoken (Applicant_ID, Linguistic)
                        VALUES (%s,%s)
                    """, (applicant_id, lang.strip()))

            # Training + auto-generate SkillCD
            # Each cert maps to multiple skills via form order
            training_certs = f.getlist('training_cert')
            training_periods = f.getlist('training_period')
            training_skills = f.getlist('training_skill')

            # Distribute skills across certs (skills are listed per cert block)
            skill_index = 0
            for i, cert in enumerate(training_certs):
                if not cert.strip():
                    skill_index += 1
                    continue
                period = training_periods[i] if i < len(training_periods) else ''
                # First skill is required to link to the training cert
                first_skillcd = None
                while skill_index < len(training_skills):
                    skill = training_skills[skill_index].strip()
                    skill_index += 1
                    if not skill:
                        continue
                    skillcd = generate_skill_cd(cursor)
                    cursor.execute("INSERT INTO Skills_Acquired (SkillCD, Skills) VALUES (%s,%s)",
                                   (skillcd, skill))
                    if first_skillcd is None:
                        first_skillcd = skillcd
                        cursor.execute("""
                            INSERT INTO Training_Certificates
                            (Applicant_ID, Training_Cert, Training_Period, SkillCD)
                            VALUES (%s,%s,%s,%s)
                        """, (applicant_id, cert, period, skillcd))
                    else:
                        # Additional skills link to same cert
                        cursor.execute("""
                            INSERT INTO Training_Certificates
                            (Applicant_ID, Training_Cert, Training_Period, SkillCD)
                            VALUES (%s,%s,%s,%s)
                        """, (applicant_id, cert, period, skillcd))
                    break  # one skill per loop iteration per cert; next cert gets next skill
                if first_skillcd is None:
                    # cert with no skill — insert placeholder
                    skillcd = generate_skill_cd(cursor)
                    cursor.execute("INSERT INTO Skills_Acquired (SkillCD, Skills) VALUES (%s,%s)",
                                   (skillcd, 'N/A'))
                    cursor.execute("""
                        INSERT INTO Training_Certificates
                        (Applicant_ID, Training_Cert, Training_Period, SkillCD)
                        VALUES (%s,%s,%s,%s)
                    """, (applicant_id, cert, period, skillcd))

            # Credentials
            for cred in f.getlist('credentials'):
                if cred.strip():
                    cursor.execute("""
                        INSERT INTO Credentials (Applicant_ID, Credentials_Title)
                        VALUES (%s,%s)
                    """, (applicant_id, cred.strip()))

            # Overseas Filipino
            is_of = f.get('is_overseas', 'No')
            cursor.execute("""
                INSERT INTO Overseas_Filipino
                (Applicant_ID, If_OverseasFilipino, OF_Dependent, OF_Location, OF_Status)
                VALUES (%s,%s,%s,%s,%s)
            """, (applicant_id, is_of,
                  f.get('of_dependent') or None,
                  f.get('of_location') or None,
                  f.get('of_status') or None))

            db.commit()
            flash(f'Application submitted! Applicant ID: {applicant_id}', 'success')
            return redirect(url_for('view_applicant', id=applicant_id))

        except Error as e:
            db.rollback()
            flash(f'Error: {e}', 'error')
        finally:
            cursor.close(); db.close()

    return render_template('apply.html')

# ─────────────────────────────────────────
# DELETE APPLICANT
# ─────────────────────────────────────────
@app.route('/delete/<id>', methods=['POST'])
def delete_applicant(id):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM Applicant WHERE Applicant_ID = %s", (id,))
        db.commit()
        flash('Applicant deleted.', 'success')
    except Error as e:
        db.rollback()
        flash(f'Error: {e}', 'error')
    finally:
        cursor.close(); db.close()
    return redirect(url_for('applicants'))

# ─────────────────────────────────────────
# SQL REPORTS PAGE
# ─────────────────────────────────────────
@app.route('/reports')
def reports():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Applicant")
    simple1 = cursor.fetchall()

    cursor.execute("SELECT * FROM Skills_Acquired")
    simple2 = cursor.fetchall()

    status_filter = request.args.get('civil_status', 'Single')
    cursor.execute("SELECT Applicant_ID, Name, Civil_Status FROM Applicant WHERE Civil_Status = %s", (status_filter,))
    moderate1 = cursor.fetchall()

    cursor.execute("""
        SELECT a.Name, e.Employment_Status, emp.Employer_Name
        FROM Applicant a
        JOIN Employment e ON a.Applicant_ID = e.Applicant_ID
        JOIN Employer emp ON e.Employer_ID = emp.Employer_ID
    """)
    moderate3 = cursor.fetchall()

    cursor.execute("""
        SELECT a.Name, l.Linguistic
        FROM Applicant a JOIN Language_Spoken l ON a.Applicant_ID = l.Applicant_ID
    """)
    moderate4 = cursor.fetchall()

    cursor.execute("""
        SELECT Employment_Status, COUNT(*) AS Total
        FROM Employment GROUP BY Employment_Status ORDER BY Total DESC
    """)
    difficult1 = cursor.fetchall()

    cursor.execute("""
        SELECT a.Name, COUNT(t.TrainingCert_ID) AS Total_Trainings
        FROM Applicant a
        JOIN Training_Certificates t ON a.Applicant_ID = t.Applicant_ID
        GROUP BY a.Applicant_ID, a.Name
        HAVING COUNT(t.TrainingCert_ID) > 1
    """)
    difficult2 = cursor.fetchall()

    cursor.execute("""
        SELECT a.Name, o.OF_Dependent, o.OF_Location, o.OF_Status
        FROM Applicant a
        JOIN Overseas_Filipino o ON a.Applicant_ID = o.Applicant_ID
        WHERE o.If_OverseasFilipino = 'Yes' AND o.OF_Dependent IS NOT NULL
    """)
    difficult3 = cursor.fetchall()

    cursor.close(); db.close()
    return render_template('reports.html',
        simple1=simple1, simple2=simple2,
        moderate1=moderate1, moderate3=moderate3, moderate4=moderate4,
        difficult1=difficult1, difficult2=difficult2, difficult3=difficult3,
        status_filter=status_filter)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
