# coding:utf-8


from flask_script import Manager
from main import app, scheduler
from flask_script import Shell
from main.models import User, UserLog
from getpass import getpass
from werkzeug.security import generate_password_hash


# 初始化管理器
manager = Manager(app)


def make_shell_context():
    return dict(app=app, User=User, UserLog=UserLog, scheduler=scheduler)


manager.add_command('shell', Shell(make_context=make_shell_context))


@manager.command
def adduser():
    name = input('Username> ')
    email = input('Email> ')
    input_password = getpass('Password> ')
    new = User(name=name, email=email, pwd=generate_password_hash(input_password))
    new.save()
    print("new user <%s> created" % name)


if __name__ == "__main__":
    manager.run()
