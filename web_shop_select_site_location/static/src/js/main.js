$(document).ready(function() {
  $('#select-site').select2()
  $('#select-site-table').css('display', 'none')

  let csrf_token = $("input[name='csrf_token']").val()
  let site_id = $('#select-site').val()

  delivery_type_select_ajax(site_id)

  $(".o_delivery_carrier_select").click(function() {
    let way = $(this).children('label').text()
    let arr_type = ['站点自提', 'Pickup@shop']
    if (way.indexOf(arr_type) > -1){
      $('#select-site-table').css('display', 'block')
    } else {
      $('#select-site-table').css('display', 'none')
      site_id = 0
      $('#select-site').val('0')
      $('.select2-selection__rendered').text('请选择')
      delivery_type_select_ajax(site_id)
    }
  })

  $('#select-site').change(function() {
    site_id = $(this).val()
    delivery_type_select_ajax(site_id)
  })

  function delivery_type_select_ajax(site_id) {
    $.ajax({
      type:"post",
      url:'/select/pending/sites',
      data: {
          site_id: site_id,
          csrf_token: csrf_token
      },
      async:true,
      success:function(res){
        val = JSON.parse(res)
        if (val['site_address']) {
          $('#site-address').text(val['site_address'])
        } else {
          $('#site-address').text('')
        }
      },
      error: function (xhr, textStatus, errorThrown) {
        console.log(xhr, textStatus, errorThrown)
      }
    })
  }

})
