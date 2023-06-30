$(document).ready(function() {
    $('#select-site').select2()
    $('#select-site-table').css('display', 'none')

    let csrf_token = $("input[name='csrf_token']").val()
    let site_id = $('#select-site').val()

    $("#site-select-input").click(function() {
      let way = $(this).is(":checked")
      site_id = $('#select-site').val()
      if (way){
        $('#select-site-table').css('display', 'block')
        delivery_type_select_ajax(site_id)
      } else {
        $('#select-site-table').css('display', 'none')
        $('#select-site').val('0')
        $('.select2-selection__rendered').text('请选择')
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


    $('.clear-button').click(function() {
        $('#pop-up-permission').css('display','none')
    })
    $('#sub-mit-btn').click(function() {
        let data = {
            csrf_token: $('#csrf-token').val(),
        }
        $.ajax({
            type:"post",
            url: '/user/detail/edit',
            data: data,
            async:true,
            success:function(res){
                if (res == '200') {
                    $('#sub-mit-btn-ok').click()
                } else {
                    $('#pop-up-permission').css('display', 'block')
                }
            },
            error: function (xhr, textStatus, errorThrown) {

            }
        })
    })
})
