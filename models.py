class User:

    def __init__(self, id):
        self.id = id


    def is_authenticated(self):
        return True


    def is_active(self):
        return True


    def is_anonymous(self):
        return True


    def get_id(self):
        return self.id


    @classmethod
    def get(cls, id):

        return cls(id=id)

