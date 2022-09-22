function ToCart(id) {
    $.post( "/change-count-in-basket", {
        canvas_data: JSON.stringify({prod_id: id, count: 1})
    }, function(err, req, resp){
        ans = $.parseJSON(resp.responseText)
        console.log(ans);
        progress_bar(ans);
        // count_in_basket(ans['total_count'])
        // update_slider(id, ans[id]['count'], ans[id]['cost'], ans[id]['saving'])
        // update_total(ans['total_count'], ans["total_cost"], ans['total_saving'])
        // set_button_state(id, true)
    });
}

function progress_bar (ans) {
    let elem = document.getElementById('progress__line_' + ans.prod_id),
        width = 0,
        max = ans["max"],
        id = setInterval(progressStatus, 1);
        function progressStatus() {
            if (width >= 100 * ans.max / ans.current) {
                clearInterval(id);
            } else {
                width = width + 0.5;
                elem.style.width = width + '%';
                elem.innerHTML = width * 1 + '%';
            }
        }
}