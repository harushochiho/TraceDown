class FilesProcessing:
    def __init__(self):
        self._contents: list[str] = []

    def read_files(self, file_paths: list[str]) -> None:
        if not file_paths:
            raise ValueError("File paths list cannot be empty.")

        for file_path in file_paths:
            with open(file_path, "r", encoding="utf-8") as file:
                print("Reading file:", file_path)
                self._contents.append(file.read())

    def get_contents(self) -> list[str]:
        if not self._contents:
            raise ValueError("No contents have been read yet.")

        return self._contents

    @staticmethod
    def write_files(path: str, content: str, time: str, line_end: str = "") -> None:
        if not str:
            raise ValueError("File paths list cannot be empty.")

        with open(path, "a", encoding="utf-8") as opening_file:
            print(f"{time} Logging {path}")
            opening_file.write(f"{time}-{content}{line_end}")
