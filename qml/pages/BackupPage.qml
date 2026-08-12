import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import Qt.labs.platform 1.1
import RinUI

FluentPage {
    id: page
    title: qsTr("备份")

    ColumnLayout {
        width: parent.width
        spacing: 16

        // ── 立即备份 ──────────────────────────────────
        Text {
            typography: Typography.Title
            text: qsTr("备份")
        }

        Frame {
            Layout.fillWidth: true
            ColumnLayout {
                width: parent.width
                spacing: 8

                Button {
                    id: backupNowBtn
                    text: qsTr("立即备份")
                    highlighted: true
                    Layout.fillWidth: true
                    onClicked: Backend.startBackup()
                }

                RowLayout {
                    Text {
                        typography: Typography.Caption
                        text: qsTr("上次备份时间: ")
                        opacity: 0.6
                    }
                    Text {
                        typography: Typography.Caption
                        text: Backend.lastBackupTime
                        opacity: 0.6
                    }
                }

                RowLayout {
                    Text {
                        typography: Typography.Caption
                        text: qsTr("备份占用空间: ")
                        opacity: 0.6
                    }
                    Text {
                        typography: Typography.Caption
                        text: Backend.backupSize
                        opacity: 0.6
                    }
                }

                RowLayout {
                    Text {
                        typography: Typography.Caption
                        text: qsTr("已备份次数: ")
                        opacity: 0.6
                    }
                    Text {
                        typography: Typography.Caption
                        text: Backend.backupNum
                        opacity: 0.6
                    }
                }
            }
        }

        // ── 自动备份 ──────────────────────────────────
        Text {
            typography: Typography.Subtitle
            text: qsTr("自动备份")
        }

        SettingCard {
            Layout.fillWidth: true
            icon.name: "ic_fluent_timer_20_regular"
            title: qsTr("自动备份间隔")
            description: qsTr("经过设定时间后自动进行一次备份")

            content: RowLayout {
                SpinBox {
                    id: autoBackupSpin
                    from: 10
                    to: 43200
                    value: Backend.autoBackupTime
                    onValueChanged: Backend.setAutoBackupTime(value)
                }
                Text {
                    text: qsTr("秒")
                    typography: Typography.Caption
                    opacity: 0.6
                }
            }
        }

        SettingCard {
            Layout.fillWidth: true
            icon.name: "ic_fluent_power_20_regular"
            title: qsTr("启动时备份")
            description: qsTr("打开软件后自动开始一次备份")

            content: Switch {
                checked: Backend.backupAtRun
                onCheckedChanged: Backend.setBackupAtRun(checked)
            }
        }

        // ── 备份文件夹 ──────────────────────────────────
        Text {
            typography: Typography.Subtitle
            text: qsTr("备份文件夹")
        }

        SettingCard {
            Layout.fillWidth: true
            icon.name: "ic_fluent_folder_20_regular"
            title: qsTr("需备份文件夹")
            description: qsTr("备份的源位置，你存放文件的地方")

            content: RowLayout {
                spacing: 8
                Text {
                    text: Backend.fromFolder === "/blank" ? qsTr("未设置") : Backend.fromFolder
                    elide: Text.ElideMiddle
                    Layout.maximumWidth: 200
                }
                Button {
                    text: qsTr("选择")
                    onClicked: fromFolderDialog.open()
                }
            }
        }

        SettingCard {
            Layout.fillWidth: true
            icon.name: "ic_fluent_folder_open_20_regular"
            title: qsTr("备份文件夹位置")
            description: qsTr("备份的目的文件夹，备份文件将存储在此处")

            content: RowLayout {
                spacing: 8
                Text {
                    text: Backend.toFolder === "/blank" ? qsTr("未设置") : Backend.toFolder
                    elide: Text.ElideMiddle
                    Layout.maximumWidth: 200
                }
                Button {
                    text: qsTr("选择")
                    onClicked: toFolderDialog.open()
                }
            }
        }

        Item { Layout.fillHeight: true }
    }

    // ── Folder Dialogs ──────────────────────────────────
    FolderDialog {
        id: fromFolderDialog
        title: qsTr("选择要备份的文件夹")
        onAccepted: Backend.setFromFolder(currentFolder.toString().replace("file://", ""))
    }

    FolderDialog {
        id: toFolderDialog
        title: qsTr("选择备份存储位置")
        onAccepted: Backend.setToFolder(currentFolder.toString().replace("file://", ""))
    }

    // ─── Backup status feedback ─────────────────────────
    Connections {
        target: Backend
        function onBackupStarted() {
            floatLayer.createInfoBar({
                severity: Severity.Info,
                title: qsTr("备份中"),
                text: qsTr("正在备份文件，请稍候..."),
                timeout: 3000
            })
        }
        function onBackupFinished() {
            floatLayer.createInfoBar({
                severity: Severity.Success,
                title: qsTr("备份完成"),
                text: qsTr("文件备份成功！"),
                timeout: 5000
            })
        }
        function onBackupError(msg) {
            floatLayer.createInfoBar({
                severity: Severity.Error,
                title: qsTr("备份失败"),
                text: msg,
                closable: true,
                timeout: 8000
            })
        }
    }
}
