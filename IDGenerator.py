import uuid
import base64

class IDGenerator:
    """
        Used to generate time and location unrelated IDs
        use UUID to generate a random 128-bit number and encode it in base64
        then return the first n characters
    """
    def __init__(self, length=10):
        self.length = length

    def get_id(self):
        uuid_code = uuid.uuid4()
        base64_code = base64.b64encode(uuid_code.bytes).decode('utf-8')
        return base64_code[:self.length]
    
if __name__ == "__main__":
    # test for IDGenerator
    print(IDGenerator().get_id())