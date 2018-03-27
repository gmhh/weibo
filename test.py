class father:
    def f(self):
        print(self.f2())

    def f2(self):
        return "f2"


class son(father):
    def f2(self):
        return "son f2"

s = son()
s.f()