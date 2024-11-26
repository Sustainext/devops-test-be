(function ($) {
  $(document).ready(function () {
    function populateOrgs(clientId) {
      if (clientId) {
        $.ajax({
          url: "/api/auth/get_orgs_by_client/" + clientId + "/",
          success: function (data) {
            var orgSelect = $("#id_orgs");
            var selectedOrgs = orgSelect.data("selected") ? orgSelect.data("selected").toString().split(",") : [];
            orgSelect.empty();
            data.orgs.forEach(function (org) {
              var option = $("<option>").val(org.id).text(org.name);
              if (selectedOrgs.includes(org.id.toString())) {
                option.attr("selected", "selected");
              }
              orgSelect.append(option);
            });
            orgSelect.trigger("change");
          },
          error: function (xhr, status, error) {
            console.error("Error fetching orgs data:", error);
          },
        });
      }
    }

    function populateCorps(selectedOrgs) {
      if (selectedOrgs && selectedOrgs.length > 0) {
        $.ajax({
          url: "/api/auth/get_corps_by_orgs/",
          data: { org_ids: selectedOrgs },
          traditional: true,
          success: function (data) {
            var corpsSelect = $("#id_corps");
            var selectedCorps = corpsSelect.data("selected") ? corpsSelect.data("selected").toString().split(",") : [];
            corpsSelect.empty();
            data.corps.forEach(function (corp) {
              var option = $("<option>").val(corp.id).text(corp.name);
              if (selectedCorps.includes(corp.id.toString())) {
                option.attr("selected", "selected");
              }
              corpsSelect.append(option);
            });
            corpsSelect.trigger("change");
          },
          error: function (xhr, status, error) {
            console.error("Error fetching corps data:", error);
          },
        });
      } else {
        $("#id_corps").empty();
      }
    }
    function populateLocs(selectedCorps) {
      if (selectedCorps && selectedCorps.length > 0) {
        $.ajax({
          url: "/api/auth/get_locs_by_corps/",
          data: { corp_ids: selectedCorps },
          traditional: true,
          success: function (data) {
            var locsSelect = $("#id_locs");
            var selectedLocs = locsSelect.data("selected") ? locsSelect.data("selected").toString().split(",") : [];
            locsSelect.empty();
            data.locs.forEach(function (loc) {
              var option = $("<option>").val(loc.id).text(loc.name);
              if (selectedLocs.includes(loc.id.toString())) {
                option.attr("selected", "selected");
              }
              locsSelect.append(option);
            });
          },
          error: function (xhr, status, error) {
            console.error("Error fetching locs data:", error);
          },
        });
      } else {
        $("#id_locs").empty();
      }
    }

    var initialClientId = $("#id_client").val();
    if (initialClientId) {
      populateOrgs(initialClientId);
    }

    $("#id_client").change(function () {
      var clientId = $(this).val();
      populateOrgs(clientId);
    });

    $("#id_orgs").change(function () {
      var selectedOrgs = $(this).val();
      populateCorps(selectedOrgs);
    });

    $("#id_corps").change(function () {
      var selectedCorps = $(this).val();
      populateLocs(selectedCorps);
    });
  });
})(django.jQuery);
