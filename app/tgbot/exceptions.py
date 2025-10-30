class RequestAlreadyExistsError(ValueError):
    def __init__(self, request):
        super().__init__(f"Заявка уже создана (id={request.id})")
        self.request = request
