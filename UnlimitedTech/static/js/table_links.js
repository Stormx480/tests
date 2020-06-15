function createLinkSubmit(el) {
    event.preventDefault();

    var data = $(el).serialize();
    var url = '/create_link';

    $.ajax({
        type: "post",
        url: url,
        data: data,
        async: true,
        dataType: "json",
        success: function(data) {
            if (data.redirect) {
                window.location.href = data.redirect_url;
            } else {
                $('#createLinkForm input').each(
                    function (index) {
                        $(this).val('')
                    }
                );
                alert(data.message_error)
            }
        }
    });
}

function deleteLink(el) {
    $.ajax({
        type: "POST",
        url: '/delete_link?id='+$(el).attr('data-id'),
        async: true,
        dataType: "json",
        success: function(data) {
            if (data.redirect) {
                window.location.href = data.redirect_url;
            } else {
                alert(data.message_error)
            }
        }
    });
}

function downloadAllLinks() {
    $('.download-link').each(function (i) {
        window.open($(this).attr('href'), '_blank');
    })
}