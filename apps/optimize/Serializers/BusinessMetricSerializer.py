from ..models.BusinessMetric import BusinessMetric
from rest_framework import serializers


class BusinessMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessMetric
        fields = "__all__"

    def validate(self, data):
        instance = getattr(self, "instance", None)

        def get_metric_status(metric):
            return data.get(metric, getattr(instance, metric, False))

        def get_weight(metric_key, weight_key, enabled):
            if not enabled:
                data[weight_key] = 0.0  # Force clear weightage if metric not selected
                return 0.0

            # If weight is explicitly in request, use it
            if weight_key in data:
                return data[weight_key]

            # Else use from instance (e.g., in PATCH)
            return getattr(instance, weight_key, 0.0) if instance else 0.0

        # Check enabled status
        fte = get_metric_status("fte")
        area = get_metric_status("area")
        revenue = get_metric_status("revenue")
        production = get_metric_status("production_volume")

        # Get weightages conditionally
        fte_weightage = get_weight("fte", "fte_weightage", fte)
        area_weightage = get_weight("area", "area_weightage", area)
        revenue_weightage = get_weight("revenue", "revenue_weightage", revenue)
        production_weightage = get_weight(
            "production_volume", "production_volume_weightage", production
        )

        # Validation
        errors = {}
        total_weightage = 0.0

        if fte:
            total_weightage += fte_weightage
            if fte_weightage <= 0:
                errors["fte_weightage"] = (
                    "Weightage must be greater than 0 if FTE is selected."
                )

        if area:
            total_weightage += area_weightage
            if area_weightage <= 0:
                errors["area_weightage"] = (
                    "Weightage must be greater than 0 if Area is selected."
                )

        if revenue:
            total_weightage += revenue_weightage
            if revenue_weightage <= 0:
                errors["revenue_weightage"] = (
                    "Weightage must be greater than 0 if Revenue is selected."
                )

        if production:
            total_weightage += production_weightage
            if production_weightage <= 0:
                errors["production_volume_weightage"] = (
                    "Weightage must be greater than 0 if Production Volume is selected."
                )

        # If at least one metric is enabled, total should be exactly 1
        if any([fte, area, revenue, production]):
            if abs(total_weightage - 1.0) > 0.001:
                errors["total_weightage"] = (
                    f"Total weightage of selected metrics must equal 1.0. Current total: {total_weightage}"
                )

        if errors:
            raise serializers.ValidationError(errors)

        return data
