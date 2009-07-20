$(document).ready(function(){
    $(".voteform_target").html("");
    
    $(".taglink").click(function(event){
        $(".taglink").css("visibility", "visible");
        $(".votelink").css("visibility", "visible");
        var current_taglink = $(this);
        current_taglink.css("visibility", "hidden");
        var id_string = $(this).attr("id");
        var match = id_string.match(/^taglink_(\S*)$/);
        var issue_no = parseInt(match[1]);
 
        var target_div = $("#voteform_" + issue_no);
        $(".voteform_target").html("");
        target_div.load("/web/ajax/tagform/" + issue_no + "/", function(){
            var CSRFTOKEN = $("#csrfmiddlewaretoken").val();
            
            var tagAdded = function(xhr, textStatus){
               // this function updates the page UI with the new tags
                eval("var jsonData = " + xhr.responseText + ";");
//                window.console.log("Callback called");
                if (textStatus == "succes"){
                    // update UI succes (blow away the tagform)
                    target_div.html("SUCCES!");
                } else if (textStatus = "error"){
                    target_div.html(jsonData.msg);
                    current_taglink.css("visibility", "visible");
                   
                    // update UI with failure (leave the tagform + add error message)
                }
            };
            
            $(".tagadd").click(function(event){
                var tag = $(this).text();
                var data = {
                    'tags' : tag,
                    'csrfmiddlewaretoken' : CSRFTOKEN,
                    'issue_no' : issue_no,
                };
                $.ajax({
                    type : "POST",
                    url : "/web/ajax/tag/" + issue_no + "/",
                    data : data,
                    complete : tagAdded,
                    dataType : "json",
                });
                return false;
            });
            
            $("#tagsubmit").click(function(event){
                var tag = $("#id_tags").val();
                var data = {
                    'tags' : tag,
                    'csrfmiddlewaretoken' : CSRFTOKEN,
                    'issue_no' : issue_no,                   
                };
                $.ajax({
                    type : "POST",
                    url : "/web/ajax/tag/" + issue_no + "/",
                    data : data,
                    complete : tagAdded,
                    dataType : "json",
                });
                return false;
            });
        });

        return false;
    });
  
});
