import configparser
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_all_conf(config_pah):
    config = configparser.ConfigParser()
    config.read('%s/conf/%s' % (BASE_DIR, config_pah))
    # 遍历所有节点
    sections = {}
    for cron_sect in config.sections():
        sections[cron_sect] = get_section(config, cron_sect)
    return sections

def get_section(config, sect):

    options = {}
    for option in config.options(sect):
        print(option)
        options[option] = config[sect][option]
    return options
