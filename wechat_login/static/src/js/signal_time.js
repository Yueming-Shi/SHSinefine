
var vercode = 0;
var time = 60;
var flag = true;   //设置点击标记，防止60内再次点击生效
//发送验证码
$('#dyMobileButton').click(function () {
    $(this).attr("disabled", true);
    var phone = $('#phone').val();
    if (phone == "" || isNaN(phone) || phone.length != 11) {
            alert("请填写正确的手机号！");
            return false;
        }
    if (flag) {
        var timer = setInterval(function () {

            if (time == 60 && flag) {
                flag = false;

                $.ajax({
                    type: 'get',
                    async: false,
                    url: 'sms.do',
                    data: {
                        "phone": phone
                    },
                    dataType: "json",
                    success: function (data) {
                        if (data.status == 0) {
                            vercode = data.data;
                            $("#dyMobileButton").html("已发送");
                        } else {
                            alert(data.msg);
                            flag = true;
                            time = 60;
                            clearInterval(timer);
                        }
                    }
                });
            } else if (time == 0) {
                $("#dyMobileButton").removeAttr("disabled");
                $("#dyMobileButton").html("获取验证码");
                clearInterval(timer);
                time = 60;
                flag = true;
            } else {
                $("#dyMobileButton").html(time + " s 重新发送");
                time--;
            }
        }, 1000);
    }

});

