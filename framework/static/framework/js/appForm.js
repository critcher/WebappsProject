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

function submitted(event, id, url) {
    event.preventDefault();
    var form = $(event.target);
    $.post(form.attr('action'), form.serialize() + "&id=" + id, function(extracted_data){
        $.ajax({
            url: url,
            type: "POST",
            data: JSON.stringify(extracted_data),
            dataType: 'json',
            crossDomain: true,
            success: 
            function(cleaned_data) {
                $.ajax({
                    url: saveSettingsUrl,
                    type: "POST",
                    data: {"settings": JSON.stringify(cleaned_data),
                           "id": id,
                           "csrfmiddlewaretoken": csrf},
                    success: 
                    function(errors) {
                        var panelStr = "#panel" + id;
                        $(panelStr + " .error").html("");
                        clr = $(panelStr+ " .colorpicker").val();
                        if (clr !== "") {
                            $(panelStr).css('background-color', clr);
                        }
                        for (var field in errors) {
                            if (errors.hasOwnProperty(field)) {
                                if (field === "error") {
                                    $(panelStr+ " #form_errors").html(errors[field]);
                                } else {
                                    $(panelStr+ " #" + field + "_error").html(errors[field]);
                                }
                            }
                        }
                    }
                });
            }
        });
    });
}



