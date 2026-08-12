import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI

FluentPage {
    id: page
    title: qsTr("关于")

    ScrollView {
        anchors.fill: parent
        anchors.margins: 32

        ColumnLayout {
            width: parent.width
            spacing: 20

            // ── Logo & Name ───────────────────────────────
            Image {
                source: Qt.resolvedUrl("../../Time-Machine.png")
                Layout.preferredWidth: 128
                Layout.preferredHeight: 128
                Layout.alignment: Qt.AlignHCenter
                fillMode: Image.PreserveAspectFit
                smooth: true
            }

            Text {
                typography: Typography.Title
                text: qsTr("Time Machine")
                Layout.alignment: Qt.AlignHCenter
            }

            Text {
                typography: Typography.Caption
                text: qsTr("简单地备份你的 Windows")
                Layout.alignment: Qt.AlignHCenter
            }

            Item { Layout.preferredHeight: 40 }

            // ── QQ ─────────────────────────────────────────
            SettingCard {
                Layout.fillWidth: true
                icon.name: "ic_fluent_chat_20_regular"
                title: qsTr("QQ 群")

                content: Button {
                    text: qsTr("Bloret Software Community")
                    onClicked: Qt.openUrlExternally("https://qm.qq.com/q/IM122YNoUo")
                }
            }

            // ── GitHub ─────────────────────────────────────
            SettingCard {
                Layout.fillWidth: true
                icon.name: "ic_fluent_code_20_regular"
                title: qsTr("GitHub")

                content: Button {
                    text: qsTr("此项目的 GitHub")
                    onClicked: Qt.openUrlExternally("https://github.com/Detritalw/Time-Machine")
                }
            }

            Item { Layout.fillHeight: true }

            // ── Copyright ──────────────────────────────────
            Text {
                typography: Typography.Caption
                text: qsTr("© 2025 Time Machine All rights reserved.")
                Layout.alignment: Qt.AlignHCenter
                opacity: 0.5
            }
        }
    }
}
