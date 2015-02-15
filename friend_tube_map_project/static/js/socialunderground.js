function getStatusMessage() {
    $.ajax({
        url: '/frontpage/status/',
        dataType: 'html',
        success: function(data) {
            $('#status').html(data);
        },
        complete: function() {
            window.setTimeout(getStatusMessage, 500);
        }
    });
}