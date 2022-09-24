function search() {
    var req = new Array();
    var text = document.getElementById('searchText').value.split(" ").forEach(element => (element != '' ? req.push(element) : null));
    if (req.length) {
        window.location.replace("/catalog/request/" + req.join("||"));
    }

//    window.location.replace("/");
//    $.post( "/search-products", {
//        canvas_data: JSON.stringify({text: document.getElementById('searchText').value})
//    }, function(err, req, resp){
//        orders = $.parseJSON(resp.responseText);
//    });
}