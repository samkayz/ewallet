var app=angular.module('inputsApp',["ngSanitize"]);app.controller('delcalccontroller',function($scope,$http){$scope.resultmsg="";$(document).ajaxStart(function(){$('body').preloader()}).ajaxStop(function(){$('body').preloader('remove')});var url=location.href+"/getdeliveryoptions";$http({method:"GET",url:url}).then(function(response){var deloptions=response.data;$scope.supported_pickup_states=deloptions.supported_pickup_states;$scope.abuja_addresses=deloptions.abuja_addresses;$scope.lagos_addresses=deloptions.lagos_addresses;$scope.abuja_del_cities=deloptions.abuja_del_cities;$scope.lagos_del_cities=deloptions.lagos_del_cities;$scope.abj_del_weights=deloptions.abj_del_weights;$scope.lag_del_weights=deloptions.lag_del_weights;$scope.delivery_cities=[];$scope.del_weights=[]});$scope.calcabuja=function(){$scope.abjresultmsg="";if($scope.abj_pickup_address&&$scope.abj_delivery_address){var url=location.href+"/calcabuja";var fd=new FormData();fd.append("source",$scope.abj_pickup_address.address_id);fd.append("destination",$scope.abj_delivery_address.address_id);$.ajax({url:url,data:fd,contentType:!1,processData:!1,type:'POST',success:function(result){$scope.abjresultmsg=result;$('html,body').animate({scrollTop:$("#abujanoticebox").offset().top},'slow');$scope.$apply()},error:function(xhr,status,error){$.alert({title:'Error!',content:'Could not complete the process. '+error});$scope.$apply()}})}else{var errMsg='<div class = "alert alert-warning">';errMsg+='<strong>Invalid, </strong>Please select the pickup and delivery addresses</div>';$scope.abjresultmsg=errMsg}};$scope.calclagos=function(){$scope.lagresultmsg="";if($scope.lag_pickup_address&&$scope.lag_delivery_address){var url=location.href+"/calclagos";var fd=new FormData();fd.append("source",$scope.lag_pickup_address.address_id);fd.append("destination",$scope.lag_delivery_address.address_id);$.ajax({url:url,data:fd,contentType:!1,processData:!1,type:'POST',success:function(result){$scope.lagresultmsg=result;$('html,body').animate({scrollTop:$("#lagosnoticebox").offset().top},'slow');$scope.$apply()},error:function(xhr,status,error){$.alert({title:'Error!',content:'Could not complete the process. '+error});$scope.$apply()}})}else{var errMsg='<div class = "alert alert-warning">';errMsg+='<strong>Invalid, </strong>Please select the pickup and delivery addresses</div>';$scope.lagresultmsg=errMsg}};$scope.refreshdeliverycities=function(){$scope.interstateresultmsg='';switch($scope.pickup_city){case 'Abuja':$scope.delivery_cities=$scope.abuja_del_cities;$scope.del_weights=$scope.abj_del_weights;break;case 'Lagos':$scope.delivery_cities=$scope.lagos_del_cities;$scope.del_weights=$scope.lag_del_weights;break;default:$scope.delivery_cities=[];$scope.del_weights=[];break}};$scope.calcinterstate=function(){$scope.interstateresultmsg='';if($scope.pickup_city&&$scope.delivery_city&&$scope.package_weight){var url=location.href+"/calcstate";var fd=new FormData();fd.append("source",$scope.pickup_city);fd.append("destination",$scope.delivery_city.city);fd.append("weight",$scope.package_weight);$.ajax({url:url,data:fd,contentType:!1,processData:!1,type:'POST',success:function(result){$scope.interstateresultmsg=result;$('html,body').animate({scrollTop:$("#interstateNotice").offset().top},'slow');$scope.$apply()},error:function(xhr,status,error){$.alert({title:'Error!',content:'Could not complete the process. '+error});$scope.$apply()}})}else{var errMsg='<div class = "alert alert-warning">';errMsg+='<strong>Invalid, </strong>Please select the pickup city, delivery city and the weight of the package</div>';$scope.interstateresultmsg=errMsg}}});app.controller('feecalculator',function($scope){$scope.resultmsg="";$(document).ajaxStart(function(){$('body').preloader()}).ajaxStop(function(){$('body').preloader('remove')});$scope.getfee=function(){$scope.resultmsg="";if($scope.amount&&$scope.amount>0){var fee=0;if($scope.amount<=30000){fee=0.04*$scope.amount}else{fee=0.03*$scope.amount}
var msg='The escrow fee for this amount will be <b>&#8358;'+$scope.numberWithCommas(fee.toFixed(2))+'</b>.<br>';msg+='The buyer and seller will pay <b>&#8358;'+$scope.numberWithCommas((fee/2).toFixed(2))+'</b> each.';var outputmsg='<div class="alert alert-warning">';outputmsg+=msg+'</div>';$scope.resultmsg=outputmsg;$('html,body').animate({scrollTop:$("#noticebox").offset().top},'slow')}else{var errMsg='<div class = "alert alert-warning">';errMsg+='<strong>Invalid, </strong>Please enter a valid amount</div>';$scope.resultmsg=errMsg}};$scope.numberWithCommas=function(x){return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g,",")}});app.controller('signin',function($scope){$scope.resultmsg="";$scope.forgorterrmsg="";$(document).ajaxStart(function(){$('body').preloader()}).ajaxStop(function(){$('body').preloader('remove')});$scope.signin=function(){$scope.resultmsg="";if($scope.email&&$scope.password){var signInUrl="bouncer/sign_in";var fd=new FormData();fd.append("email",$scope.email);fd.append("password",$scope.password);$.ajax({url:signInUrl,data:fd,contentType:!1,processData:!1,type:'POST',success:function(result){var resultObj=JSON.parse(result);if(resultObj.status==='success'){window.location=resultObj.nexturl}else{$scope.resultmsg=resultObj.message;$('html,body').animate({scrollTop:$("#signInNotice").offset().top},'slow')}
$scope.$apply()},error:function(xhr,status,error){$.alert({title:'Error!',content:'Could not complete the process. '+error});$scope.$apply()}})}else{var errMsg='Sorry, please provide your login details';$scope.resultmsg=errMsg}};$scope.resetPassword=function(){$scope.forgorterrmsg="";if($scope.resetemail){var mUrl="forgot/reset";mUrl+="/"+$scope.resetemail+"/";$.ajax({type:'GET',url:mUrl,data:{},success:function(result){$scope.forgorterrmsg=result;$('html,body').animate({scrollTop:$("#forgotNotice").offset().top},'slow');$("#recoverpanel").hide();$scope.$apply()},error:function(xhr,status,error){$.alert({title:'Error!',content:'Could not complete the process. '+error})}})}else{var errMsg='Sorry, please provide your email address';$scope.resultmsg=errMsg}}});app.controller('signupctrl',function($scope){$scope.resultmsg="";$(document).ajaxStart(function(){$('body').preloader()}).ajaxStop(function(){$('body').preloader('remove')});$scope.usernameIsValid=function(username){var username_pattern=/^[\w]+$/;return(username.match(username_pattern))};$scope.numberIsValid=function(phone){var phone_pattern=/^(?:0([79][0]|[8][01])[0-9]{8})$/;return(phone.match(phone_pattern))};$scope.signUp=function(){$scope.resultmsg="";if($scope.email&&$scope.password&&$scope.password2&&$scope.phone&&$scope.password){if($scope.password!==$scope.password2){var message="<div class = 'alert alert-danger'>"+"<strong>Error! </strong> Passwords do not match"+"</div>";$scope.resultmsg=message}else if(!$scope.numberIsValid($scope.phone)){var message="<div class = 'alert alert-danger'>"+"<strong>Invalid! </strong> Please provide a valid local Nigerian phone number."+"</div>";$scope.resultmsg=message}else{var signUpUrl="registrar/sign_up";var fd=new FormData();fd.append("email",$scope.email);fd.append("fullname",$scope.fullname);fd.append("password",$scope.password);fd.append("phone_number",$scope.phone);$.ajax({url:signUpUrl,data:fd,contentType:!1,processData:!1,type:'POST',success:function(result){var resultObj=JSON.parse(result);if(resultObj.status==='success'){window.location=resultObj.nexturl}else{$scope.resultmsg=resultObj.message;$('html,body').animate({scrollTop:$("#signUpNotice").offset().top},'slow')}
$scope.$apply()},error:function(xhr,status,error){$.alert({title:'Error!',content:'Could not complete the process. '+error});$scope.$apply()}})}}else{$scope.resultmsg="Please fill all fields"}}});app.controller('verifyctrl',function($scope){$scope.resultmsg="";$(document).ajaxStart(function(){$('body').preloader()}).ajaxStop(function(){$('body').preloader('remove')});$scope.verify=function(){$scope.resultmsg="";var verifyUrl="verify/confirm";verifyUrl+="/"+$scope.code;$.ajax({type:'GET',url:verifyUrl,data:{},success:function(result){var resultObj=JSON.parse(result);if(resultObj.status==='success'){window.location=resultObj.nexturl}else{$scope.resultmsg=resultObj.message;$('html,body').animate({scrollTop:$("#verifyNotice").offset().top},'slow')}
$scope.$apply()},error:function(xhr,status,error){$.alert({title:'Error!',content:'Could not complete the process. '+error})}})}});app.controller('resetctrl',function($scope){$scope.resultmsg="";$(document).ajaxStart(function(){$('body').preloader()}).ajaxStop(function(){$('body').preloader('remove')});$scope.resetPassword=function(){$scope.resultmsg="";if($scope.password!==$scope.password2){var message="<div class = 'alert alert-danger'>"+"<a href = '#' class = 'close' data-dismiss = 'alert'>&times;</a>"+"<strong>Error! </strong> Passwords do not match"+"</div>";$scope.resultmsg=message}else{var email=$("#txtPassword").attr("data-user-email");var code=$("#txtPassword").attr("data-user-code");var resetUrl="reset/resetPassword";var fd=new FormData();fd.append("email",email);fd.append("password",$scope.password);fd.append("code",code);$.ajax({url:resetUrl,data:fd,contentType:!1,processData:!1,type:'POST',success:function(result){var resultObj=JSON.parse(result);if(resultObj.status==='success'){window.location=resultObj.nexturl}else{$scope.resultmsg=resultObj.message;$('html,body').animate({scrollTop:$("#resetNotice").offset().top},'slow')}
$scope.$apply()},error:function(xhr,status,error){$.alert({title:'Error!',content:'Could not complete the process. '+error})}})}}})