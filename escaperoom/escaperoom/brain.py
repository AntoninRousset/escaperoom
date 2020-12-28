NEED_STATES_CHECK_SIG = 17


def check_states(num):
    print('TODO')
    return


try:
    from uwsgi import register_signal
    register_signal(NEED_STATES_CHECK_SIG, 'worker', check_states)
except ModuleNotFoundError:
    print("uwsgi cannot be imported, states checks won't work")


def request_states_check():
    try:
        import uwsgi
        uwsgi.signal(NEED_STATES_CHECK_SIG)
    except ModuleNotFoundError:
        check_states(NEED_STATES_CHECK_SIG)
