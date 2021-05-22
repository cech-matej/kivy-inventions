# Import aplikačního
import os
import uuid

from kivy.app import App
# Importy Kivy komponent
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
# Importy potřebných MD komponent
from kivymd.uix.button import MDFlatButton, MDFillRoundFlatIconButton, MDFloatingActionButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem, ImageLeftWidget, IconRightWidget
from kivymd.uix.menu import MDDropdownMenu
# Import databázového modulu a jeho tříd
from modules.db import Database, Inventor, Nation, Invention, Category

from kivymd.uix.picker import MDDatePicker


# ----------------------------------------------

from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from shutil import copyfile

from PIL import Image


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

# ----------------------------------------------


# Třída se stará o vytvoření obsahu dialogového okna pro vytvoření / editaci osob
class InventorContent(BoxLayout):
    def __init__(self, id, *args, **kwargs):
        super().__init__(**kwargs)

        self.predane_id = id

        # Jestliže již existuje id osoby (předané jako parametr)
        if id:
            # Do proměnné person se načtou údaje z daného databázového objektu (vybrán podle id)
            # Funkce vars zajistí konverzi objektu do podoby slovníku v Pythonu (typ dictionary)
            inventor = vars(app.inventors.database.read_inventor_by_id(id))
        else:
            # Když id neexistuje, do proměnné person se vloží výchozí hodnoty (nový záznam)
            inventor = {"id": "", "first_name": "", "last_name": "", "nation_id": "Stát"}
            # inventor = {"id": "", "first_name": "", "last_name": "", "nation_id": "Stát", "photo": ""}

        print(inventor)

        # Do editačního prvku označeného id=person_name se předá údaj z proměnné person (jméno osoby)
        self.ids.inventor_first_name.text = inventor['first_name']
        self.ids.inventor_last_name.text = inventor['last_name']
        # Do promměnné states budou načteny všechny státy uložené v databázi
        states = app.inventors.database.read_nations()
        # Do promměnné menu_items se pomocí proměnné states vytvoří seznam (list) položek-států, které budou použity jako obsah DropDownMenu
        # Atribut on_release definuje metodu, která ošetří výběr některého státu
        menu_items = [{"viewclass": "OneLineListItem", "text": f"{state.abbr}",
                       "on_release": lambda x=f"{state.abbr}": self.set_item(x)} for state in states]
        # Vytvoření objektu menu_states pro výběr státu
        self.menu_states = MDDropdownMenu(
            caller=self.ids.nation_item,
            items=menu_items,
            position="center",
            width_mult=5,
        )

        # Nastavení aktivní položky v seznamu států podle státní příslušnosti dané osoby
        if type(inventor['nation_id']) == str:
            self.ids.nation_item.set_item(inventor['nation_id'])
            self.ids.nation_item.text = inventor['nation_id']
        # print(app.inventors.database.read_nation_abbr_by_id(inventor['nation_id']))
        else:
            self.ids.nation_item.set_item(app.inventors.database.read_nation_abbr_by_id(inventor['nation_id']))
            self.ids.nation_item.text = app.inventors.database.read_nation_abbr_by_id(inventor['nation_id'])
        # self.ids.nation_item.set_item(app.inventors.database.read_nation_by_id(inventor['nation_id']))
        # self.ids.nation_item.text = app.inventors.database.read_nation_by_id(inventor['nation_id'])

        birthday_button = self.ids.inventor_birthday
        birthday_button.on_release = self.show_date_picker

        img_button = self.ids.inventor_img
        if id:
            img_button.on_release = self.show_load
        else:
            img_button.on_release = self.nono

    def on_save(self, instance, value, date_range):
        print(value)
        ''' DATUM SE ZATÍM NIKAM NEUKLÁDÁ, POUZE SE VYPISUJE DO KONZOLE '''

    def on_cancel(self, instance, value):
        '''Events called when the "CANCEL" dialog box button is clicked.'''

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

    # Metoda ošetřuje výběr státu z menu
    def set_item(self, text_item):
        # Podle textu vybrané položky se nastaví aktuálně vybraný stát
        self.ids.nation_item.set_item(text_item)
        self.ids.nation_item.text = text_item
        # Uzavření menu
        self.menu_states.dismiss()

    # File chooser
    def load(self, path, filename):
        with open(os.path.join(path, filename[0])):
            ext = filename[0].split('.')[-1]
            # file_name = "%s.%s" % (uuid.uuid4(), ext)
            file_name = "%s.%s" % (self.predane_id, ext)
            destination = os.path.join('gallery', file_name)
            copyfile(os.path.join(path, filename[0]), destination)

            if ext != "jpg":
                im = Image.open(f"gallery/{file_name}")
                im_conv = im.convert('RGB')
                im_conv.save(f"gallery/{self.predane_id}.jpg")

            # print("%s.%s" % (self.predane_id, ext))

        # inventor = vars(app.inventors.database.read_inventor_by_id(self.predane_id))
        # inventor['photo'] = file_name
        # app.inventors.update(inventor)

        # print(inventor)
        print(file_name)

        self._popup.dismiss()
        # app.inventors.rewrite_list()

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        cont = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Výběr obrázku", content=cont, size_hint=(0.9, 0.9))
        self._popup.open()

    def nono(self):
        # cont = Label(text="Nejdřív musíte vynálezce přidat do databáze, poté nastavit obrázek")
        cont = Button(text="Zavřít")
        popup = Popup(content=cont, size_hint=(0.8, 0.2), title="Nejdřív musíte vynálezce přidat do databáze, poté nastavit obrázek")
        cont.bind(on_press=popup.dismiss)
        popup.open()


