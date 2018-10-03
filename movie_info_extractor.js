

function processMovieData() {
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
