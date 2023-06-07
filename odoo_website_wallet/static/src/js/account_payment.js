$(document).ready(function() {
    $('.point-payment').click(function () {
      val = $('#order-id-btn').val()
      invoice_total = $("input[name='invoice_total']").val()
      point_balance = $("input[name='point_balance']").val()

      $('#point-payment-form').css('display','block')

      btn_div = $('.balance-sufficient')

      if ( parseFloat(point_balance.replace(',', '')) > parseFloat(invoice_total.replace(',', '')) ) {
        $('.balance-sufficient').replaceAll(btn_div)
        $('.not-balance').css('display', 'none')
      } else {
        $('.balance-sufficient').replaceAll("<p></p>")
        $('.not-balance').css('display', 'block')
      }
    })
    $('.clear-point-inpt').click(function () {
      $('#point-payment-form').css('display','none')
    })
});
