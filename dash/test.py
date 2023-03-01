


class A(object):
    def __init__(self):
        pass

    def __call__(*args, **kwargs):
        print('called ', args, kwargs)


a =A()
a('hello')        