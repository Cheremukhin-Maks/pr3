from abc import abstractmethod

class PluginMeta(type):
    _registry: dict[str, type] = {}
    REQUIRED_ATTRS = ("name", "version")
    
    def __new__(mcs, cls_name: str, bases: tuple, namespace: dict):
        new_cls = super().__new__(mcs, cls_name, bases, namespace)
        if bases:
            for i in mcs.REQUIRED_ATTRS:
                if i not in namespace:
                    raise TypeError(f"Клас {cls_name} повинен містити атрибут '{i}'")
            mcs._registry[new_cls.name] = new_cls
        return new_cls


    @classmethod
    def get_registry(mcs) -> dict[str, type]:
        return mcs._registry.copy()

    @classmethod
    def create_plugin(mcs, plugin_name: str):
        if plugin_name in mcs._registry:
            return mcs._registry[plugin_name]()
        else:
            raise ValueError(f"Плагін '{plugin_name}' не знайдений")


class BasePlugin(metaclass=PluginMeta):
    @abstractmethod
    def execute(self, data: str) -> str:
        pass

class UpperPlugin(BasePlugin):
    name = "upper"
    version = "1.0"
    def execute(self, data: str) -> str:
        return data.upper()

class ReversePlugin(BasePlugin):
    name = "reverse"
    version = "1.0"
    def execute(self, data: str) -> str:
        return data[::-1]

class CensorPlugin(BasePlugin):
    name = "censor"
    version = "1.1"
    def __init__(self, target_words=None):
        self.target_words = target_words or ["Світ"]

    def execute(self, data: str) -> str:
        result = data
        for word in self.target_words:
            result = result.replace(word, "***")
        return result

def hash_execute(self, data: str) -> str:
    return str(hash(data))

HashPlugin = type("HashPlugin", (BasePlugin,), {"name": "hash", "version": "2.0", "execute": hash_execute, })


def main():

    print("Зареєстровані плагіни:")

    for name, cls in PluginMeta.get_registry().items():

        print(f"  {name} (v{cls.version}): {cls.__name__}")


    test_data = "Привіт Світ"

    for name in PluginMeta.get_registry():

        plugin = PluginMeta.create_plugin(name)

        print(f"  {name}: {plugin.execute(test_data)}")

    try:
        class BadPlugin(BasePlugin):
            pass
    except TypeError as e:
        print(f"Помилка створення класу: {e}")

if __name__ == "__main__":

    main()