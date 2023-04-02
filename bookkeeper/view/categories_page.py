"""
Виджет для отображения страницы списка категорий в окне приложения
"""
from PySide6 import QtWidgets, QtCore
from typing import Callable, Optional

from bookkeeper.models.category import Category


class categoriesList(QtWidgets.QWidget):
    """
    Элемент отображения дерева категорий

    Для отображения необходимо указать функцию,
    которая будет возвращать дерево для отображения
    (json-like объект)
    """
    def __init__(
            self,
            *args,
            category_getter: Optional[Callable],
            category_editor: Optional[Callable],
            **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.getter = category_getter
        self.editor = category_editor

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.expenses_title = QtWidgets.QLabel("Категории расходов")
        self.layout.addWidget(self.expenses_title)

        self.categories_table = QtWidgets.QTableWidget(3, 20)
        self.categories_table.setColumnCount(3)
        self.categories_table.setRowCount(3)
        self.categories_table.setHorizontalHeaderLabels(
            ["Список категорий", "Id категории", "Id родительской категории"]
        )
        self.header = self.categories_table.horizontalHeader()
        self.header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            2, QtWidgets.QHeaderView.Stretch)

        self.set_categories(category_getter=category_getter)

        # self.set_tree(category_tree_getter=category_getter)

    # def build_category_tree(
    #         self,
    #         data: dict[str, dict] | None = None,
    #         parent: QtWidgets.QTreeWidgetItem | QtWidgets.QTreeWidget | None = None
    #         ) -> None:
    #     for key, value in data.items():
    #         if not isinstance(key, str):
    #             item = QtWidgets.QTreeWidgetItem(parent)
    #             item.setText(0, value["name"])
    #             item.setText(1, str(key))
    #             if isinstance(value, dict):
    #                 self.build_category_tree(data=value, parent=item)
    #
    # def set_tree(self, category_tree_getter: Callable) -> None:
    #     if self.category_tree.itemAt(0, 0) is not None:
    #         self.category_tree.setParent(None)
    #
    #     self.category_tree = QtWidgets.QTreeWidget()
    #     self.category_tree.setHeaderLabels(["Список категорий", "Id категории", "Id родительской категории"])
    #     self.category_tree.setColumnCount(2)
    #     tree_data = category_tree_getter()
    #     self.build_category_tree(data=tree_data, parent=self.category_tree)
    #     self.layout.addWidget(self.category_tree)

    def build_categories(self, data: list[Category]) -> None:
        for i, row in enumerate(data):
            self.categories_table.setItem(
                i, 0,
                QtWidgets.QTableWidgetItem(str(row.name).capitalize())
            )
            category_id_item = QtWidgets.QTableWidgetItem(str(row.pk))
            category_id_item.setFlags( QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled )
            self.categories_table.setItem(
                i, 1,
                category_id_item
            )
            self.categories_table.setItem(
                i, 2,
                QtWidgets.QTableWidgetItem(str(row.parent))
            )

    def set_categories(self, category_getter: Callable) -> None:
        if self.categories_table.itemAt(0, 0) is not None:
            self.layout.removeWidget(self.categories_table)

        categories_data = category_getter()

        self.categories_table = QtWidgets.QTableWidget(3, len(categories_data))
        self.categories_table.setColumnCount(3)
        self.categories_table.setRowCount(len(categories_data))
        self.categories_table.setHorizontalHeaderLabels(
            ["Список категорий", "Id категории", "Id родительской категории"]
        )
        self.header = self.categories_table.horizontalHeader()
        self.header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            2, QtWidgets.QHeaderView.Stretch)

        self.build_categories(categories_data)
        self.categories_table.itemChanged.connect(self.table_item_changed)
        self.layout.addWidget(self.categories_table)

    @QtCore.Slot()
    def table_item_changed(self, item):
        table_position = self.categories_table.indexFromItem(item)
        row, column = table_position.row(), table_position.column()

        category = self.categories_table.item(row, 0).text()
        category_id = int(self.categories_table.item(row, 1).text())
        parent_id = self.categories_table.item(row, 2).text()

        print("table item changed: ",
              category, " with ID ", category_id,
              " and parent with ID ", parent_id)
        self.editor(category_id, category, parent_id)


