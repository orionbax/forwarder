import asyncio
import os
import sys
import json
import time

def clear():
    try:
        os.system('cls')
    except Exception as err:
        os.system('clear')

def download_dep():
    with open('requirements.txt', 'w') as file:
        deps = ['pyrogram\n']
        for dep in deps:
            file.write(dep)

    with open('run.bat', 'w') as file:
        cmds = ['pip install -r requirements.txt\n', 'pause']
        for cmd in cmds:
            file.write(cmd)

    os.startfile('run.bat')


try:
    from pyrogram import Client
    from pyrogram import errors
except Exception as err:
    download_dep()
    input('Restart the program...')
    sys.exit()

settings_file_name = 'mySettings.json'
if settings_file_name not in os.listdir(os.getcwd()):
    with open(settings_file_name, 'w') as file:
        file.write('')
session_name = 'my_account'
session_name = next(iter([name for name in os.listdir() if '.session' in name])) or session_name
session_name = session_name.split('.')[0]

app = Client(session_name.split('.')[0])




def reset():
    data = {
        "sources": {},
        "blocked_words": [],
        "transform_words": {},
    }
    with open(settings_file_name, 'w+') as file:
        json.dump(data, file)


def read_settings():
    try:
        with open(settings_file_name, 'r') as file:
            data = json.load(file)
    except json.JSONDecodeError as err:
        print("Creating new settings")
        reset()
        data = read_settings()
    except Exception as err:
        print(err)
    return data


settings = read_settings()


def toggle_options(source=None):
    os.system('clear')
    new_pref = settings['sources'][source]
    all_prefs = [key for key in settings['sources'][source] if 'allow' in key]
    options = [
        f'{i + 1}, {all_prefs[i]} -> {new_pref[all_prefs[i]]}' for i in range(len(all_prefs))]

    print('0, To return to the main page')
    for option in options:
        print(option)

    try:
        cmd = int(input('toggle by choosing their index: '))
        if cmd == 0:
            main()
        elif cmd <= len(all_prefs):
            negate = not new_pref[all_prefs[cmd - 1]]
            new_pref[all_prefs[cmd - 1]] = not new_pref[all_prefs[cmd - 1]]
    except ValueError as err:
        print(err)
    except Exception as err:
        print(err)
    if source:
        settings['sources'][source] = new_pref
        save_changes()
    toggle_options(source=source)


def set_preferences_page():
    sources = [source for source in settings['sources']]
    os.system('clear')
    if sources:
        for i in range(len(sources)):
            print(f'{i + 1}, {sources[i]}')
        index = int(input("select by index: ")) - 1
        if index + 1 == 0:
            main()
        toggle_options(sources[index])
    main()


async def check_exist(id):
    global app
    try:
        if app.is_connected:
            chat = await app.get_chat(chat_id=id)
            return chat
        else: 
            async with Client(session_name) as app:
                chat = await app.get_chat(chat_id=id)
                if chat:
                    return chat
    except Exception as err:
        pass
        # print(err)
    return False

# Working -
def add_channel_page():
    os.system('clear')
    print('Add Source page')
    options = '0, To return to the main page\n1, Add Source\n2, Remove Source'
    print(options)
    cmd = input('Enter: ')
    if cmd == '1':
        os.system('clear')
        id = '-' + input('Source id -: ').replace(' ', '').replace('-',  '')
        
        # Check if channel exists
        channel = asyncio.run(check_exist(id))  #app.loop.run_until_complete(check_exist(id))
        if channel:
            add_channel(channel)
            save_changes()
            print("Chat exist!")
            time.sleep(3)
        else:
            print(f"Channel {id} does not exist ")
            time.sleep(3)
        main()
        
    elif cmd == '2':
        os.system('clear')
        if settings['sources']:
            titles = [key for key in settings['sources']]
            print('0, To return to the main page')
            for i in range(len(titles)):
                print(f'{i + 1}, {titles[i]}')
            cmd = int(input('select by their index\n: ')) - 1
            if cmd == -1:
                main()
            elif settings['sources'].get(titles[cmd], None):
                del settings['sources'][titles[cmd]]
                save_changes()
        main()
    else:
        main()


