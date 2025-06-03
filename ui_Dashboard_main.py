# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Dashboard_main.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QMainWindow, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

from Custom_Widgets.QCustomQStackedWidget import QCustomQStackedWidget
from Custom_Widgets.QCustomSlideMenu import QCustomSlideMenu
import resource_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1166, 702)
        MainWindow.setStyleSheet(u"*{\n"
"	border:none;\n"
"	background-color:transparent;\n"
"	background:none;\n"
"	background: transparent;\n"
"	padding:0;\n"
"	color:#fff;\n"
"	margin:0;\n"
"}\n"
"\n"
"\n"
"#leftSB,#frame3,#leftMenu{\n"
"    border-bottom-left-radius:10px; \n"
"}\n"
"#leftSB,#frame,#leftMenu{\n"
"    border-top-left-radius:10px; \n"
"}\n"
"\n"
"#mainBody,#header{\n"
"    border-top-right-radius:10px; \n"
"}\n"
"#mainBody,#footerContainer{\n"
"    border-bottom-right-radius:10px; \n"
"}\n"
"\n"
"\n"
"#centralwidget{\n"
"	background-color: #1E1E1E ;\n"
"    border-radius: 20px;\n"
"}\n"
"#leftSB{\n"
"	background-color: #290a30;\n"
"	\n"
"}\n"
"#leftSB QPushButton {\n"
"    text-align: left;\n"
"    padding: 5px 10px;\n"
"	border-bottom-left-radius:15px;  \n"
"    border-top-right-radius:10px;   \n"
"}\n"
"\n"
"#centerMenuSB,#rightMenuContainerSub{\n"
"	background-color: #290a30;            ;\n"
"	border-top-right-radius: 20px;\n"
"    border-bottom-right-radius: 20px;\n"
"}\n"
"\n"
"#rightMenuContainerSub{\n"
"	border-radius:"
                        " 10px;\n"
"}\n"
"#frame_4, #frame_8,#popNotificationSubContainer{\n"
"	background-color: #750080  ;\n"
"	border-radius: 20px;\n"
"}\n"
"#header,#footerContainer{\n"
"	background-color: #750080 ;\n"
"}\n"
"")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.leftMenu = QCustomSlideMenu(self.centralwidget)
        self.leftMenu.setObjectName(u"leftMenu")
        self.leftMenu.setMaximumSize(QSize(45, 16777215))
        self.verticalLayout = QVBoxLayout(self.leftMenu)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.leftSB = QWidget(self.leftMenu)
        self.leftSB.setObjectName(u"leftSB")
        self.leftSB.setStyleSheet(u"")
        self.verticalLayout_2 = QVBoxLayout(self.leftSB)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(self.leftSB)
        self.frame.setObjectName(u"frame")
        self.frame.setStyleSheet(u"background-color: #750080 ; ")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 9, 0, 10)
        self.menuBtn = QPushButton(self.frame)
        self.menuBtn.setObjectName(u"menuBtn")
        icon = QIcon()
        icon.addFile(u":/icons/icons/align-justify.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.menuBtn.setIcon(icon)
        self.menuBtn.setIconSize(QSize(24, 24))

        self.horizontalLayout_2.addWidget(self.menuBtn, 0, Qt.AlignTop)


        self.verticalLayout_2.addWidget(self.frame)

        self.frame_2 = QFrame(self.leftSB)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setStyleSheet(u"")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame_2)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 10, 0, 10)
        self.homeBtn = QPushButton(self.frame_2)
        self.homeBtn.setObjectName(u"homeBtn")
        self.homeBtn.setStyleSheet(u"background-color: #750080   ;\n"
"")
        icon1 = QIcon()
        icon1.addFile(u":/icons/icons/home.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.homeBtn.setIcon(icon1)
        self.homeBtn.setIconSize(QSize(24, 24))

        self.verticalLayout_3.addWidget(self.homeBtn)

        self.logBtn = QPushButton(self.frame_2)
        self.logBtn.setObjectName(u"logBtn")
        icon2 = QIcon()
        icon2.addFile(u":/icons/icons/activity.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.logBtn.setIcon(icon2)
        self.logBtn.setIconSize(QSize(24, 24))

        self.verticalLayout_3.addWidget(self.logBtn)

        self.systemBtn = QPushButton(self.frame_2)
        self.systemBtn.setObjectName(u"systemBtn")
        icon3 = QIcon()
        icon3.addFile(u":/icons/icons/airplay.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.systemBtn.setIcon(icon3)
        self.systemBtn.setIconSize(QSize(24, 24))

        self.verticalLayout_3.addWidget(self.systemBtn)


        self.verticalLayout_2.addWidget(self.frame_2, 0, Qt.AlignTop)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.frame_3 = QFrame(self.leftSB)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_3)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 10, 0, 0)
        self.infoBtn = QPushButton(self.frame_3)
        self.infoBtn.setObjectName(u"infoBtn")
        icon4 = QIcon()
        icon4.addFile(u":/icons/icons/info.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.infoBtn.setIcon(icon4)
        self.infoBtn.setIconSize(QSize(24, 24))

        self.verticalLayout_4.addWidget(self.infoBtn)

        self.helpBtn = QPushButton(self.frame_3)
        self.helpBtn.setObjectName(u"helpBtn")
        icon5 = QIcon()
        icon5.addFile(u":/icons/icons/help-circle.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.helpBtn.setIcon(icon5)
        self.helpBtn.setIconSize(QSize(24, 24))

        self.verticalLayout_4.addWidget(self.helpBtn)


        self.verticalLayout_2.addWidget(self.frame_3, 0, Qt.AlignBottom)


        self.verticalLayout.addWidget(self.leftSB)


        self.horizontalLayout.addWidget(self.leftMenu, 0, Qt.AlignLeft)

        self.centerMenu = QCustomSlideMenu(self.centralwidget)
        self.centerMenu.setObjectName(u"centerMenu")
        self.centerMenu.setMinimumSize(QSize(250, 0))
        self.verticalLayout_5 = QVBoxLayout(self.centerMenu)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.centerMenuSB = QWidget(self.centerMenu)
        self.centerMenuSB.setObjectName(u"centerMenuSB")
        self.centerMenuSB.setMinimumSize(QSize(250, 0))
        self.verticalLayout_6 = QVBoxLayout(self.centerMenuSB)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(9, 6, 9, 4)
        self.frame_4 = QFrame(self.centerMenuSB)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setMinimumSize(QSize(0, 0))
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_4)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(9, 9, -1, -1)
        self.label = QLabel(self.frame_4)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_3.addWidget(self.label)

        self.closeCenterMenuBtn = QPushButton(self.frame_4)
        self.closeCenterMenuBtn.setObjectName(u"closeCenterMenuBtn")
        icon6 = QIcon()
        icon6.addFile(u":/icons/icons/x-circle.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.closeCenterMenuBtn.setIcon(icon6)
        self.closeCenterMenuBtn.setIconSize(QSize(24, 24))

        self.horizontalLayout_3.addWidget(self.closeCenterMenuBtn, 0, Qt.AlignRight)


        self.verticalLayout_6.addWidget(self.frame_4)

        self.centerMenuPages = QCustomQStackedWidget(self.centerMenuSB)
        self.centerMenuPages.setObjectName(u"centerMenuPages")
        self.centerMenuPages.setMinimumSize(QSize(250, 0))
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.verticalLayout_8 = QVBoxLayout(self.page_2)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.label_3 = QLabel(self.page_2)
        self.label_3.setObjectName(u"label_3")
        font = QFont()
        font.setPointSize(13)
        self.label_3.setFont(font)
        self.label_3.setAlignment(Qt.AlignCenter)

        self.verticalLayout_8.addWidget(self.label_3)

        self.centerMenuPages.addWidget(self.page_2)
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.verticalLayout_9 = QVBoxLayout(self.page_3)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.label_4 = QLabel(self.page_3)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(0, 0))
        self.label_4.setFont(font)
        self.label_4.setAlignment(Qt.AlignCenter)

        self.verticalLayout_9.addWidget(self.label_4)

        self.centerMenuPages.addWidget(self.page_3)

        self.verticalLayout_6.addWidget(self.centerMenuPages)


        self.verticalLayout_5.addWidget(self.centerMenuSB, 0, Qt.AlignLeft)


        self.horizontalLayout.addWidget(self.centerMenu)

        self.mainBody = QWidget(self.centralwidget)
        self.mainBody.setObjectName(u"mainBody")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.mainBody.sizePolicy().hasHeightForWidth())
        self.mainBody.setSizePolicy(sizePolicy1)
        self.mainBody.setStyleSheet(u"")
        self.verticalLayout_10 = QVBoxLayout(self.mainBody)
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.header = QWidget(self.mainBody)
        self.header.setObjectName(u"header")
        self.horizontalLayout_5 = QHBoxLayout(self.header)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.frame_5 = QFrame(self.header)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_7.setSpacing(6)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.label_5 = QLabel(self.frame_5)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMaximumSize(QSize(35, 35))
        self.label_5.setPixmap(QPixmap(u":/images/log.png"))
        self.label_5.setScaledContents(True)

        self.horizontalLayout_7.addWidget(self.label_5)

        self.label_6 = QLabel(self.frame_5)
        self.label_6.setObjectName(u"label_6")
        font1 = QFont()
        font1.setPointSize(10)
        font1.setBold(True)
        self.label_6.setFont(font1)
        self.label_6.setStyleSheet(u"")

        self.horizontalLayout_7.addWidget(self.label_6)


        self.horizontalLayout_5.addWidget(self.frame_5, 0, Qt.AlignLeft)

        self.frame_6 = QFrame(self.header)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_6)
        self.horizontalLayout_6.setSpacing(6)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)

        self.horizontalLayout_5.addWidget(self.frame_6, 0, Qt.AlignHCenter)

        self.frame_7 = QFrame(self.header)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setStyleSheet(u"")
        self.frame_7.setFrameShape(QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_7)
        self.horizontalLayout_4.setSpacing(1)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.minimizeBtn = QPushButton(self.frame_7)
        self.minimizeBtn.setObjectName(u"minimizeBtn")
        icon7 = QIcon()
        icon7.addFile(u":/icons/icons/minus.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.minimizeBtn.setIcon(icon7)
        self.minimizeBtn.setIconSize(QSize(20, 20))

        self.horizontalLayout_4.addWidget(self.minimizeBtn)

        self.restoreBtn = QPushButton(self.frame_7)
        self.restoreBtn.setObjectName(u"restoreBtn")
        icon8 = QIcon()
        icon8.addFile(u":/icons/icons/square.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.restoreBtn.setIcon(icon8)
        self.restoreBtn.setIconSize(QSize(20, 20))

        self.horizontalLayout_4.addWidget(self.restoreBtn)

        self.closeBtn = QPushButton(self.frame_7)
        self.closeBtn.setObjectName(u"closeBtn")
        icon9 = QIcon()
        icon9.addFile(u":/icons/icons/x.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.closeBtn.setIcon(icon9)
        self.closeBtn.setIconSize(QSize(20, 20))

        self.horizontalLayout_4.addWidget(self.closeBtn)


        self.horizontalLayout_5.addWidget(self.frame_7, 0, Qt.AlignRight)


        self.verticalLayout_10.addWidget(self.header)

        self.mainBodyContainer = QWidget(self.mainBody)
        self.mainBodyContainer.setObjectName(u"mainBodyContainer")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.mainBodyContainer.sizePolicy().hasHeightForWidth())
        self.mainBodyContainer.setSizePolicy(sizePolicy2)
        self.mainBodyContainer.setMinimumSize(QSize(871, 515))
        self.horizontalLayout_8 = QHBoxLayout(self.mainBodyContainer)
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.mainContainContainer = QWidget(self.mainBodyContainer)
        self.mainContainContainer.setObjectName(u"mainContainContainer")
        self.verticalLayout_15 = QVBoxLayout(self.mainContainContainer)
        self.verticalLayout_15.setSpacing(0)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.mainPages = QCustomQStackedWidget(self.mainContainContainer)
        self.mainPages.setObjectName(u"mainPages")
        self.page_6 = QWidget()
        self.page_6.setObjectName(u"page_6")
        self.verticalLayout_16 = QVBoxLayout(self.page_6)
        self.verticalLayout_16.setSpacing(0)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.label_10 = QLabel(self.page_6)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setMinimumSize(QSize(200, 0))
        font2 = QFont()
        font2.setPointSize(13)
        font2.setBold(True)
        self.label_10.setFont(font2)
        self.label_10.setStyleSheet(u"padding: 1.2rem;\n"
"        background: #290a30;\n"
"        font-size: 1.8rem;\n"
"        text-align: center;\n"
"        font-weight: bold;\n"
"        text-transform: uppercase;\n"
"        color: white;  /* Optional: set the text color */")
        self.label_10.setAlignment(Qt.AlignCenter)

        self.verticalLayout_16.addWidget(self.label_10)

        self.mainPages.addWidget(self.page_6)
        self.page_7 = QWidget()
        self.page_7.setObjectName(u"page_7")
        self.verticalLayout_17 = QVBoxLayout(self.page_7)
        self.verticalLayout_17.setSpacing(0)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.verticalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.label_11 = QLabel(self.page_7)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setMinimumSize(QSize(200, 0))
        self.label_11.setFont(font2)
        self.label_11.setStyleSheet(u"padding: 1.2rem;\n"
"        background: #290a30;\n"
"        font-size: 1.8rem;\n"
"        text-align: center;\n"
"        font-weight: bold;\n"
"        text-transform: uppercase;\n"
"        color: white;  /* Optional: set the text color */")
        self.label_11.setAlignment(Qt.AlignCenter)

        self.verticalLayout_17.addWidget(self.label_11)

        self.mainPages.addWidget(self.page_7)
        self.page_9 = QWidget()
        self.page_9.setObjectName(u"page_9")
        self.verticalLayout_19 = QVBoxLayout(self.page_9)
        self.verticalLayout_19.setSpacing(0)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.verticalLayout_19.setContentsMargins(0, 0, 0, 0)
        self.label_13 = QLabel(self.page_9)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setMinimumSize(QSize(200, 0))
        self.label_13.setFont(font2)
        self.label_13.setStyleSheet(u"padding: 1.2rem;\n"
"        background: #290a30;\n"
"        font-size: 1.8rem;\n"
"        text-align: center;\n"
"        font-weight: bold;\n"
"        text-transform: uppercase;\n"
"        color: white;  /* Optional: set the text color */")
        self.label_13.setAlignment(Qt.AlignCenter)

        self.verticalLayout_19.addWidget(self.label_13)

        self.mainPages.addWidget(self.page_9)

        self.verticalLayout_15.addWidget(self.mainPages)


        self.horizontalLayout_8.addWidget(self.mainContainContainer)


        self.verticalLayout_10.addWidget(self.mainBodyContainer)

        self.footerContainer = QWidget(self.mainBody)
        self.footerContainer.setObjectName(u"footerContainer")
        sizePolicy.setHeightForWidth(self.footerContainer.sizePolicy().hasHeightForWidth())
        self.footerContainer.setSizePolicy(sizePolicy)
        self.horizontalLayout_11 = QHBoxLayout(self.footerContainer)
        self.horizontalLayout_11.setSpacing(0)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.frame_10 = QFrame(self.footerContainer)
        self.frame_10.setObjectName(u"frame_10")
        self.frame_10.setFrameShape(QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_12 = QHBoxLayout(self.frame_10)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.label_16 = QLabel(self.frame_10)
        self.label_16.setObjectName(u"label_16")
        font3 = QFont()
        font3.setBold(True)
        self.label_16.setFont(font3)

        self.horizontalLayout_12.addWidget(self.label_16)


        self.horizontalLayout_11.addWidget(self.frame_10)

        self.sizeGrip = QFrame(self.footerContainer)
        self.sizeGrip.setObjectName(u"sizeGrip")
        self.sizeGrip.setMinimumSize(QSize(30, 30))
        self.sizeGrip.setMaximumSize(QSize(30, 30))
        self.sizeGrip.setFrameShape(QFrame.StyledPanel)
        self.sizeGrip.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_11.addWidget(self.sizeGrip, 0, Qt.AlignRight)


        self.verticalLayout_10.addWidget(self.footerContainer)


        self.horizontalLayout.addWidget(self.mainBody)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.centerMenuPages.setCurrentIndex(1)
        self.mainPages.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
#if QT_CONFIG(tooltip)
        MainWindow.setToolTip(QCoreApplication.translate("MainWindow", u"Menu", None))
#endif // QT_CONFIG(tooltip)
        self.menuBtn.setText("")
#if QT_CONFIG(tooltip)
        self.homeBtn.setToolTip(QCoreApplication.translate("MainWindow", u"Home", None))
#endif // QT_CONFIG(tooltip)
        self.homeBtn.setText(QCoreApplication.translate("MainWindow", u"Home", None))
#if QT_CONFIG(tooltip)
        self.logBtn.setToolTip(QCoreApplication.translate("MainWindow", u"Log Analysis", None))
#endif // QT_CONFIG(tooltip)
        self.logBtn.setText(QCoreApplication.translate("MainWindow", u"Log Analysis", None))
#if QT_CONFIG(tooltip)
        self.systemBtn.setToolTip(QCoreApplication.translate("MainWindow", u"System Analysis", None))
#endif // QT_CONFIG(tooltip)
        self.systemBtn.setText(QCoreApplication.translate("MainWindow", u"System Analysis", None))
#if QT_CONFIG(tooltip)
        self.infoBtn.setToolTip(QCoreApplication.translate("MainWindow", u"Information", None))
#endif // QT_CONFIG(tooltip)
        self.infoBtn.setText(QCoreApplication.translate("MainWindow", u"Information", None))
#if QT_CONFIG(tooltip)
        self.helpBtn.setToolTip(QCoreApplication.translate("MainWindow", u"Get more help", None))
#endif // QT_CONFIG(tooltip)
        self.helpBtn.setText(QCoreApplication.translate("MainWindow", u"Help", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"More Menu", None))
#if QT_CONFIG(tooltip)
        self.closeCenterMenuBtn.setToolTip(QCoreApplication.translate("MainWindow", u"Close Menu", None))
#endif // QT_CONFIG(tooltip)
        self.closeCenterMenuBtn.setText("")
        self.label_3.setText(
        QCoreApplication.translate(
                "MainWindow",
                u"<b>Information</b>: Log analysis is a vital process for organizations aiming to maintain secure, efficient, and compliant IT environments. "
                "Logs are generated by a wide range of sources—operating systems, firewalls, servers, applications, and cloud services—and contain "
                "a wealth of information about system activity, user behavior, and potential threats.\n\n"
                
                "For cybersecurity and IT professionals, analyzing these logs enables early detection of suspicious activities such as brute-force attacks, "
                "malware infections, unauthorized access attempts, and configuration anomalies. Effective log analysis can support real-time alerting, "
                "incident response, forensic investigations, and long-term threat intelligence.\n\n"
                
                "Modern log analysis is enhanced by technologies ML and Natural Language Processing (NLP). ML algorithms can learn "
                "patterns of normal behavior and identify deviations that suggest anomalies or security breaches. NLP helps interpret unstructured log messages, "
                "categorize events, and extract meaningful insights from textual data. These approaches make it possible to automate the detection of complex threats, "
                "reduce false positives, and perform deep, large-scale analysis.\n\n",
                
                None
        )
        )
        self.label_3.setWordWrap(True)
     

        # Enable word wrap
        self.label_3.setWordWrap(True)

        # Optional: Style it nicely
        self.label_3.setStyleSheet("color: white; font-size: 13px; padding: 5px;")



        self.label_4.setText(
        QCoreApplication.translate(
                "MainWindow",
                u"<b>Help</b><br><br>"
                "This project is a <b>Final Year Project</b> developed by: <b>Nandini</b>, <b>Suraj</b>, <b>Gaurav</b>, and <b>Rupesh</b>.<br>"
                "For inquiries, contact: <b>rupeshborse45@gmail.com</b><br><br>"
                
                "<b>Key Features:</b><br>"
                "• Real-time <b>Network Log Analysis</b><br>"
                "• <b>Machine Learning (ML)</b>-based <b>Deep Analysis</b> and <b>Anomaly Detection</b><br>"
                "• Support for analyzing <b>large log files</b> efficiently<br>"
                "• <b>Keyword Search</b> across <b>multiple files simultaneously</b><br>"
                "• Detection and tagging of suspicious or unusual activities<br>"
                "• Ability to <b>download results</b> of both <b>anomaly detection</b> and <b>deep analysis</b> in <b>Excel format</b><br><br>"

                "This tool is built to support cybersecurity professionals and IT teams in simplifying log analysis using smart, automated techniques."
                ,
                None
        )
        )
        self.label_4.setWordWrap(True)
        self.label_4.setStyleSheet("color: white; font-size: 13px; padding: 5px;")

        self.label_5.setText("")
#if QT_CONFIG(tooltip)
        self.label_6.setToolTip(QCoreApplication.translate("MainWindow", u"Log Analysis", None))
#endif // QT_CONFIG(tooltip)
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"<p><span style=\"text-transform: uppercase;\">Log Ana<span style=\"color: #ee0979 ;\">l</span>ysis</span></p>\n"
"", None))
#if QT_CONFIG(tooltip)
        self.minimizeBtn.setToolTip(QCoreApplication.translate("MainWindow", u"Minimize Window", None))
#endif // QT_CONFIG(tooltip)
        self.minimizeBtn.setText("")
#if QT_CONFIG(tooltip)
        self.restoreBtn.setToolTip(QCoreApplication.translate("MainWindow", u"Restore Window", None))
#endif // QT_CONFIG(tooltip)
        self.restoreBtn.setText("")
#if QT_CONFIG(tooltip)
        self.closeBtn.setToolTip(QCoreApplication.translate("MainWindow", u"Close Window", None))
#endif // QT_CONFIG(tooltip)
        self.closeBtn.setText("")
#if QT_CONFIG(tooltip)
        self.page_6.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"", None))
#if QT_CONFIG(tooltip)
        self.page_7.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"", None))
#if QT_CONFIG(tooltip)
        self.footerContainer.setToolTip(QCoreApplication.translate("MainWindow", u"Log Analysis By HUSTLE SQUAD", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.label_16.setToolTip(QCoreApplication.translate("MainWindow", u"\u00a9Nandini \u00a9Rupesh \u00a9Gaurav \u00a9Suraj", None))
#endif // QT_CONFIG(tooltip)
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>\u00a9Copyright Team HUSTLE SQUAD(<span style=\" color:#ee0979;\">NRGS</span>) </p></body></html>", None))
    # retranslateUi

