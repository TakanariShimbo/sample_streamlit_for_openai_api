from enums.global_enum import PageEnum
from enums.s_state_enum import GlobalSStateEnum
from s_states.base_s_states import BaseSState


class PageSState(BaseSState[PageEnum]):
    @staticmethod
    def get_name() -> str:
        return f"{GlobalSStateEnum.CURRENT_PAGE}".replace(".", "_")

    @staticmethod
    def get_default() -> PageEnum:
        return PageEnum.HOME