# Třída umožní vytvořit dialogové okno k editaci osobních údajů
class InventorDialog(MDDialog):
    def __init__(self, id, *args, **kwargs):
        super(InventorDialog, self).__init__(
            # Vytvoření objektu s uživatelským obsahem (podle třídy PersonContent)
            type="custom",
            content_cls=InventorContent(id=id),
            title='Záznam osoby',
            text='Ahoj',
            size_hint=(.8, 1),
            buttons=[
                MDFlatButton(text='Uložit', on_release=self.save_dialog),
                MDFlatButton(text='Zrušit', on_release=self.cancel_dialog)
            ]
        )
        self.id = id

    # Ošetření tlačítka "Uložit"
    def save_dialog(self, *args):
        # Vytvoření nového slovníku, kterému jsou předány údaje z dialogových prvků
        inventor = {}
        inventor['first_name'] = self.content_cls.ids.inventor_first_name.text
        inventor['last_name'] = self.content_cls.ids.inventor_last_name.text
        inventor['nation_id'] = self.content_cls.ids.nation_item.text
        # Jestliže už existuje id, provádíme aktualizaci...
        if self.id:
            inventor["id"] = self.id
            app.inventors.update(inventor)
        # ...v opačném případě vytváříme nový záznam
        else:
            app.inventors.create(inventor)
        # Zavření dialogového okna
        self.dismiss()

    # Ošetření tlačítka "Zrušit"
    def cancel_dialog(self, *args):
        self.dismiss()


# Třída MyItem řeší akce související s jednou položkou (osobou) v seznamu
class MyItem(TwoLineAvatarIconListItem):
    # Konstruktoru se předává parametr item - datový objekt jedné osoby
    def __init__(self, item, *args, **kwargs):
        super(MyItem, self).__init__()
        # Předání informací o osobě do parametrů widgetu
        self.id = item['id']
        self.text = f"{item['first_name']} {item['last_name']}"
        self.database = Database(dbtype='sqlite', dbname='inventions.db')

        # self.secondary_text = app.inventors.database.read_nation_by_id(item['nation_id'])

        self.secondary_text = self.database.read_nation_by_id(item['nation_id']).name
        self._no_ripple_effect = True
        # Zobrazení vlajky podle státu osoby
        self.image = ImageLeftWidget()
        # Vlajky jsou umístěny ve složce images
        if item['photo'] is None:
            path_to_img = f"gallery/{item['id']}.jpg"
            if os.path.isfile(path_to_img):
                self.image.source = f"gallery/{item['id']}.jpg"

            else:
                self.image.source = f"img/profile.jpg"

        else:
            # self.image.source = f"images/inventors/{item['id']}.png"
            self.image.source = f"gallery/{item['photo']}"
        self.add_widget(self.image)
        # Vložení ikony pro vymazání osoby ze seznamu
        self.icon = IconRightWidget(icon="delete", on_release=self.on_delete)
        self.add_widget(self.icon)

    def on_press(self):
        """
        Metoda je vyvolána po stisknutí tlačítka v oblasti widgetu
        Otevře se dialogové okno pro editaci osobních dat
        """
        self.dialog = InventorDialog(id=self.id)
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
        app.inventors.database.delete_inventor(self.id)
        self.dialog_confirm.dismiss()
        app.inventors.rewrite_list()

    # Reakce na stisknutí tlačítka Ne
    def no_button_release(self, *args):
        self.dialog_confirm.dismiss()


