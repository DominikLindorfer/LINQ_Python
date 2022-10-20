from py_linq import Enumerable

Enumerable([80, 90, 25, 65]).order_by(lambda x: x).take(2).where(lambda x: x > 25).to_list() # results [25, 65, 80, 90]

class tclass:

    def __init__(self, x=5, y=5):
        self.x = x
        self.y = y

    def setxy(self, x_=5, y_=10):
        self.x = x_
        self.y = y_
    
    def setname(self, name = ""):
        self.name = name


clist = [tclass(i, i*2) for i in range(5)]

for i in range(5):
    clist[i].setname("Null")

clist[1].setname("Eins")
clist[2].setname("Zwei")

result = Enumerable(clist).order_by(lambda x: x.x).take(2).where(lambda x: x.x > 0).to_list() 
result[0].x
result[0].y

result = Enumerable(clist).group_by(key_names = ["name"], key=lambda x: x.name).select(lambda g: g.key.name).to_list()
result = Enumerable(clist).group_by(key_names = ["name"], key=lambda x: x.name).select(lambda g: {g.key.name : g.get_data()}).to_list()
result = Enumerable(clist).group_by(key=lambda x: x.name).select(lambda g: g.get_data()).to_list()

for i in result:
    for j in i:
        print(j.name, j.x, j.y)


Enumerable([
    {'value': 1},
    {'value': 2},
    {'value': 3}
]).contains({'value' : 2}, lambda x: x['value'])

Enumerable([80, 90, 25, 65]).contains(26)

clist[0].name

Enumerable(clist).any(lambda x: x.name == 'Drei')
Enumerable(clist).any(lambda x: x.name == 'Null')

students = Enumerable([{ 'name': 'Joe Smith', 'marks': [80, 90, 75]}, { 'name': 'Joanne Smith', 'marks': [67, 89, 91]}])
students.select_many(lambda x: x['marks']).to_list()
students.select(lambda x: x['marks']).to_list()

Enumerable(clist).select(lambda x: x.y).where(lambda y: y > 3).to_list()


Enumerable([80, 90, 25, 65, 80]).index_of(80)
Enumerable([80, 90, 25, 65, 80]).last_index_of(80)

