import functools
import time


def cache(max_size: int = 128):
    def decorator(func):
        _cache = {}
        _call_order = []

        @functools.wraps(func)
        def wrapper(*args):
            if args in _cache:
                print("cache hit")
                return _cache[args]
            else:
                print("cache miss")
                res = func(*args)
                _cache[args] = res
                _call_order.append(args)

                if len(_cache) > max_size:
                    oldest_key = _call_order.pop(0)
                    del _cache[oldest_key]

                return res

        wrapper.cache_info = lambda: {
            "size": len(_cache), "max_size": max_size
        }
        wrapper.cache_clear = lambda: (_cache.clear(), _call_order.clear())
        return wrapper

    return decorator


def rate_limit(max_calls: int, period: float = 60.0):
    def decorator(func):
        call_times = []

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal call_times
            current_time = time.time()
            call_times = [t for t in call_times if current_time - t < period]

            if len(call_times) >= max_calls:
                raise RuntimeError(f"Перевищено ліміт викликів: макс {max_calls} за {period}с")

            call_times.append(current_time)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log(level: str = "INFO"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            args_str = ", ".join(repr(a) for a in args)
            kwargs_str = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
            all_args = ", ".join(filter(None, [args_str, kwargs_str]))
            
            print(f"[{level}] Виклик {func.__name__}({all_args})")
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                exec_time = time.time() - start_time
                print(f"[{level}] {func.__name__} → {result} (час: {exec_time:.4f}с)")
                return result
            except Exception as e:
                print(f"[ERROR] Помилка у функції {func.__name__}: {e}")
                raise

        return wrapper

    return decorator

@cache(max_size=64)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


@rate_limit(max_calls=5, period=10.0)
def send_notification(message: str) -> str:
    return f"Надіслано: {message}"


@log(level="DEBUG")
def divide(a: float, b: float) -> float:
    return a / b


def main():
    print("Результат fibonacci(30):", fibonacci(30))
    print("Статистика кешу:", fibonacci.cache_info())
    print()

   
    for i in range(1, 7):
        try:
            res = send_notification(f"Повідомлення №{i}")
            print(res)
        except RuntimeError as e:
            print(f"Перехоплено виняток: {e}")
    print()

    try:
        divide(10, 3)
    except Exception:
        pass

    try:
        divide(10, 0)
    except Exception:
        pass


if __name__ == "__main__":
    main()

