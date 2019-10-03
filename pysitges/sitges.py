import codecs
import re
import logging
from time import localtime, strftime

import requests
import json

from lxml import etree

from flask import Flask, request, Response, url_for, jsonify, render_template
from werkzeug.contrib.cache import SimpleCache

import urllib3
urllib3.disable_warnings()

def get_sessions():
    url = "http://sitgesfilmfestival.com/cat/programa/projeccions"
    
    response = requests.post(url, verify=False)
    
    tree = etree.HTML(response.text)
    table = tree.xpath('//*[@id="premsa_buscador"]')[0]

    sessions = []
    date_str = ""
    place = ""
    date_int = 20171004
    
    children = table.getchildren()
    for tr in children:
        if "class" not in tr.attrib:
            td = tr.getchildren()[0]
            date_str = td.xpath("string()").strip()
            date_int += 1
            
        elif tr.attrib["class"] == "parrilla_espai":
            td = tr.getchildren()[0]
            place = td.xpath("string()").strip()
            place = place.encode("latin1").decode("utf8")
            
        elif tr.attrib["class"] == "table_tr_0":
            pass
            
        else:
            hour, title, section, duration, buy = tr.getchildren()
            buy_elems = buy.getchildren()
            if buy_elems:
                session = {}
                session["date"] = date_str
                session["place"] = place
                session["hour"] = hour.text.strip()
                if title.getchildren():
                    session["title"] = etree.tostring(title.getchildren()[0]).strip()
                else:
                    session["title"] = title.xpath("string()").strip()
                
                try:
                    session["title"] = session["title"].encode("latin1").decode("utf8")
                except:
                    session["title"] = session["title"].encode("utf8").decode("utf8")
                    
                session["duration"] = duration.text.strip()

                session["day_coded"] = date_int
                session["date_coded"] = str(date_int) + session["hour"].replace(":", "")
                
                buy_url = buy_elems[0].attrib["href"]
                pieces = buy_url.rsplit("=", 1)
                if len(pieces) == 2:
                    sessionId = pieces[1]
                else:
                    sessionId = None
                session["buy_url"] = buy_url
                session["sessionId"] = sessionId
                
                sessions.append(session)
                # print date_str, place, hour.text.strip(), title.xpath("string()").strip(), duration.text.strip(), sessionId
                
    return sessions

def get_sessions_2018(): 
    url = "http://sitgesfilmfestival.com/cat/programa"

    response = requests.post(url, verify=False)

    tree = etree.HTML(response.text)
    table = tree.xpath('//*[@id="program-table"]')[0]

    sessions = []
    rows = table.xpath('tbody/tr')
    for row in rows:
        cells = row.xpath('td')
        
        date = re.sub("\s+", " ", cells[1].xpath("string()")).strip()
        day, hour = date.split(" ")
        day_pieces = day.split("-")
        day_coded = int(day_pieces[2] + day_pieces[1] + day_pieces[0])
        
        title = re.sub("\n\s+", "\n", cells[2].xpath("string()").strip())
        info_url = cells[2].xpath("a")[0].attrib["href"]
        place = cells[3].xpath("string()").strip()
        section = cells[4].xpath("string()")
        duration = cells[5].xpath("string()").strip()
        try:
            buy_url = cells[6].xpath("a")[0].attrib["href"]
 
            pieces = buy_url.rsplit("=", 1)
            if len(pieces) == 2:
                sessionId = pieces[1]
            else:
                sessionId = None
        except:
            buy_url = None
            sessionId = None

        session = {}
        session['title'] = title
        session['info_url'] = info_url
        session['date'] = date
        session['day'] = day
        session['hour'] = hour
        session['day_coded'] = day_coded
        session['place'] = place
        session['duration'] = duration
        session['buy_url'] = buy_url
        session['sessionId'] = sessionId

        sessions.append(session)
        
    return sessions



def get_session_other_info(sessionId):
    # 2017
    url = "https://www.4tickets.es/repositorios/repo43/public/cgi/Gateway.php"
    # 2018
    url = "https://www.4tickets.es/repositorios/repo43r4/public/cgi/Gateway.php"
    # 2019
    url = "https://www.4tickets.es/repositorios/repo43r9a/public/cgi/GatewayV3.php"
    
    now = strftime("%Y%m%d%H%M%S", localtime())
    session_data = {'IdTerminalWeb': '9455',
                    'Idioma': {'0': '02', '1': '02'},
                    'Nivel': 'DetalleAforo',
                    'UserSession': '1570114303.6318',
                    'idIdioma': 'CA',
                    'idSesion': sessionId,
                    'instala': '_4TICK',
                    'seccion': '4',
                    'idRecinto': 'FS4',
                    'idEvento': 'SFF17_303',
                    'IDsRecinto': '0;FS4',
                    'IDSEvento': '0;SFF17_303',
                    'conexiones': '0',
                    'idTipoE': '251',
                    'Etiquetas': '0000000000111489',
                    'NivelPrecios': '0',
                    'timeStamp': now}
                    
    response = requests.post(url, data=session_data)
    #2017
    seats_array = re.findall("\['Disponible'\] *= \"(\d+)\"", response.text)
    #2018
    seats_array = re.findall('"Disponible":"(\d+)"', response.text)
     
    # check
    total = 0
    for seat_count in seats_array[1:]:
        total += int(seat_count)
        
    if (total != int(seats_array[0])):
        print "\n\nERROOOOOOOOOOOOOOOR!!\n\n"
        
    return int(seats_array[0])


