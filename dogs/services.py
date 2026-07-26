import logging
from django.core.cache import cache
from .models import Dog


logger = logging.getLogger(__name__)


def get_cache_key(slug=None, pk=None):
    """
    Генерирует ключ кэша на основе slug или pk
    """
    if slug:
        return f"dog_slug_{slug}"
    elif pk:
        return f"dog_pk_{pk}"
    return None


def get_dog_from_cache(slug=None, pk=None):
    """
    Получает объект Dog из кэша по slug или pk
    Если объекта нет в кэше, загружает его из базы данных и сохраняет в кэш
    """
    cache_key = get_cache_key(slug=slug, pk=pk)
    if not cache_key:
        logger.warning("Не указан slug или pk для получения объекта Dog.")
        return None

    dog = cache.get(cache_key)

    if not dog:
        logger.info(f"Объект Dog с ключом {cache_key} не найден в кэше. Загрузка из базы данных.")
        try:
            if slug:
                dog = Dog.objects.select_related('breed', 'owner').get(slug=slug)
            elif pk:
                dog = Dog.objects.select_related('breed', 'owner').get(pk=pk)

            cache.set(cache_key, dog, timeout=600)
            logger.info(f"Объект Dog с ключом {cache_key} сохранен в кэш.")
        except Dog.DoesNotExist:
            logger.error(f"Объект Dog с ключом {cache_key} не существует в базе данных.")
            return None

    return dog


def clear_dog_cache(slug=None, pk=None):
    """
    Очищает кэш для конкретной собаки по slug или pk
    """
    cache_key = get_cache_key(slug=slug, pk=pk)
    if not cache_key:
        logger.warning("Не указан slug или pk для очистки кэша.")
        return

    cache.delete(cache_key)
    logger.info(f"Кэш для объекта Dog с ключом {cache_key} очищен.")


def clear_all_cache():
    """
    Очищает весь кэш, связанный с собаками
    """
    logger.info("Очистка всего кэша, связанного с собаками.")
    cache.clear()
