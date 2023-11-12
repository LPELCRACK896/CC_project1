
class CodeStack:
    content: list

    def __init__(self):
        self.content = []

    def initialize_content(self, content):
        self.content = content

    def push(self, item):
        self.content.append(item)

    def pop(self):
        if len(self.content) > 0:
            return self.content.pop()
        return None

    def seek(self):
        if len(self.content) > 0:
            return self.content[-1]
        return None

    def remove(self):
        if len(self.content) > 0:
            return self.content.pop(0)
        return None

    def size(self):
        return len(self.content)

    def is_empty(self):
        return len(self.content)>0

    def multiple_pop(self, how_many):
        buffer = []

        count = 0
        while count < how_many and self.content:
            buffer.append(self.pop())
            count += 1

        return buffer

    def extend(self, position: int, new_content: list):
        """

        :param new_content: list of items to add
        :param position: 0 to set at the start, -1 to set at the end
        :return:
        """
        if not (position == 0 or position == -1):
            position = -1

        if position == -1:
            self.content.extend(new_content)
        else:  # position = 0
            new_content.extend(self.content)
            self.content = new_content

    def extend_at_the_start(self, new_content):
        self.extend(0, new_content)

    def extend_at_the_end(self, new_content):
        self.extend(-1, new_content)
