new Vue({
    el: '#app',
    components: {
        'carousel': VueCarousel.Carousel,
        'slide': VueCarousel.Slide
    }
});

var app = angular.module('useraccess', ["ngSanitize"]);

app.controller('registerctrl', function ($scope) {
    $scope.buttontext = 'Register';
    $scope.email = "";
    $scope.password = "";
    $scope.fullname = "";
    $scope.phone = "";
    $scope.errmsg = "";
    $scope.referee = $('#referee').val();

    $scope.registeruser = function () {
        $scope.errmsg = "";
        $scope.actbusy();

        if ($scope.email && $scope.password && $scope.fullname && $scope.phone) {
            var fd = new FormData();

            fd.append("email", $scope.email);
            fd.append("password", $scope.password);
            fd.append("fullname", $scope.fullname);
            fd.append("phone", $scope.phone);
            fd.append("referee", $scope.referee);

            $.ajax({
                data: fd,
                url: "registeruser",
                contentType: false,
                processData: false,
                type: 'POST',
                success: function (result) {
                    var resultObj = JSON.parse(result);
                    if (resultObj.status === 'success') {
                        $scope.errmsg = resultObj.message;
                        window.location = resultObj.nexturl;
                    } else {
                        $scope.errmsg = resultObj.message;
                        $scope.actnormal();
                    }
                    $scope.$apply();
                },
                error: function (xhr, status, error) {
                    $scope.errmsg = error;
                    $scope.actnormal();
                }
            });
        } else {
            var errMsg = 'Sorry, please provide your details';
            $scope.errmsg = errMsg;
            $scope.actnormal();
        }
    };

    $scope.actbusy = function () {
        $('#submitbtn').attr("disabled", "true");
        $scope.buttontext = 'Please Wait...';
        $('#submitbtn').addClass('button--loading');
    };
    $scope.actnormal = function () {
        $('#submitbtn').removeAttr("disabled");
        $scope.buttontext = 'Register';
        $('#submitbtn').removeClass('button--loading');
    };

    $scope.checkCookie = function () {
        var referee = $scope.getCookie("referee");
        if (referee == "Sumo Bank" || referee == "") {
            $scope.setCookie("referee", $scope.referee, 30);
        } else {
            $scope.referee = referee;
        }
    };

    $scope.getCookie = function (cname) {
        var name = cname + "=";
        var ca = document.cookie.split(';');
        for (var i = 0; i < ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0) == ' ') {
                c = c.substring(1);
            }
            if (c.indexOf(name) == 0) {
                return c.substring(name.length, c.length);
            }
        }
        return "";
    };

    $scope.setCookie = function (cname, cvalue, exdays) {
        var d = new Date();
        d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
        var expires = "expires=" + d.toUTCString();
        document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
    };
    $scope.checkCookie();

});