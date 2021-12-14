from .MonetDBTableSelect import MonetDBTableSelectDialog
from qgis.PyQt.QtWidgets import QTableWidgetItem, QTableView

#
# Dialog that shows the table rows selection screen
#
def show_table_config_dialog(table_conf, db):
    table_select = MonetDBTableSelectDialog()
    selected = table_conf.tableWidget.selectedItems()
    rows = list(chunk(selected, 3))

    col_names = []
    for i in rows:
        q = f"SELECT name FROM sys.describe_columns('{i[1].text()}', '{i[0].text()}')"
        result = db.query(q)
        for x in result:
            col_names.append((x[0], i[0].text(), i[1].text()))

    table_select.tableWidget.setRowCount(len(col_names))
    table_select.tableWidget.setColumnCount(4)
    table_select.tableWidget.setSelectionBehavior(QTableView.SelectRows)

    table_select.tableWidget.setHorizontalHeaderLabels([
         u'Col Name',
         u'Table Name',
         u'Schema',
         u'Interpret as'
    ])
    for row in range(len(col_names)):
        for col in range(1):
            table_item = QTableWidgetItem(str(col_names[row][0]).strip())
            table_select.tableWidget.setItem(row, 0, table_item)

            _table_name = QTableWidgetItem(str(col_names[row][1]).strip())
            table_select.tableWidget.setItem(row, 1, _table_name)

            schema_name = QTableWidgetItem(str(col_names[row][2]).strip())
            table_select.tableWidget.setItem(row, 2, schema_name)

            interpretation = QTableWidgetItem("")
            table_select.tableWidget.setItem(row, 3, interpretation)

    table_select.tableWidget.resizeColumnsToContents()
    table_select.show()
    table_select_result = table_select.exec_()

    if table_select_result:
        table_selected_cols = table_select.tableWidget.selectedItems()
        selected_rows = list(chunk(table_selected_cols, 4))
        column_settings = []

        for i in selected_rows:
            col_name = i[0].text()
            table_name = i[1].text()
            schema_name = i[2].text()
            interpret_as = i[3].text()

            column_settings.append((schema_name, table_name, col_name, interpret_as))

        return column_settings

def chunk(lst, n):
    return zip(*[iter(lst)]*n)
