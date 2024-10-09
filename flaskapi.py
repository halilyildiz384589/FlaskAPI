# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 10:51:27 2023

@author: halil
"""
import mysql.connector
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from flask import render_template

app = Flask(__name__)
CORS(app)  # veri paylaşımı güvenliği için


def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="B0H0R_@sude35",
        database="code_of_qr"
    )



@app.route("/")
def index():
    return render_template("index.html")

@app.route('/scan-qr', methods=['POST'])
def scan_qr():
    try:
        data = request.json
        raw_data = data['raw_data']

        db = get_db_connection()
        cursor = db.cursor()

        # Veritabanında raw_data'ya göre arama yapın
        query1 = "SELECT static_id,date,seller FROM staticqr WHERE static_url = %s"
        try:
            cursor.execute(query1, (raw_data,))
            satirlar = cursor.fetchall()
            if not isinstance(satirlar, list) or not satirlar:
                results = "qrverisiyok"
                id = ""
                tarih = ""
                satici = ""
            else:
                results = satirlar
                for satir in satirlar:
                    id = satir[0]
                    tarih = satir[1]
                    satici = satir[2]
        except mysql.connector.Error as e:
            return jsonify(arror=str(e.args[1]))

        cursor.close()
        db.commit()
        db.close()

        if results:  # Sadece sonuç varsa döndür
            return jsonify(results=results, tarih=tarih, satici=satici, id=id)
        else:
            return jsonify(results=results)

    except Exception as e:
        return jsonify(error=str(e))


@app.route('/secondqr', methods=['POST'])
def secondqr():
    try:
        data = request.json
        raw_data = data['raw_data']

        db = get_db_connection()
        cursor = db.cursor()

        # Veritabanında raw_data'ya göre arama yapın
        query1 = "SELECT static_id,unique_id FROM `unique` WHERE uniq_url = %s "
        try:
            cursor.execute(query1, (raw_data,))
            satirlar = cursor.fetchall()
            if not isinstance(satirlar, list) or not satirlar:
                results = "qrverisiyok"
                st_id = ""
            else:
                results = satirlar
                for satir in satirlar:
                    st_id = satir[0]
                    un_id = satir[1]
        except mysql.connector.Error as e:
            return jsonify(arror=str(e.args[1]))

        cursor.close()
        db.commit()
        db.close()

        if results:  # Sadece sonuç varsa döndür
            return jsonify(results=results, st_id=st_id,un_id=un_id)
        else:
            return jsonify(results=results)

    except Exception as e:
        return jsonify(error=str(e))


@app.route('/scan_name', methods=['POST'])
def scan_name():
    try:
        data = request.json
        raw_data = data['raw_data']

        db = get_db_connection()
        cursor = db.cursor()

        # Veritabanında raw_data'ya göre arama yapın
        query1 = "SELECT lot,date,seller FROM staticqr WHERE static_url = %s"
        try:
            cursor.execute(query1, (raw_data,))
            satirlar = cursor.fetchall()
            if not isinstance(satirlar, list) or not satirlar:
                results = "qrverisiyok"
                lot = ""
                tarih = ""
                satici = ""
            else:
                results = satirlar
                for satir in satirlar:
                    lot = satir[0]
                    tarih = satir[1]
                    satici = satir[2]
        except mysql.connector.Error as e:
            return jsonify(arror=str(e.args[1]))

        cursor.close()
        db.commit()
        db.close()

        if results:  # Sadece sonuç varsa döndür
            return jsonify(results=results, lot=lot, tarih=tarih, satici=satici)
        else:
            return jsonify(results=results)

    except Exception as e:
        return jsonify(error=str(e))


@app.route('/signin',
           methods=['POST'])  # uygulama sadece dışarıdan gelen searchlere açıktır. Hatta sadece HTTP POST için açıktırç
def search_in_database():
    try:
        data = request.json
        email = data['email']

        db = get_db_connection()
        cursor = db.cursor()

        query = "SELECT user.user_type, user.password, email_salt.salt FROM user INNER JOIN email_salt ON user.email = email_salt.email WHERE user.email = %s"
        try:
            cursor.execute(query, (email,))
            satirlar = cursor.fetchall()
        except mysql.connector.Error as e:
            return jsonify(arror=str(e.args[1]))

        if not isinstance(satirlar, list) or not satirlar:
            results = "sonuc"
        else:
            satir1 = satirlar[0]
            results = satir1

        if results:  # Sadece sonuç varsa döndür
            return jsonify(results=results)
        else:
            return jsonify(results=results)

    except Exception as e:
        return jsonify(error=str(e))


@app.route('/signup',
           methods=['POST'])  # uygulama sadece dışarıdan gelen searchlere açıktır. Hatta sadece HTTP POST için açıktırç
def signup():
    try:
        data = request.json
        email = data['email']
        phonenumber = data['phonenumber']
        password = data['pass']
        user_type = data['user_type']
        encodedSalt = data['encodedSalt']
        statu = 1

        db = get_db_connection()
        cursor = db.cursor()

        try:
            query = "INSERT INTO email_salt(email,salt) Values (%s, %s)"
            cursor.execute(query, (email, encodedSalt))  # SQL sorgusunu çalıştırdık
            query = "INSERT INTO user(email,phone,password,user_type,statu) Values (%s, %s, %s, %s ,%s)"
            cursor.execute(query, (email, phonenumber, password, user_type, statu))  # SQL sorgusunu çalıştırdık
            results = cursor.rowcount

        except mysql.connector.Error as e:
            return jsonify(arror=str(e.args[1]))

        # Veritabanı yanıtını ekle

        cursor.close()
        db.commit()
        db.close()

        # affected_rows değerini döndür
        if results:  # Sadece sonuç varsa döndür
            return jsonify(results=results)
        else:
            return jsonify(results=results)


    except Exception as e:
        return jsonify(error=str(e))


@app.route('/scanned_qr',
           methods=['POST'])  # uygulama sadece dışarıdan gelen searchlere açıktır. Hatta sadece HTTP POST için açıktırç
def scanned_qr():
    global hm_times_scanned, first_scan_date, last_scan_date

    try:
        data = request.json
        email = data['email']
        staticqr = data['first_id']
        uniqueqr = data['second_id']

        db = get_db_connection()
        cursor = db.cursor()
        try:
            query5 = "SELECT SUM(hm_times_scanned) AS hm_times_scanned, MIN(scan_date) AS first_scan_date, MAX(last_scanned_date) AS last_scan_date FROM  scanned_qr_code where static_id=%s and unique_id=%s"
            cursor.execute(query5, (staticqr, uniqueqr))  # SQL sorgusunu çalıştırdık
            deneme = cursor.fetchone()
            if deneme[0] is not None and deneme[1] is not None and deneme[2] is not None:
                hm_times_scanned = deneme[0]
                first_scan_date = deneme[1]
                last_scan_date = deneme[2]
                asda = "kayıtvar"

            else:
                hm_times_scanned = 0
                first_scan_date = datetime.datetime.now()
                last_scan_date = datetime.datetime.now()
                asda = "kayıtyok"

        except mysql.connector.Error as e:
            return jsonify(arror=str(e.args[1]))
        try:
            query4 = "SELECT hm_times_scanned,scnqr_id FROM  scanned_qr_code where scn_user_id=%s and static_id=%s and unique_id=%s"
            cursor.execute(query4, (email, staticqr, uniqueqr))  # SQL sorgusunu çalıştırdık
            row = cursor.fetchone()
            if row is None:
                try:
                    query3 = "INSERT INTO scanned_qr_code(scn_user_id,static_id,unique_id) Values (%s, %s, %s)"
                    cursor.execute(query3, (email, staticqr, uniqueqr))  # SQL sorgusunu çalıştırdık
                except mysql.connector.Error as e:
                    return jsonify(arror=str(e.args[1]))

            else:
                hm_times_scanned = row[0]
                scan_qr_id = row[1]
                try:
                    update_hm_times = hm_times_scanned + 1
                    query1 = "UPDATE scanned_qr_code SET hm_times_scanned = %s , last_scanned_date = NOW() where scnqr_id= %s"
                    cursor.execute(query1, (update_hm_times, scan_qr_id))  # SQL sorgusunu çalıştırdık
                except mysql.connector.Error as e:
                    return jsonify(mrror=str(e.args[1]))

        except mysql.connector.Error as e:
            return jsonify(error=str(e.args[1]))

        # Veritabanı yanıtını ekle

        cursor.close()
        db.commit()
        db.close()

        return jsonify(asda=asda, hm_times_scanned=hm_times_scanned, first_scan_date=first_scan_date,
                       last_scan_date=last_scan_date)

    except Exception as e:
        return jsonify(error=str(e))


@app.route('/emply', methods=[
    'POST'])  # uygulama sadece dışarıdan gelen searchlere açıktır. Hatta sadece HTTP POST için açıktırç
def emply():
    try:
        data = request.json
        eml = data['email']
        name = data['name']
        surname = data['surname']
        department = data['department']

        db = get_db_connection()
        cursor = db.cursor()

        sorgu = "SELECT user_id FROM  user where email = %s"
        cursor.execute(sorgu, (eml,))
        cs_user_id = cursor.fetchone()[0]

        query = "INSERT INTO company_emp(cn_user_id,name,surname,Department) Values (%s, %s, %s, %s)"
        cursor.execute(query, (cs_user_id, name, surname, department))  # SQL sorgusunu çalıştırdık

        # Veritabanı yanıtını ekle
        affected_rows = cursor.rowcount
        query1 = "UPDATE user SET user_type = 'ct' WHERE email = %s"
        cursor.execute(query1, (eml,))
        cursor.close()
        db.commit()
        db.close()

        # affected_rows değerini döndür
        return jsonify(affected_rows=affected_rows)

    except Exception as e:
        return jsonify(error=str(e))


@app.route('/kayit', methods=[
    'POST'])  # uygulama sadece dışarıdan gelen searchlere açıktır. Hatta sadece HTTP POST için açıktırç
def kayit():
    try:
        data = request.json
        eml = data['email']
        name = data['name']
        surname = data['surname']
        birth_date = data['birthday']
        gender = data['gender']
        city = data['selectedCity']

        db = get_db_connection()
        cursor = db.cursor()

        sorgu = "SELECT user_id FROM  user where email = %s"
        cursor.execute(sorgu, (eml,))
        cs_user_id = cursor.fetchone()[0]

        query = "INSERT INTO customer(cs_user_id,name,surname,birth_date,gender,city) Values (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (cs_user_id, name, surname, birth_date, gender, city))  # SQL sorgusunu çalıştırdık

        # Veritabanı yanıtını ekle
        affected_rows = cursor.rowcount
        query1 = "UPDATE user SET user_type = 'cs' WHERE email = %s"
        cursor.execute(query1, (eml,))
        cursor.close()
        db.commit()
        db.close()

        # affected_rows değerini döndür
        return jsonify(affected_rows=affected_rows)

    except Exception as e:
        return jsonify(error=str(e))


@app.route('/hesapvarmı', methods=[
    'POST'])  # uygulama sadece dışarıdan gelen searchlere açıktır. Hatta sadece HTTP POST için açıktırç
def hesapvarmı():
    try:
        data = request.json
        email = data['email']

        db = get_db_connection()
        cursor = db.cursor()

        query1 = "SELECT email FROM  user where email = %s"
        try:
            cursor.execute(query1, (email,))
            satirlar = cursor.fetchall()

        except mysql.connector.Error as e:
            return jsonify(arror=str(e.args[1]))

        if not isinstance(satirlar, list) or not satirlar:
            results = "hesapyok"
        else:
            results = cursor.rowcount

        cursor.close()
        db.commit()
        db.close()

        if results:  # Sadece sonuç varsa döndür
            return jsonify(results=results)
        else:
            return jsonify(results=results)

    except Exception as e:
        return jsonify(error=str(e))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    print("Flask API is running.")