def get_session_info(sessionId):
    # 2017
    url = "https://www.4tickets.es/repositorios/repo43/public/cgi/Gateway.php"
    # 2018
    url = "https://www.4tickets.es/repositorios/repo43r4/public/cgi/Gateway.php"
    # 2019
    url = "https://www.4tickets.es/repositorios/repo43r9a/public/cgi/GatewayV3.php"
    
    timeStamp = strftime("%Y%m%d%H%M%S", localtime())
    
    #sessionId = '0000000000157570'
    #timeStamp = '20191003165143'
    userSession = '1570114303.6318'

    session_data = {
                    'idSesion': sessionId,
                    'Idioma': {
                        '0': '02', 
                        '1': '02'},
                    'idIdioma': 'CA',
                    'Nivel': 'Detalle_1_Sesion',
                    'IdTerminalWeb': '9455',
                    'seccion': '1',
                    'instala': '_4TICK',
                    'timeStamp': timeStamp, #now,
                    'UserSession': userSession # 'd:1538387869.519136905670166015625;', #'d:1537379369.8864629268646240234375;',
                }
     
    response = requests.post(url, data=session_data)
    json_dict = json.loads(response.text[8:])[0]
    
    try:
        return json_dict["Sesion"]["Sesion"][0]
    except Exception as e:
        # print session_data
        # print json_dict
        print "Error! Size of session section: ", len(json_dict["Sesion"]["Sesion"])
        raise

def check_day(session_day, start_day, day_count=1):
    if not start_day:
        start_day = int(strftime("%Y%m%d", localtime()))
        
    return session_day >= start_day and session_day < start_day+day_count

