import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI

FluentPage {
    id: page
    title: qsTr("设置")

    ColumnLayout {
        width: parent.width
        spacing: 16

        // ── 版本 ──────────────────────────────────────
        Text {
            typography: Typography.Title
            text: qsTr("设置")
        }

        SettingCard {
            Layout.fillWidth: true
            icon.name: "ic_fluent_info_20_regular"
            title: qsTr("当前版本")

            content: Text {
                text: Backend.version
                typography: Typography.BodyStrong
            }
        }

        Text {
            typography: Typography.Caption
            text: qsTr("部分设置需要重启程序后生效。")
            opacity: 0.6
            Layout.fillWidth: true
            wrapMode: Text.WordWrap
        }

        // ── 系统 ──────────────────────────────────────
        Text {
            typography: Typography.Subtitle
            text: qsTr("系统")
        }

        SettingCard {
            Layout.fillWidth: true
            icon.name: "ic_fluent_power_20_regular"
            title: qsTr("开机自启动")
            description: qsTr("开机时一并打开 Time Machine，并最小化至系统托盘")

            content: Switch {
                checked: Backend.selfStarting
                onCheckedChanged: Backend.setSelfStarting(checked)
            }
        }

        Item { Layout.fillHeight: true }
    }
}
