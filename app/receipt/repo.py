from sqlalchemy.orm import Session


class ReceiptRepository:
    def __init__(self, session: Session):
        self.session = session
