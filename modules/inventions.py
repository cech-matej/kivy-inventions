from kivy.app import App

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView

from kivymd.uix.button import MDFlatButton, MDFloatingActionButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem, ImageLeftWidget, IconRightWidget

from modules.db import Database, Invention


# Vytvoření obsahu dialogového okna pro vložení nového vynálezu do databáze
class InventionContent(BoxLayout):
    def __init__(self, id, *args, **kwargs):
        super().__init__(**kwargs)
        # Jestliže již existuje id vynálezu (předané jako parametr)
        if id:
            invention = vars(app.inventions.database.read_invention_by_id(id))
        else:
            # Když id neexistuje, do proměnné person se vloží výchozí hodnoty (nový záznam)
            invention = {"id": "", "name": "", "description": ""}

        print(invention)

        self.ids.invention_name.text = invention['name']

        if invention['description'] is None:
            self.ids.invention_description.text = ""
        else:
            self.ids.invention_description.text = invention['description']


# Třída vytvářející dialogové okno pro vložení nového vynálezu
class InventionDialog(MDDialog):
    def __init__(self, id, *args, **kwargs):
        # Nastavení parametrů dialogového okna
        super(InventionDialog, self).__init__(
            # Dialogové okno s uživatelským obsahem
            type="custom",
            # Vytvoření objektu s uživatelským obsahem (podle třídy StateContent)
            content_cls=InventionContent(id=id),
            title='Nový vynález',
            size_hint=(.8, 1),
            # Vytvoření tlačítek s odkazy na ohlasové metody
            buttons=[
                MDFlatButton(text='Uložit', on_release=self.save_dialog),
                MDFlatButton(text='Zrušit', on_release=self.cancel_dialog)
            ]
        )

        self.id = id

    # Implementace ohlasových metod
    # Uložení nového záznamu státu
    def save_dialog(self, *args):
        invention = {}
        invention['name'] = self.content_cls.ids.invention_name.text
        invention['description'] = self.content_cls.ids.invention_description.text

        # Vytvoření nového státu v databázi
        if self.id:
            invention["id"] = self.id
            app.inventions.update(invention)
        # ...v opačném případě vytváříme nový záznam
        else:
            app.inventions.create(invention)

        # Zavření dialogového okna
        self.dismiss()

    # Zavření dialogového okna bez uložení
    def cancel_dialog(self, *args):
        self.dismiss()


# Třída MyItem řeší akce související s jednou položkou (vynálezem) v seznamu
class MyItem(TwoLineAvatarIconListItem):
    # Konstruktoru se předává parametr item - datový objekt jednoho vynálezu
    def __init__(self, item, *args, **kwargs):
        super(MyItem, self).__init__()
        # Předání informací o vynálezu do parametrů widgetu
        self.id = item['id']
        self.text = item['name']

        if item['description'] is None:
            self.secondary_text = ""
        else:
            self.secondary_text = item['description']
        self._no_ripple_effect = True

        # Zobrazení obrázku
        self.image = ImageLeftWidget()
        if item['photo'] is None:
            self.image.source = f"img/profile.jpg"
        else:
            self.image.source = f"images/inventions/{item['flag'].decode('utf-8')}"
        self.add_widget(self.image)

        # Vložení ikony pro vymazání osoby ze seznamu
        self.icon = IconRightWidget(icon="delete", on_release=self.on_delete)
        self.add_widget(self.icon)

    def on_press(self):
        """
        Metoda je vyvolána po stisknutí tlačítka v oblasti widgetu
        Otevře se dialogové okno pro editaci osobních dat
        """
        self.dialog = InventionDialog(id=self.id)
        self.dialog.open()

    def on_delete(self, *args):
        """
        Metoda je vyvolána po kliknutí na ikonu koše - vymazání záznamu
        """
        yes_button = MDFlatButton(text='Ano', on_release=self.yes_button_release)
        no_button = MDFlatButton(text='Ne', on_release=self.no_button_release)
        self.dialog_confirm = MDDialog(type="confirmation", title='Smazání záznamu',
                                       text="Chcete opravdu smazat tento záznam?", buttons=[yes_button, no_button])
        self.dialog_confirm.open()

    # Reakce na stisknutí tlačítka Ano
    def yes_button_release(self, *args):
        # Vyvolána metoda zajišťující vymazání záznamu podle předaného id
        app.inventions.database.delete_invention(self.id)
        self.dialog_confirm.dismiss()
        app.inventions.rewrite_list()

    # Reakce na stisknutí tlačítka Ne
    def no_button_release(self, *args):
        self.dialog_confirm.dismiss()


# Třída Inventions řeší akce související se seznamem osob
class Inventions(BoxLayout):
    def __init__(self, *args, **kwargs):
        super(Inventions, self).__init__(orientation="vertical")
        # Globální proměnná - obsahuje kontext aplikace
        global app
        app = App.get_running_app()
        # Vytvoření rolovacího seznamu
        scrollview = ScrollView()
        self.list = MDList()
        # Volání metody, která vytvoří databázový objekt
        self.database = Database(dbtype='sqlite', dbname='inventions.db')
        # Volání metody, která načte a přepíše seznam vynálezů na obrazovku
        self.rewrite_list()
        scrollview.add_widget(self.list)
        self.add_widget(scrollview)
        # Vytvoření nového boxu pro tlačítko
        button_box = BoxLayout(orientation='horizontal', size_hint_y=0.1)

        new_invention_btn = MDFloatingActionButton()
        new_invention_btn.icon = "plus"
        new_invention_btn.md_bg_color = [0, 0.5, 0.8, 1]
        new_invention_btn.pos_hint = {"center_x": .5}
        new_invention_btn.on_release = self.on_create_invention
        button_box.add_widget(new_invention_btn)

        self.add_widget(button_box)

    def rewrite_list(self):
        """
        Metoda přepíše seznam osob na obrazovce
        """
        # Odstraní všechny stávající widgety (typu MyItem) z listu
        self.list.clear_widgets()
        # Načte všechny vynálezy z databáze
        inventions = self.database.read_inventions()
        # Pro všechny vynálezy v seznamu inventions vytváří widget MyItem
        for invention in inventions:
            print(vars(invention))
            self.list.add_widget(MyItem(item=vars(invention)))

    def on_create_invention(self, *args):
        """
        Metoda reaguje na tlačítko + a vyvolá dialogové okno InventionDialog
        """
        self.dialog = InventionDialog(id=None)
        self.dialog.open()

    def create(self, invention):
        """
        Metoda vytvoří nový záznam o vynálezu
        """
        create_invention = Invention()
        create_invention.name = invention['name']
        create_invention.description = invention['description']
        self.database.create_invention(create_invention)
        self.rewrite_list()

    def update(self, nation):
        """
        Metoda aktualizuje záznam osoby
        """
        update_invention = self.database.read_invention_by_id(nation['id'])
        update_invention.name = nation['name']
        update_invention.description = nation['description']
        self.database.update()
        self.rewrite_list()

    def delete(self, id):
        """
        Metoda smaže záznam o osobě - podle předaného id
        """
        self.database.delete_invention(id)
        self.rewrite_list()
