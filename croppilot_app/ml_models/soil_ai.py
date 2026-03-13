def predict_soil_ai(region, weather):
    if weather == 'rainy':
        return "Clay Loam"
    elif weather == 'dry':
        return "Sandy Loam"
    else:
        return "Loamy Soil"
