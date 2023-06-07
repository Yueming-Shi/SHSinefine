$(document).ready(function() {
    $('#select-site').select2()
    $('#select-site-table').css('display', 'none')

    $("#site-select-input").click(function() {
      let way = $(this).is(":checked")
      console.log(way)
      if (way){
        $('#select-site-table').css('display', 'block')
      } else {
        $('#select-site-table').css('display', 'none')
        $('#select-site').val('0')
        $('.select2-selection__rendered').text('请选择')
      }
    })


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
