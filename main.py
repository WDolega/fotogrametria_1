import math
import sys

import matplotlib.patches as patches
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QComboBox, QLabel, QGridLayout, QPlainTextEdit, QPushButton, QMessageBox, QMainWindow, \
    QApplication, QFileDialog, QLineEdit
from fotogrametria import *


# cessna402 = Airplane('Cessna 402', 132, 428, 8200, 5)
# cessnaT206H = Airplane('Cessna T206H Nav III', 100, 280, 4785, 5)
# vulcan = Airplane('Vulcan Air P68 Observer 2', 135, 275, 6100, 6)
# tencam = Airplane('Tencam MMA', 120, 267, 4572, 6)
#
# ZI = Camera('Z/I DMC IIe 230', 15552, 14144, 5.6 * 10 ** -6, 'R, G, B, NIR', 92 * 10 ** -3, 1.8, 63)
# leica = Camera('Leica DMC II', 25728, 14592, 3.9*10**-6, 'R, G, B, NIR', 92*10**-3, 1.9, 63)
# falcon = Camera('UltraCam Falcon M2 70', 17310, 11310, 6.0*10**-6, 'R, G, B, NIR', 70*10**-3, 1.65, 61)
# eagle = Camera('UltraCam Eagle M2 80', 23010, 14790, 4.6*10**-6, 'R, G, B, NIR', 80*10**-3, 1.35, 61) 22


def countHeight(GSD, camera):
    return GSD * camera.focal_distance / camera.pixel_size


def countRangeX(GSD, camera):
    return GSD * camera.mat_size2


def countRangeY(GSD, camera):
    return GSD * camera.mat_size1


def countMaxFlightHeight(GSD, camera, airplane):
    return airplane.ceiling - countHeight(GSD, camera)


def countBaseX(GSD, camera, P):
    return countRangeX(GSD, camera) * (100 - P) / 100


def countBaseY(GSD, camera, Q):
    return countRangeY(GSD, camera) * (100 - Q) / 100


def countPhotos(GSD, camera, P, Dx):
    return math.ceil(Dx / countBaseX(GSD, camera, P) + 4)


def countStringNumber(GSD, camera, Q, Dy):
    return math.ceil(Dy / countBaseY(GSD, camera, Q))


def countCorrectedBaseX(GSD, camera, P, Dx):
    return Dx / (countPhotos(GSD, camera, P, Dx) - 4)


def countCorrectedBaseY(GSD, camera, Q, Dy):
    return Dy / countStringNumber(GSD, camera, Q, Dy)


def countCorrectedP(GSD, camera, P, Dx):
    return 100 - 100 * countCorrectedBaseX(GSD, camera, P, Dx) / countRangeX(GSD, camera)


def countCorrectedQ(GSD, camera, Q, Dy):
    return 100 - 100 * countCorrectedBaseY(GSD, camera, Q, Dy) / countRangeY(GSD, camera)


def countAvgInterval(GSD, camera, P, Dx, airplane):
    return countCorrectedBaseX(GSD, camera, P, Dx) / airplane.getAvgVelocity()


def countMinInterval(GSD, camera, P, Dx, airplane):
    return 36 * countCorrectedBaseX(GSD, camera, P, Dx) / (10 * airplane.max_velocity)


def countMaxInterval(GSD, camera, P, Dx, airplane):
    return 36 * countCorrectedBaseX(GSD, camera, P, Dx) / (10 * airplane.min_velocity)


def countPhotoNumber(GSD, camera, P, Q, Dx, Dy):
    return countPhotos(GSD, camera, P, Dx) * countStringNumber(GSD, camera, Q, Dy)


def countRaidTime(GSD, camera, P, Q, Dx, Dy, airplane):
    r = countStringNumber(GSD, camera, Q, Dy)
    return (countPhotos(GSD, camera, P, Dx) - 1) * countMinInterval(GSD, camera, P, Dx, airplane) * r \
           + 140 * (r - 1)


