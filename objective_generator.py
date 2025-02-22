# objective_generator.py

def generar_objetivos(personalidad: dict, emociones: dict) -> str:
    """
    Genera objetivos personalizados basados en el perfil de personalidad y el análisis emocional.
    """
    objetivos = []
    
    # Ejemplo: si el nivel de neuroticismo es alto, se sugiere reducirlo.
    if personalidad.get("neuroticismo", 0) > 0.5:
        objetivos.append("Trabaja en estrategias para reducir el neuroticismo.")
    
    # Ejemplo: si las emociones positivas son bajas, se sugiere fomentar emociones positivas.
    if emociones.get("Happy", 0) < 0.2:
        objetivos.append("Fomenta actividades que te hagan sentir feliz y relajado.")
    
    if not objetivos:
        objetivos.append("Mantén tu equilibrio emocional y sigue con tus rutinas.")
    
    return " ".join(objetivos)
