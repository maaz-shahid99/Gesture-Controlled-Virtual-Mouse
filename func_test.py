def map_value(value, input_range, output_range):
    input_min, input_max = input_range
    output_min, output_max = output_range
    
    # Map the input value to the output range
    mapped_value = output_min + (output_max - output_min) * ((value - input_min) / (input_max - input_min))
    
    # Make sure the mapped value stays within the output range
    mapped_value = max(min(mapped_value, output_max), output_min)
    
    return int(mapped_value)

# Example usage:
input_value = 570
input_range = (80, 560)
output_range = (0, 640)

mapped_value = map_value(input_value, input_range, output_range)
print(mapped_value)  # Output: 640
