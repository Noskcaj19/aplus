import colorama

class Colors:
    @staticmethod
    def bright(string: str):
        return colorama.Style.BRIGHT + string + colorama.Style.NORMAL

    @staticmethod
    def active_course(string: str):
        return colorama.Fore.CYAN + colorama.Style.BRIGHT + string + colorama.Fore.RESET + colorama.Style.NORMAL
