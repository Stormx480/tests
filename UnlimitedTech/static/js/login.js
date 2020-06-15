function submitLoginForm(el) {
    event.preventDefault();

    var data = $(el).serialize();
    var url = '/login';

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
                $('#loginForm input').each(
                    function (index) {
                        $(this).val('')
                    }
                );
                alert(data.message_error)
            }
        }
    });
}