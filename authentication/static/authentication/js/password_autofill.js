(function ($) {
  $(document).ready(function () {
    var defaultPassword = "asdfghjkl@1234567890";
    $("#id_password1").val(defaultPassword).prop("readonly", true);
    $("#id_password2").val(defaultPassword).prop("readonly", true);
  });
})(django.jQuery);
