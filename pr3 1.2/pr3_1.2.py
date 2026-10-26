class ValidatedField:
    def __init__(self, expected_type: type, min_value=None, max_value=None):
        self.expected_type = expected_type
        self.min_value = min_value
        self.max_value = max_value

    def __set_name__(self, owner, name):
         self.name = name
         self.private_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj == None:
            return self
        else:
            return getattr(obj, self.private_name, None)

    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError("TypeError")
        if self.min_value is not None and value < self.min_value:
            raise ValueError("ValueError")
        if self.max_value is not None and value > self.max_value:
            raise ValueError("ValueError")
        setattr(obj, self.private_name, value)

class ConfigSection:
    _sections: dict[str, type] = {}
    def __init_subclass__(cls, section_name: str = "", **kwargs):
        if section_name:
            cls._sections[section_name] = cls
        super().__init_subclass__(**kwargs)

    @classmethod
    def get_section(cls, name: str):
        return cls._sections.get(name)

    @classmethod
    def list_sections(cls) -> list[str]:
        return list(cls._sections.keys())


class DatabaseConfig(ConfigSection, section_name="database"):
    host = ValidatedField(str)
    port = ValidatedField(int, min_value=1, max_value=65535)
    max_connections = ValidatedField(int, min_value=1, max_value=1000)
    def __init__(self, host, port, max_connections):
        self.host = host
        self.port = port
        self.max_connections = max_connections


class LoggingConfig(ConfigSection, section_name="logging"):
    level = ValidatedField(str)
    max_file_size_mb = ValidatedField(int, min_value=1, max_value=1024)

    def __init__(self, level, max_file_size_mb):
        self.level = level
        self.max_file_size_mb = max_file_size_mb



def main():
    print(f"Зареєстровані секції: {ConfigSection.list_sections()}")

    db_config = DatabaseConfig(host="localhost", port=5432, max_connections=100)
    print(f"DatabaseConfig: host={db_config.host}, port={db_config.port}, max_connections={db_config.max_connections}")

    try:
        db_bad_type = DatabaseConfig(host="localhost", port="5432", max_connections=100)
    except TypeError as e:
        print(f"Помилка: {e}")

    try:
        db_bad_val = DatabaseConfig(host="localhost", port=70000, max_connections=100)
    except ValueError as e:
        print(f"Помикла: {e}")

    log_cls = ConfigSection.get_section("logging")
    if log_cls:
        log_config = log_cls(level="INFO", max_file_size_mb=10)
        print(f"LoggingConfig створений через get_section: level={log_config.level}, max_file_size={log_config.max_file_size_mb}MB")


if __name__ == "__main__":

    main()