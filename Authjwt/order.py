class Order:
    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity
        self._filled = False

    def fill(self, warehouse):
        has_inventry = warehouse.has_inventery(
            self.product,
            self.quantity
        )
        if has_inventry:
            has_removed =  warehouse.remove(self.product, self.quantity)
            if has_removed:
                self._filled = True

    def is_filled(self):
        return self._filled
