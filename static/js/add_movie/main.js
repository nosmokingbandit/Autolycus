$(document).ready(function() {
    var url_base = $("meta[name='url_base']").attr("content");

    $("#search_input").keyup(function(event){
        if(event.keyCode == 13){
            $("#search_button").click();
        }
    });

    // Sends request to search ajax handler
    $("#search_button").click(function(e) {
        var movie_results_dict = {};
        if ( $("input[name='search_term']").val() == "" ){
            return false;
        }

        // if it is open, hide it first. makes it pretty
        if ( $("#database_results").css("display") == "block" ){
            $("#database_results").hide();
            $("#artist_list").empty();
        }

        $('#thinker').fadeIn();

        $.post(url_base + "/ajax/search_itunes", {
            "search_term": $("input[name='search_term']").val()
        })

        .done(function(r) {
            if (r != ''){
                results = JSON.parse(r);

                var $artist_list = $("#artist_list")
                // move this to a py template or just have the post function return the html ?
                $.each(results, function(ind, dict){
                    if(dict['image'] != null){
                        img_url = dict['image']
                    } else {
                        img_url = url_base + "/static/images/blank_artist.jpg"
                    }
                    data = JSON.stringify(dict);
                    li = `<li class='artist'>
                            <img src='${img_url}' alt='${dict['artistName']}'/>
                            <ul class='artist_info'>
                                <li class='artist_name'>
                                    ${dict['artistName']}
                                </li>
                                <li class='artist_genre'>
                                    ${dict['primaryGenreName']}
                                </li>
                                <li>
                                    <a href='${dict['artistLinkUrl']}' target='_blank'>
                                        <i class='fa fa-music'/>
                                        View on iTunes
                                    </a>
                                </li>
                                <li class='add_artist' data=${data}>
                                    <i class='fa fa-plus-square'/>
                                    Add Artist to Library
                                </li>
                            </ul>
                        </li>`

                    $li = $(li);
                    $li.find("li.add_artist").attr("data", data);

                    $artist_list.append($li);
                });
            }

            $("#database_results").fadeIn();
            $('#thinker').fadeOut();
        });

        e.preventDefault();
    });


    $("div#database_results").on("click", "li.add_artist", function(){
        $this = $(this)

        data = $this.attr('data');

        $.post(url_base+"/ajax/add_artist", {'data':data})
        .done(function(r){
            response = JSON.parse(r);

            if(response['response'] == true){
                toastr.success(response['message']);
            } else {
                toastr.success(response['error']);

            }
        });

    });

});
