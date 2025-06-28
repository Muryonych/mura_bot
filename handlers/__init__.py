from .reputation_handler import labeler as reputation_labeler
from .mura_info_handler import labeler as mura_info_labeler
from .commands_handler import labeler as commands_labeler
from .meme_handler import labeler as meme_labeler
from .chat_settings_handler import labeler as settings_labeler 
from .markov_handler import labeler as markov_labeler

def register_handlers(bot):
    bot.labeler.load(reputation_labeler)
    bot.labeler.load(mura_info_labeler)
    bot.labeler.load(commands_labeler)
    bot.labeler.load(meme_labeler)
    bot.labeler.load(settings_labeler) 
    bot.labeler.load(markov_labeler)
