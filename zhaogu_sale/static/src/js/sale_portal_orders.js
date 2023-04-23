$(document).ready(function() {
    url = window.location.search
    if(url == '?ytype=all') {
      $('.all').css({'background':'#E3170D','color':'white'})
    } else if(url == '?ytype=draft'){
      $('.drk').css({'background':'#E3170D','color':'white'})
    }else if(url == '?ytype=valuedno'){
      $('.dzf').css({'background':'#E3170D','color':'white'})
    }else if(url == '?ytype=valued'){
      $('.dfh').css({'background':'#E3170D','color':'white'})
    }else if(url == '?ytype=arrived'){
      $('.dqs').css({'background':'#E3170D','color':'white'})
    }

    $('.return-shipment').click(function () {
      val = $(this).siblings('#order-id-btn').val()
      $('#order-id').val(val)
      $('#return-shipment-form').css('display','block')
      $('.return-shipment-detail').attr("required", "true");
    })
    $('#clear-btn').click(function () {
      $('#return-shipment-form').css('display','none')
      $('.return-shipment-detail').attr("required", "false");
    })

    $('.point-payment').click(function () {
      val = $('#order-id-btn').val()
      shipping_total = $("input[name='shipping_total']").val()
      point_balance = $("input[name='point_balance']").val()

      $('.point-order-id').val(val)
      $('.deduction-balance').text(shipping_total)
      $('#point-payment-form').css('display','block')

      btn_div = $('.balance-sufficient')

      if ( parseFloat(point_balance.replace(',', '')) > parseFloat(shipping_total.replace(',', '')) ) {
        $('.balance-sufficient').replaceAll(btn_div)
        $('.not-balance').css('display', 'none')
      } else {
        $('.balance-sufficient').replaceAll("<p></p>")
        $('.not-balance').css('display', 'block')
      }
    })
    $('#clear-point, .clear-x').click(function () {
      $('#point-payment-form').css('display','none')
    })

})