import functools
import time


def auto_repr(cls):
    orig_init = cls.__init__

    def __repr__(self):
        param_names = orig_init.__code__.co_varnames[1:orig_init.__code__.co_argcount]
        args_str = ", ".join(f"{name}={getattr(self, name)!r}" for name in param_names if hasattr(self, name))
        return f"{cls.__name__}({args_str})"

    cls.__repr__ = __repr__
    return cls


def frozen(cls):
    orig_init = cls.__init__

    def new_init(self, *args, **kwargs):
        self._frozen = False
        orig_init(self, *args, **kwargs)
        object.__setattr__(self, "_frozen", True)

    def new_setattr(self, name, value):
        if getattr(self, "_frozen", False):
            raise AttributeError(f"Клас {cls.__name__} заморожений. Неможливо змінити або додати атрибут '{name}'.")
        object.__setattr__(self, name, value)

    cls.__init__ = new_init
    cls.__setattr__ = new_setattr
    return cls


def log_methods(cls):
    for attr_name in list(cls.__dict__.keys()):
        if not attr_name.startswith("_"):
            attr_value = getattr(cls, attr_name)
            if callable(attr_value):
                
                def make_wrapper(func):
                    @functools.wraps(func)
                    def wrapper(self, *args, **kwargs):
                        args_str = ", ".join(repr(a) for a in args)
                        kwargs_str = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
                        all_args = ", ".join(filter(None, [args_str, kwargs_str]))
                        
                        print(f"[LOG] Виклик {cls.__name__}.{func.__name__}({all_args})")
                        res = func(self, *args, **kwargs)
                        print(f"[LOG] {cls.__name__}.{func.__name__} повернув: {res!r}")
                        return res
                    return wrapper

                setattr(cls, attr_name, make_wrapper(attr_value))

    return cls



@auto_repr
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance_to(self, other: "Point") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@frozen
class ImmutableConfig:
    def __init__(self, host: str, port: int, debug: bool = False):
        self.host = host
        self.port = port
        self.debug = debug


@log_methods
class MathService:
    def add(self, a: float, b: float) -> float:
        return a + b

    def multiply(self, a: float, b: float) -> float:
        return a * b

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Ділення на нуль")
        return a / b


def main():
    
    p = Point(3.0, 4.0)
    print(repr(p))  
    print()

   
    cfg = ImmutableConfig("localhost", 8080, debug=True)
    print(f"Config: {cfg.host}:{cfg.port}")
    try:
        cfg.host = "remote" 
    except AttributeError as e:
        print(f"Очікувана помилка: {e}")
    print()

    svc = MathService()
    svc.add(10, 20)
    svc.multiply(3, 7)
    try:
        svc.divide(10, 0)
    except ValueError as e:
        print(f"Очікувана помилка: {e}")


if __name__ == "__main__":
    main()
