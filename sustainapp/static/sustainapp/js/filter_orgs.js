(function ($) {
  $(document).ready(function () {
    // Function to populate organizations based on selected client
    function populateOrganizations(clientId) {
      if (clientId) {
        $.ajax({
          url: "/api/auth/get_orgs_by_client/" + clientId + "/", // Update API URL if needed
          success: function (data) {
            var orgSelect = $("#id_organization");
            var selectedOrgs = orgSelect.data("selected") ? orgSelect.data("selected").toString().split(",") : [];

            // Clear existing options
            orgSelect.empty();

            // Populate new options
            data.orgs.forEach(function (org) {
              var option = $("<option>").val(org.id).text(org.name);
              if (selectedOrgs.includes(org.id.toString())) {
                option.attr("selected", "selected");
              }
              orgSelect.append(option);
            });

            // Trigger change event to update dependencies (if any)
            orgSelect.trigger("change");
          },
          error: function (xhr, status, error) {
            console.error("Error fetching organizations data:", error);
          },
        });
      } else {
        // Clear the organization dropdown if no client is selected
        $("#id_organization").empty();
      }
    }

    // Initial population of organizations if a client is pre-selected
    var initialClientId = $("#id_client").val();
    if (initialClientId) {
      populateOrganizations(initialClientId);
    }

    // Populate organizations on client change
    $("#id_client").change(function () {
      var clientId = $(this).val();
      populateOrganizations(clientId);
    });
  });
})(django.jQuery);
