$(document).ready(function(){

    $(".votelink").click(function(event){
        // Clear all voteforms (they might have been added through javscript):
        var clicked_votelink = $(this);
        $(".voteform_target").html("");

        // User requested a voteform. Hide the clicked votelink, unhide the
        // others if present:
        $(".votelink").css("visibility", "visible");
        $(".taglink").css("visibility", "visible");
        clicked_votelink.css("visibility", "hidden");
        // Find the number of the issue under consideration:
        var id_string = $(this).attr("id");
        var match = id_string.match(/^votelink_(\S*)$/);
        var issue_no = parseInt(match[1]);
        
        // Find the right div to add a voteform to and grab the form using the
        // jQuery load function:
        var target_div = $("#voteform_" + issue_no);
        target_div.load("/web/ajax/voteform/" + issue_no + "/", function(){
        
            // Deal with normal votes and blank votes. This assumes the HTML 
            // form that was received defaults to a blank vote. Only show the
            // motivation dropdown for blank votes.
            $("#id_vote").change(function(){
                if ($(this).val() != 0){
                    $("#id_motivation").fadeOut();
                } else {
                    $("#id_motivation").fadeIn();
                }
            });
            
            // Deal with the submission of this form:
            $("#castvote").click(function(event){
                var vote = $("#id_vote").val();
                var motivation = $("#id_motivation").val();
                var CSRFTOKEN = $("#csrfmiddlewaretoken").val();
                
                // Deal with case of anymous users are not shown the
                // keep_private checkbox. (Just try catch and default to false.)
                // TODO, check this, look into the server side as well.
                try {
                    var keep_private = $("#id_keep_private").val();
                } catch(err){
                    var keep_private = false;
                }

                var data = {
                    'motivation' : motivation, 
                    'vote' : vote,
                    'csrfmiddlewaretoken' : CSRFTOKEN,
                    'issue_no' : issue_no,
                    'keep_private' : keep_private,
                };
                
                var afterVote = function(xhr, textStatus){
                    // This function updates the user interface after an 
                    // asynchronous javascript request to vote is handled by the
                    // Emocracy server.
                    
                    // Following is only save if no user submitted data is send
                    // by the server --- because that might contain malicious 
                    // javascript, which clearly should not be eval()-ed !
                    
                    // Look into also updating the userprofile information on
                    // the current page.
                    eval("var jsonData = " + xhr.responseText + ";");
                     
                    if (textStatus == "success"){
                        $("#score_" + jsonData.issue_no).html("" + jsonData.score);
                        $("#votes_" + jsonData.issue_no).html("" + jsonData.votes);
                        var opinion_target = $("#opinion_" + jsonData.issue_no);
                        opinion_target.html(jsonData.vote_text);
                        opinion_target.attr("class", jsonData.css_class);
                        target_div.html("Vote was cast");
                        clicked_votelink.css("visibility", "visible");
                    } else if (textStatus == "error"){
                        target_div.html("Error occured, no vote cast.");
                        clicked_votelink.css("visibility", "visible");                        
                    }
                };
                                
                $.ajax({
                    type : "POST",
                    url : "/web/ajax/vote/",
                    data : data,
                    complete : afterVote,
                    dataType : "json",
                });
                
                return false;
            });
        });
        
        return false;
    });
    
  
});
