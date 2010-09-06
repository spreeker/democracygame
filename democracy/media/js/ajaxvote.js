$(function(){

    $("form").click(function(event){

        // Find the number of the issue under consideration:
        var issue_id = $(this:parent).attr("id");
            
        // Deal with the submission of this form:
        var vote = $("direction").val();
        
        var data = {
            'vote' : vote,
            'issue_id' : issue_no,
        };
        
        var afterVote = function(xhr, textStatus){
            // updates the user interface after an vote
            
            eval("var jsonData = " + xhr.responseText + ";");
            
        };
        $.ajax({
            type : "POST",
            url : "/vote/" + issue_id ,
            data : data,
            dataType : "json",
        });
        return false;
        });
        return false;
    });
});
