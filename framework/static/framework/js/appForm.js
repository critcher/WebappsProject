

$(function() {
    $( ".datepicker" ).datepicker();
    $( ".timepicker" ).timepicker();
});

function submitted(event) {
    event.preventDefault();
    var form = $(event.target);
    $.post(form.attr('action'), form.serialize(), function(data, status){
        alert(JSON.stringify(data));
    });
}



