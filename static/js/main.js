$(document).ready(function() {
    $(window).scroll(function() {
        if ($(this).scrollTop() > 50) {  // Si se desplaza más de 50px
            $('.navbar').addClass('scrolled');
        } else {
            $('.navbar').removeClass('scrolled');
        }
    });
});

