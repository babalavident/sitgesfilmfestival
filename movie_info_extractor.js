
function LinkFormatter(value, row, index) {
      return "<a href='"+row.info_url+"' target='_blank'>"+value.replace(/(\r\n|\n|\r)/gm, "<br>")+"</a>";
}

function retrieveCapacity(sessionInfo) {
    var proxy = "https://cors.bridged.cc/";
    var url = "https://www.4tickets.es/repositorios/repo43r10.ck/public/cgi/Gateway.php";

    var date = new Date();
    var now = parseInt(date.toJSON().replace(/-|T|:/g, "").substring(0, 14)) + 20000;
                        
    var capacity_request_data = new FormData();
    capacity_request_data.append('idSesion', sessionInfo['sessionId']);
    capacity_request_data.append('Idioma', '02');
    capacity_request_data.append('idIdioma', 'CA');
    capacity_request_data.append('Nivel', 'Detalle_1_Sesion');
    capacity_request_data.append('IdTerminalWeb', '9455');
    capacity_request_data.append('seccion', '1');
    capacity_request_data.append('instala', '_4TICK');
    capacity_request_data.append('timeStamp', now);
    capacity_request_data.append('Idioma', '02');
    capacity_request_data.append('UserSession', '1633000862.8897');

    var promise = fetch(proxy+url, {
        method: 'POST',
        body: capacity_request_data,
        cache: 'no-cache'
    })
    .then(response => {
        if (!response.ok) {
            throw Error(response.statusText);
        }
        return response;
    })
    .then(response => response.text())
    .then(data => {
        try {
            var json = JSON.parse(data.replace("##JSON##", ""));
            var capacity = json[0]["Sesion"]["Sesion"][0];
        
            sessionInfo['agotado'] = capacity["Agotado"];
            sessionInfo['aforo'] = parseInt(capacity["AforoTotal"]);
            sessionInfo['ocupado'] = parseInt(capacity["AforoOcupado"]);
            sessionInfo['libres_real'] = sessionInfo['aforo'] - sessionInfo['ocupado'];
            
        } catch(e) {
            console.log('Something happened while retrieving capacity!\n' + e)
            sessionInfo['agotado'] = null;
            sessionInfo['aforo'] = null;
            sessionInfo['ocupado'] = null;
            sessionInfo['libres_real'] = null;
        }
    })
    .catch(error => console.log("Error on getting capacity page: " + error));

    return promise;
}

function retrieveSeats(sessionInfo) {
    var proxy = "https://cors.bridged.cc/";
    var url = "https://www.4tickets.es/repositorios/repo43r10.ck/public/cgi/Gateway.php";

    var date = new Date();
    var now = parseInt(date.toJSON().replace(/-|T|:/g, "").substring(0, 14)) + 20000;
    
    var seat_request_data = new FormData();
    seat_request_data.append('Idioma', '02');
    seat_request_data.append('idIdioma', 'CA');
    seat_request_data.append('Nivel', 'DetalleAforo');
    seat_request_data.append('idRecinto', 'FS4');
    seat_request_data.append('idEvento', 'SFF21_24');
    seat_request_data.append('IDsRecinto', '0;FS4');
    seat_request_data.append('IDSEvento', '0;SFF21_24');
    seat_request_data.append('conexiones', '0');
    seat_request_data.append('idTipoE', '251');
    seat_request_data.append('idSesion', sessionInfo['sessionId']);
    seat_request_data.append('Etiquetas', '0000000000199973;4941;104;1');
    seat_request_data.append('IdTerminalWeb', '9455');
    seat_request_data.append('seccion', '4');
    seat_request_data.append('instala', '_4TICK');
    seat_request_data.append('timeStamp', now);
    seat_request_data.append('NivelPrecios', '0');
    seat_request_data.append('IdAforoMatriz', '13077');
    seat_request_data.append('Idioma', '02');
    seat_request_data.append('UserSession', '1632999065.2949');
    
    var promise = fetch(proxy+url, {
        method: 'POST',
        body: seat_request_data,
        cache: 'no-cache'
    })
    .then(response => {
        if (!response.ok) {
            throw Error(response.statusText);
        }
        return response;
    })
    .then(response => response.text())
    .then(data => {
        try {
            var regex = /"Disponible" *: *"(\d+)"/g;
            var match = regex.exec(data);

            var seats = 0;
            while (match != null) {
                seats += parseInt(match[1]);
                match = regex.exec(data);
            }
            sessionInfo['libres'] = seats/2;

        } catch(e) {
            console.log('Something happened while retrieving seats!\n' + e)
            sessionInfo['libres'] = null;
        }
    })
    .catch(error => console.log("Error on getting seats page: " + error));
            
    return promise;
}

