$(document).ready(function() {
  $('.select-click').click(function() {
    $(this).removeClass('select-not-enabled').addClass('select')
    $(this).siblings('.select-click').removeClass('select').addClass('select-not-enabled')
  })
})