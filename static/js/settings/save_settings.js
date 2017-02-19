$(document).ready(function () {
    var url_base = $("meta[name='url_base']").attr("content");

    $("div#save").click(function(e){
        var change_check = false;
        if(verify_data() == false){
            return;
        }

        $this = $(this);
        $thisi = $this.children(":first");

        cat = $this.attr("cat");
        if(cat == "server"){
            data = server();
        } else if(cat == "search"){
            data = search();
        } else if(cat == "quality"){
            change_check = true;
            data = quality();
        } else if(cat == "providers"){
            data = providers();
        } else if(cat == "downloader"){
            data = downloader();
        }else if(cat == "postprocessing"){
            data = postprocessing();
        }else if(cat == "plugins"){
            data = plugins();
        }

        if(data == false){
            return
        }

        post_data = JSON.stringify(data);

        $thisi.removeClass("fa-save")
        $thisi.addClass("fa-circle faa-burst animated");

        $.post(url_base + "/ajax/save_settings", {
            "data": post_data
        })

        .done(function(r) {
            response = JSON.parse(r);
            if(response["response"] == true){
                toastr.success("Settings Saved");
            } else {
                toastr.error(response["error"]);
            }

            $thisi.removeClass("fa-circle faa-burst animated");
            $thisi.addClass("fa-save");
        });

        e.preventDefault();
    });



    function server(){
        var data = {};
        var server = {};
        server["Proxy"] = {};
        var blanks = false;
        $("ul#server i.checkbox").each(function(){
            $this = $(this);
            server[$this.attr("id")] = is_checked($this);
        });
        $("ul#server :input").each(function(){
            $this = $(this);
            if($this.attr("id") == "theme"){
            }
            else if($this.val() == ""){
                blanks = true;
                highlight($this);
            }

            if($this.attr("type") == "number"){
                server[$this.attr("id")] = parseInt($this.val());
            }
            else{
                server[$this.attr("id")] = $this.val();
            }
        });

        $("ul#interface i.checkbox").each(function(){
            $this = $(this);
            server[$this.attr("id")] = is_checked($this);
        });
        $("ul#interface :input").each(function(){
            $this = $(this);
            if($this.attr("id") == "theme"){
            }
            else if($this.val() == ""){
                blanks = true;
                highlight($this);
            }

            if($this.attr("type") == "number"){
                server[$this.attr("id")] = parseInt($this.val());
            }
            else{
                server[$this.attr("id")] = $this.val();
            }
        });

        $("ul#updates i.checkbox").each(function(){
            $this = $(this);
            server[$this.attr("id")] = is_checked($this);
        });
        $("ul#updates :input").each(function(){
            $this = $(this);
            if($this.attr("id") == "theme"){
            }
            else if($this.val() == ""){
                blanks = true;
                highlight($this);
            }

            if($this.attr("type") == "number"){
                server[$this.attr("id")] = parseInt($this.val());
            }
            else{
                server[$this.attr("id")] = $this.val();
            }
        });

        $("ul#proxy i.checkbox").each(function(){
            $this = $(this);
            server["Proxy"][$this.attr("id")] = is_checked($this);
        });
        $("ul#proxy :input").each(function(){
            $this = $(this);
            if($this.attr("id") == "type"){
                server["Proxy"]["type"] = $(this).val();
            }
            else if($this.attr("type") == "number"){
                server["Proxy"][$this.attr("id")] = parseInt($this.val());
            }
            else{
                server["Proxy"][$this.attr("id")] = $this.val();
            }
        });


        if(blanks == true){
            return false;
        };

        data["Server"] = server

        return data
    }

    function search(){
        var data = {};
        var search = {};
        var watchlists = {};
        var blanks = false;

        $("ul#search i.checkbox").each(function(){
            $this = $(this);
            search[$this.attr("id")] = is_checked($this);
        })
        $("ul#search :input").each(function(){
            $this = $(this);

            if($this.val() == "" && $this.attr("id") != "imdbrss"){
                blanks = true;
                highlight($this);
            }
            if($this.attr("type") == "number"){
                search[$this.attr("id")] = parseInt($this.val());
            }
            else{
                search[$this.attr("id")] = $this.val();
            }
        });

        data["Search"] = search;

        if(blanks == true){
            return false;
        };

        $("ul#watchlists i.checkbox").each(function(){
            $this = $(this);
            watchlists[$this.attr("id")] = is_checked($this);
        })
        $("ul#watchlists :input").each(function(){
            $this = $(this);
            if($this.attr("type") == "number"){
                watchlists[$this.attr("id")] = parseInt($this.val());
            }
            else{
                watchlists[$this.attr("id")] = $this.val();
            }
        });

        data["Search"]["Watchlists"] = watchlists

        return data
    }

    function quality(){
        var data = {};
        var profile = {};
        var blanks = false;
        var names = [];

        $("ul.quality_profile").each(function(){
            var $this = $(this);
            var tmp = {};
            var name = $this.find("li.name input.name").val();

            if(name === undefined){
                name = "Default"
            }

            if(name == "" || name === undefined){
                blanks = true;
                toastr.warning("Please enter a name for each profile.");
                return false;
            }

            if(names.includes(name)){
                blanks = true;
                toastr.warning("Please enter a unique name for each profile.");
                return false;
            }

            names.push(name);

            profile[name] = {};

            var q_list = [];
            $this.find("ul#resolution i.checkbox").each(function(){
                $_this = $(this);
                res = $_this.attr("id");
                enabled = is_checked($_this)
                profile[name][res] = [enabled];
            });

            // order of resolutions
            var arr = $this.find("ul#resolution").sortable("toArray");
            arr.shift();
            $.each(arr, function(value, res){
                profile[name][res].push(value)
            });

            // min/max sizes
            $this.find("#resolution_size :input").each(function(){
                $_this = $(this);
                if($_this.val() == ""){
                    blanks = true;
                    highlight($_this);
                }
                res = $_this.attr("id");
                size = parseInt($_this.val());
                profile[name][res].push(size);
            });

            // word lists
            $this.find("ul#filters li input").each(function(){
                $_this = $(this);
                id = $_this.attr("id");
                value = $_this.val();
                profile[name][id] = value;
            });

            $this.find("ul#toggles li i.checkbox").each(function(){
                profile[name][$(this).attr("id")] = is_checked($(this));
            });

        })

        if(blanks == true){
            return false;
        };

        $("ul#quality i.checkbox").each(function(){
            $this = $(this)
            profile[name][$this.attr("id")] = is_checked($this);
        })


        data["Quality"] = {}
        data["Quality"]["Profiles"] = {}
        data["Quality"]["Profiles"] = profile

        return data;
    }

    function providers(){
        var data = {};
        data["Indexers"] = {};
        var ind = 1;
        var cancel = false;

        newznab_indexers = {};
        $("#newznab_list li").each(function(){
            $this = $(this);
            if ($this.attr("class") == "newznab_indexer"){
                var check = is_checked($this.children("i.newznab_check"));
                var url = $this.children("input.newznab_url").val();
                var api = $this.children("input.newznab_api").val();

                // check if one field is blank and both are not blank
                if ( (url == "" || api == "") && (url + api !=="") ){
                    toastr.warning("Please complete or clear out incomplete providers.");
                    newznab_indexers = {}
                    cancel = true;
                }
                // but ignore it if both are blank
                else if (url + api !=="") {
                    newznab_indexers[ind] = [url, api, check];
                    ind++;
                }
            }
        });
        data["Indexers"]["NewzNab"] = newznab_indexers;

        potato_indexers = {};
        ind = 1;
        $("#potato_list li").each(function(){
            $this = $(this);
            if ($this.attr("class") == "potato_indexer"){
                var check = is_checked($this.children("i.potato_check"));
                var url = $this.children("input.potato_url").val();
                var api = $this.children("input.potato_api").val();

                // check if one field is blank and both are not blank
                if ( (url == "" || api == "") && (url + api !=="") ){
                    toastr.warning("Please complete or clear out incomplete providers.");
                    potato_indexers = {}
                    cancel = true;
                }

                // but ignore it if both are blank
                else if (url + api !=="") {
                    potato_indexers[ind] = [url, api, check]
                    ind++;
                }
            }
        });

        data["Indexers"]["TorrentPotato"] = potato_indexers;

        torrent_indexers = {}
        $("#torrentindexer_list li").each(function(){
            $this = $(this);
            if ($this.attr("class") == "torrent_indexer"){
                name = $this.attr("id");
                check = is_checked($this.children("i.torrent_check"));
                torrent_indexers[name] = check;
            }
        });
        data["Indexers"]["Torrent"] = torrent_indexers;

        if(cancel == true){
            return false;
        } else {
            return data
        };
    }

    function downloader(){
        var data = {};
        data["Downloader"] = {"Torrent": {}, "Usenet": {}};


        var sources = {};
        sources["usenetenabled"] = is_checked($("i#usenetenabled"));
        sources["torrentenabled"] = is_checked($("i#torrentenabled"));
        data["Downloader"]["Sources"] = sources;

        var sabnzbd = {};
        sabnzbd["enabled"] = is_checked($("i#sabenabled"));
        $("ul#sabnzbd li input").each(function(){
            sabnzbd[$(this).attr("id")] = $(this).val();
        });
        $("ul#sabnzbd li select").each(function(){
            sabnzbd[$(this).attr("id")] = $(this).val();
        });
        data["Downloader"]["Usenet"]["Sabnzbd"] = sabnzbd;

        var nzbget = {};
        nzbget["enabled"] = is_checked($("i#nzbgetenabled"));
        $("ul#nzbget li i.checkbox").each(function(){
            $this = $(this)
            nzbget[$this.attr("id")] = is_checked($this);
        });
        $("ul#nzbget li input").not("[type=button]").each(function(){
            nzbget[$(this).attr("id")] = $(this).val();
        });
        $("ul#nzbget li select").each(function(){
            nzbget[$(this).attr("id")] = $(this).val()
        });
        data["Downloader"]["Usenet"]["NzbGet"] = nzbget;

        var transmission = {};
        transmission["enabled"] = is_checked($("i#transmissionenabled"));
        $("ul#transmission li i.checkbox").each(function(){
            $this = $(this)
            transmission[$this.attr("id")] = is_checked($this);
        });
        $("ul#transmission li input").not("[type=button]").each(function(){
            transmission[$(this).attr("id")] = $(this).val();
        });
        $("ul#transmission li select").each(function(){
            transmission[$(this).attr("id")] = $(this).val()
        });
        data["Downloader"]["Torrent"]["Transmission"] = transmission;

        var delugerpc = {};
        delugerpc["enabled"] = is_checked($("i#delugerpcenabled"));
        $("ul#delugerpc li i.checkbox").each(function(){
            $this = $(this);
            delugerpc[$this.attr("id")] = is_checked($this);
        });
        $("ul#delugerpc li input").not("[type=button]").each(function(){
            delugerpc[$(this).attr("id")] = $(this).val();
        });
        $("ul#delugerpc li select").each(function(){
            delugerpc[$(this).attr("id")] = $(this).val()
        });
        data["Downloader"]["Torrent"]["DelugeRPC"] = delugerpc;

        var delugeweb = {};
        delugeweb["enabled"] = is_checked($("i#delugewebenabled"));
        $("ul#delugeweb li i.checkbox").each(function(){
            $this = $(this);
            delugeweb[$this.attr("id")] = is_checked($this);
        });
        $("ul#delugeweb li input").not("[type=button]").each(function(){
            delugeweb[$(this).attr("id")] = $(this).val();
        });
        $("ul#delugeweb li select").each(function(){
            delugeweb[$(this).attr("id")] = $(this).val()
        });
        data["Downloader"]["Torrent"]["DelugeWeb"] = delugeweb;

        var qbittorrent = {};
        qbittorrent["enabled"] = is_checked($("i#qbittorrentenabled"));
        $("ul#qbittorrent li i.checkbox").each(function(){
            $this = $(this);
            qbittorrent[$this.attr("id")] = is_checked($this);
        });
        $("ul#qbittorrent li input").not("[type=button]").each(function(){
            qbittorrent[$(this).attr("id")] = $(this).val();
        });
        $("ul#qbittorrent li select").each(function(){
            qbittorrent[$(this).attr("id")] = $(this).val()
        });
        data["Downloader"]["Torrent"]["QBittorrent"] = qbittorrent;

        return data
    }

    function postprocessing(){
        var data = {};
        var postprocessing = {};
        postprocessing['RemoteMapping'] = {};

        $("ul#postprocessing li i.checkbox").each(function(){
            $this = $(this);
            postprocessing[$this.attr("id")] = is_checked($this);
        });
        $("ul#postprocessing li input").not("[type=button]").each(function(){
            $this = $(this);
            if($this.attr("id") == "moveextensions"){
                postprocessing["moveextensions"] = $this.val().split(", ").join(",");
            } else {
            postprocessing[$this.attr("id")] = $this.val();
            }
        });

        $("ul#remote_mapping li.remote_mapping_row").each(function(){
            $this = $(this);
            local = $this.find("input.local_path").val();
            remote = $this.find("input.remote_path").val();

            // check if one field is blank and both are not blank
            if ( (local == "" || remote == "") && (local + remote !=="") ){
                toastr.warning("Please complete or clear out incomplete remote mappings.");
            }
            // but ignore it if both are blank
            else if (local + remote !=="") {
                postprocessing['RemoteMapping'][remote] = local;
            }
        })

        data["Postprocessing"] = postprocessing;

        return data
    }

    function plugins(){
        var data = {};
        var plugins = {};

        var added = {};
        var arr = $("ul#added").sortable("toArray");
        var order = 0
        $.each(arr, function(index, value){
            $li = $("li#" + value);
            plugin = $li.attr("plugin");
            enabled = is_checked($li.find("i.checkbox"));
            if(is_checked($li.find("i.checkbox"))){
                added[plugin] = [enabled, order];
                order++;
            }
        })
        plugins["added"] = added

        var snatched = {};
        var arr = $("ul#snatched").sortable("toArray");
        var order = 0
        $.each(arr, function(index, value){
            $li = $("li#" + value);
            plugin = $li.attr("plugin");
            if(is_checked($li.find("i.checkbox"))){
                snatched[plugin] = [true, order];
                order++;
            }
        })
        plugins["snatched"] = snatched

        var finished = {};
        var arr = $("ul#finished").sortable("toArray");
        var order = 0;
        $.each(arr, function(index, value){
            $li = $("li#" + value);
            plugin = $li.attr("plugin");
            enabled = is_checked($li.find("i.checkbox"));
            if(is_checked($li.find("i.checkbox"))){
                finished[plugin] = [enabled, order];
                order++;
            }
        })
        plugins["finished"] = finished

        data["Plugins"] = plugins;

        return data
    }

    function is_checked(checkbox){
        // Turns value of checkbox "True"/"False" into js bool
        // checkbox: object jquery object of checkbox <i>
        return (checkbox.attr("value") == "True")
    }

    function verify_data(){
        // checks if only one downloader is active
        // Returns bool
        var enabled = 0
        $("ul#downloader > li > i.checkbox").each(function(){
            if(is_checked($(this))){
                enabled++;
            }
        });

        if(enabled > 1){
            toastr.warning("Please enable only one downloader.")
            return false
        }
        return true
    }

    function highlight(element){
        // Highlights empty or invalid inputs
        // element: object JQ object of input to highlight
        orig_bg = element.css("background-color");
        element.css("background-color", "#f4693b");
        element.delay(500).animate({"background-color": orig_bg}, 1000);
    }

});
