from PyQt6 import uic, QtWidgets, QtCore
import sys
from functools import partial
from operator import itemgetter

# import rating
class rating:
    @staticmethod
    def rating(*_, **__): pass


class StimWindow(QtWidgets.QWidget):
    def __init__(self, parent, dt, ht, htt):
        self.dt = dt
        self.ht = ht
        self.htt = htt
        super().__init__(parent, QtCore.Qt.WindowType.Window)
        uic.loadUi("Stim.ui", self)
        self.stimButton = self.findChild(QtWidgets.QPushButton, "StimButton")
        self.stimButton.clicked.connect(self.stim)
        self.stopButton = self.findChild(QtWidgets.QPushButton, "StopButton")
        self.stopButton.clicked.connect(self.stop)
        self.findChild(QtWidgets.QLineEdit, "DT").setText(str(dt))
        self.findChild(QtWidgets.QLineEdit, "HT").setText(str(ht))
        self.findChild(QtWidgets.QLineEdit, "HTT").setText(str(htt))

    def stim(self):
        rating.rating(rateLevel=0, DT=self.dt, HT=self.ht, HTT=self.htt)

    def stop(self): self.close()


class RatingWindow(QtWidgets.QWidget):
    sens_set = False
    pain_set = False
    tole_set = False

    def __init__(self, parent, session):
        self.result = {}
        self.parent = parent
        self.session = session
        super().__init__(parent, QtCore.Qt.WindowType.Window)
        uic.loadUi("Rating.ui", self)

        self.painLevel = self.findChild(QtWidgets.QSlider, "PainLevel")
        self.stimLevel = self.findChild(QtWidgets.QLineEdit, "StimLevel")
        self.stimButton = self.findChild(QtWidgets.QPushButton, "StimButton")
        self.rateButton = self.findChild(QtWidgets.QPushButton, "RateButton")
        self.stopButton = self.findChild(QtWidgets.QPushButton, "StopButton")
        # self.mA = self.findChild(QtWidgets.QLineEdit, "mA")
        self.sensitivity = self.findChild(QtWidgets.QLineEdit, "Sensitivity")
        self.painOnset = self.findChild(QtWidgets.QLineEdit, "PainOnset")
        self.tolerance = self.findChild(QtWidgets.QLineEdit, "Tolerance")
        self.table = self.findChild(QtWidgets.QTableWidget, "Table")

        self.stimButton.clicked.connect(self.stimulate)
        self.rateButton.clicked.connect(self.rate)
        self.stopButton.clicked.connect(self.stop)

    def stimulate(self):
        self.stimButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.painLevel.setEnabled(False)
        self.rateButton.setEnabled(False)
        global app
        app.processEvents()
        stim = int(self.stimLevel.text())
        rating.rating(rateLevel = stim)
        self.stimButton.setEnabled(True)
        self.stopButton.setEnabled(True)
        self.painLevel.setEnabled(True)
        self.rateButton.setEnabled(True)

    def rate(self):
        self.rateButton.setEnabled(False)
        pain = self.painLevel.value()
        stim = int(self.stimLevel.text())
        rowpos = self.table.rowCount()
        self.table.insertRow(rowpos)
        self.table.setItem(rowpos, 0, QtWidgets.QTableWidgetItem(self.stimLevel.text()))
        self.table.setItem(rowpos, 1, QtWidgets.QTableWidgetItem(str(pain)))
        if pain >= 0 and not self.sens_set:
            self.sens_set = True
            self.sensitivity.setText(str(stim))
            self.result["sensitivity"] = stim
        if pain >= 1 and not self.pain_set:
            self.pain_set = True
            self.painOnset.setText(str(stim))
            self.result["painOnset"] = stim
        if pain == 10 and not self.tole_set:
            self.tole_set = True
            self.tolerance.setText(str(stim))
            self.result["tolerance"] = stim
            self.stop(success=True)
        self.stimLevel.setText(str(stim + 200))

    def stop(self, success=False):
        if success: self.parent.ratingSuccess(self)
        self.close()


class MainWindow(QtWidgets.QMainWindow):
    state = {}

    def __init__(self):
        super().__init__()
        self.sessionButtons = {}
        self.sessions = {}
        uic.loadUi('Main.ui', self)
        # 'S0R0' is for Final Rating
        for buttonName in ['S1R1', 'S1R2', 'S2R1', 'S2R2', 'S0R0']:
            button = self.findChild(QtWidgets.QPushButton, buttonName)
            button.clicked.connect(partial(self.showRating, buttonName))
            self.sessionButtons[buttonName] = button
        self.table = self.findChild(QtWidgets.QTableWidget, "Table")
        self.stim1 = self.findChild(QtWidgets.QPushButton, "Stim1Button")
        self.stim1.clicked.connect(partial(self.showStim, 1))
        self.stim2 = self.findChild(QtWidgets.QPushButton, "Stim2Button")
        self.stim2.clicked.connect(partial(self.showStim, 2))

    def showRating(self, session):
        window = RatingWindow(self, session)
        window.show()

    def showStim(self, num):
        [dt, ht, htt] = itemgetter("dt", "ht", "htt")(self.state[num])
        window = StimWindow(self, dt, ht, htt)
        window.show()

    def ratingSuccess(self, rating):
        self.sessions[rating.session] = rating.result
        self.updateValues(rating.session)
        self.updateTable(rating)
        self.nextButton(rating.session)

    def updateValues(self, session):
        [s, r] = [int(c) for c in session if c.isdigit()]
        ig = itemgetter("sensitivity", "painOnset", "tolerance")
        if s == 0:
            [s,p,t] = ig(self.sessions[session])
            self.findChild(QtWidgets.QLineEdit, "FinalSens").setText(str(s))
            self.findChild(QtWidgets.QLineEdit, "FinalPain").setText(str(p))
            self.findChild(QtWidgets.QLineEdit, "FinalTole").setText(str(t))
        elif r == 2:
            [s1, p1, t1] = ig(self.sessions["S" + str(s) + "R1"])
            [s2, p2, t2] = ig(self.sessions["S" + str(s) + "R2"])
            dt = (s1 + s2) / 2
            po = (p1 + p2) / 2
            t = (t1 + t2) / 2
            ht = po + (t-po) * 0.5
            htt = po + (t-po) * 0.75
            self.state[s] = {"dt": dt, "ht": ht, "htt": htt}
            self.findChild(QtWidgets.QLineEdit, "DT"+str(s)).setText(str(dt))
            self.findChild(QtWidgets.QLineEdit, "HT"+str(s)).setText(str(ht))
            self.findChild(QtWidgets.QLineEdit, "HTT"+str(s)).setText(str(htt))
            self.findChild(QtWidgets.QPushButton, "Stim"+str(s)+"Button").setEnabled(True)

    def updateTable(self, rating):
        if self.table.rowCount() < rating.table.rowCount():
            self.table.setRowCount(rating.table.rowCount())
        col = ["S1R1", "S1R2", "S2R1", "S2R2", "S0R0"].index(rating.session) + 1
        for row in range(rating.table.rowCount()):
            self.table.setItem(row, 0, rating.table.item(row, 0).clone())
            self.table.setItem(row, col, rating.table.item(row, 1).clone())

    def nextButton(self, session):
        button = self.sessionButtons[session]
        button.setEnabled(False)
        button.setStyleSheet("background-color: green")
        nextButton = {"S1R1": "S1R2",
                       "S1R2": "S2R1",
                       "S2R1": "S2R2",
                       "S2R2": "S0R0"}
        if session in nextButton:
            self.sessionButtons[nextButton[session]].setEnabled(True)


def main():
    global app
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
