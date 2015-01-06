$(function () {
    $('.navbar-toggle').click(function () {
        $('.navbar-nav').toggleClass('slide-in');
        $('.side-body').toggleClass('body-slide-in');
        $('#search').removeClass('in').addClass('collapse').slideUp(200);

        /// uncomment code for absolute positioning tweek see top comment in css
        //$('.absolute-wrapper').toggleClass('slide-in');

    });

    // Remove menu for searching
    $('#search-trigger').click(function () {
        $('.navbar-nav').removeClass('slide-in');
        $('.side-body').removeClass('body-slide-in');

        /// uncomment code for absolute positioning tweek see top comment in css
        //$('.absolute-wrapper').removeClass('slide-in');

    });

    // For links with data-async, send these requests via AJAX
    $('a[data-async="true"]').click(function(e){
        e.preventDefault();
        var self = $(this),
        url = self.data('url'),
        target = self.data('target'),
        cache = self.data('cache');

        $.ajax({
            url: url,
            cache : cache,
            type: 'POST',
            success: function(data){
                if (target !== 'undefined'){
                    // alert(data);
                    $('#'+target).replaceWith( data );
                }
            }
        });
    });

    // Send comments via AJAX when enter is pressed
    $('input[data-async="true"]').keydown(function(e){
        if(e.keyCode == 13){
            e.preventDefault();
            var self = $(this),
            url = self.data('url'),
            target = self.data('target'),
            cache = self.data('cache')
            key = self.data('key');

            $.ajax({
                url: url,
                cache : cache,
                data: '{"' + key + '": "' + $(this).val() + '"}',
                type: 'POST',
                success: function(data){
                    if (target !== 'undefined'){
                        // alert(data);
                        $('#'+target).replaceWith( data );
                    }
                }
            });
        }
    });
});
