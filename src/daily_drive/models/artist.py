from dataclasses import dataclass


@dataclass(frozen=True)  # Adicionar isto
class Artist:
    id: str
    name: str
    uri: str
    url: str
