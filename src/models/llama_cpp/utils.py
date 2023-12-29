class MockTensor:
    def __init__(self, data, dim=0):
        self.data = data
        self._dim = dim

    def to(self, device):
        # Mimics moving to a device (does nothing in mock)
        return self

    def dim(self):
        # Mimics moving to a device (does nothing in mock)
        return self._dim

    def __str__(self):
        return self.data

    def __repr__(self):
        return repr(self.data)

