function toggleAppDisplay(id){
    var on = true;
    return function() {
        if (on) {
            $("#calendar").fullCalendar('removeEventSource', sources[id]);
        } else {
            $("#calendar").fullCalendar('addEventSource', sources[id]);
        }
        on = !on;
        return true;
    }
};