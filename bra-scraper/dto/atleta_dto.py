from dataclasses import dataclass, field
from typing import List

# Notação que cria alguns métodos padrões "por baixo dos panos", nesse contexto é útil pelo método construtor
@dataclass
class atleta_dto:
    nome: str
    clube_nome: str
    nacionalidade: str
    setor: List[str] = field(default_factory=list)
    partidasJogadas: float = 0.0
    cartaoAmarelo: int = 0
    segundoCartaoAmarelo: int = 0
    cartaoVermelho: int = 0