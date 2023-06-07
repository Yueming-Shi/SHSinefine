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

})