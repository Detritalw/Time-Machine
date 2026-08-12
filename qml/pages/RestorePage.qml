import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15
import RinUI

FluentPage {
    id: page
    title: qsTr("还原")

    property var currentTimestamp: ""
    property var restoreFiles: []

    ColumnLayout {
        width: parent.width
        spacing: 16

        Text {
            typography: Typography.Title
            text: qsTr("还原")
        }

        SettingCard {
            Layout.fillWidth: true
            icon.name: "ic_fluent_history_20_regular"
            title: qsTr("还原到...")
            description: qsTr("选择过去的时间来查看过去的文件")

            content: ComboBox {
                id: timeCombo
                width: 280
                model: Backend.backupTimeList
                textRole: "label"
                valueRole: "timestamp"
                placeholderText: qsTr("选择备份时间")
                currentIndex: -1

                onCurrentIndexChanged: {
                    if (currentIndex >= 0) {
                        currentTimestamp = model[currentIndex].timestamp
                        refreshFileList()
                    }
                }

                Component.onCompleted: {
                    if (model && model.length > 0) {
                        currentIndex = model.length - 1
                        currentTimestamp = model[model.length - 1].timestamp
                        refreshFileList()
                    }
                }
            }
        }

        Text {
            typography: Typography.Subtitle
            text: qsTr("备份文件")
            visible: restoreFiles.length > 0
        }

        Repeater {
            id: fileRepeater
            model: restoreFiles

            Frame {
                Layout.fillWidth: true
                Layout.preferredHeight: 60

                RowLayout {
                    anchors.fill: parent
                    spacing: 12

                    Icon {
                        name: modelData.type === "folder"
                            ? "ic_fluent_folder_20_regular"
                            : "ic_fluent_document_20_regular"
                        size: 20
                        Layout.alignment: Qt.AlignVCenter
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Text {
                            typography: Typography.Body
                            text: modelData.name
                        }
                        Text {
                            typography: Typography.Caption
                            text: (modelData.type === "folder" ? qsTr("文件夹") : qsTr("文件")) + " · " + modelData.fullPath
                            opacity: 0.6
                            elide: Text.ElideMiddle
                            Layout.maximumWidth: 400
                        }
                    }

                    Button {
                        text: qsTr("恢复")
                        onClicked: {
                            Backend.restoreFile(modelData.fullPath, currentTimestamp)
                            floatLayer.createInfoBar({
                                severity: Severity.Success,
                                title: qsTr("恢复成功"),
                                text: qsTr("文件已恢复到原位置: ") + modelData.fullPath,
                                timeout: 5000
                            })
                        }
                    }

                    Button {
                        text: qsTr("删除")
                        flat: true
                        onClicked: {
                            Backend.deleteBackupFile(modelData.fullPath, currentTimestamp)
                            floatLayer.createInfoBar({
                                severity: Severity.Success,
                                title: qsTr("删除成功"),
                                text: qsTr("备份文件已从备份中移除"),
                                timeout: 3000
                            })
                            refreshFileList()
                        }
                    }
                }
            }
        }

        Text {
            typography: Typography.Caption
            text: qsTr("暂无备份记录或未选择备份时间")
            opacity: 0.5
            visible: restoreFiles.length === 0 && timeCombo.currentIndex >= 0
            Layout.alignment: Qt.AlignHCenter
            Layout.topMargin: 40
        }

        Item { Layout.fillHeight: true }
    }

    function refreshFileList() {
        restoreFiles = Backend.getRestoreFiles(currentTimestamp)
    }
}
