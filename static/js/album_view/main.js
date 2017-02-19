$(document).ready(function(){


    $('i.view_details').click(function(){
        $this = $(this);
        $details = $(this).parent().parent().siblings('div.details');
        if($this.hasClass('open')){
            $details.slideUp();
            $this.removeClass('open');
            $this.removeClass('fa-chevron-circle-up')
            $this.addClass('fa-chevron-circle-down')
        } else {
            $details.slideDown();
            $this.addClass('open');
            $this.addClass('fa-chevron-circle-up')
            $this.removeClass('fa-chevron-circle-down')

        }


    });

    $('i.media_preview').click(function(){
        $this = $(this);
        audio = $this.siblings('audio')[0];

        if($this.hasClass('fa-play')){
            $audios = $('audio').each(function(i, elem){
                elem.pause();
                elem.currentTime = 0;
            });

            $('i.media_preview').removeClass('fa-stop').addClass('fa-play');

            $this.removeClass('fa-play');
            $this.addClass('fa-stop');
            audio.play();
            audio.addEventListener('ended', function(){
                $this.removeClass('fa-stop');
                $this.addClass('fa-play');
            });
        } else {
            $this.removeClass('fa-stop');
            $this.addClass('fa-play');
            audio.pause();
            audio.currentTime = 0;
        }


    })





});
