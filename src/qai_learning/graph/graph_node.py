from PySide6.QtCore import QObject, QRectF, Qt, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPen,
)
from PySide6.QtWidgets import (
    QGraphicsItem,
)


class NodeSignals(QObject):
    clicked = Signal(int, str)


class GraphNode(QGraphicsItem):
    def __init__(self, node_id, text, initial_status="pending", radius=20):
        super().__init__()
        self.node_id = node_id
        self.text = text
        self.radius = radius
        self.status = initial_status
        self.signals = NodeSignals()
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setCursor(Qt.PointingHandCursor)

    def set_status(self, new_status):
        self.status = new_status
        self.update()

    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def paint(self, painter, option, widget):
        # Dobieranie kolorów na podstawie trójstanowej logiki
        if self.status == "done":
            bg_color = QColor(76, 175, 80)  # Zielony
            text_color = QColor(255, 255, 255)
        elif self.status == "in_progress":
            bg_color = QColor(255, 152, 0)  # Pomarańczowy (zapisana odpowiedź)
            text_color = QColor(255, 255, 255)
        else:
            bg_color = QColor(255, 255, 255)  # Biały (brak akcji)
            text_color = QColor(0, 0, 0)

        # Rysowanie kółka węzła
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(bg_color))
        painter.drawEllipse(
            -self.radius, -self.radius, 2 * self.radius, 2 * self.radius
        )

        # Rysowanie tekstu (numer pytania)
        painter.setPen(QPen(text_color))
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.boundingRect(), Qt.AlignCenter, str(self.node_id))

    def mousePressEvent(self, event):
        self.signals.clicked.emit(self.node_id, self.text)
        super().mousePressEvent(event)
