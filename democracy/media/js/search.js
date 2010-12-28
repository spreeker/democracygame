
$(function() {
    function log(message) {
        $("<div/>").text(message).prependTo("#log");
        $("#log").attr("scrollTop", 0);
    }

    var searchbox = $("#searchbox");

    if(searchbox.length){    
        searchbox.autocomplete({
            source: "/issue/xhr_search/",
            minLength: 2,
            select: function(event, ui) {
                log(ui.item ? ("Selected: " + ui.item.value + " aka " + ui.item.id) : "Nothing selected, input was " + this.value);
            }
        });
    };

    var search_user = $('#search_user');

    if(search_user.length){
        search_user.autocomplete({
            source: "/profile/xhr_search/",
            minLength: 2,
            select: function(event, ui) {
                log(ui.item ? ("Selected: " + ui.item.value + " aka " + ui.item.id) : "Nothing selected, input was " + this.value);
            }
        });
    };
});

