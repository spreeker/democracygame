function displaymessage(txt){
    $(messagebar).append('<div class="notice">' + txt + '</div>');
}

function getScoresFrom(score){
    // results = json
    // we need some logic to display the scores properly.
    _for = ""; blank = ""; against = "";
    for (direction in score){
        console.log(direction);
        if(direction == 1){ _for = score[1];}
        else if (direction == -1){ against = score[-1];}
        else {
            if( blank == "") { blank = 0; }
            console.log("blank_" + direction);
            blank += results.score[direction]; 
        }
    }
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
    return;
}



function vote(){
    // Find the issue id under consideration:
    var forms = $(this).parent();
    var issue = forms.parent();
    var issue_id = issue.attr('id');
    var direction = $("input[name=direction]", this).val();
    if (direction == undefined){
        var direction = $("select option:selected", this).val();
    }
    var data = {
        'direction' : direction,
        'issue_id' : issue_id,
    };
    var afterVote = function(xhr, textStatus){
        // updates the user interface after a vote
        // if an error occurs print this on screen.
        if(textStatus.match(/error/g)) {
            handleError(xhr, textStatus);
        }
        // get the results to show on screen.
        results = $.parseJSON(xhr.responseText);
        score = getScoresFrom(results.score)  
        score_box =  $('.score', issue)
        // update issue with new scores.
        console.log(_for);
        console.log(blank);
        console.log(against);
        $('.for', score_box).text(_for);
        $('.blank', score_box).text(blank);
        $('.against', score_box).text(against);
        // notify user of any messages.
        if(results.message){
            displaymessage(results.message);    
        }
    };
    $.ajax({
        type : "POST",
        url : "/issue/vote/" + issue_id ,
        data : data,
        dataType : "json",
        complete : afterVote,
    });
    return false;
}
$(function(){
    $("form").click(function(){
       vote.apply(this);
       return false;
       });  
    $("form").change(function(){
        vote.apply(this);
        return false;
        });
    //hide the blank vote button on the page we dont need it.
    blank_submit = $("form.blank").find("input[type='submit']");
    $(blank_submit).hide();
});
