# from datetime import datetime
# from requests import get
# from telegram_token import TOKEN, CHAT_IDs
#
#
# def make_an_order(name, email, tel, address, index, payment_method, comment):
#     date = datetime.now().strftime("%m.%d.%Y")
#     ready = f'*{date}*\n{name}\n{email}\n{tel}\n{address}\n{index}\n{comment}'
#     for chat_id in CHAT_IDs:
#         resp = get(f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={ready}')
#         print(resp.json())
