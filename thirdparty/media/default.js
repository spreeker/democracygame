var debug = false;
if ( debug == true ) {
    $.ajaxSetup({"error":function(XMLHttpRequest,textStatus, errorThrown) {   
            alert(textStatus);
            alert(errorThrown);
            alert(XMLHttpRequest.responseText);
        }
    });
}

$(document).ready(function(){

    getIssueList('new');
    getIssueList('popular');
    getIssueList('controversial');
    $(".issuehead").live("click", function() {
        $("div.body").hide();
        $("div.abstainvotes").hide();
    });
    // hook click event to title
    $("div.title").live("click", function(){
        //find the body whose title was clicked
        var body = $(this).parent().children("div.body");
        //slide the panel
        body.slideToggle();
    });
    // hook click event to abstain vote button 
    $("div.abstain").live("click", function(){
        //find the body whose title was clicked
        var body = $(this).parent().parent().parent().children("div.abstainvotes");
        //slide the panel
        body.slideToggle();
    });
    // hook the vote clicks
    $("div.for").live("click", function(){
        isv = $(this).parent().parent().find(".my_vote_issue").attr("value");
        process_vote(isv, 1);
        //find the body whose title was clicked
        var body = $(this).parent().parent().parent().children("div.abstainvotes");
        //slide the panel
        body.slideUp();
    });
    $("div.against").live("click", function(){
        isv = $(this).parent().parent().find(".my_vote_issue").attr("value");
        process_vote(isv, -1);
        //find the body whose title was clicked
        var body = $(this).parent().parent().parent().children("div.abstainvotes");
        //slide the panel
        body.slideUp();
    });
    $("div.unconvincing").live("click", function(){
        isv = $(this).parent().parent().find(".my_vote_issue").attr("value");
        process_vote(isv, 10);
        $(this).parent().parent().find("div.abstainvotes").hide();
    });
    $("div.notpolitical").live("click", function(){
        isv = $(this).parent().parent().find(".my_vote_issue").attr("value");
        process_vote(isv, 11);
        $(this).parent().parent().find("div.abstainvotes").hide();
    });
    $("div.cantagree").live("click", function(){
        isv = $(this).parent().parent().find(".my_vote_issue").attr("value");
        process_vote(isv, 12);
        $(this).parent().parent().find("div.abstainvotes").hide();
    });
    $("div.needsmorework").live("click", function(){
        isv = $(this).parent().parent().find(".my_vote_issue").attr("value");
        process_vote(isv, 13);
        $(this).parent().parent().find("div.abstainvotes").hide();
    });
    $("div.badlyworded").live("click", function(){
        isv = $(this).parent().parent().find(".my_vote_issue").attr("value");
        process_vote(isv, 14);
        $(this).parent().parent().find("div.abstainvotes").hide();
    });
    $("div.duplicate").live("click", function(){
        isv = $(this).parent().parent().find(".my_vote_issue").attr("value");
        process_vote(isv, 15);
        $(this).parent().parent().find("div.abstainvotes").hide();
    });
    $("div.unrelated").live("click", function(){
        isv = $(this).parent().parent().find(".my_vote_issue").attr("value");
        process_vote(isv, 16);
        $(this).parent().parent().find("div.abstainvotes").hide();
    });
    $("div.needtoknowmore").live("click", function(){
        isv = $(this).parent().parent().find(".my_vote_issue").attr("value");
        process_vote(isv, 17);
        $(this).parent().parent().find("div.abstainvotes").hide();
    });
    $("div.askmelater").live("click", function(){
        isv = $(this).parent().parent().find(".my_vote_issue").attr("value");
        process_vote(isv, 18);
        $(this).parent().parent().find("div.abstainvotes").hide();
    });

});
    //var lala = $.getJSON('/ajax/issues/new/', null, null);
    //alert(lala.responseText);
    //var lala = eval ( response );