def configure_key_words_page():
    options = "1, Add words to blacklist\n2, Remove from blacklist\n3, Add words to replace\n4, Remove replace words"
    print(options)
    cmd = input("enter: ")
    try:
        if cmd == '1':
            word = input("word: ").lower()
            if word and word not in settings['blocked_words']:
                settings['blocked_words'].append(word)
                save_changes()

        elif cmd == '2':
            print(f'You have blocked {len(settings["blocked_words"])} words')
            if settings['blocked_words']:
                for i in range(len(settings['blocked_words'])):
                    print(f"{i + 1}, {settings['blocked_words'][i]}")

                word = input('word: ').lower().replace(' ', '')
                if word == '0':
                    main()

                elif int(word) <= len(settings['blocked_words']):
                    settings['blocked_words'].remove(
                        settings['blocked_words'][int(word) - 1])
                    save_changes()

        elif cmd == '3':
            key = input('word to look for: ').lower().replace(' ', '')
            value = input('word to replace it with: ').lower().replace(' ', '')
            settings['transform_words'][key] = value
            save_changes()

        elif cmd == '4':
            rep_words = [word for word in settings['transform_words']]
            if rep_words:
                print(f'You have {len(rep_words)} words')
                print('ENTER 0 TO EXIT')
                for i in range(len(rep_words)):
                    print(
                        f'{i + 1}, {rep_words[i]} -> {settings["transform_words"][rep_words[i]]}')

                index = input('select by their index: ')
                if index != '0':
                    word = rep_words[int(index) - 1]
                    if settings['transform_words'].get(word, None):
                        del settings['transform_words'][word]
                        save_changes()
        else:
            print('invalid input')

    except KeyError as err:
        print(err, 'key')

    except Exception as err:
        print(err, 'exception')
    main()


def remove_destination():
    try:
        os.system('clear')
        sources = [source for source in settings['sources']]
        for i in range(len(sources)):
            source = sources[i]
            print(f'{i + 1}, {source}')

        destiny = int(input('to which channel: ')) - 1
        if destiny != '0':
            source = sources[destiny]
            destinations = settings['sources'][source]['destinations']
            for i in range(len(destinations)):
                destiny = destinations[i]
                print(f'{i + 1}, {destiny}')

            if destinations:
                destiny = input('choose: ')
                if destiny != '0':
                    destiny = destinations[int(destiny) - 1]
                    settings['sources'][source]['destinations'].remove(destiny)
                    save_changes()
                    main()

    except KeyError as err:
        add_destination()
    except Exception as err:
        print(err)
        input('move')
    main()


def add_destination():
    try:
        os.system('clear')
        sources = [source for source in settings['sources']]
        print('ENTER 0 TO exit')
        print("[Choose a channel to forward from]")
        
        for i in range(len(sources)):
            source = sources[i]
            name = settings['sources'][source]['name']
            print(f'{i + 1}, {name}')

        destination = input('choose: ')
        if destination != '0':
            destination = int(destination) - 1
            source = sources[destination]
            id = '-' + (input("id:").replace(' ', '').replace('-', ''))
            if id and id not in settings['sources'][source]['destinations']:
                channel = asyncio.run(check_exist(id))
                if channel:
                    settings['sources'][source]['destinations'].append([channel.title, id])
                    save_changes()
                    main()
                else:
                    print(f"{id} is an INVALID id !")
                    time.sleep(2)
    except KeyError as err:
        add_destination()
    except Exception as err:
        print(err)
        input('move')


def save_changes():
    with open(settings_file_name, 'w+') as file:
        json.dump(settings, file)


def add_channel(channel):
    titles = [key for key in settings['sources'] if key == str(channel.id)]
    if len(titles) > 0:
        return 
    val = {"name": channel.title,"allow_image": True, "allow_video": True, "allow_audio": False,
           'allow_text': True, 'allow_poll': True, "allow_document": True, 'destinations': []}
    settings['sources'][channel.id] = val
    with open(settings_file_name, 'w') as file:
        json.dump(settings, file)


# Case sensetive
def configure_text(caption):
    tempCaption = caption
    if caption:
        # caption = caption.lower()
        for word in settings['blocked_words']:
            if word in caption:
                tempCaption = caption.replace(word, '')
        return transform_caption(tempCaption)
    return transform_caption(caption)

# Case sensetive
def transform_caption(caption):
    newCaption = caption
    if caption:
        # newCaption = caption.lower()
        for key, value in settings['transform_words'].items():
            if key.replace(' ', '') in newCaption:
                newCaption = newCaption.replace(key, value)#.capitalize()
    return newCaption


def remove_files():
    curDir = os.getcwd()
    try:
        if 'downloads' in os.listdir(curDir):
            os.chdir('downloads')
            for dir in os.listdir(os.getcwd()):
                os.remove(dir)
    except Exception as err:
        print(err)
    os.chdir(curDir)


