from dataclasses import dataclass
from dto.atleta_dto import atleta_dto

# Notação que cria alguns métodos padrões "por baixo dos panos", nesse contexto é útil pelo método construtor
@dataclass
# Classe "filha" de atleta_dto
class goleiro_dto(atleta_dto):
    defesas: int = 0
    golsSofridos: int = 0
    porcentagemDefesa: float = 0.0
    jogosSemSofrerGols: int = 0
    chutesSofridos: int = 0