function submitRegisterForm(el) {
    event.preventDefault();

    var data = $(el).serialize();
    var url = '/register';

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
                $('#registerForm input').each(
                    function (index) {
                        $(this).val('')
                    }
                );
                alert(data.error_message)
            }
        }
    });
}