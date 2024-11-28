(function ($) {
  $(document).ready(function () {
    // Variable to store the currently selected client ID
    let currentClientId = $("#id_client").val();
    console.log("Initial client ID:", currentClientId);

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

          // Retrieve preselected organizations
          var orgSelect = $("#id_organization");
          var selectedOrgs = clearSelected
            ? [] // Clear selection if the client changes
            : orgSelect.data("selected") // Use preselected values if available
            ? orgSelect.data("selected").toString().split(",") // Convert to array
            : [];

          console.log("Preselected organization IDs:", selectedOrgs);

          // Temporary map to retain current selection
          let currentSelection = {};
          orgSelect.find("option:selected").each(function () {
            currentSelection[$(this).val()] = true; // Store currently selected orgs
          });

          // Clear existing options
          orgSelect.empty();

          // Populate new options
          data.orgs.forEach(function (org) {
            var option = $("<option>").val(org.id).text(org.name);

            // Check both preselected IDs and temporary current selection
            if (selectedOrgs.includes(org.id.toString()) || currentSelection[org.id]) {
              option.prop("selected", true); // Retain selected state
              console.log("Preselecting organization:", org.name);
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

    // Populate organizations for the initial client ID on page load
    if (currentClientId) {
      console.log("Fetching organizations for initial client ID:", currentClientId);
      populateOrganizations(currentClientId); // Fetch and render organizations
    }

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
