
import sys
from PyQt6.QtWidgets import QApplication
from logic import Logic


def main() -> None:
    application: QApplication = QApplication(sys.argv)
    window: Logic = Logic()
    window.show()
    sys.exit(application.exec())


if __name__ == "__main__":
    main()
