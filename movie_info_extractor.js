

function parseRow(row) {
    
        cells = row.evaluate('td', row, null, XPathResult.ANY_TYPE, null);
        
        date = re.sub("\s+", " ", cells[1].textContent);//.strip()
        /*
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
        */
        session = {}
        /*
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
        */
        return session;
}

function processMovieData(data) {
    var table = data.evaluate('//*[@id="program-table"]', data, null, XPathResult.ANY_TYPE, null);
    
    var rows = data.evaluate('tbody/tr', table, null, XPathResult.ANY_TYPE, null);
    var row = rows.iterateNext();
    while (row) {
        parseRow(row);
        row = rows.iterateNext();
    }
    return [];
}

function extractData() {
    var proxy = "https://cors-anywhere.herokuapp.com/";
    var url = "http://sitgesfilmfestival.com/cat/programa";
    
    $.ajax({
            type: 'GET',
            url: proxy + url,
            crossDomain: true,
            success: function (data, textStatus, jqXHR) {
                alert("Ok!");
                console.log(data);

                $('#movie_table').bootstrapTable({
                    data: processMovieData(data)
                });
            },
            error: function (jqXHR, textStatus, errorThrown) {
                alert("Wait, take a look: " + textStatus + ", " + errorThrown);
            },
            complete: function (jqXHR, textStatus ) {
                alert("Status: " + textStatus);
            }
        });
}

$(function () {
    extractData();
});
