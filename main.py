import asyncio

from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import defer_call, info as session_info, run_async

MAX_MESSAGES_CNT = 100

chat_msgs = []
online_users = set()


async def refresh_msg(my_name):
    global chat_msgs
    last_idx = len(chat_msgs)
    while True:
        await asyncio.sleep(0.5)
        for m in chat_msgs[last_idx:]:
            if m[0] != my_name:
                put_markdown('`%s`: %s' % m, sanitize=True, scope='msg-box')

        if len(chat_msgs) > MAX_MESSAGES_CNT:
            chat_msgs = chat_msgs[len(chat_msgs) // 2:]

        last_idx = len(chat_msgs)


async def main():
    global chat_msgs

    put_scrollable(put_scope('msg-box'), height=300, keep_bottom=True)
    nickname = await input("Your nickname", required=True, validate=lambda n: 'This name is already been used' if n in online_users or n == '📢' else None)
    if nickname == "Boyan":
        await input("Password", required=True, type="password", validate=lambda x: "Password is not correct" if x != "utrg0" else None)
        online_users.add(f"Admin {nickname}")
        chat_msgs.append(('📢', '`%s` joins the room. %s users currently online' % (nickname, len(online_users))))
        put_markdown('`📢`: `%s` join the room. %s users currently online' % (nickname, len(online_users)), sanitize=True, scope='msg-box')
    else:
        online_users.add(nickname)
        chat_msgs.append(('📢', '`%s` joins the room. %s users currently online' % (nickname, len(online_users))))
        put_markdown('`📢`: `%s` join the room. %s users currently online' % (nickname, len(online_users)), sanitize=True, scope='msg-box')

    @defer_call
    def on_close():
        online_users.remove(nickname)
        chat_msgs.append(('📢', '`%s` leaves the room. %s users currently online' % (nickname, len(online_users))))

    refresh_task = run_async(refresh_msg(nickname))

    while True:
        data = await input_group('Send message', [
            input(name='msg', help_text='Message content supports inline Markdown syntax'),
            actions(name='cmd', buttons=['Send', 'Multiline Input', {'label': 'Exit', 'type': 'cancel'}])
        ], validate=lambda d: ('msg', 'Message content cannot be empty') if d['cmd'] == 'Send' and not d['msg'] else None)
        if data is None:
            break
        if data["msg"] == "Users":
            chat_msgs.append(('📢', f'В чата има {len(online_users)} и те са: {", ".join(online_users)}'))
        if data['cmd'] == 'Multiline Input':
            data['msg'] = '\n' + await textarea('Message content', help_text='Message content supports Markdown syntax')
        if nickname == "Boyan":
            put_markdown(f'`Admin` `%s`: %s' % (nickname, data['msg']), sanitize=True, scope='msg-box')
            chat_msgs.append((nickname, data['msg']))
        else:
            put_markdown(f'`%s`: %s' % (nickname, data['msg']), sanitize=True, scope='msg-box')
            chat_msgs.append((nickname, data['msg']))

    refresh_task.close()
    toast("You have left the chat room")


if __name__ == '__main__':
    start_server(main, debug=True, port=8080)