/*
    $("div.folder").each(function() {
        var folder = $(this).attr("id");
        $(this).find("div.issue").each( function() {
            var my_vote = parseInt($("#my_vote", this).val());
            var my_issue = parseInt($("#my_vote_issue", this).val());
            var my_privacy = parseInt($("#my_vote_privacy", this).val());

            render_bars(my_issue, null);
            render_abs(my_issue, my_vote);

            $("td.for", this).mouseup(function(){
                process_vote(my_issue, 1);
            });
            $("td.abstain", this).mouseup(function(){
                var body = $("#"+folder+my_issue).find("div.abstainvotes");
                body.slideToggle();
                //process_vote(my_issue, 17);
            });
            $("td.against", this).mouseup(function(){
                process_vote(my_issue, -1);
            });
            $("#"+folder+"-un-"+my_issue).mouseup(function() {
                process_vote(my_issue, 10);
            });
            $(".abstainvotes", this).find("#unconvincing").mouseup(function() {
                var body = $("#"+folder).find(".abs-"+my_issue);
                body.slideToggle();
                $(".abs-"+my_issue).each(function() {
                    $(this).children().css({'background-color' : '#9ef8fb'});
                });
                $(".abs-"+my_issue).find("#unconvincing").css({'background-color' : '#4cf5fb'});
                process_vote(my_issue, 10);
            });
            $(".abstainvotes", this).find("#notpolitical").mouseup(function() {
                var body = $("#"+folder).find(".abs-"+my_issue);
                body.slideToggle();
                $(".abs-"+my_issue).each(function() {
                    $(this).children().css({'background-color' : '#9ef8fb'});
                });
                $(".abs-"+my_issue).find("#notpolitical").css({'background-color' : '#4cf5fb'});
                process_vote(my_issue, 11);
            });
            $(".abstainvotes", this).find("#cantagree").mouseup(function() {
                var body = $("#"+folder).find(".abs-"+my_issue);
                body.slideToggle();
                $(".abs-"+my_issue).each(function() {
                    $(this).children().css({'background-color' : '#9ef8fb'});
                });
                $(".abs-"+my_issue).find("#cantagree").css({'background-color' : '#4cf5fb'});
                process_vote(my_issue, 12);
            });
            $(".abstainvotes", this).find("#needsmorework").mouseup(function() {
                var body = $("#"+folder).find(".abs-"+my_issue);
                body.slideToggle();
                $(".abs-"+my_issue).each(function() {
                    $(this).children().css({'background-color' : '#9ef8fb'});
                });
                $(".abs-"+my_issue).find("#needsmorework").css({'background-color' : '#4cf5fb'});
                process_vote(my_issue, 13);
            });
            $(".abstainvotes", this).find("#badlyworded").mouseup(function() {
                var body = $("#"+folder).find(".abs-"+my_issue);
                body.slideToggle();
                $(".abs-"+my_issue).each(function() {
                    $(this).children().css({'background-color' : '#9ef8fb'});
                });
                $(".abs-"+my_issue).find("#badlyworded").css({'background-color' : '#4cf5fb'});
                process_vote(my_issue, 14);
            });
            $(".abstainvotes", this).find("#duplicate").mouseup(function() {
                var body = $("#"+folder).find(".abs-"+my_issue);
                body.slideToggle();
                $(".abs-"+my_issue).each(function() {
                    $(this).children().css({'background-color' : '#9ef8fb'});
                });
                $(".abs-"+my_issue).find("#duplicate").css({'background-color' : '#4cf5fb'});
                process_vote(my_issue, 15);
            });
            $(".abstainvotes", this).find("#unrelated").mouseup(function() {
                var body = $("#"+folder).find(".abs-"+my_issue);
                body.slideToggle();
                $(".abs-"+my_issue).each(function() {
                    $(this).children().css({'background-color' : '#9ef8fb'});
                });
                $(".abs-"+my_issue).find("#unrelated").css({'background-color' : '#4cf5fb'});
                process_vote(my_issue, 16);
            });
            $(".abstainvotes", this).find("#needtoknowmore").mouseup(function(){
                var body = $("#"+folder).find(".abs-"+my_issue);
                body.slideToggle();
                $(".abs-"+my_issue).each(function() {
                    $(this).children().css({'background-color' : '#9ef8fb'});
                });
                $(".abs-"+my_issue).find("#needtoknowmore").css({'background-color' : '#4cf5fb'});
                process_vote(my_issue, 17);
            });
            $(".abstainvotes", this).find("#askmelater").mouseup(function() {
                var body = $("#"+folder).find(".abs-"+my_issue);
                body.slideToggle();
                $(".abs-"+my_issue).each(function() {
                    $(this).children().css({'background-color' : '#9ef8fb'});
                });
                $(".abs-"+my_issue).find("#askmelater").css({'background-color' : '#4cf5fb'});
                process_vote(my_issue, 18);
            });
        });
    });
    // hide all issue bodies
    $("div.body").each(function() {
	    $(this).hide();
    });
    $("div.folder").each(function() {
        $(this).hide();
    });
    $("div.abstainvotes").each(function() {
        $(this).hide();
    });
    //hook the mouseup events to each title
    $("div.issue").children("div.title").mouseup(function(){
    
        //find the body whose title was clicked
        var body = $(this).parent().children("div.body");

        //slide the panel
        body.slideToggle();
    });
    $("div.myissues").mouseup(function() {
        var body = $(this).parent().find("#myissue");
        body.slideToggle();
    });
    $("div.hotissues").mouseup(function() {
        var body = $(this).parent().find("#hotissue");
        body.slideToggle();
    });
    $("div.newissues").mouseup(function() {
        var body = $(this).parent().find("#newissue");
        body.slideToggle();
    });
    $("div.genissues").mouseup(function() {
        var body = $(this).parent().find("#genissue");
        body.slideToggle();
    });
});
*/
function process_vote(issue, new_vote) {
    $old_vote_txt = $("div.i-"+issue).find(".my_vote").val();
    if($old_vote_txt == "None") {
        old_vote = -10;
    }
    else {
        old_vote = parseInt($old_vote_txt);
    }
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
                $.get("/totals/"+issue+"/", function(totals) {
                    $("div.i-"+issue).each(function() {
                        $(this).find("div.votes").replaceWith(totals);
                        $("div.i-"+issue).find(".my_vote").html(""+new_vote);
                        render_bars(issue, new_vote);
                    });
                });
            // fix layouts here
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

function render_abs(issue, vote) {
    $(".abs-"+issue).each(function() {
        $(this).children().removeClass('absselected');
    });
    $(".abs-"+issue).find(".vabs-"+vote).addClass('absselected');
}

function render_bars(issue, new_vote){
    var old_vote = parseInt($(".i-"+issue).find(".my_vote").val());
    vote = old_vote;
    // reset the bar colors to their unvoted colors
    $(".i-"+issue).find("div.for").removeClass('forselected');
    $(".i-"+issue).find("div.abstain").removeClass('abstainselected');
    $(".i-"+issue).find("div.against").removeClass('againstselected');
    if(new_vote!=null) {
        vote = new_vote;
    }
    // set voted color, if any
    if(vote ==1) {
        $(".i-"+issue).find("div.for").addClass('forselected');
    }
    if(vote >=10) {
        $(".i-"+issue).find("div.abstain").addClass('abstainselected');
    }
    if(vote ==-1) {
        $(".i-"+issue).find("div.against").addClass('againstselected');
    }
    render_abs(issue, vote);
    // get vote totals
    var vfor = parseInt($(".i-"+issue).find("div.for").html());
    var vabs = parseInt($(".i-"+issue).find("div.abstain").html());
    var vaga = parseInt($(".i-"+issue).find("div.against").html());
    //alert (vfor+" "+vabs+" "+vaga);
    // update vote totals, subtract from old vote totals and reset colors.
    if(new_vote != null) {
        $(".i-"+issue).find("div.for").html(""+vfor);
        $(".i-"+issue).find("div.abstain").html(""+vabs);
        $(".i-"+issue).find("div.against").html(""+vaga);
        $(".i-"+issue).find(".my_vote").val(new_vote);
    }
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
    $(".i-"+issue).find("div.for").width(per['for']+"%");
    $(".i-"+issue).find("div.abstain").width(per['abs']+"%");
    $(".i-"+issue).find("div.against").width(per['aga']+"%");
}

function handle_errors(error) {
    if(error == "Must be logged in.") {
        window.location = "/login/";
    }
    if(error == "Must have access token.") {
        window.location = "/oauth/auth/";
    }
}
function getIssueList(sortorder) {
    $.getJSON("/ajax/issues/"+sortorder+"/", function(data) {
        for( var i in data ) {
            id = url2id(data[i][0]);
            getIssue(sortorder, id);
        }
    });
    $("div.abstainvotes").hide();
    $("div#"+sortorder)
        .hide();
    $("div."+sortorder).mouseup(function() {
        var body = $(this).parent().find("div#"+sortorder);
        body.slideToggle();
    });
}

function getIssue(sortorder, issueid) {
    // get the issue content
    $.get("/issue/"+issueid+"/", function(issue) {
        $(issue).appendTo("div#"+sortorder);
        // get user's current vote.
        $.get("/myvote/"+issueid+"/", function (myvote) {
            $("div#"+sortorder)
                .find("div.p-"+issueid)
                .append(myvote);
            mv = $(".my_vote",myvote).attr('value');
            if(mv != "None") {
                $.get("/totals/"+issueid+"/", function (totals) {
                    $("div#"+sortorder)
                        .find(".v-"+issueid)
                        .replaceWith(totals);
                    render_bars(issueid, null);
                });
            }
        });
    });
}

function url2id(url) {
    return url.split(/\//)[4];
}

