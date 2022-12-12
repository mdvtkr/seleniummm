from selenium.webdriver.support.ui import WebDriverWait
import traceback

def do_web_command(browser, condition, retry_cnt, action, action_param_list=None):
    if action == browser.get:
        print("                 url loading: {0}".format(*action_param_list[0]))
    elif action == browser.close:
        print("                 window closing")
    elif action == browser.switch_to.window:
        print("                 window switching: {0}".format(action))
    else:
        print("                 action: {0}, param: {1}".format(action, action_param_list))

    if action is not None:
        if action_param_list == None:
            action()
        else:
            action(*action_param_list)

    try:
        WebDriverWait(browser, 3).until(condition)
    except BaseException as e:
        try_cnt_left = retry_cnt-1
        if action is None:
            print(f'timeout: - retry left:{try_cnt_left} / waiting {condition}')
        else:
            print(f'timeout: {action.__name__}({action_param_list}) - retry left:{try_cnt_left} / waiting {condition}')

        print(traceback.format_exc())
        if retry_cnt > 0:
            do_web_command(browser, condition, try_cnt_left, action, action_param_list)
        else:
            raise e