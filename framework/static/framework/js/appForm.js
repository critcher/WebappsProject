// Get the json for all of the forms
formUrls.map(function(setting) {
    var jqxhr = $.getJSON( setting['url']);

    jqxhr.done(function(data) {
        var jqxhr2 = $.post( json2form, {"id": setting['id'], "data":JSON.stringify(data), 'csrfmiddlewaretoken': csrf});
        jqxhr2.done(function(data){
            var domElement = $("#App" + setting['id']);
            domElement.html(data);
            domElement.find("script").each(function(i) {
                    eval($(this).text());
            });
        });
        
    });
});

function submitted(event) {
    event.preventDefault();
    var form = $(event.target);
    $.post(form.attr('action'), form.serialize(), function(data, status){
        alert(JSON.stringify(data));
    });
}



