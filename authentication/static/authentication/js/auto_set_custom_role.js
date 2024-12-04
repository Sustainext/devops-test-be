(function ($) {
  $(document).ready(function () {
    function updateCustomRole() {
      var isAdminChecked = $("#id_admin").is(":checked");
      var isClientAdminChecked = $("#id_is_client_admin").is(":checked");
      var customRoleSelect = $("#id_custom_role");
      var collectSelect = $("#id_collect");
      var analyzeSelect = $("#id_analyse");
      var reportSelect = $("#id_report");
      var trackSelect = $("#id_track");
      var optimizeSelect = $("#id_optimise");

      var roleName = isClientAdminChecked ? "ClientAdmin" : isAdminChecked ? "Admin" : roleName;

      customRoleSelect.find("option").each(function () {
        if ($(this).text() === roleName) {
          $(this).prop("selected", true);
        }
      });
      if (isAdminChecked || isClientAdminChecked) {
        customRoleSelect.prop("disabled", true);
        collectSelect.prop("disabled", true).prop("checked", true);
        analyzeSelect.prop("disabled", true).prop("checked", true);
        reportSelect.prop("disabled", true).prop("checked", true);
        trackSelect.prop("disabled", true).prop("checked", true);
        optimizeSelect.prop("disabled", true).prop("checked", true);
      } else {
        customRoleSelect.prop("disabled", false);
        collectSelect.prop("disabled", false);
        analyzeSelect.prop("disabled", false);
        reportSelect.prop("disabled", false);
        trackSelect.prop("disabled", false);
        optimizeSelect.prop("disabled", false);
      }
    }

    updateCustomRole();

    $("#id_admin, #id_is_client_admin").change(function () {
      updateCustomRole();
    });
    // Enable disabled fields before submitting the form
    $("form").submit(function () {
      $("#id_custom_role, #id_collect, #id_analyse, #id_report, #id_track, #id_optimise").prop("disabled", false);
    });
  });
})(django.jQuery);
