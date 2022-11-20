$(document).ready(function(){
        $('.change-behind').click(function(){
            if($('.content, .btn-wrapper').attr("trigger")==="0"){
                $('.content, .btn-wrapper').animate({"left":"20%"},700);
                $('.content, .btn-wrapper').attr("trigger","1");
                $('.change-behind').text("←" == $(this).text() ? "→" : "←");
            }
            else{
                $('.content, .btn-wrapper').animate({"left":"50px"},700);
                $('.content, .btn-wrapper').attr("trigger","0");
                $('.change-behind').text("&larr;" == $(this).text() ? "&larr;" : "→");
            }
          });

// SLIDESHOW 1 - NEW Workshop_scripts_in_practice
$('a[href*="Workshop_scripts_in_practice"]').click(function(){
    $('.scriptothek-chapter').hide();
    $('.scriptothek-chapter-1').show();
  });

  $('.scriptothek-slideshow-1').click(function() {
    $('.close-wrapper, .close1').show();
    // unique image adjustments
    $('.scriptothek-chapter-1 .script-image-wrapper').css({"min-width":"80%"});
  });
});

