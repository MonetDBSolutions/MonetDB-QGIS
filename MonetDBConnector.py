# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MonetDBConnector
                                 A QGIS plugin
 MonetDBConnector
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-09-27
        git sha              : $Format:%H$
        copyright            : (C) 2021 by MonetDBSolutions
        email                : info@monetdb.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QTableWidgetItem, QTableView

from qgis.core import (
  Qgis,
  QgsProject,
  QgsFeature,
  QgsGeometry,
  QgsVectorLayer,
)

from .logger import Logger

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .MonetDBConnector_dialog import MonetDBConnectorDialog
import os.path
import _thread

from . import monetdbconn
from . import table_config_dialog
from . import table_select_dialog


class MonetDBConnector:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'MonetDBConnector_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&MonetDBConnector')

        self.logger = Logger()

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('MonetDBConnector', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = self.plugin_dir + "/icon.png"
        self.add_action(
            icon_path,
            text=self.tr(u''),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&MonetDBConnector'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        if self.first_start:
            self.first_start = False
            self.dlg = MonetDBConnectorDialog()
        
        self.logger.log("Succesfully initialized plugin", Qgis.Info)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            self.username = self.dlg.usernameEdit.text()
            self.password = self.dlg.passwordEdit.text()
            self.hostname = self.dlg.hostnameEdit.text()
            self.database = self.dlg.databaseEdit.text()

            self.logger.log(f"Connecting to hostname {self.hostname} with credentials: {self.username}, {self.database}", Qgis.Info)

            self.db = monetdbconn.MonetDB(self.username, self.password,
                                           self.hostname, self.database, self.logger)

            table_conf = table_select_dialog.show_table_select_dialog(self.db)

            table_conf.tableWidget.resizeColumnsToContents()
            table_conf.show()
            table_conf_result = table_conf.exec_()

            if table_conf_result:
                out = table_config_dialog.show_table_config_dialog(
                        table_conf, self.db
                )

                if out is not None:
                    for s in out:
                        _thread.start_new_thread(self.show_vector_layer,
                                                (s[0], s[1], s[2], s[3]))

    def show_vector_layer(self, schema, table_name, column, interpretation):
        db = monetdbconn.MonetDB(self.username, self.password,
                                  self.hostname, self.database, self.logger)

        self.logger.log(
            f"""Drawing vector layer with parameters: 
                schema={schema}, table_name={table_name} 
                column={column}, interpretation={interpretation} 
             """, Qgis.Info
        )

        query_for_col_type = f"SELECT {column} FROM {schema}.{table_name}"

        self.logger.log(f"query_for_col_type: \n {query_for_col_type}", Qgis.Info) 

        col_type_data = db.query(query_for_col_type)

        self.logger.log(f"col_type_data: {col_type_data}", Qgis.Info) 

        geom_type = None

        try:
            geom_type = db.get_column_type(col_type_data[0][0])
        except IndexError:
            self.logger.log(f"Unable to get the GEOM type from this table.", Qgis.Critical) 
            

        query = ""
        if interpretation:
            query = f"SELECT st_asbinary(st_transform({column},{interpretation})) FROM {schema}.{table_name}"
        else:
            query = f"SELECT st_asbinary({column}) FROM {schema}.{table_name}"

        data_points = db.query(query)

        self.logger.log(f"Received data points length: {len(data_points)}", Qgis.Info) 
      
        vl = QgsVectorLayer(geom_type, table_name, "memory")
        if not vl.isValid():
            self.logger.error("layer failed to load", Qgis.Critical)

        pr = vl.dataProvider()
        vl.startEditing()

        for _, i in enumerate(data_points):
            g = QgsGeometry()
            fet = QgsFeature()
            d = bytes.fromhex(i[0])
            g.fromWkb(d)
            fet.setGeometry(g)
            pr.addFeatures([fet])

        vl.updateExtents()
        vl.commitChanges()

        QgsProject.instance().addMapLayer(vl)
