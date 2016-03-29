$(function() {
    $( ".datepicker" ).datepicker();
    $( ".timepicker" ).timepicker();
});

function submitted(event) {
    event.preventDefault();
    alert("The form was submitted");
}