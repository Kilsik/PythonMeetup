from functools import partial

from telegram import Update

from .common import (
    show_future_events,
    edit_event,
    show_event,
    show_speech_list,
    show_start_menu,
    register,
    ask,
    meet,
    donate,
    ask_for_event_title,
    ask_for_event_text,
    delete_event
)


def handle_main_menu(update, context):
    query = update.callback_query.data
    actions = {
        'future_events': show_future_events,
        'create_event': ask_for_event_title
    }
    action = actions.get(
        query,
        partial(show_event, event_id=query)
    )
    if action:
        return action(update, context)


def handle_event_menu(update, context):
    query = update.callback_query.data
    event_id = context.user_data['current_event']
    actions = {
        'speech_list': partial(show_speech_list, event_id=event_id),
        'back': show_start_menu,
        'register': partial(register, event_id=event_id),
        'ask': ask,
        'meet': meet,
        'edit': edit_event,
        'donate': partial(donate, event_id=event_id)
    }
    if action := actions.get(query):
        return action(update, context)


def handle_future_events(update, context):
    query = update.callback_query.data
    if query == 'back':
        return show_start_menu(update, context)
    else:
        event_id = context.user_data['current_event']
        return show_event(update, context, event_id)


def handle_speech_list_menu(update, context):
    query = update.callback_query.data
    event_id = context.user_data.get('current_event')
    if query == 'back':
        return show_event(update, context, event_id)


def handle_edit_event(update, context):
    query = update.callback_query.data
    event_id = context.user_data.get('current_event')
    if query == 'back':
        if event_id:
            return show_event(update, context, event_id)
        else:
            return show_start_menu(update, context)

    actions = {
        'title': ask_for_event_title,
        'text': ask_for_event_text,
        'delete': partial(delete_event, event_id=event_id)
    }
    if action := actions.get(query):
        return action(update, context)


def handle_event_title(update, context):
    if update.message:
        title = update.message.text
        return edit_event(update, context, title=title)

    if context.user_data.get('current_event'):
        return edit_event(update, context)
    else:
        return show_start_menu(update, context)


def handle_event_text(update, context):
    if update.message:
        text = update.message.text
        return edit_event(update, context, text=text)
    return edit_event(update, context)


def handle_users_reply(update, context):
    if update.message:
        user_reply = update.message.text
    elif update.callback_query:
        user_reply = update.callback_query.data
    else:
        return

    if user_reply in ['/start', 'start']:
        user_state = 'START'
    else:
        user_state = context.user_data.get('state')
    state_functions = {
        'START': show_start_menu,
        'HANDLE_MAIN_MENU': handle_main_menu,
        'HANDLE_EVENT_MENU': handle_event_menu,
        'HANDLE_FUTURE_EVENTS': handle_future_events,
        'HANDLE_SPEECH_LIST_MENU': handle_speech_list_menu,
        'HANDLE_EDIT_EVENT': handle_edit_event,
        'HANDLE_EVENT_TITLE': handle_event_title,
        'HANDLE_EVENT_TEXT': handle_event_text
    }
    state_handler = state_functions.get(user_state, show_start_menu)
    next_state = state_handler(
        update=update,
        context=context
    )
    context.user_data['state'] = next_state
