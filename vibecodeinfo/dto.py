import dataclasses


@dataclasses.dataclass()
class NewsDTO:
    title: str
    description: str
    source: str
