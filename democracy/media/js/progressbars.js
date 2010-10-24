

function update_vote_bar(){
    
    var total_votes = localStorage.getItem('total_votes');
    var total_issues= localStorage.getItem('total_issues');

    console.log(total_votes);
    console.log(total_issues);

    if(total_votes == null){
        total_votes = $('#total_votes').text();
    };
    if(total_issues == null){
        total_issues = $('#total_issues').text();
    };

    progress = total_votes / total_issues * 100;

    $("#progressbar").progressbar("value", progress)
}


$(function(){
    $("#progressbar").progressbar({ value: 1 });

    update_vote_bar();

});
