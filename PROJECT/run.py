from multiprocessing import Process
from main import main
from bot import run_bot
from bot import reply_check_loop

if __name__ == '__main__':
    bot_process = Process(target=run_bot)
    reply_check_process = Process(target=reply_check_loop)
    bot_process.start()
    reply_check_process.start()

    try:
        main()  # Запуск основного приложения
    except KeyboardInterrupt:
        print("Flask остановлен")

    bot_process.terminate()
    bot_process.join()
