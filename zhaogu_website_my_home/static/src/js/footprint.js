$(document).ready(function () {
  $('.star').on('click', function () {
    var selectedStar = $(this).data('star');
    $('.star').removeClass('active');
    for (var i = 1; i <= selectedStar; i++) {
      $(this).parent('div').children('.star[data-star=' + i + ']').addClass('active');
    }
    $(this).parent('div').find('#ratingText').val(selectedStar);
  });
});