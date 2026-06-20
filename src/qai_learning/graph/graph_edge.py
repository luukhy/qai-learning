import math

from PySide6.QtCore import QLineF, QPointF, QRectF
from PySide6.QtGui import (
    QBrush,
    QColor,
    QPen,
    QPolygonF,
)
from PySide6.QtWidgets import (
    QGraphicsItem,
)


class GraphEdge(QGraphicsItem):
    def __init__(self, source_point, dest_point, node_radius=20):
        super().__init__()
        self.source_point = source_point
        self.dest_point = dest_point
        self.node_radius = node_radius

    def boundingRect(self):
        return (
            QRectF(self.source_point, self.dest_point)
            .normalized()
            .adjusted(-15, -15, 15, 15)
        )

    def paint(self, painter, option, widget):
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setBrush(QBrush(QColor(100, 100, 100)))

        line = QLineF(self.source_point, self.dest_point)
        if line.length() == 0:
            return

        angle = math.atan2(-line.dy(), line.dx())
        dest_x = self.dest_point.x() - self.node_radius * math.cos(angle)
        dest_y = self.dest_point.y() + self.node_radius * math.sin(angle)
        p2 = QPointF(dest_x, dest_y)
        line.setP2(p2)

        painter.drawLine(line)

        arrow_size = 10
        arrowP1 = p2 - QPointF(
            math.sin(angle + math.pi / 3) * arrow_size,
            math.cos(angle + math.pi / 3) * arrow_size,
        )
        arrowP2 = p2 - QPointF(
            math.sin(angle + math.pi - math.pi / 3) * arrow_size,
            math.cos(angle + math.pi - math.pi / 3) * arrow_size,
        )

        arrowHead = QPolygonF([p2, arrowP1, arrowP2])
        painter.drawPolygon(arrowHead)
