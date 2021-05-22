# Import aplikačního
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


# Třída se stará o vytvoření obsahu dialogového okna pro vložení nového státu do databáze
class NationContent(BoxLayout):
    def __init__(self, id, *args, **kwargs):
        super().__init__(**kwargs)
        # Jestliže již existuje id osoby (předané jako parametr)
        if id:
            # Do proměnné person se načtou údaje z daného databázového objektu (vybrán podle id)
            # Funkce vars zajistí konverzi objektu do podoby slovníku v Pythonu (typ dictionary)
            # inventor = vars(app.inventors.database.read_inventor_by_id(id))
            nation = vars(app.nations.database.read_nation_by_id(id))
        else:
            # Když id neexistuje, do proměnné person se vloží výchozí hodnoty (nový záznam)
            # inventor = {"id": "", "first_name": "", "last_name": "", "nation_id": "Stát"}
            nation = {"id": "", "abbr": "", "name": ""}

        print(nation)

        # Do editačního prvku označeného id=person_name se předá údaj z proměnné person (jméno osoby)
        # self.ids.inventor_first_name.text = inventor['first_name']
        self.ids.nation_abbr.text = nation['abbr']
        # self.ids.inventor_last_name.text = inventor['last_name']
        self.ids.nation_name.text = nation['name']
        # Do promměnné states budou načteny všechny státy uložené v databázi
        # states = app.inventors.database.read_nations()
        # Do promměnné menu_items se pomocí proměnné states vytvoří seznam (list) položek-států, které budou použity jako obsah DropDownMenu
        # Atribut on_release definuje metodu, která ošetří výběr některého státu
        # menu_items = [{"viewclass": "OneLineListItem", "text": f"{state.abbr}",
        #                "on_release": lambda x=f"{state.abbr}": self.set_item(x)} for state in states]
        # Vytvoření objektu menu_states pro výběr státu
        # self.menu_states = MDDropdownMenu(
        #     caller=self.ids.nation_item,
        #     items=menu_items,
        #     position="center",
        #     width_mult=5,
        # )

        # # Nastavení aktivní položky v seznamu států podle státní příslušnosti dané osoby
        # self.ids.nation_item.set_item(inventor['nation_id'])
        # # print(app.inventors.database.read_nation_abbr_by_id(inventor['nation_id']))
        # # self.ids.nation_item.set_item(app.inventors.database.read_nation_by_id(inventor['nation_id']))
        #
        # self.ids.nation_item.text = inventor['nation_id']
        # # self.ids.nation_item.text = app.inventors.database.read_nation_by_id(inventor['nation_id'])


