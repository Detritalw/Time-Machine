import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI

FluentWindow {
    id: window
    width: 860
    height: 640
    minimumWidth: 600
    minimumHeight: 450

    navigationView.navExpandWidth: 220

    navigationItems: [
        {
            title: qsTr("备份"),
            page: Qt.resolvedUrl("pages/BackupPage.qml"),
            icon: "ic_fluent_sync_20_regular",
            position: Position.Top
        },
        {
            title: qsTr("还原"),
            page: Qt.resolvedUrl("pages/RestorePage.qml"),
            icon: "ic_fluent_history_20_regular",
            position: Position.Top
        },
        {
            title: qsTr("设置"),
            page: Qt.resolvedUrl("pages/SettingsPage.qml"),
            icon: "ic_fluent_settings_20_regular",
            position: Position.Bottom
        },
        {
            title: qsTr("关于"),
            page: Qt.resolvedUrl("pages/AboutPage.qml"),
            icon: "ic_fluent_info_20_regular",
            position: Position.Bottom
        }
    ]

    Component.onCompleted: {
        Backend.refreshAll()
    }
}
