from abc import ABC, abstractmethod


class GestionUsuarioInterface(ABC):
    """
    Contrato que cualquier módulo que gestione creación/soft-delete de
    Usuario debe implementar (RN-06). apps.usuarios depende únicamente
    de esta interfaz — nunca importa apps.integracion directamente.

    Todos los métodos son estáticos porque no necesitan estado de instancia,
    igual que el resto de Services del proyecto (ver 11_backend_logic.md).
    """

    @staticmethod
    @abstractmethod
    def crear_credenciales(data: dict, ejecutor):
        """Crea un Usuario con debe_cambiar_password=True, opcionalmente lo
        vincula a una Persona vía UsuarioXPersona, y programa el envío de
        credenciales por correo."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def desactivar_usuario(user_id: int, ejecutor):
        """Soft-delete: is_active=False + invalidación de tokens JWT activos."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def activar_usuario(user_id: int, ejecutor):
        """Activa un usuario (usado también en la creación inicial)."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def reactivar_usuario(user_id: int, ejecutor):
        """Reactiva un usuario previamente desactivado de forma explícita."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def reasignar_persona_a_usuario(usuario_id: int, nueva_persona_id: int, ejecutor):
        """Cierra la asignación UsuarioXPersona activa (si existe) y crea una nueva."""
        raise NotImplementedError
    
    @staticmethod
    @abstractmethod
    def listar_creados_por(ejecutor):
        """Devuelve todos los Usuario (activos e inactivos) cuyo creado_por
        es el ejecutor. Permite a Facultad reutilizar/reactivar una cuenta
        de un tutor o jurado que ya creó antes, en vez de duplicarla."""
        raise NotImplementedError