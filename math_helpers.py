def clamp(value, minimum, maximum):
    # Check types
    if not isinstance(value, (float, int)):
        raise TypeError(
            f"value in clamp function should be float or int, but is {type(value)}"
        )

    # Validate thresholds
    if minimum > maximum:
        raise ValueError(
            f"Minimum threshold ({minimum}) cannot be greater than maximum threshold ({maximum})"
        )

    # Perform clamping
    return max(min(value, maximum), minimum)