# Třída vytvářející dialogové okno pro vložení nového státu
class NationDialog(MDDialog):
    def __init__(self, id, *args, **kwargs):
        # Nastavení parametrů dialogového okna
        super(NationDialog, self).__init__(
            # Dialogové okno s uživatelským obsahem
            type="custom",
            # Vytvoření objektu s uživatelským obsahem (podle třídy StateContent)
            content_cls=NationContent(id=id),
            title='Nový stát',
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
        # Vytvoření nového datového objektu státu
        # nation = Nation()
        nation = {}
        # Uložení údajů o novém státu podle prvků dialogového okna
        # nation.abbr = self.content_cls.ids.nation_abbr.text
        nation['abbr'] = self.content_cls.ids.nation_abbr.text
        # nation.name = self.content_cls.ids.nation_name.text
        nation['name'] = self.content_cls.ids.nation_name.text
        # Vytvoření nového státu v databázi

        # app.nations.database.create_nation(state)

        if self.id:
            nation["id"] = self.id
            app.nations.update(nation)
        # ...v opačném případě vytváříme nový záznam
        else:
            app.nations.create(nation)

        # Zavření dialogového okna
        self.dismiss()

    # Zavření dialogového okna bez uložení
    def cancel_dialog(self, *args):
        self.dismiss()


# Třída MyItem řeší akce související s jednou položkou (osobou) v seznamu
class MyItem(TwoLineAvatarIconListItem):
    # Konstruktoru se předává parametr item - datový objekt jedné osoby
    def __init__(self, item, *args, **kwargs):
        super(MyItem, self).__init__()
        # Předání informací o osobě do parametrů widgetu
        self.id = item['id']
        # self.text = f"{item['first_name']} {item['last_name']}"
        self.text = item['abbr']
        # self.database = Database(dbtype='sqlite', dbname='inventions.db')

        # self.secondary_text = app.inventors.database.read_nation_by_id(item['nation_id'])

        # self.secondary_text = self.database.read_nation_by_id(item['nation_id']).name
        self.secondary_text = item['name']
        self._no_ripple_effect = True
        # Zobrazení vlajky podle státu osoby
        self.image = ImageLeftWidget()
        # Vlajky jsou umístěny ve složce images
        if item['flag'] is None:
            self.image.source = f"img/profile.jpg"
        else:
            # self.image.source = f"images/states/{item['id']}.png"
            self.image.source = f"images/states/{item['flag'].decode('utf-8')}"
        self.add_widget(self.image)
        # Vložení ikony pro vymazání osoby ze seznamu
        self.icon = IconRightWidget(icon="delete", on_release=self.on_delete)
        self.add_widget(self.icon)

    def on_press(self):
        """
        Metoda je vyvolána po stisknutí tlačítka v oblasti widgetu
        Otevře se dialogové okno pro editaci osobních dat
        """
        self.dialog = NationDialog(id=self.id)
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
        app.nations.database.delete_nation(self.id)
        self.dialog_confirm.dismiss()
        app.nations.rewrite_list()

    # Reakce na stisknutí tlačítka Ne
    def no_button_release(self, *args):
        self.dialog_confirm.dismiss()


# Třída Persons řeší akce související se seznamem osob
class Nations(BoxLayout):
    # Metoda konstruktoru
    def __init__(self, *args, **kwargs):
        super(Nations, self).__init__(orientation="vertical")
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
        scrollview.add_widget(self.list)
        self.add_widget(scrollview)
        # Vytvoření nového boxu pro tlačítka Nová osoba a Nový stát
        button_box = BoxLayout(orientation='horizontal', size_hint_y=0.1)

        new_nation_btn = MDFloatingActionButton()
        new_nation_btn.icon = "plus"
        new_nation_btn.md_bg_color = [0, 0.5, 0.8, 1]
        new_nation_btn.pos_hint = {"center_x": .5}
        new_nation_btn.on_release = self.on_create_nation
        button_box.add_widget(new_nation_btn)

        self.add_widget(button_box)

    def rewrite_list(self):
        """
        Metoda přepíše seznam osob na obrazovce
        """
        # Odstraní všechny stávající widgety (typu MyItem) z listu
        self.list.clear_widgets()
        # Načte všechny osoby z databáze
        nations = self.database.read_nations()
        # Pro všechny osoby v seznamu persons vytváří widget MyItem
        for nation in nations:
            print(vars(nation))
            self.list.add_widget(MyItem(item=vars(nation)))

    def on_create_nation(self, *args):
        """
        Metoda reaguje na tlačítko Nový stát a vyvolá dialogové okno StateDialog
        """
        self.dialog = NationDialog(id=None)
        self.dialog.open()

    def create(self, nation):
        """
        Metoda vytvoří nový záznam o osobě
        """
        create_nation = Nation()
        create_nation.abbr = nation['abbr']
        create_nation.name = nation['name']
        # create_inventor.nation_id = inventor['nation_id']
        # create_nation.nation_id = app.inventors.database.read_nation_id_by_abbr(inventor['nation_id'])
        self.database.create_nation(create_nation)
        self.rewrite_list()

    def update(self, nation):
        """
        Metoda aktualizuje záznam osoby
        """
        update_nation = self.database.read_nation_by_id(nation['id'])
        update_nation.abbr = nation['abbr']
        update_nation.name = nation['name']
        # update_nation.nation_id = inventor['nation_id']
        self.database.update()
        self.rewrite_list()

    def delete(self, id):
        """
        Metoda smaže záznam o osobě - podle předaného id
        """
        self.database.delete_nation(id)
        self.rewrite_list()
