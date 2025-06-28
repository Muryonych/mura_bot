
import random

def should_reply(probability=0.1):
    """Возвращает True с заданной вероятностью (по умолчанию 10%)"""
    return random.random() < probability
