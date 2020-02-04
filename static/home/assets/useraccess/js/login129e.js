new Vue({
    el: '#app',
    components: {
        'carousel': VueCarousel.Carousel,
        'slide': VueCarousel.Slide
    }
});

var app = angular.module('useraccess', ["ngSanitize"]);

app.controller('loginctrl', function ($scope) {
    $scope.buttontext = 'Login';
    $scope.phone = "";
    $scope.password = "";
    $scope.errmsg = "";

    $scope.loginuser = function () {

        $scope.errmsg = "";
        $scope.actbusy();

        if ($scope.phone && $scope.password) {
            var fd = new FormData();
            fd.append("phone", $scope.phone);
            fd.append("password", $scope.password);
            $.ajax({
                data: fd,
                url: "loginuser",
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
            var errMsg = 'Sorry, please provide your login details';
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
        $scope.buttontext = 'Login';
        $('#submitbtn').removeClass('button--loading');
    };
});