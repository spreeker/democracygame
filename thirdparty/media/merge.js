$(document).ready(function(){
  
    $("tr").each(function(){
        var vfor = parseInt($("td.for", this).html());
        var vabs = parseInt($("td.abstain", this).html());
        var vaga = parseInt($("td.against", this).html());
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
        $("td.for", this).width(per['for']+"%");
        $("td.abstain", this).width(per['abs']+"%");
        $("td.against", this).width(per['aga']+"%");
    });
  //Fixes an animation glitch caused by the
  //div's dynamic height.  Need to set the
  //height style so the slide functions work
  //correctly.
  $("div.body").each(function() {
	  $(this).hide();
	 });
  //hook the mouseup events to each header
  $("div.issue").children("div.title").mouseup(function(){
    
    //find the body whose header was clicked
    var body = $(this).parent().children("div.body");

    //slide the panel
    body.slideToggle();
  });
});
