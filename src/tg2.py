import botogram
import logbook
import acl
import logging
from plumbum import local, CommandNotFound
import yaml
import argparse
from os import environ, path
from sys import exit, argv

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

"""
Functions
"""


def configfileload(filename):
    with open(filename) as configfile:
        return yaml.safe_load(configfile)


def check_argument(mess):
    print(mess.parsed_text)
    if mess.parsed_text and mess.parsed_text.__contains__("plain"):
        return str(mess.parsed_text[1]).strip()
    else:
        return


def execute_and_check(command, args):
    try:
        binary = local
        retval = binary[command][args].run(retcode=None)
        """
        using run to capture standard error as well
        see https://github.com/tomerfiliba/plumbum/blob/master/docs/local_commands.rst
        """
        if retval[0] == 0:
            return retval[1]
        else:
            errcode = retval[2]
            logging.error(errcode)
    except CommandNotFound:
        logging.error(f"command {command} not found in path")

def apt_install(aptlist):
    if aptlist:
        log.info('Updating apt sources')
        print(execute_and_check("sudo", ["apt", "update"]))
        log.info('Installing packages')
        print(execute_and_check("sudo", ["apt", "install", aptlist, "-y"]))

def add_markdown_syntax():
    """TODO"""
    pass


def check_config_file():
    """TODO"""
    pass


def check_env(env):
    """Check environment"""
    envkey = environ.get(env)
    if envkey is not None:
        return envkey
    else:
        log.error(f"ERROR: no token provided, check {env} variable")
        exit(1)

def check_file_arg(a):
    """ Check if file exist"""
    if path.exists(a):
       try:
         validyaml = yaml.safe_load(a)
       except ValueError as e:
         return False
       return True


"""
Prestart
"""

log = logbook.Logger("botogram bot")
log.info("Starting...")
log.info("Preflight check...")
bot = botogram.create(check_env("TGTOKEN"))

parser = argparse.ArgumentParser("tg2")
parser.add_argument("configfile", help="Configuration file", type=str)
args = parser.parse_args()
if check_file_arg(args.configfile):
    cmdlist = configfileload(args.configfile)

"""
Base commands
"""


@bot.command("version")
def version_command(chat, message, args):
    """Bot version and link"""
    chat.send("TG2 *Version*: 0.0.1", syntax="markdown")


@bot.command("echo")
def echo_command(chat, message, args):
    """Echo command"""
    checkedmsg = check_argument(message)
    if checkedmsg:
        chat.send(check_argument(message))
    else:
        log.error("No argument given")
        chat.send("ERROR: No input given")


@bot.command("info")
def info_command(chat, message, args):
    """Return info about user, channel"""
    m = message
    out = f"*Your Name:* {str(m.sender.name)}\n*Your id*: `{str(m.sender.id)}` \n*Chat id*: `{str(m.chat.id)}`\n*Chat title*: _{str(m.chat.title)}_"
    chat.send(out, syntax="markdown")


@bot.command("reload")
def reload_command(chat, message, args):
    """TODO: Hot reload configuration """
    pass

@bot.command("config")
def print_config(chat, message, args):
    """Print configfile"""
    chat.send(f"```{(yaml.dump(cmdlist, default_flow_style=False)).strip()}```", syntax="markdown")

"""
Run
"""

class BotCommands(botogram.Component):
    def __init__(self):
        for name, cmd in cmdlist["commands"].items():

            def reply(message: str, chat: int):
                """helpers
                c = command, parse message to obtain command in list
                r = returnlist, return the value of command objent from loop
                """
                c = message.parsed_text[0].text[1:].split("@")[0]
                r = cmdlist["commands"][c]
                posargs = check_argument(message)

                if r["args"] is not None and "$1" in r["args"]:
                    """check if args is '$1' and create a new dict with the argument given"""
                    filledargs = [
                        str(posargs).strip() if x == "$1" else x for x in r["args"]
                    ]
                    cmdwithargs = execute_and_check(r["command"], filledargs)
                else:
                    cmdwithargs = execute_and_check(r["command"], r["args"])

                if r["output"] is not None and r["output"] == "code":
                    chat.send(f"```\n{str(cmdwithargs)}\n```", syntax="markdown")
                else:
                    chat.send(str(cmdwithargs), syntax="plain")

            reply.__doc__ = cmd["description"]
            self.add_command(name, reply, order=int(cmd["id"]))


if __name__ == "__main__":
    if cmdlist["about"]:
        bot.about = cmdlist["about"]
    if cmdlist["setup"]:
        apt_install(cmdlist['setup'])
    mycmd = BotCommands()
    acl = acl.MyACL()
    acl.allowed = cmdlist["myid"]
    log.info(f"Bot username: {bot.itself.username}")
    bot.use(mycmd, acl)
    bot.run()
