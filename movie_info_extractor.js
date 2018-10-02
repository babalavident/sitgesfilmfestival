

function extractData() {
    var url = "http://sitgesfilmfestival.com/cat/programa";
    
    $.ajax({
            type: 'GET',
            url: url,
            crossDomain: true,
            success: function (data, textStatus, jqXHR) {
                alert("Ok!");

                $('#movie_table').bootstrapTable({
                    data: extractData()
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

});