def checkWorkTime(GSD, camera, P, Q, Dx, Dy, airplane):
    if countRaidTime(GSD, camera, P, Q, Dx, Dy, airplane) <= airplane.flight_time:
        return true
    else:
        return false


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.timer = QTimer(self)
        self.textArea = QPlainTextEdit()
        self.textArea.setReadOnly(True)
        # self.textArea.setStyleSheet("border: 3px solid red; background-color: black; color: white")
        self.textArea.setStyleSheet("border: 3px solid red; background-image: url(grey.png)")
        self.textArea.setFont(QtGui.QFont('Courier', 10))
        self.lab1 = QLabel('Ustaw parametry nalotu')
        self.lab4 = QLabel('Zapisz plik na dysk')
        self.lab5 = QLabel('Wyczyść konsolę')
        self.lab1.setMaximumSize(280, 35)
        self.lab4.setMaximumWidth(230)
        self.lab5.setMaximumWidth(230)
        myFont = QtGui.QFont('Courier', 14)
        # myFont.setBold(True)
        self.lab1.setFont(myFont)
        self.lab4.setFont(QtGui.QFont('Courier', 13))
        self.lab5.setFont(QtGui.QFont('Courier', 13))
        self.lab6 = QLabel('Ustawienia')
        self.lab6.setMaximumHeight(50)
        self.lab7 = QLabel(':Samolot')
        self.lab8 = QLabel(':Kamera')
        self.lab9 = QLabel(':Dx [m]')
        self.lab10 = QLabel(':Dy [m]')
        self.lab11 = QLabel(':GSD [cm]')
        self.lab12 = QLabel(':min p [%]')
        self.lab13 = QLabel(':min q [%]')
        self.lab6.setFont(QtGui.QFont('Courier', 13))
        self.lab7.setFont(QtGui.QFont('Courier', 10))
        self.lab8.setFont(QtGui.QFont('Courier', 10))
        self.lab9.setFont(QtGui.QFont('Courier', 10))
        self.lab10.setFont(QtGui.QFont('Courier', 10))
        self.lab11.setFont(QtGui.QFont('Courier', 10))
        self.lab12.setFont(QtGui.QFont('Courier', 10))
        self.lab13.setFont(QtGui.QFont('Courier', 10))
        self.comb7 = QComboBox()
        self.comb8 = QComboBox()
        self.comb7.setFont(QtGui.QFont('Courier', 10))
        self.comb8.setFont(QtGui.QFont('Courier', 10))
        list7 = ['Cessna 402', 'Cessna T206H NAV III', 'Vulcan Air P68 Observer 2', 'Tencam MMA']
        list8 = ['Z/I DMC IIe 230', 'Leica DMC III', 'UltraCam Falcon M2 70', 'UltraCam Eagle M2 80']
        self.comb7.addItems(list7)
        self.comb8.addItems(list8)
        self.comb7.setMaximumSize(230, 28)
        self.comb8.setMaximumSize(230, 28)
        self.comb7.setStyleSheet("border: 2px solid red")
        self.comb8.setStyleSheet("border: 2px solid black")
        self.dx_edt = QLineEdit()
        self.dy_edt = QLineEdit()
        self.gsd_edt = QLineEdit()
        self.p_edt = QLineEdit()
        self.q_edt = QLineEdit()
        self.dx_edt.setFont(QtGui.QFont('Courier', 10))
        self.dy_edt.setFont(QtGui.QFont('Courier', 10))
        self.gsd_edt.setFont(QtGui.QFont('Courier', 10))
        self.p_edt.setFont(QtGui.QFont('Courier', 10))
        self.q_edt.setFont(QtGui.QFont('Courier', 10))
        self.dx_edt.setMaximumSize(230, 28)
        self.dy_edt.setMaximumSize(230, 28)
        self.gsd_edt.setMaximumSize(230, 28)
        self.p_edt.setMaximumSize(230, 28)
        self.q_edt.setMaximumSize(230, 28)
        self.dx_edt.setStyleSheet("border: 2px solid red")
        self.dy_edt.setStyleSheet("border: 2px solid black")
        self.gsd_edt.setStyleSheet("border: 2px solid red")
        self.p_edt.setStyleSheet("border: 2px solid black")
        self.q_edt.setStyleSheet("border: 2px solid red")
        load_btn = QPushButton('Ustaw port', self)
        count_btn = QPushButton('Oblicz', self)
        end_btn = QPushButton('&Koniec', self)
        save_btn = QPushButton('Zapisz dane', self)
        clear_btn = QPushButton('Wyczyść', self)
        draw_btn = QPushButton('Rysuj', self)
        end_btn.resize(end_btn.sizeHint())
        # load_btn.setMaximumWidth(245)
        # count_btn.setMaximumWidth(245)
        # save_btn.setMaximumWidth(245)
        # clear_btn.setMaximumWidth(245)
        # end_btn.setMaximumWidth(245)
        load_btn.setFont(QtGui.QFont('Courier', 13))
        count_btn.setFont(QtGui.QFont('Courier', 13))
        save_btn.setFont(QtGui.QFont('Courier', 13))
        clear_btn.setFont(QtGui.QFont('Courier', 13))
        end_btn.setFont(QtGui.QFont('Courier', 13))
        draw_btn.setFont(QtGui.QFont('Courier', 13))
        load_btn.setStyleSheet('QPushButton { background-color: red; color: white; font: bold}'
                               'QPushButton:pressed { background-color: black}')
        count_btn.setStyleSheet('QPushButton { background-color: black; color: white; font: bold}'
                                'QPushButton:pressed { background-color: grey}')
        save_btn.setStyleSheet('QPushButton { background-color: red; color: white; font: bold}'
                               'QPushButton:pressed { background-color: black}')
        draw_btn.setStyleSheet('QPushButton { background-color: black; color: white; font: bold}'
                               'QPushButton:pressed { background-color: grey}')
        clear_btn.setStyleSheet('QPushButton { background-color: red; color: white; font: bold}'
                                'QPushButton:pressed { background-color: grey}')
        end_btn.setStyleSheet('QPushButton { background-color: black; color: white; font: bold}'
                              'QPushButton:pressed { background-color: black}')
        layout = QGridLayout()
        layout.addWidget(self.lab1, 0, 3, 1, 2)
        # layout.addWidget(self.lab4, 9, 3, 1, 2)
        # layout.addWidget(self.lab5, 11, 3, 1, 2)
        layout.addWidget(self.lab7, 1, 4, 1, 1)
        layout.addWidget(self.lab8, 2, 4, 1, 1)
        layout.addWidget(self.lab9, 3, 4, 1, 1)
        layout.addWidget(self.lab10, 4, 4, 1, 1)
        layout.addWidget(self.lab11, 5, 4, 1, 1)
        layout.addWidget(self.lab12, 6, 4, 1, 1)
        layout.addWidget(self.lab13, 7, 4, 1, 1)
        layout.addWidget(self.comb7, 1, 3, 1, 1)
        layout.addWidget(self.comb8, 2, 3, 1, 1)
        layout.addWidget(self.dx_edt, 3, 3, 1, 1)
        layout.addWidget(self.dy_edt, 4, 3, 1, 1)
        layout.addWidget(self.gsd_edt, 5, 3, 1, 1)
        layout.addWidget(self.p_edt, 6, 3, 1, 1)
        layout.addWidget(self.q_edt, 7, 3, 1, 1)
        layout.addWidget(end_btn, 12, 3, 1, 2)
        layout.addWidget(count_btn, 8, 3, 1, 2)
        layout.addWidget(save_btn, 9, 3, 1, 2)
        layout.addWidget(draw_btn, 10, 3, 1, 2)
        layout.addWidget(clear_btn, 11, 3, 1, 2)
        layout.setColumnStretch(3, 1)
        layout.addWidget(self.textArea, 0, 0, 14, 3)
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        end_btn.clicked.connect(self.end)
        count_btn.clicked.connect(self.count)
        save_btn.clicked.connect(self.save_file)
        draw_btn.clicked.connect(self.draw)
        clear_btn.clicked.connect(self.clear_wind)
        self.setGeometry(500, 250, 800, 680)
        self.setStyleSheet('background-color: white')
        # self.setFont(myFont)
        self.setCentralWidget(widget)
        self.setWindowIcon(QIcon("pw.png"))
        self.setWindowTitle('Fotogrametria - nalot fotogrametryczny')
        self.show()

    def end(self):
        self.close()

    def count(self):
        global cam, plane
        try:
            dx = float(self.dx_edt.text())
            dy = float(self.dy_edt.text())
            gsd = float(self.gsd_edt.text()) / 100
            p = float(self.p_edt.text())
            q = float(self.q_edt.text())
            if p > 100 or q > 100:
                QMessageBox.warning(self, 'Błąd!', '  Wprowadź poprawne dane!         ', QMessageBox.Ok)
            airplane_name = str(self.comb7.currentText())
            camera_name = str(self.comb8.currentText())
            if len(airplane_name) == 0 or len(camera_name) == 0:
                QMessageBox.warning(self, 'Błąd!', '  Wprowadź poprawne dane!         ', QMessageBox.Ok)
            if airplane_name == 'Cessna 402':
                plane = Airplane('Cessna 402', 132, 428, 8200, 5)
            elif airplane_name == 'Cessna T206H NAV III':
                plane = Airplane('Cessna T206H NAV III', 100, 280, 4785, 5)
            elif airplane_name == 'Vulcan Air P68 Observer 2':
                plane = Airplane('Vulcan Air P68 Observer 2', 135, 275, 6100, 6)
            elif airplane_name == 'Tencam MMA':
                plane = Airplane('Tencam MMA', 120, 267, 4572, 6)
            if camera_name == 'Z/I DMC IIe 230':
                cam = Camera('Z/I DMC IIe 230', 15552, 14144, 5.6 * 10 ** -6, 'R, G, B, NIR', 92 * 10 ** -3, 1.8, 63)
            elif camera_name == 'Leica DMC III':
                cam = Camera('Leica DMC III', 25728, 14592, 3.9 * 10 ** -6, 'R, G, B, NIR', 92 * 10 ** -3, 1.9, 63)
            elif camera_name == 'UltraCam Falcon M2 70':
                cam = Camera('UltraCam Falcon M2 70', 17310, 11310, 6.0 * 10 ** -6, 'R, G, B, NIR', 70 * 10 ** -3, 1.65,
                             61)
            elif camera_name == 'UltraCam Eagle M2 80':
                cam = Camera('UltraCam Eagle M2 80', 23010, 14790, 4.6 * 10 ** -6, 'R, G, B, NIR', 80 * 10 ** -3, 1.35,
                             61)
            self.textArea.appendPlainText('Samolot fotogrametryczny: ' + airplane_name)
            self.textArea.appendPlainText('Kamera fotogrametryczna: ' + camera_name)
            self.textArea.appendPlainText('Wymiary obszaru opracowania: ' + str(round(dx)) + ' m ' + 'x '
                                          + str(round(dy)) + ' m')
            self.textArea.appendPlainText('GSD: ' + str(gsd * 100) + ' cm')
            self.textArea.appendPlainText('Wysokość lotu: ' + str(round(countHeight(gsd, cam))) + ' m')
            self.textArea.appendPlainText('Zasięg terenowy x: ' + str(countRangeX(gsd, cam)) + ' m')
            self.textArea.appendPlainText('Zasięg terenowy y: ' + str(countRangeY(gsd, cam)) + ' m')
            # self.textArea.appendPlainText(str(countMaxFlightHeight(gsd, cam, plane)))
            self.textArea.appendPlainText('Wymiary bazy: ' + str(countBaseX(gsd, cam, p)) + ' m' + ' x '
                                          + str(countBaseY(gsd, cam, q)) + ' m')
            # self.textArea.appendPlainText(str(countBaseY(gsd, cam, q)))
            self.textArea.appendPlainText('Liczba zdjęć w szeregu: ' + str(countPhotos(gsd, cam, p, dx)))
            self.textArea.appendPlainText('Liczba szeregów: ' + str(countStringNumber(gsd, cam, q, dy)))
            self.textArea.appendPlainText('Poprawione wymiary bazy: ' + str(round(countCorrectedBaseX(gsd, cam, p, dx)))
                                          + ' m' + ' x ' + str(round(countCorrectedBaseY(gsd, cam, q, dy))) + ' m')
            # self.textArea.appendPlainText(str(countCorrectedBaseY(gsd, cam, q, dy)))
            self.textArea.appendPlainText('Poprawione pokrycie p: ' + str(round(countCorrectedP(gsd, cam, p, dx), 1))
                                          + '%')
            self.textArea.appendPlainText('Poprawione pokrycie q: ' + str(round(countCorrectedQ(gsd, cam, q, dy), 1))
                                          + '%')
            self.textArea.appendPlainText('Zakres czasu potrzebny do zrobienia dwóch zdjęć: ' + 'min '
                                          + str(round(countMinInterval(gsd, cam, p, dx, plane), 1)) + ' s  '
                                          + 'max ' + str(round(countMaxInterval(gsd, cam, p, dx, plane), 1)) + ' s')
            self.textArea.appendPlainText('Liczba zdjęć: ' + str(countPhotoNumber(gsd, cam, p, q, dx, dy)))
            self.textArea.appendPlainText('Minimalny czas wykonania nalotu: '
                                          + str(round((countRaidTime(gsd, cam, p, q, dx, dy, plane) / 60), 1)) + ' min')
            self.textArea.appendPlainText('\n############################################## \n')
        except (ValueError, TypeError, AttributeError, ZeroDivisionError):
            QMessageBox.warning(self, 'Błąd!', '  Wprowadź poprawne dane!         ', QMessageBox.Ok)

    def draw(self):
        global cam, plane
        try:
            dx = float(self.dx_edt.text())
            dy = float(self.dy_edt.text())
            gsd = float(self.gsd_edt.text()) / 100
            p = float(self.p_edt.text())
            q = float(self.q_edt.text())
            if p > 100 or q > 100:
                QMessageBox.warning(self, 'Błąd!', '  Wprowadź poprawne dane!         ', QMessageBox.Ok)
            airplane_name = str(self.comb7.currentText())
            camera_name = str(self.comb8.currentText())
            if len(airplane_name) == 0 or len(camera_name) == 0:
                QMessageBox.warning(self, 'Błąd!', '  Wprowadź poprawne dane!         ', QMessageBox.Ok)
                # 'Cessna 402','Cessna T206H NAV III', 'Vulcan Air P68 Observer 2', 'Tencam MMA'
            if airplane_name == 'Cessna 402':
                plane = Airplane('Cessna 402', 132, 428, 8200, 5)
            elif airplane_name == 'Cessna T206H NAV III':
                plane = Airplane('Cessna T206H NAV III', 100, 280, 4785, 5)
            elif airplane_name == 'Vulcan Air P68 Observer 2':
                plane = Airplane('Vulcan Air P68 Observer 2', 135, 275, 6100, 6)
            elif airplane_name == 'Tencam MMA':
                plane = Airplane('Tencam MMA', 120, 267, 4572, 6)
            if camera_name == 'Z/I DMC IIe 230':
                cam = Camera('Z/I DMC IIe 230', 15552, 14144, 5.6 * 10 ** -6, 'R, G, B, NIR', 92 * 10 ** -3, 1.8, 63)
            elif camera_name == 'Leica DMC III':
                cam = Camera('Leica DMC III', 25728, 14592, 3.9 * 10 ** -6, 'R, G, B, NIR', 92 * 10 ** -3, 1.9, 63)
            elif camera_name == 'UltraCam Falcon M2 70':
                cam = Camera('UltraCam Falcon M2 70', 17310, 11310, 6.0 * 10 ** -6, 'R, G, B, NIR', 70 * 10 ** -3, 1.65,
                             61)
            elif camera_name == 'UltraCam Eagle M2 80':
                cam = Camera('UltraCam Eagle M2 80', 23010, 14790, 4.6 * 10 ** -6, 'R, G, B, NIR', 80 * 10 ** -3, 1.35,
                             61)

            fig, ax = plt.subplots()
            plt.axis('off')
            fig.set_size_inches(10, 5)
            idy = int(round(dy))
            idx = int(round(dx))
            iBaseY = int(countCorrectedBaseY(gsd, cam, q, dy))
            iBaseX = int(countCorrectedBaseX(gsd, cam, p, dx))
            row = int(countStringNumber(gsd, cam, q, dy))
            counter = 0
            # x_cords = []
            # y_cords = []
            rect = patches.Rectangle((0, 0), dx, dy, linewidth=1, edgecolor='g', facecolor='none')
            ax.add_patch(rect)
            for y in range(idy, 0, -iBaseY):
                plt.plot([0, idx], [y, y], color='#a60010', lw=0.3)
            for x in range(idx, 0, -iBaseX):  # idx // countPhotos(gsd, cam, p, dx)
                plt.plot([x, x], [0, idy], color='#a60010', lw=1)
            for y in range(idy - iBaseY // 2, 0, -iBaseY):
                for x in range(idx + iBaseX, -iBaseX, -iBaseX):
                    circ = patches.Circle((x, y), 100, edgecolor='#000000')
                    ax.add_patch(circ)
                if counter % 2 == 0:
                    plt.plot([idx + iBaseX, -iBaseX],
                             [(idy - iBaseY // 2 - counter * iBaseY), (idy - iBaseY // 2 - counter * iBaseY)],
                             color='#000000', linestyle='dotted', lw=1)
                    if counter < row - 1:
                        arcs = patches.Arc((-iBaseX, idy - (counter + 1) * iBaseY), 2 * iBaseX, 2 * iBaseX, 270, 180,
                                           linestyle='dotted', lw=1)
                        ax.add_patch(arcs)
                elif counter % 2 == 1:
                    plt.plot([-iBaseX, idx + iBaseX],
                             [(idy - iBaseY // 2 - counter * iBaseY), (idy - iBaseY // 2 - counter * iBaseY)],
                             color='#000000', linestyle='dotted', lw=1)
                    if counter < row - 1:
                        arcs = patches.Arc((idx + iBaseX, idy - (counter + 1) * iBaseY), 2 * iBaseX, 2 * iBaseX, 90,
                                           180,
                                           linestyle='dotted', lw=1)
                        ax.add_patch(arcs)
                counter += 1
            # for i in range(0, row, 1):
            #     if i % 2 == 0:
            #         x_cords.append(idx + iBaseX)
            #         y_cords.append(idy - iBaseY // 2 - i * iBaseY)
            #         x_cords.append(-iBaseX)
            #         y_cords.append(idy - iBaseY // 2 - i * iBaseY)
            #         if i < row - 1:
            #             x_cords.append((-2 * iBaseX))
            #             y_cords.append(idy - (i + 1) * iBaseY)
            #     if i % 2 == 1:
            #         x_cords.append(-iBaseX)
            #         y_cords.append(idy - iBaseY // 2 - i * iBaseY)
            #         x_cords.append(idx + iBaseX)
            #         y_cords.append(idy - iBaseY // 2 - i * iBaseY)
            #         if i < row - 1:
            #             x_cords.append(idx + 2 * iBaseX)
            #             y_cords.append(idy - (i + 1) * iBaseY)
            #
            # plt.plot(x_cords, y_cords, color='#000000', linestyle='dotted', marker='o',
            #          markerfacecolor='blue', markersize=1, label='Tor lotu samolotu')
            # plt.legend(loc='upper right', bbox_to_anchor=(1.12, 1.10))
            plt.xlim([-3 * iBaseX, dx + 3 * iBaseX])
            plt.ylim([-2000, dy + 2000])
            plt.title(f'Nalot fotogrametryczyny - kamera: {cam.name}; samolot: {plane.name}')
            plt.show()
        except (ValueError, TypeError, AttributeError, ZeroDivisionError):
            QMessageBox.warning(self, 'Błąd!', '  Wprowadź poprawne dane!         ', QMessageBox.Ok)

    def closeEvent(self, event):
        odp = QMessageBox.question(
            self, 'Komunikat',
            'Czy na pewno chcesz zamknąć aplikację?    ',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if odp == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def clear_wind(self):
        self.textArea.clear()

    def save_file(self):
        try:
            name = QFileDialog.getSaveFileName(self, '/', '.txt')[0]
            save = open(name, 'w')
            save.writelines(self.textArea.toPlainText())
            save.close()
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    app.exec_()