def generate_page(start_day=0, day_count=1):
    page_html = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

    <head>
        <meta charset="UTF-8">
        <title>Resumen Festival de sitges</title>
        <style>
            h4 {
                margin-left: 30px;
            }
            table {
                width: 600px;
                margin-left: 50px;
            }
            ul {
                margin: unset;
                padding: unset;
                list-style: none;                
            }
            td.session-title {
                white-space: normal;
            }
            td.hour {
                width: 50px;
            }
            td.seats {
                width: 50px;
                text-align:center; 
            }
            td.full {
                background-color: tomato;
            }
            td.almost_full {
                background-color: khaki;
            }
            td.available {
                background-color: palegreen;
            }
        </style>        
    </head>
    <body>
        <table>
    """
     
    sessions = get_sessions_2018()

    previous_date = 0
    previous_place = ""
    for session in sessions:
        if check_day(session["day_coded"], start_day, day_count):
            app.logger.info("Inserting '%s'..." % session['title'])
            
            if previous_date != session["day_coded"]:
                page_html += "\t\t</table>\n"
                page_html += "\t\t<h3>%s</h3>\n" % session["date"]
                page_html += "\t\t<h4>"
                page_html += session["place"]
                page_html += "</h4>\n\t\t<table>\n"
                page_html += "\t\t\t<tr>\n\t\t\t\t<th>Hora</th>\n\t\t\t\t<th>Plazas</th>\n\t\t\t\t<th style='text-align: left'>Titulo</th>\n\t\t\t</tr>\n"
                previous_place = session["place"]
                previous_date = session["day_coded"]

            elif previous_place != session["place"]:
                page_html += "\t\t</table>\n"
                page_html += "\t\t<h4>"
                page_html += session["place"]
                page_html += "</h4>\n\t\t<table>\n"
                page_html += "\t\t\t<tr>\n\t\t\t\t<th>Hora</th>\n\t\t\t\t<th>Plazas</th>\n\t\t\t\t<th style='text-align: left'>Titulo</th>\n\t\t\t</tr>\n"
                previous_place = session["place"]
                
            try:
                session_info = get_session_info(session["sessionId"])
                agotado = session_info["Agotado"]
                aforo = int(session_info["AforoTotal"])
                ocupado = int(session_info["AforoOcupado"])

                libres = get_session_other_info(session["sessionId"])
                
                if libres == 0:
                    session_color = "full"
                elif libres < 20:
                    session_color = "almost_full"
                else:
                    session_color = "available"
                    
                seats_html = "<a title='%s' href='%s'>%d</a>" % (aforo-ocupado, session["buy_url"], libres)
                
                #print session_info["Agotado"], session_info["AforoTotal"], session_info["AforoOcupado"]
                
            except:
                seats_html = "-"
                session_color = "full"
            
            page_html += "\t\t\t<tr>\n"
            page_html += "\t\t\t\t<td class='hour'>%s</td>\n" % session["hour"]
            page_html += "\t\t\t\t<td class='seats %s'>%s</td>\n" % (session_color, seats_html)
            page_html += "\t\t\t\t<td class='session-title'>"
            try:
                page_html += session["title"].replace("\n", "<br/>")
            except:
                page_html += "!!!!Invalid title!!!!"
            page_html += "</td>\n"

            #print session["date"], session["hour"], session["title"][:20].encode("utf8"),
            page_html += "\t\t\t</tr>\n"
        """
        if (int(now) + 10000) < int(session["date_coded"]):
            print int(now) + 10000, int(session["date_coded"])
            break
        """

    page_html += "\t\t</table>\t</body></html>"
    return page_html
    

def html_to_file():

    with codecs.open("sitges.html", "w", "utf8") as output:
        page_html = generate_page()
        output.write(page_html)   

app = Flask(__name__)
cache = SimpleCache()

@app.route('/api/movie_list/<int:day_coded>')
def get_json(day_coded):
    
    movie_list = []
    
    sessions = get_sessions_2018()
    for session in sessions:
        if check_day(session["day_coded"], day_coded):
            
            app.logger.info("Adding '%s'..." % session['title'])
            movie_list.append(session)
            
            if session["sessionId"]:
                try:
                    session_info = get_session_info(session["sessionId"])

                    session["agotado"] = session_info["Agotado"]
                    session["aforo"] = int(session_info["AforoTotal"])
                    session["ocupado"] = int(session_info["AforoOcupado"])

                    session["libres"] = get_session_other_info(session["sessionId"])
                    session["libres_real"] = session["aforo"] - session["ocupado"]
                    
                    if session["libres"] == 0:
                        session_color = "full"
                    elif session["libres"] < 20:
                        session_color = "almost_full"
                    else:
                        session_color = "available"
                        
                    #seats_html = "<a title='%s' href='%s'>%d</a>" % (aforo-ocupado, session["buy_url"], libres)
                    
                    #print session_info["Agotado"], session_info["AforoTotal"], session_info["AforoOcupado"]
                    
                except Exception as e:
                    session["agotado"] = None
                    session["aforo"] = None
                    session["ocupado"] = None
                    session["libres"] = None
                    
                    app.logger.warn("Something happened!\n Exception message: %s", e)
                    #raise
            else:
                session["agotado"] = None
                session["aforo"] = None
                session["ocupado"] = None
                session["libres"] = None
                

    return Response(json.dumps(movie_list),  mimetype='application/json')

@app.route('/search')
def get_page():

    start_day = request.args.get("start_day", 0)
    day_count = request.args.get("day_count", 1)

    key = 'sitges_page'
    if start_day:
        key += start_day
        
    if day_count:
        key += str(day_count)
    
    app.logger.info("Request for %s received!" % key)
        
    cached_page = cache.get(key)
    if cached_page is None or 'force' in request.args:
        app.logger.info("Generating %s..." % key)
        cached_page = generate_page(start_day=int(start_day), day_count=int(day_count))
        cache.set(key, cached_page, timeout=120 * 60)
        
    app.logger.info("Done!")
    return cached_page


@app.route('/worker.js')
def worker():
    return render_template('worker.js')


@app.route('/movie_info_extractor.js')
def js():
    return render_template('movie_info_extractor.js')

@app.route('/test_index')
def test_index():
    return render_template('index.html')

@app.route('/')
def root():
    return render_template('sitges_2018.html')

#Old index
def index():
    page_html = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

    <head>
        <meta charset="UTF-8">
        <title>Resumen Festival de sitges</title>    
    </head>
    <body>
        <table>
    """
    base_url = "/sitges"
    base_url = ""
    
    page_html += "<a href='%s'>Viernes 5</a><br/>" % (base_url + "/search?start_day=20181005")
    page_html += "<a href='%s'>Sabado  6</a><br/>" % (base_url + "/search?start_day=20181006")
    page_html += "<a href='%s'>Domingo 7</a><br/>" % (base_url + "/search?start_day=20181007")
    page_html += "<a href='%s'>Lunes   8</a><br/>" % (base_url + "/search?start_day=20181008")
    page_html += "<a href='%s'>Martes  9</a><br/>" % (base_url + "/search?start_day=20181009")
    page_html += "<a href='%s'>Miercoles 10</a><br/>" % (base_url + "/search?start_day=28171010")
    page_html += "<a href='%s'>Jueves  11</a><br/>" % (base_url + "/search?start_day=20181011")
    page_html += "<a href='%s'>Viernes 12</a><br/>" % (base_url + "/search?start_day=20181012")
    page_html += "<a href='%s'>Sabado  13</a><br/>" % (base_url + "/search?start_day=20181013")
    page_html += "<a href='%s'>Domingo 14</a><br/>" % (base_url + "/search?start_day=20181014")
    
    page_html +="</body></html>"
    
    return page_html

def launch_server():
    
    app.debug = True
    app.debug_log_format = "%(asctime)s - %(levelname)s - %(message)s"
    app.config['PROPAGATE_EXCEPTIONS'] = True
    
    app.run(host='0.0.0.0', port=9900)

if __name__ == "__main__":
    
    #html_to_file()

    launch_server()
    