async def send_message(source, message, is_media=False):
    try:
        destinations = source['destinations']
        file_path = message.text.capitalize() if message.text else None
        caption = configure_text(message.caption).capitalize() if message.caption else None
        if destinations:
            if message.poll:
                pass
            elif is_media and (source['allow_image'] or source['allow_video'] or source['allow_audio'] or source['allow_document']):
                print(message, "Message")
                file_path = await app.download_media(message,in_memory=True)

            if message.photo and source['allow_image']:
                for destination in destinations:
                    title, destination = destination
                    await app.send_photo(destination, photo=file_path, caption=caption)
            elif message.document and source['allow_document']:
                for destination in destinations:
                    title, destination = destination
                    await app.send_document(destination, document=file_path, caption=caption)
            elif message.video and source['allow_video']:
                for destination in destinations:
                    title, destination = destination
                    await app.send_video(destination, video=file_path, caption=caption)
            elif message.voice and source['allow_audio']:
                for destination in destinations:
                    title, destination = destination
                    await app.send_audio(destination, audio=file_path, caption=caption)
            elif message.text and source['allow_text']:
                for destination in destinations:
                    title, destination = destination
                    f=print(f"Title = {title}, destination = {destination}")
                    if configure_text(message.text): # To avoid sending an empty message
                        await app.send_message(int(destination),text=configure_text(message.text))
            elif message.poll and source['allow_poll']:
                for destination in destinations:
                    title, destination = destination
                    options = [option.text for option in message.poll.options]
                    await app.send_poll(destination, question=message.poll.question, options=options)
            elif message.sticker or message.animation and source['allow_image']:
                if message.animation:
                    for destination in destinations:
                        title, destination = destination
                        await app.send_animation(destination, animation=file_path,caption=caption)
                elif message.sticker:
                    for destination in destinations:
                        title, destination = destination
                        await app.send_sticker(destination, sticker=file_path)

    except Exception as err:
        print(err)
        print('[message for the developer]: This error happened in the send_message()')



@app.on_message()
async def process_channel_message(client, message):
    try:
        id = message.chat.id
        source = settings['sources'].get(str(id), None)

        if source:
            try:
                await send_message(source, message, message.media)
            except errors.UsernameNotOccupied as err:
                print(err)
            except ConnectionError as err:
                print('conn error')
            except Exception as err:
                print(err)
                print(
                    '[message for the developer]: This error happened in the process_channel_message() [inner]')
                print(message)
    except Exception as err:
        print(err)
        print('[message for the developer]: This error happened in the process_channel_message() [outer]')


async def reconnect():
    try:
        username = input("Give your session a username(optional): ")
        api_id = int(input('api_id: '))
        api_hash = input('api_hash: ').replace(' ', '')
        phone_number = input(
            'phone number: +').replace('+', '').replace(' ', '')
        session_name = username if len(username) > 0 else session_name
        app = Client(session_name.split('.')[0], api_id=api_id,
                     api_hash=api_hash,
                     phone_number=phone_number)
        async with app:
            await app.get_me()
            print("Created session!")
            time.sleep(2)

    except Exception as err:
        print(err)

        os.remove(session_name)
        print('restart the program and login again')
        input('ENTER to exit...')
        sys.exit()
        input()


async def start_app():
    global app
    
    try:
        async with Client(session_name) as app:
            await app.get_me()

    except AttributeError as err:
        await reconnect()
    except ConnectionError as err:
        print(err)
        print("Poor connection!!!")
        sys.exit()
    except Exception as err:
        print(err)
        print("in the start_app function")
        sys.exit()


def main():
    try:
        remove_files()
        os.system('clear')
        print("Main Page")
        print('0, To quit the program')
        options = "1, Add or Remove a Source\n2, Key Words\n3, Preferences\n4, Add Destination\n5, Remove destination"
        print(options)
        cmd = input("enter: ")
        os.system('clear')

        if cmd == '1':
            add_channel_page()
        elif cmd == '2':
            configure_key_words_page()
        elif cmd == '3':
            set_preferences_page()
        elif cmd == '4':
            add_destination()
        elif cmd == '5':
            remove_destination()
        elif cmd == '0':
            print('Quiting...')
            sys.exit()
        else:
            print('invalid input')

    except KeyboardInterrupt as err:
        sys.exit()
    except Exception as err:
        print(err)
        input('here')
    main()


##New Functions

async def update():

    for source in settings['sources']:
        channel = await check_exist(source)
        if channel:
            val = settings['sources'][source]
            val['name'] = channel.title
            settings['sources'][source] = val
            settings['UPDATE'] = False
        # settings['sources'][channel.id] = val
    with open(settings_file_name, 'w') as file:
        json.dump(settings, file)

if __name__ == '__main__':
    
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(start_app())
    options = "1, Start bot\n2, Configure bot"
    print(options)
    cmd = input('Choose: ')
    try:
        if cmd == '1':
            try:
                print(f'Listening to {len(settings["sources"])} sources')
                app.run()
            except Exception as err:
                print(err)
                asyncio.run(start_app()) #loop.run_until_complete(start_app())
                input('Hit enter to restart...')
                sys.exit()
        elif cmd == '2':
            main()
        else:
            print('invalid input')
    except KeyboardInterrupt as err:
        remove_files()
        sys.exit()

    except Exception as err:
        print(err)

# if settings.get('UPDATE', None):
#     asyncio.run(update())
# else: 
#     print('up to date')
# # asyncio.run(update())


# print(app.loop.run_until_complete(check_exist(id="-1001531935230")))
