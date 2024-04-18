import class_test

obj = class_test.HandDetector()

input_range_x = (int((obj.wCam-obj.cursor_res_x)/2), int(obj.cursor_res_x+(obj.wCam-obj.cursor_res_x)/2))
input_range_y = (int((obj.hCam-obj.cursor_res_y)/2), int(obj.cursor_res_y+(obj.hCam-obj.cursor_res_y)/2))


def map_value_x(value):
    input_min, input_max = input_range_x
    output_min, output_max = (0,640)
    
    # Map the input value to the output range
    mapped_value = output_min + (output_max - output_min) * ((value - input_min) / (input_max - input_min))
    
    # Make sure the mapped value stays within the output range
    mapped_value = max(min(mapped_value, output_max), output_min)
    
    return int(mapped_value)

def map_value_y(value):
    input_min, input_max = input_range_y
    output_min, output_max = (0,480)
    
    # Map the input value to the output range
    mapped_value = output_min + (output_max - output_min) * ((value - input_min) / (input_max - input_min))
    
    # Make sure the mapped value stays within the output range
    mapped_value = max(min(mapped_value, output_max), output_min)
    
    return int(mapped_value)