from dataclasses import dataclass
from dto.atleta_dto import atleta_dto

# Notação que cria alguns métodos padrões "por baixo dos panos", nesse contexto é útil pelo método construtor
@dataclass
# Classe "filha" de atleta_dto
class linha_dto(atleta_dto):
    gols: int = 0
    assistencias: int = 0
    chutes: int = 0
    chutesNoGol: int = 0
    desarmes: int = 0
    cruzamentos: int = 0