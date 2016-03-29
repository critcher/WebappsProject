    $(document).ready(function() {
        $('#calendar').fullCalendar({
            header: {
                left: 'prev,next today',
                center: 'title',
                right: 'month,agendaWeek,agendaDay'
            },
            editable: false,
            eventLimit: true, // allow "more" link when too many events
            eventSources: [
                {
                    url: {% url 'json_events' %},
                    color: 'white',
                    textColor: 'black'
                }
            ],
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