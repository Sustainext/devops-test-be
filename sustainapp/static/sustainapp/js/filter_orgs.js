(function ($) {
  $(document).ready(function () {
    // Variable to store the currently selected client ID
    let currentClientId = $("#id_client").val();
    console.log("Initial client ID:", currentClientId);

    // Ensure no change event is fired programmatically on initial load
    let preventProgrammaticChange = true;

    // Function to populate organizations based on selected client
    function populateOrganizations(clientId, clearSelected = false) {
      console.log("Populating organizations for client:", clientId);

      // If no client is selected, clear the dropdown
      if (!clientId) {
        console.log("Clearing organizations as no client is selected.");
        $("#id_organization").empty();
        return;
      }

      // Fetch organizations via AJAX
      $.ajax({
        url: "/api/auth/get_orgs_by_client/" + clientId + "/", // API URL to fetch organizations
        beforeSend: function () {
          console.log("Fetching organizations from API for client:", clientId);
          $("#id_organization").prop("disabled", true); // Disable while loading
        },
        success: function (data) {
          console.log("Organizations fetched successfully:", data);

          // Retrieve preselected organizations only if clearSelected is false
          var orgSelect = $("#id_organization");
          var selectedOrgs = clearSelected
            ? [] // Clear selection if the client changes
            : orgSelect.data("selected") // Use preselected values if available
            ? orgSelect.data("selected").toString().split(",")
            : [];

          // Clear existing options
          orgSelect.empty();

          // Populate new options
          data.orgs.forEach(function (org) {
            var option = $("<option>").val(org.id).text(org.name);
            if (selectedOrgs.includes(org.id.toString())) {
              option.prop("selected", true); // Set selected if preselected
            }
            orgSelect.append(option);
          });

          // Trigger change event to update dependencies (if any)
          orgSelect.trigger("change");
        },
        complete: function () {
          console.log("Dropdown population complete.");
          $("#id_organization").prop("disabled", false); // Re-enable the dropdown after loading
        },
        error: function (xhr, status, error) {
          console.error("Error fetching organizations data:", error);
        },
      });
    }

    // Populate organizations if a client is pre-selected on page load
    if (currentClientId && !preventProgrammaticChange) {
      populateOrganizations(currentClientId); // Load with preselected values
    }
    preventProgrammaticChange = false;

    // Populate organizations on client change
    $("#id_client").change(function () {
      var clientId = $(this).val();
      if (clientId === currentClientId) {
        console.log("Client has not changed, skipping fetch.");
        return; // Skip if client ID has not changed
      }
      console.log("Client changed to:", clientId);
      currentClientId = clientId; // Update the current client ID
      populateOrganizations(clientId, true); // Clear selection on client change
    });
  });
})(django.jQuery);
