# context_manager.py
from diary_manager import obtener_entradas

def recuperar_contexto(user_id: str) -> str:
    """
    Recupera el contexto relevante del usuario a partir de las entradas del diario.
    En el futuro se puede ampliar usando bases vectoriales o métodos de embedding.
    """
    entradas = obtener_entradas(user_id)
    contexto = ""
    for entrada in entradas:
        contexto += f"{entrada.get('fecha')}: {entrada.get('texto')}\n"
    return contexto if contexto else "No hay entradas previas."
