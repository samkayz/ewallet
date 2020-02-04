new Vue({
    el: '#app',
    components: {
        'carousel': VueCarousel.Carousel,
        'slide': VueCarousel.Slide
    }
});

var app = angular.module('useraccess', ["ngSanitize"]);

app.controller('forgotctrl', function ($scope) {
    $scope.buttontext = 'Send Link';
    $scope.email = "";
    
    $scope.errmsg = "";
    $scope.sendlink = function () {
        $scope.errmsg = "";
        $scope.actbusy();

        if ($scope.email) {
            var fd = new FormData();
            fd.append("email", $scope.email);
            $.ajax({
                data: fd,
                url: "sendlink",
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
            var errMsg = 'Sorry, please provide your email address';
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
        $scope.buttontext = 'Send Link';
        $('#submitbtn').removeClass('button--loading');
    };
});