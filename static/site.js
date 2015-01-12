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

    // Send comments via AJAX when submit is pressed
    $('button[data-async="true"]').click(function(e){
        e.preventDefault();
        var self = $(this),
        url = self.data('url'),
        target = self.data('target'),
        cache = self.data('cache'),
        key = self.data('key'),
        source = self.data('source');

        if (source !== 'undefined'){
            payload = $('#' + source).val();
        }
        else {
            payload = ''
        }

        $.ajax({
            url: url,
            cache : cache,
            data: '{"' + key + '": "' + payload + '"}',
            type: 'POST',
            success: function(data){
                if (target !== 'undefined'){
                    // alert(data);
                    $('#'+target).replaceWith( data );
                }
            }
        });
    });

    // http://bootsnipp.com/snippets/featured/google-plus-styled-post
    $('.panel-google-plus > .panel-footer > .input-placeholder, .panel-google-plus > .panel-google-plus-comment > .panel-google-plus-textarea > button[type="reset"]').on('click', function(event) {
        var $panel = $(this).closest('.panel-google-plus');
        $comment = $panel.find('.panel-google-plus-comment');

        $comment.find('.btn:first-child').addClass('disabled');
        $comment.find('textarea').val('');

        $panel.toggleClass('panel-google-plus-show-comment');

        if ($panel.hasClass('panel-google-plus-show-comment')) {
            $comment.find('textarea').focus();
        }
    });
    $('.panel-google-plus-comment > .panel-google-plus-textarea > textarea').on('keyup', function(event) {
        var $comment = $(this).closest('.panel-google-plus-comment');

        $comment.find('button[type="submit"]').addClass('disabled');
        if ($(this).val().length >= 1) {
            $comment.find('button[type="submit"]').removeClass('disabled');
        }
    });
});
