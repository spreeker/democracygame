function displaymessage(txt){
    $(messagebar).append('<div class="notice">' + txt + '</div>');
}

function getScoresFrom(score){
    // results = json
    // we need some logic to display the scores properly.
    // default are empty strings.
    _for = ""; blank = ""; against = "";
    //check if we got valid scores and update.  
    if (score[1]) { _for = score[1] }
    if (score[0]) { blank = score[0] }
    if (score[-1]) { against = score[-1]}
    //create the new displayable score object.
    score = new Object(); 
    score._for = _for; 
    score.blank = blank;
    score.against = against;
    return score;
}

function handleError(xhr, textStatus){
    console.log(textStatus);
    document.open();
    document.write(xhr.responseText);
    document.close();
}


function vote(){
    // Find the issue id under consideration:
    var forms = $(this).parent();
    var issue = forms.parent();
    var issue_id = issue.attr('id').match(/\d+/g);
    var direction = $("input[name=direction]", this).val();
    if (direction == undefined){
        var direction = $("select option:selected", this).val();
    }
    var action = $(this).attr('action');

    var data = {
        'direction' : direction,
        'issue_id' : issue_id,
    };
    localStorage.setItem(issue_id, direction)
    var afterVote = function(xhr, textStatus){
        // updates the user interface after a vote
        // if an error occurs print this on screen.
        if(textStatus.match(/error/g)) {
            handleError(xhr, textStatus);
            return;
        }
        // get the results to show on screen.
        results = $.parseJSON(xhr.responseText);
        score = getScoresFrom(results.score)  
        score_box =  $('.score', issue)
        // update issue with new scores.
        $('.for', score_box).text(score._for);
        $('.blank', score_box).text(score.blank);
        $('.against', score_box).text(score.against);
        // notify user of any messages.
        if(results.message){
            displaymessage(results.message);    
        }
    };
    $.ajax({
        type : "POST",
        url : action ,
        data : data,
        dataType : "json",
        complete : afterVote,
    });
    if (direction == -1){
        $("button.negative", this).addClass('selected');
        $("button.positive", forms).removeClass('selected');
    } else if (direction == 1){
        $("button.positive", this).addClass('selected');
        $("button.negative", forms).removeClass('selected');
    };

    return false;
}
$(function(){
    $(".forms").find("form").click(function(){
       vote.apply(this);
       return false;
       });  
    $(".forms").find("form").change(function(){
        vote.apply(this);
        return false;
        });
    //hide the blank vote button on the page we dont need it.
    blank_submit = $("form.blank").find("input[type='submit']");
    $(blank_submit).hide();
});
