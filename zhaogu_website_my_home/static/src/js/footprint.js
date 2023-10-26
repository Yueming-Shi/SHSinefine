$(document).ready(function () {
    $('.star').on('click', function () {
      var selectedStar = $(this).data('star');
      $('.star').removeClass('active');
      for (var i = 1; i <= selectedStar; i++) {
        $('.star[data-star=' + i + ']').addClass('active');
      }
      $('#ratingText').val(selectedStar);
    });
});