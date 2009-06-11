var debug = true;
$(document).ready(function(){
  
    $("div.issue").each(function(){
        //var vote_form = $('form', this);
        var my_vote = parseInt($("#my_vote", this).val());
        var my_issue = parseInt($("#my_vote_issue", this).val());
        var my_privacy = parseInt($("#my_vote_privacy", this).val());

        render_bars(my_issue, my_vote);

        $("td.for", this).mouseup(function(){
            process_vote(my_issue, 1);
        });
        $("td.abstain", this).mouseup(function(){
            process_vote(my_issue, 17);
        });
        $("td.against", this).mouseup(function(){
            process_vote(my_issue, -1);
        });
    });
    // hide all issue bodies
    $("div.body").each(function() {
	    $(this).hide();
    });
    //hook the mouseup events to each title
    $("div.issue").children("div.title").mouseup(function(){
    
        //find the body whose title was clicked
        var body = $(this).parent().children("div.body");

        //slide the panel
        body.slideToggle();
    });
});

function process_vote(issue, new_vote) {
    var old_vote = parseInt($("#issue"+issue).find("#my_vote").val());
    if(old_vote == new_vote) {
        return
    }
    if(old_vote!=new_vote) {
        $.post('/ajax/vote/cast/', {
            issue : issue,
            vote : new_vote,
            keep_private : false
        }, function(data) {
            if(data.status=="success"){
            // fix layouts here
                $("#issue"+issue).find("#my_vote").html(""+new_vote);
                render_bars(issue, new_vote);
            } else if(data.status=="debug") {
                if(debug) {
                    alert(data.error);
                }
            } else {
                handle_errors(data.error);
            }
        }, "json");
    }
}

function render_bars(issue, new_vote){
    var old_vote = parseInt($("#issue"+issue).find("#my_vote").val());
    // reset the bar colors to their unvoted colors
    $("#issue"+issue).find("td.for").css({'background-color' : '#a1f2a3'});
    $("#issue"+issue).find("td.abstain").css({'background-color' : '#9ef8fb'});
    $("#issue"+issue).find("td.against").css({'background-color' : '#f99f9b'});
    if(new_vote==null) {
    // first page render, set voted color, if any
        if(old_vote ==1) {
            $("#issue"+issue).find("td.for").css({'background-color' : '#49f24d'});
        }
        if(old_vote >=10) {
            $("#issue"+issue).find("td.abstain").css({'background-color' : '#4cf5fb'});
        }
        if(old_vote ==-1) {
            $("#issue"+issue).find("td.against").css({'background-color' : '#f9645e'});
        }
    }
    // get vote totals
    var vfor = parseInt($("#issue"+issue).find("td.for > a").html());
    var vabs = parseInt($("#issue"+issue).find("td.abstain > a").html());
    var vaga = parseInt($("#issue"+issue).find("td.against > a").html());
    // update vote totals, subtract from old vote totals and reset colors.
    if(new_vote == 1) {
        $("#issue"+issue).find("td.for").css({'background-color' : '#49f24d'});
        vfor += 1;
        if(old_vote >=10) {
            vabs -= 1;
        }
        if(old_vote ==-1) {
            vaga -= 1;
        }
    }
    if(new_vote >= 10) {
        $("#issue"+issue).find("td.abstain").css({'background-color' : '#4cf5fb'});
        vabs += 1;
        if(old_vote ==1) {
            vfor -= 1;
        }
        if(old_vote ==-1) {
            vaga -= 1;
        }
    }
    if(new_vote == -1) {
        $("#issue"+issue).find("td.against").css({'background-color' : '#f9645e'});
        vaga += 1;
        if(old_vote ==1) {
            vfor -= 1;
        }
        if(old_vote >=10) {
            vabs -= 1;
        }
    }
    $("#issue"+issue).find("td.for").find("a").html(""+vfor);
    $("#issue"+issue).find("td.abstain").find("a").html(""+vabs);
    $("#issue"+issue).find("td.against").find("a").html(""+vaga);
    $("#issue"+issue).find("#my_vote").val(new_vote);
    var total = vfor + vabs + vaga;
    var per = new Array();
    per['for'] = vfor / total;
    per['abs'] = vabs / total;
    per['aga'] = vaga / total;
    var biggest = "none";
    var big = 0;
    for (var i in per) {
        if(per[i] > big) {
            big = per[i];
            biggest = i;
        }
    }
    for (var i in per) {
        if(per[i] < 0.1) {
            per[biggest] -= (0.1 - per[i]);
            per[i] = 0.1;
        }
    }
    for (var i in per) {
        per[i] = per[i]*100;
    }
    $("#issue"+issue).find("td.for").width(per['for']+"%");
    $("#issue"+issue).find("td.abstain").width(per['abs']+"%");
    $("#issue"+issue).find("td.against").width(per['aga']+"%");
}

function handle_errors(error) {
    if(error == "Must be logged in.") {
        window.location = "/login/";
    }
    if(error == "Must have access token.") {
        window.location = "/oauth/auth/";
    }
}
