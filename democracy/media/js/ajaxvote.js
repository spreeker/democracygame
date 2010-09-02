$(function(){

    $(".voteform").click(function(event){

        // Find the number of the issue under consideration:
        var id_string = $(this).attr("id");
        var match = id_string.match(/^votelink_(\S*)$/);
        var issue_no = parseInt(match[1]);
        
        // Find the right div to add a voteform to and grab the form using the
        // jQuery load function:
        var target_div = $("#voteform_" + issue_no);
        target_div.load("/web/ajax/voteform/" + issue_no + "/", function(){
            
            });
            
            // Deal with the submission of this form:
            $("#castvote").click(function(event){
                var vote = $("#id_vote").val();
                var motivation = $("#id_motivation").val();
                var CSRFTOKEN = $("#csrfmiddlewaretoken").val();
                
                var data = {
                    'vote' : vote,
                    'csrfmiddlewaretoken' : CSRFTOKEN,
                    'issue_no' : issue_no,
                    'keep_private' : keep_private,
                };
                
                var afterVote = function(xhr, textStatus){
                    // This function updates the user interface after an 
                    // asynchronous javascript request to vote is handled by the
                    
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
