from abc import ABC, abstractmethod


class BaseOutput(ABC):
    @abstractmethod
    def save(self, data, output_path: str) -> None:
        pass
    
    @abstractmethod
    def get_extension(self) -> str:
        pass