async function retrieveSessionsData(sessions) {
    
    var movie_list = [];
    movie_list.push({
        "date": "Loading...",
        "place": "-",
        "title": "-"
    });

    for (i = 0; i < sessions.length; i++) {
        
        var sessionInfo = sessions[i];
        if (sessionInfo) {
            if (sessionInfo['sessionId']) {
                await retrieveCapacity(sessionInfo);
                await retrieveSeats(sessionInfo)
            }
            movie_list.push(sessionInfo);
            $('#movie_table').bootstrapTable('hideLoading');
            $('#movie_table').bootstrapTable('load', movie_list);
        }
    }

    movie_list.pop();
    $('#movie_table').bootstrapTable('load', movie_list);
    sitges.date_info[day_coded] = movie_list;
    $('#dates').removeAttr('disabled');
    
    return movie_list;
}


function loadDaySessions(day) {

    if (day in sitges.date_info) {
        $('#movie_table').bootstrapTable('hideLoading');
        $('#movie_table').bootstrapTable('load', sitges.date_info[day]);

    } else if (day in sitges.sessions) {
        $('#dates').attr('disabled', 'disabled');
        $('#movie_table').bootstrapTable('showLoading');
        
        retrieveSessionsData(sitges.sessions[day]);
        
    } else {
        var msg = "Date not covered has been found: " + day;
        alert(msg);
        // console.log(msg)
    }
}

function parseRow(row) {

    var session = {};

    var cells = row.getElementsByTagName('td');
    if (cells.length) {
        var date = cells[1].textContent.replace(/\s+/g, " ").trim();
        var pieces = date.split(" ");
        var day = pieces[0];
        var hour = pieces[1];
        
        var day_pieces = day.split("-");
        var day_coded = parseInt(day_pieces[2] + day_pieces[1] + day_pieces[0]);
        
        var title = cells[2].textContent.replace(/\n\s+/g, "\n").trim();
        var info_url = cells[2].getElementsByTagName('a')[0].getAttribute('href');
        var place = cells[3].textContent.trim();
        var section = cells[4].textContent;
        var duration = cells[5].textContent.trim();
        
        var buy_url = null;
        var sessionId = null;
        var a_tags = cells[6].getElementsByTagName('a');
        if (a_tags.length) {     
            
            buy_url = a_tags[0].getAttribute('href');
            var pieces = buy_url.split("=");
            if (pieces.length > 1) {
                sessionId = pieces.slice(-1)[0];
            }
        }
        
        session['title'] = title;
        session['info_url'] = info_url;
        session['date'] = date;
        session['day'] = day;
        session['hour'] = hour;
        session['day_coded'] = day_coded;
        session['place'] = place;
        session['duration'] = duration;
        session['buy_url'] = buy_url;
        session['sessionId'] = sessionId;
    }
    
    return session;
}

function processSessionData(data) {
    
    var parser = new DOMParser();
    var htmlDoc = parser.parseFromString(data, "text/html");
    
    var table = htmlDoc.getElementById("program-table");
    
    var sessions = {};
    var rows = table.getElementsByTagName('tr');
    for (i = 0; i < rows.length; i++) {
        var sessionInfo = parseRow(rows[i]);
        
        day_coded = sessionInfo['day_coded'];
        if (!(day_coded in sessions)) {
            sessions[day_coded] = []
        }
        sessions[day_coded].push(sessionInfo);
    }
    
    return sessions;
}

function retrieveSessions(afterRetrievalCallback) {
    
    var proxy = "https://cors.bridged.cc/";
    var url = "https://sitgesfilmfestival.com/cat/programa";

    fetch(proxy+url, {
        type: 'GET',
        cache: 'no-cache'
    })
    .then(response => response.text())
    .then(data => {
            //alert("Ok!");
            //console.log(data);
            sitges.sessions = processSessionData(data);
            
            afterRetrievalCallback();
    })
    .catch(error => console.log("Error on getting program page: " + error));
}    

sitges = {};
sitges.sessions = {};
sitges.date_info = {};

$(function () {
    $('#movie_table').bootstrapTable('showLoading');

    retrieveSessions(function() {
        var date = new Date();
        var now = parseInt(date.toJSON().replace(/-|T|:/g, "").substring(0, 8));
        $('#dates')[0].value = now;
        loadDaySessions(now);        
    });

    $('#dates')[0].onchange = function() {
        loadDaySessions(this.value);
    };

});
