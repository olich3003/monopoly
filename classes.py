from config import *


class Room:
    def __init__(self, bot, max_t, update_period):
        self.users = list()
        self.now_user = -1
        self.bot = bot
        self.step_timer = self.Timer(max_t, update_period, self)
    
    class Timer:
        def __init__(self, max_t, period, other_instance):
            self.remaining_time = max_t
            self.other_instance = other_instance
            self.max_t = max_t
            self.period = period
            self.all_timers = list()

        def update_remaining_time(self, context):
            # срабатывает каждые self.period секунд
            self.remaining_time -= self.period
            # добавить обновление собощения для текущего игрока

        def enable_timer(self):
            # создает какое-то кол-во таймеров с промежутком period
            for time in range(self.period, self.max_t, self.period):
                self.all_timers.append(job.run_once(self.update_remaining_time, time))
            # создаем таймер на переход хода
            self.all_timers.append(job.run_once(self.other_instance.step, self.max_t))
            

    async def step(self, context):
        self.now_user = (self.now_user + 1) % len(self.users)
        await self.update_message(context)


    async def update_message(self, context):
        winner = self.is_winner()
        if winner != None:
            keyboard = [[InlineKeyboardButton("Закончить игру", callback_data='end_game')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            txt = f"Ты выиграл!\n Твой счет: {self.users[winner].score}\n"
            await context.bot.edit_message_text(chat_id=self.users[winner].chat_id, message_id=self.users[winner].last_message, 
                                                text=txt, reply_markup=reply_markup)
            for i, user in enumerate(self.users):
                if i != winner:
                    txt = f"Ты проиграл!\n Счет победителя {self.users[winner].name}: {self.users[winner].score}\n Твой счет: {user.score}"
                    await context.bot.edit_message_text(chat_id=user.chat_id, message_id=user.last_message, text=txt,
                                                        reply_markup=reply_markup)
            return
        #тут другая часть (ходы)
        for i, user in enumerate(self.users):
            txt = f"Твой счет:{user.score}\n"
            for j, user1 in enumerate(self.users):
                if j != i:
                    txt += f"Счёт игрока {user1.name}:{user1.score}\n"
            if i == self.now_user:
                keyboard = [[InlineKeyboardButton("Походить", callback_data='hod')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                self.step_timer = job.run_once(self.step, 5)
                print(self.step_timer.removed)
                await context.bot.edit_message_text(chat_id=user.chat_id, message_id=user.last_message, 
                                                    text="Сейчас твой ход!\n"+txt+"Походи", reply_markup=reply_markup)
            else:
                await context.bot.edit_message_text(chat_id=user.chat_id ,message_id=user.last_message, 
                                                    text="сейчас ход другого игрока\n"+txt+"Подожди")
    '''
    self.timer_queue = []
    for i in range(10):
        timer.queue.append(timer_i(update_message_for_user, 10*(i+1)))
    last_timer(self.step, 180)
    '''
    def is_winner(self):
      winner = None
      for i, user in enumerate(self.users):
          if user.score >= 15:
              winner = i
      return winner

class User:
    def __init__(self, chat_id, name):
        self.chat_id = chat_id
        self.name = name
        self.last_message = None
        self.cur_room = None
        self.score = 0