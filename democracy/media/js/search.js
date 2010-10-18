
$(function() {
    function log(message) {
        $("<div/>").text(message).prependTo("#log");
        $("#log").attr("scrollTop", 0);
    }
    
    $("#searchbox").autocomplete({
        source: "/issue/xhr_search/",
        minLength: 2,
        select: function(event, ui) {
            log(ui.item ? ("Selected: " + ui.item.value + " aka " + ui.item.id) : "Nothing selected, input was " + this.value);
        }
    });
    $("#search_user").autocomplete({
        source: "/profile/xhr_search/",
        minLength: 2,
        select: function(event, ui) {
            log(ui.item ? ("Selected: " + ui.item.value + " aka " + ui.item.id) : "Nothing selected, input was " + this.value);
        }
    });

});

