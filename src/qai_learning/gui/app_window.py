import json
import os

from PySide6.QtCore import QPointF, Qt, QTimer
from PySide6.QtGui import (
    QKeySequence,
    QShortcut,
)
from PySide6.QtWidgets import (
    QComboBox,
    QGraphicsScene,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from qai_learning.graph.graph_edge import GraphEdge
from qai_learning.graph.graph_node import GraphNode
from qai_learning.graph.graph_view import GraphView
from qai_learning.utils.resources import load_json, save_json

STATE_FILE = "graph_state.json"
ANSWERS_FILE = "user_answers.json"


class ChatBubble(QWidget):
    def __init__(self, text, role="user"):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)

        self.msg_label = QLabel(text)
        self.msg_label.setWordWrap(True)
        self.msg_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # Style based on who is speaking
        if role == "user":
            self.msg_label.setStyleSheet("""
                background-color: #2b5278; 
                color: white; 
                padding: 12px; 
                border-radius: 12px;
                font-size: 15px;
            """)
            layout.addStretch()  # Pushes the bubble to the right
            layout.addWidget(self.msg_label)
        else:
            self.msg_label.setStyleSheet("""
                background-color: #2a2a2a; 
                color: #e0e0e0; 
                padding: 12px; 
                border-radius: 12px;
                font-size: 15px;
                border: 1px solid #444;
            """)
            layout.addWidget(self.msg_label)
            layout.addStretch()  # Pushes the bubble to the left

        # Ensure the bubble doesn't stretch across the whole screen
        self.msg_label.setMaximumWidth(600)


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graf Zagadnień - OuK")
        self.resize(1200, 700)

        self.node_items = {}
        self.total_questions = 0
        self.app_state = self.load_state()
        self.user_answers = self.load_answers()
        self.current_selected_node_id = None

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.setup_graph_view()
        self.setup_detail_view()
        self.load_graph()

    def load_state(self):
        state = load_json("graph_state")
        return state

    def save_state(self):
        save_json("graph_state", self.app_state)

    def load_answers(self):
        ans = load_json("user_answers")
        return ans

    def save_answers_to_file(self):
        save_json("user_answers", self.user_answers)

    def setup_graph_view(self):
        self.scene = QGraphicsScene()
        self.view = GraphView(self.scene)

        graph_container = QWidget()
        container_layout = QGridLayout(graph_container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        self.progress_label = QLabel("Postęp: 0 / 0 (0%)")
        self.progress_label.setStyleSheet("""
            QLabel {
                color: #ffffff; 
                background-color: rgba(30, 30, 30, 0.85); 
                font-size: 15px; 
                font-weight: bold;
                border: 1px solid #4CAF50;
                border-radius: 6px;
                padding: 8px 15px;
                margin: 15px;
            }
        """)

        container_layout.addWidget(self.view, 0, 0)
        container_layout.addWidget(
            self.progress_label, 0, 0, Qt.AlignTop | Qt.AlignRight
        )

        self.stacked_widget.addWidget(graph_container)

    def setup_detail_view(self):
        self.detail_widget = QWidget()
        self.detail_widget.setStyleSheet("background-color: #0d0d0d;")

        main_split_layout = QHBoxLayout(self.detail_widget)
        main_split_layout.setContentsMargins(20, 20, 20, 20)
        main_split_layout.setSpacing(20)

        # LEWA STRONA
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self.question_label = QLabel("")
        self.question_label.setStyleSheet("color: #FFFFFF; font-size: 24px;")
        self.question_label.setWordWrap(True)
        self.question_label.setAlignment(Qt.AlignCenter)

        btn_layout = QHBoxLayout()

        self.back_button = QPushButton("← Wróć do grafu")
        self.back_button.setStyleSheet("""
            QPushButton { background-color: #333333; color: white; font-size: 16px; padding: 12px 20px; border-radius: 6px; }
            QPushButton:hover { background-color: #555555; }
        """)
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.clicked.connect(self.navigate_back)

        self.toggle_status_btn = QPushButton()
        self.toggle_status_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_status_btn.clicked.connect(self.toggle_current_node_status)

        btn_layout.addStretch()
        btn_layout.addWidget(self.back_button)
        btn_layout.addSpacing(20)
        btn_layout.addWidget(self.toggle_status_btn)
        btn_layout.addStretch()

        left_layout.addStretch()
        left_layout.addWidget(self.question_label)
        left_layout.addSpacing(60)
        left_layout.addLayout(btn_layout)
        left_layout.addStretch()

        # PRAWA STRONA (Chat Interface)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)

        # 1. Header with Status and Provider Selection
        header_layout = QHBoxLayout()
        chat_label = QLabel("Tutor AI:")
        chat_label.setStyleSheet("color: #AAAAAA; font-size: 18px; font-weight: bold;")

        self.model_selector = QComboBox()
        self.model_selector.addItems(["Llama 3 (Lokalnie)", "GPT-4o (Cloud)"])
        self.model_selector.setStyleSheet("""
            QComboBox { background-color: #333; color: white; border-radius: 4px; padding: 5px; }
        """)

        self.save_status_label = QLabel("")
        self.save_status_label.setStyleSheet(
            "color: #4CAF50; font-size: 14px; font-weight: bold;"
        )

        header_layout.addWidget(chat_label)
        header_layout.addStretch()
        header_layout.addWidget(self.model_selector)
        header_layout.addWidget(self.save_status_label)

        # 2. Chat History Area (Scrollable)
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical { background: #1a1a1a; width: 10px; }
            QScrollBar::handle:vertical { background: #555; border-radius: 5px; }
        """)

        self.chat_history_widget = QWidget()
        self.chat_history_widget.setStyleSheet("background-color: transparent;")
        self.chat_layout = QVBoxLayout(self.chat_history_widget)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(10)
        self.chat_scroll.setWidget(self.chat_history_widget)

        # 3. Input Area
        input_layout = QHBoxLayout()

        self.answer_input = QTextEdit()
        self.answer_input.setPlaceholderText("Napisz odpowiedź lub zadaj pytanie...")
        self.answer_input.setFixedHeight(
            70
        )  # Zamiast dużego okna, mniejsze pole do pisania
        self.answer_input.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a; 
                color: #FFFFFF; 
                font-size: 15px; 
                border: 1px solid #333333; 
                padding: 10px; 
                border-radius: 8px;
            }
            QTextEdit:focus { border: 1px solid #4CAF50; }
        """)

        self.send_button = QPushButton("Wyślij")
        self.send_button.setCursor(Qt.PointingHandCursor)
        self.send_button.setFixedSize(80, 70)
        self.send_button.setStyleSheet("""
            QPushButton { background-color: #4CAF50; color: white; font-weight: bold; border-radius: 8px; }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.send_button.clicked.connect(self.handle_send_message)

        input_layout.addWidget(self.answer_input)
        input_layout.addWidget(self.send_button)

        # Assemble Right Side
        right_layout.addLayout(header_layout)
        right_layout.addWidget(self.chat_scroll)
        right_layout.addLayout(input_layout)

        main_split_layout.addWidget(left_widget, stretch=1)
        main_split_layout.addWidget(right_widget, stretch=1)

        self.stacked_widget.addWidget(self.detail_widget)

        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self.detail_widget)
        self.save_shortcut.activated.connect(self.save_current_answer)

    def update_progress_display(self):
        done_count = sum(
            1 for state in self.app_state.values() if state.get("status") == "done"
        )
        if self.total_questions > 0:
            percentage = int((done_count / self.total_questions) * 100)
        else:
            percentage = 0
        self.progress_label.setText(
            f"Postęp: {done_count} / {self.total_questions} ({percentage}%)"
        )

    def handle_send_message(self):
        user_text = self.answer_input.toPlainText().strip()
        if not user_text:
            return

        # 1. Add User Message to UI
        user_bubble = ChatBubble(user_text, role="user")
        self.chat_layout.addWidget(user_bubble)
        self.answer_input.clear()

        # Scroll to bottom smoothly
        self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        )

        # 2. Mock AI Response (We will replace this with real AI later)
        QTimer.singleShot(500, lambda: self.mock_ai_typing())

    def mock_ai_typing(self):
        ai_response = "To świetne pytanie! Pomyślmy o tym w ten sposób... (Tutaj podłączymy LLM w następnym kroku)."
        ai_bubble = ChatBubble(ai_response, role="ai")
        self.chat_layout.addWidget(ai_bubble)

        self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        )

    def update_node_visual_state(self, node_id_str):
        """Metoda dynamicznie aktualizująca kolor okręgu na podstawie wpisanego tekstu i statusu ukończenia"""
        if node_id_str in self.node_items:
            status = self.app_state.get(node_id_str, {}).get("status", "pending")
            has_answer = bool(self.user_answers.get(node_id_str, "").strip())

            if status == "done":
                visual_status = "done"
            elif has_answer:
                visual_status = "in_progress"
            else:
                visual_status = "pending"

            self.node_items[node_id_str].set_status(visual_status)

    def save_current_answer(self):
        if self.current_selected_node_id:
            answer_text = self.answer_input.toPlainText()
            self.user_answers[self.current_selected_node_id] = answer_text
            self.save_answers_to_file()

            # Odświeżenie wyglądu węzła po zapisie odpowiedzi
            self.update_node_visual_state(self.current_selected_node_id)

            self.save_status_label.setText("✔ Zapisano!")
            QTimer.singleShot(2000, lambda: self.save_status_label.setText(""))

    def navigate_back(self):
        self.save_current_answer()
        self.stacked_widget.setCurrentWidget(self.stacked_widget.widget(0))

    def show_question(self, node_id, text):
        self.current_selected_node_id = str(node_id)
        self.question_label.setText(f"Pytanie {node_id}:\n\n{text}")

        existing_answer = self.user_answers.get(self.current_selected_node_id, "")
        self.answer_input.setPlainText(existing_answer)
        self.save_status_label.setText("")

        status = self.app_state.get(self.current_selected_node_id, {}).get(
            "status", "pending"
        )
        if status == "done":
            self.toggle_status_btn.setText("✖ Odznacz jako zrobione (Cofnij)")
            self.toggle_status_btn.setStyleSheet("""
                QPushButton { background-color: #FF9800; color: white; font-size: 16px; padding: 12px 20px; border-radius: 6px; font-weight: bold;}
                QPushButton:hover { background-color: #F57C00; }
            """)
        else:
            self.toggle_status_btn.setText("✔ Oznacz jako zrobione")
            self.toggle_status_btn.setStyleSheet("""
                QPushButton { background-color: #4CAF50; color: white; font-size: 16px; padding: 12px 20px; border-radius: 6px; font-weight: bold;}
                QPushButton:hover { background-color: #45a049; }
            """)

        self.stacked_widget.setCurrentWidget(self.detail_widget)

    def toggle_current_node_status(self):
        if not self.current_selected_node_id:
            return

        if self.current_selected_node_id not in self.app_state:
            self.app_state[self.current_selected_node_id] = {}

        current_status = self.app_state[self.current_selected_node_id].get(
            "status", "pending"
        )
        new_status = "pending" if current_status == "done" else "done"

        self.app_state[self.current_selected_node_id]["status"] = new_status
        self.save_state()

        # Odświeżenie węzła i paska postępu
        self.update_node_visual_state(self.current_selected_node_id)
        self.update_progress_display()

        self.show_question(
            int(self.current_selected_node_id),
            self.question_label.text().split("\n\n")[1],
        )

    def load_graph(self):
        data = load_json("graph_config")
        # try:
        #     with open("graph_config.json", "r", encoding="utf-8") as f:
        #         data = json.load(f)
        # except FileNotFoundError:
        #     print("Nie znaleziono pliku graph_config.json!")
        #     return

        nodes_data = data.get("nodes", [])
        edges_data = data.get("edges", [])

        self.total_questions = len(nodes_data)

        adj_list = {n["id"]: [] for n in nodes_data}
        for e in edges_data:
            adj_list[e["from"]].append(e["to"])

        levels = {1: 0}
        queue = [1]
        while queue:
            curr = queue.pop(0)
            for neighbor in adj_list[curr]:
                if neighbor not in levels:
                    levels[neighbor] = levels[curr] + 1
                    queue.append(neighbor)

        for n in nodes_data:
            if n["id"] not in levels:
                levels[n["id"]] = 0

        level_counts = {}
        for nid, lvl in levels.items():
            level_counts[lvl] = level_counts.get(lvl, 0) + 1

        current_counts = {}
        positions = {}
        x_spacing = 100
        y_spacing = 120

        for n in nodes_data:
            nid = n["id"]
            lvl = levels[nid]
            idx = current_counts.get(lvl, 0)
            current_counts[lvl] = idx + 1

            total_in_lvl = level_counts[lvl]
            x = (idx - total_in_lvl / 2) * x_spacing
            y = lvl * y_spacing
            positions[nid] = QPointF(x, y)

        for e in edges_data:
            from_pos = positions.get(e["from"])
            to_pos = positions.get(e["to"])
            if from_pos and to_pos:
                edge_item = GraphEdge(from_pos, to_pos)
                self.scene.addItem(edge_item)

        for n in nodes_data:
            pos = positions[n["id"]]
            node_id_str = str(n["id"])

            status = self.app_state.get(node_id_str, {}).get("status", "pending")
            has_answer = bool(self.user_answers.get(node_id_str, "").strip())

            # Logika sprawdzania stanu początkowego przy ładowaniu aplikacji
            if status == "done":
                visual_status = "done"
            elif has_answer:
                visual_status = "in_progress"
            else:
                visual_status = "pending"

            node_item = GraphNode(n["id"], n["text"], initial_status=visual_status)
            node_item.setPos(pos)
            node_item.signals.clicked.connect(self.show_question)

            self.scene.addItem(node_item)
            self.node_items[node_id_str] = node_item

        self.update_progress_display()
