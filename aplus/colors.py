import colorama


class Colors:
    @staticmethod
    def bright(string: str):
        return colorama.Style.BRIGHT + string + colorama.Style.NORMAL

    @staticmethod
    def question(string: str):
        return colorama.Style.DIM + string + colorama.Style.NORMAL

    @staticmethod
    def check(string: str):
        return colorama.Style.BRIGHT + colorama.Fore.GREEN + string + colorama.Style.NORMAL + colorama.Fore.RESET

    @staticmethod
    def error(string: str):
        return colorama.Style.BRIGHT + colorama.Fore.RED + string + colorama.Style.NORMAL + colorama.Fore.RESET

    @staticmethod
    def today(string: str):
        return colorama.Fore.YELLOW + string + colorama.Fore.RESET

    @staticmethod
    def active_course(string: str):
        return colorama.Fore.CYAN + colorama.Style.BRIGHT + string + colorama.Fore.RESET + colorama.Style.NORMAL
