from qgis.PyQt.QtWidgets import QTableWidgetItem, QTableView
from .MonetDBTableConfig_dialog import MonetDBTableConfigDialog


def show_table_select_dialog(db):
    table_conf = MonetDBTableConfigDialog()
    tables = db.query(
        "SELECT name, schema_id FROM sys._tables WHERE system = False"
    )

    _tables = [(x[0], x[1]) for x in tables]
    tables = []
    for i in _tables:
        schema_names = db.query(
            f"SELECT name FROM sys.schemas WHERE id = {str(i[1])}"
        )
        i = (i[0], i[1], schema_names[0][0])
        tables.append(i)

    table_conf.tableWidget.setRowCount(len(tables))
    table_conf.tableWidget.setColumnCount(3)
    table_conf.tableWidget.setSelectionBehavior(QTableView.SelectRows)

    table_conf.tableWidget.setHorizontalHeaderLabels([u'Table Name',
                                                      u'Schema Name',
                                                      u'Schema ID'])

    for row in range(len(tables)):
        for col in range(1):
            table_item = QTableWidgetItem(
                str(tables[row][0]).strip()
            )
            table_conf.tableWidget.setItem(row, 0, table_item)

            table_schema_id = QTableWidgetItem(
                str(tables[row][1]).strip()
            )
            table_conf.tableWidget.setItem(row, 2, table_schema_id)

            table_schema_name = QTableWidgetItem(
                str(tables[row][2]).strip()
            )
            table_conf.tableWidget.setItem(row, 1, table_schema_name)

    return table_conf
