$(document).ready(function() {
    var eventSources = [];
    for(var k in sources) {
        eventSources.push(sources[k]);
    }

    $('#calendar').fullCalendar({
        customButtons: {
            addEventButton: {
                click: function() {
                    window.open("https://calendar.google.com/calendar/render?action=template");
                },
                text: "+"
            }
        },
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay,addEventButton'
        },
        editable: false,
        eventLimit: true, // allow "more" link when too many events
        eventSources: eventSources,
        eventClick: function(event) {
            if (event.url) {
                window.open(event.url);
                return false;
            }
        },
        eventRender: function(event, element) {
          $(element).tooltip({title: event.title});
        },
        allDayDefault: false
    });
});