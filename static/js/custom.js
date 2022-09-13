$(document).ready(function(){
    $('#movable').click(function(){
        if($(this).attr("trigger")==="0"){
            $(this).animate({"left":"100px"},700);
            $(this).attr("trigger","1");
        }
        else{
            $(this).animate({"left":"0px"},700);
            $(this).attr("trigger","0");
        }
    }); 

    $(".change-behind").click(function(){
        $(".scriptothek").hide();
        console.log('sure')
    })
});