# Třída Persons řeší akce související se seznamem osob
class Inventors(BoxLayout):
    # Metoda konstruktoru
    def __init__(self, *args, **kwargs):
        super(Inventors, self).__init__(orientation="vertical")
        # Globální proměnná - obsahuje kontext aplikace
        global app
        app = App.get_running_app()
        # Vytvoření rolovacího seznamu
        scrollview = ScrollView()
        self.list = MDList()
        # Volání metody, která vytvoří databázový objekt
        self.database = Database(dbtype='sqlite', dbname='inventions.db')
        # Volání metody, která načte a přepíše seznam osob na obrazovku
        self.rewrite_list()

        # scrollview.pos_hint = {'x': 0, 'y': 500}
        # # print(scrollview.pos)
        # # self.list.pos = (0, 500)
        # self.list.pos_hint = {'x': 0, 'y': 500}
        # # print(self.list.pos)

        scrollview.add_widget(self.list)
        self.add_widget(scrollview)
        # Vytvoření nového boxu pro tlačítka Nová osoba a Nový stát
        button_box = BoxLayout(orientation='horizontal', size_hint_y=0.1)

        new_inventor_btn = MDFloatingActionButton()
        new_inventor_btn.icon = "plus"
        new_inventor_btn.md_bg_color = [0, 0.5, 0.8, 1]
        new_inventor_btn.pos_hint = {"center_x": .5}
        new_inventor_btn.on_release = self.on_create_inventor
        button_box.add_widget(new_inventor_btn)

        self.add_widget(button_box)

    def rewrite_list(self):
        """
        Metoda přepíše seznam osob na obrazovce
        """
        # Odstraní všechny stávající widgety (typu MyItem) z listu
        self.list.clear_widgets()
        # Načte všechny osoby z databáze
        inventors = self.database.read_inventors()
        # Pro všechny osoby v seznamu persons vytváří widget MyItem
        for inventor in inventors:
            print(vars(inventor))
            self.list.add_widget(MyItem(item=vars(inventor)))

    def on_create_inventor(self, *args):
        """
        Metoda reaguje na tlačítko Nová osoba a vyvolá dialogové okno PersonDialog
        """
        self.dialog = InventorDialog(id=None)
        self.dialog.open()

    # def on_create_state(self, *args):
    #     """
    #     Metoda reaguje na tlačítko Nový stát a vyvolá dialogové okno StateDialog
    #     """
    #     self.dialog = NationDialog()
    #     self.dialog.open()

    def create(self, inventor):
        """
        Metoda vytvoří nový záznam o osobě
        """
        create_inventor = Inventor()
        create_inventor.first_name = inventor['first_name']
        create_inventor.last_name = inventor['last_name']
        # create_inventor.nation_id = inventor['nation_id']
        create_inventor.nation_id = app.inventors.database.read_nation_id_by_abbr(inventor['nation_id'])
        # create_inventor.photo = inventor['photo']
        self.database.create_inventor(create_inventor)
        self.rewrite_list()

    def update(self, inventor):
        """
        Metoda aktualizuje záznam osoby
        """
        update_inventor = self.database.read_inventor_by_id(inventor['id'])
        update_inventor.first_name = inventor['first_name']
        update_inventor.last_name = inventor['last_name']
        update_inventor.nation_id = app.inventors.database.read_nation_id_by_abbr(inventor['nation_id'])
        # update_inventor.photo = inventor['photo']
        self.database.update()
        self.rewrite_list()

    def delete(self, id):
        """
        Metoda smaže záznam o osobě - podle předaného id
        """
        self.database.delete_inventor(id)
        self.rewrite_list()
