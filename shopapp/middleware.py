
import time
from django.core.cache import cache
from django.conf import settings
import time
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseBadRequest
from django.conf import settings

# shopapp/middleware.py (версия с in-memory словарем)
import time
from django.http import HttpResponse
from threading import Lock


class ThrottlingMiddleware:
    """
    Middleware для ограничения частоты запросов от одного IP
    Использует словарь в памяти: {ip: [list_of_request_times]}
    """

    # Статический словарь для хранения времени запросов по IP
    _request_history = {}  # {ip: [timestamp1, timestamp2, ...]}
    _lock = Lock()  # Для потокобезопасности

    def __init__(self, get_response):
        self.get_response = get_response
        self.max_requests = 10  # 10 запросов
        self.time_window = 60  # за 60 секунд

    def __call__(self, request):
        # Пропускаем админку и статические файлы
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return self.get_response(request)

        ip_address = self.get_client_ip(request)

        if not self.check_throttle(ip_address):
            return HttpResponse(
                f'Превышен лимит запросов! '
                f'Максимум {self.max_requests} запросов за {self.time_window} секунд.',
                status=429
            )

        return self.get_response(request)

    def get_client_ip(self, request):
        """Получение реального IP адреса клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def check_throttle(self, ip_address):
        """Проверка лимита с использованием словаря {ip: [times]}"""
        current_time = time.time()

        with self._lock:  # Блокировка для безопасности в многопоточной среде
            # Получаем историю запросов для этого IP
            request_times = self._request_history.get(ip_address, [])

            # Очищаем старые запросы (вне временного окна)
            request_times = [
                t for t in request_times
                if current_time - t < self.time_window
            ]

            # Проверяем лимит
            if len(request_times) >= self.max_requests:
                return False

            # Добавляем текущий запрос
            request_times.append(current_time)

            # Сохраняем обновленную историю
            self._request_history[ip_address] = request_times

            # Очищаем старые записи для других IP (опционально)
            self._cleanup_old_records()

        return True

    def _cleanup_old_records(self):
        """Очистка старых записей для экономии памяти"""
        current_time = time.time()
        to_delete = []

        for ip, times in self._request_history.items():
            # Удаляем записи, если все запросы старше 2 временных окон
            if not times or current_time - max(times) > self.time_window * 2:
                to_delete.append(ip)

        for ip in to_delete:
            del self._request_history[ip]


class AdminThrottlingExemptMiddleware:
    """
    Middleware, который не применяет throttling к админке
    (можно добавить, если нужно исключить админку из ограничений)
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.throttling = ThrottlingMiddleware(get_response)

    def __call__(self, request):
        # Пропускаем админку без throttling
        if request.path.startswith('/admin/'):
            response = self.get_response(request)
            return response

        # Для остальных URL применяем throttling
        return self.throttling(request)