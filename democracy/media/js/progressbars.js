
function create_bar(id, text){
    //add div with id bar and div with id_text after votebars.
    bar_id = "#"+id+"_bar";
    text_id = "#"+id+"_text";
    var bar = $(bar_id);
    //create tagbar diff if it not exists already.
    if(!bar.length){
        var bar = $("<div id='"+id+"_bar'></div>");
        var bar_text = $("<div id='"+text_id+"'>"+text+" <span id='"+id+"value'></span></div>");
        $('#votebar').after(bar_text);
        $(bar_text).after(bar);
        bar.progressbar({ value: 1 });
        return bar_text
    };
};

function create_vote_bar(){
    var userdata = localStorage.getItem('user'); 
    var total_votes = null;
    var total_issues = null;

    if(userdata){
        userdata = $.parseJSON(userdata);
        total_votes = userdata.votes.length;
        total_issues = localStorage.getItem('total_issues');
    };

    if(total_votes == null){
        total_votes = $('#total_votes').text();
        localStorage.setItem('total_votes', total_votes);
    };
    if(total_issues == null){
        total_issues = $('#total_issues').text();
        localStorage.setItem('total_issues', total_issues);
    };

    var progress = total_votes / total_issues * 100.0;
    progress = Math.round(progress);

    $("#votebar").progressbar("value", progress);
    $("#votebar_value").text(progress + "%");

};

function update_bar(id, issue_ids){

    var userdata = localStorage.getItem('user'); 
    userdata = $.parseJSON(userdata);
    votes = userdata.votes;

    var match = 0;
    $.each(issue_ids, function(index, issue_id){
        direction = votes[issue_id];
        if(direction != undefined){ match += 1; };
    });
    progress = Math.round( (match / issue_ids.length ) * 100 );
    $("#"+id+"_bar").progressbar("value", progress );
    $("#"+id+"value").text(progress + "%");
    return progress;

};

function create_tag_bar(){
    var tag = $("#tags").find('a.notice');

    if(!tag.length){ return };
    tag = $("font", tag).text();
    var tag_bar = $('#tag_bar');
    //create tagbar diff if it not exists already.
    if(!tag_bar.length){
        create_bar('tag', tag);
    };
    // get ids of tag.
    var votes;
    var issue_ids;
    
    // now check if we have the needed id's.
    var collect_data = function(){
        var tagdata = localStorage.getItem('tag_'+tag);
        tagdata = $.parseJSON(tagdata);
        tag_key = 'tag_'+tag;
        issue_ids = tagdata[tag_key]; 
        //console.log('draw?');
        if(issue_ids.length){
            //console.log('we are going to draw!');
            update_bar('tag', issue_ids);
        };
    }
    // get isue ids of tag data.
    get_key_data('tag_' + tag, collect_data);
    // get ids of user votes.

};

function create_follow_bar(){
    //TODO here the code should come to see progress on who you follow.
};

function create_party_bar(){
    //code to follow party programs progres
    //get parties.
    //get data for parties.
    //create bars for parties.
    
    var draw_party_bars = function(){
        var partydata = localStorage.getItem('parties');
        partydata = $.parseJSON(partydata);
         
        $.each(partydata.names, function(index, name){
            var text = "<a href='/issue/by/"+name+"'>"+name+"</a>"
            var bar_text = create_bar(name, text);
            var progress = update_bar(name, partydata[name]); 
            //if(progress == 100){
                //var url = "/profile/compare_votes_to_user/"+name;
                //var link = $("a", bar_text);
                //link.attr('href', url);
            //}
        });

    };

    get_key_data('parties', draw_party_bars)

};
//does not work..yet
var error_load_key = function(xhr, textStatus, error){
    console.log(textStatus);
    p = $('p').text('Oops something went wrong' + error);
    $('#messagebar').append(p);
}


function get_key_data(key, callback){
    //genric method to get key value information from local storage
    //with fall back to server. caching results default local for 1 hour.
    //should reload anonymous data on login.
    var key_data = localStorage.getItem(key);
    var key_data_date = localStorage.getItem(key+'date');
    var key_user_id = localStorage.getItem(key+'user');

    var callback = callback;
    var cachetime = 3600000; //1 hour.
    var cachetime = 360000; //6 min.

    var now = new Date()
    now = now.getTime();

    var delta = now - key_data_date;
    //console.log('delta')
    //console.log(delta);
    //console.log(key_data_date);

    var user_id =  $('#username');
    if(user_id.length){
        username = user_id.text();
    } else {
        username = 'anonymous';
    };
    //console.log(username);
    //console.log(key_user_id);
    // now check if user_id is still key_user_id.
    if(key_user_id != username){
        //user change since last time.
        delta = cachetime+10; 
        //forcing cache reload.
    }; 
    

    if((delta < cachetime )){
            //less then 1 hour old.
            if(callback){callback();};
    } else {
        var data = {};
        var setKeyData = function(xhr, textStatus){
            localStorage.setItem(key, xhr.responseText); 
            localStorage.setItem(key+'date', now);
            localStorage.setItem(key+'user', username);
            if(callback){callback();};
        };
        //get data from the server.
        $.ajax({
            type : "GET",
            data : {'key' : key },
            url : '/game/data/',
            dataType : "json",
            complete : setKeyData,
        });
    }
}

var update_progressbars = function(){
    $("#votebar").progressbar({ value: 1 });
    create_vote_bar();
    create_party_bar();
    create_tag_bar();
}

$(function(){
    get_key_data('user', update_progressbars());
});