class addCategoryInput(QtWidgets.QWidget):
    """
    Элемент добавления новой категории в дерево
    """
    def __init__(self, *args, category_adder: Optional[Callable], **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.adder = category_adder

        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.input_category_name = QtWidgets.QLineEdit()
        self.input_category_name.setPlaceholderText("Введите название новой категории")

        self.input_parent_id = QtWidgets.QLineEdit()
        self.input_parent_id.setPlaceholderText("Введите id родительской категории")

        self.save_btn = QtWidgets.QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.save_btn_clicked)

        self.layout.addWidget(self.input_category_name)
        self.layout.addWidget(self.input_parent_id)
        self.layout.addWidget(self.save_btn)

    @QtCore.Slot()
    def save_btn_clicked(self):
        new_category_name = self.input_category_name.text()
        parent_text = self.input_parent_id.text()
        parent_id = int(parent_text) if parent_text != "" else None
        print("add new category: ", new_category_name, " with parent ", parent_id)
        self.adder(new_category_name, parent_id)


class editCategoryInput(QtWidgets.QWidget):
    """
    Элемент редактирования категории в дереве
    """
    def __init__(self, *args, category_editor: Optional[Callable], **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.editor = category_editor

        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.input_id_category = QtWidgets.QLineEdit()
        self.input_id_category.setPlaceholderText("Введите id изменяемой категории")

        self.input_category_name = QtWidgets.QLineEdit()
        self.input_category_name.setPlaceholderText("Введите новое название категории")

        self.input_parent_id = QtWidgets.QLineEdit()
        self.input_parent_id.setPlaceholderText("Введите id родительской категории")

        self.save_btn = QtWidgets.QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.save_btn_clicked)

        self.layout.addWidget(self.input_id_category)
        self.layout.addWidget(self.input_category_name)
        self.layout.addWidget(self.input_parent_id)
        self.layout.addWidget(self.save_btn)

    @QtCore.Slot()
    def save_btn_clicked(self):
        category_id = int(self.input_id_category.text())
        new_category_name = self.input_category_name.text()
        new_id = self.input_parent_id.text()
        new_parent_id = int(new_id) if new_id != "" else None
        print("edit category: ", category_id,
              " with new name ", new_category_name,
              " and parent_id ", new_parent_id)
        self.editor(category_id, new_category_name, new_parent_id)


class deleteCategoryInput(QtWidgets.QWidget):
    """
    Элемент удаления категории из дерева
    """
    def __init__(self, *args, category_deleter: Optional[Callable], **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.deleter = category_deleter

        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.input_id_category = QtWidgets.QLineEdit()
        self.input_id_category.setPlaceholderText("Введите id удаляемой категории")

        self.delete_btn = QtWidgets.QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.delete_btn_clicked)

        self.layout.addWidget(self.input_id_category)
        self.layout.addWidget(self.delete_btn)

    @QtCore.Slot()
    def delete_btn_clicked(self):
        category_id = int(self.input_id_category.text())
        print("delete category: ", category_id)
        self.deleter(category_id)


class elementAddCategory(QtWidgets.QWidget):
    def __init__(self, *args, adder: Optional[Callable], **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.add_category_title = QtWidgets.QLabel("Добавление новой категории")

        self.layout.addWidget(self.add_category_title)
        self.layout.addWidget(addCategoryInput(category_adder=adder))


class elementEditCategory(QtWidgets.QWidget):
    def __init__(self, *args, editor: Optional[Callable], **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.add_category_title = QtWidgets.QLabel("Редактирование категории")

        self.layout.addWidget(self.add_category_title)
        self.layout.addWidget(editCategoryInput(category_editor=editor))


class elementDeleteCategory(QtWidgets.QWidget):
    def __init__(self, *args, deleter: Optional[Callable], **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.add_category_title = QtWidgets.QLabel("Удаление существующей категории")

        self.layout.addWidget(self.add_category_title)
        self.layout.addWidget(deleteCategoryInput(category_deleter=deleter))


class categoriesPage(QtWidgets.QWidget):
    def __init__(self, *args,
                 get_handler: Optional[Callable],
                 add_handler: Optional[Callable],
                 edit_handler: Optional[Callable],
                 delete_handler: Optional[Callable],
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.categories_list = categoriesList(category_getter=get_handler, category_editor=edit_handler)
        self.layout.addWidget(self.categories_list)

        self.add_category = elementAddCategory(adder=add_handler)
        self.layout.addWidget(self.add_category)

        # self.edit_category = elementEditCategory(editor=edit_handler)
        # self.layout.addWidget(self.edit_category)

        self.delete_category = elementDeleteCategory(deleter=delete_handler)
        self.layout.addWidget(self.delete_category)
