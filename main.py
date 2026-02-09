# main.py - Script principal de l'application de gestion d'inventaire
import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.lang import Builder

# Pour la caméra et le scan de codes-barres
import cv2
from pyzbar import pyzbar
import json
from datetime import datetime
import os

# Interface Kivy
Builder.load_string('''
<ScannerPopup>:
    size_hint: (0.9, 0.9)
    title: "Scanner EAN"
    
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        
        Label:
            id: scanner_status
            text: "Prêt à scanner"
            size_hint_y: 0.1
            halign: 'center'
        
        Image:
            id: camera_preview
            size_hint_y: 0.7
        
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: 0.2
            padding: 10
            spacing: 10
            
            Button:
                text: "Démarrer"
                on_press: root.start_scan()
                background_color: 0.2, 0.7, 0.3, 1
            
            Button:
                text: "Arrêter"
                on_press: root.stop_scan()
                background_color: 0.9, 0.5, 0.2, 1
            
            Button:
                text: "Fermer"
                on_press: root.dismiss()
                background_color: 0.8, 0.2, 0.2, 1
''')


class ScannerPopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.capture = None
        self.scanning = False
        
    def start_scan(self):
        if not self.scanning:
            self.scanning = True
            try:
                self.capture = cv2.VideoCapture(0)
                if self.capture.isOpened():
                    self.ids.scanner_status.text = "Scan en cours..."
                    Clock.schedule_interval(self.update_frame, 1.0/30.0)
                else:
                    self.ids.scanner_status.text = "Caméra non disponible"
                    self.scanning = False
            except Exception as e:
                self.ids.scanner_status.text = f"Erreur: {str(e)}"
                self.scanning = False
    
    def stop_scan(self):
        if self.scanning:
            self.scanning = False
            if self.capture:
                self.capture.release()
            Clock.unschedule(self.update_frame)
            self.ids.scanner_status.text = "Scan arrêté"
    
    def update_frame(self, dt):
        if self.scanning and self.capture:
            ret, frame = self.capture.read()
            if ret:
                # Détecter les codes-barres
                barcodes = pyzbar.decode(frame)
                
                for barcode in barcodes:
                    barcode_data = barcode.data.decode("utf-8")
                    barcode_type = barcode.type
                    
                    self.ids.scanner_status.text = f"EAN détecté: {barcode_data}"
                    
                    # Appeler le callback avec les données
                    if self.callback:
                        self.callback(barcode_data)
                        self.stop_scan()
                        Clock.schedule_once(lambda dt: self.dismiss(), 0.5)
                        break
                
                # Afficher le flux vidéo
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.flip(frame, 0)
                
                # Convertir pour Kivy
                buf = frame.tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='rgb')
                texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
                
                self.ids.camera_preview.texture = texture
    
    def on_dismiss(self):
        self.stop_scan()


class InventoryApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_file = "inventory_data.json"
        self.inventory = []
        self.load_data()
    
    def build(self):
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # En-tête
        header = Label(
            text="📦 GESTION D'INVENTAIRE",
            size_hint_y=0.08,
            font_size='26sp',
            bold=True,
            color=(0.1, 0.4, 0.8, 1)
        )
        main_layout.add_widget(header)
        
        # Formulaire
        form_container = BoxLayout(orientation='vertical', size_hint_y=0.4)
        
        # Grille pour les champs
        form_grid = GridLayout(cols=2, spacing=10, padding=10)
        
        # Champs de saisie
        form_grid.add_widget(Label(text="Nom du produit:", bold=True))
        self.product_name = TextInput(
            multiline=False, 
            hint_text="Ex: Ordinateur Portable",
            size_hint_y=None,
            height=40
        )
        form_grid.add_widget(self.product_name)
        
        form_grid.add_widget(Label(text="Quantité:", bold=True))
        self.quantity = TextInput(
            multiline=False, 
            hint_text="Ex: 5",
            input_filter='int',
            size_hint_y=None,
            height=40
        )
        form_grid.add_widget(self.quantity)
        
        form_grid.add_widget(Label(text="Numéro de série:", bold=True))
        self.serial = TextInput(
            multiline=False, 
            hint_text="Ex: SN123456",
            size_hint_y=None,
            height=40
        )
        form_grid.add_widget(self.serial)
        
        form_grid.add_widget(Label(text="Code EAN:", bold=True))
        ean_box = BoxLayout(spacing=5)
        self.ean = TextInput(
            multiline=False, 
            hint_text="13 chiffres",
            size_hint_x=0.7,
            size_hint_y=None,
            height=40
        )
        ean_box.add_widget(self.ean)
        
        scan_btn = Button(
            text="📷 Scan",
            size_hint_x=0.3,
            size_hint_y=None,
            height=40,
            background_color=(0.2, 0.6, 0.9, 1)
        )
        scan_btn.bind(on_press=self.open_scanner)
        ean_box.add_widget(scan_btn)
        
        form_grid.add_widget(ean_box)
        
        form_container.add_widget(form_grid)
        
        # Boutons du formulaire
        btn_box = BoxLayout(spacing=10, size_hint_y=0.2)
        
        add_btn = Button(
            text="➕ AJOUTER PRODUIT",
            background_color=(0.2, 0.7, 0.3, 1),
            bold=True
        )
        add_btn.bind(on_press=self.add_product)
        btn_box.add_widget(add_btn)
        
        clear_btn = Button(
            text="🗑️ EFFACER",
            background_color=(0.9, 0.5, 0.2, 1)
        )
        clear_btn.bind(on_press=self.clear_form)
        btn_box.add_widget(clear_btn)
        
        form_container.add_widget(btn_box)
        main_layout.add_widget(form_container)
        
        # Séparateur
        separator = Label(
            text="─" * 50,
            size_hint_y=0.02,
            color=(0.5, 0.5, 0.5, 1)
        )
        main_layout.add_widget(separator)
        
        # Liste des produits
        list_header = Label(
            text="📋 PRODUITS ENREGISTRÉS",
            size_hint_y=0.06,
            font_size='18sp',
            bold=True,
            color=(0.3, 0.3, 0.3, 1)
        )
        main_layout.add_widget(list_header)
        
        # ScrollView pour la liste
        scroll = ScrollView(size_hint_y=0.4)
        self.product_list = BoxLayout(
            orientation='vertical',
            spacing=5,
            size_hint_y=None
        )
        self.product_list.bind(minimum_height=self.product_list.setter('height'))
        scroll.add_widget(self.product_list)
        main_layout.add_widget(scroll)
        
        # Boutons d'action
        action_box = BoxLayout(spacing=10, size_hint_y=0.08)
        
        export_btn = Button(
            text="💾 EXPORTER",
            background_color=(0.4, 0.4, 0.8, 1)
        )
        export_btn.bind(on_press=self.export_data)
        action_box.add_widget(export_btn)
        
        delete_all_btn = Button(
            text="🗑️ TOUT SUPPRIMER",
            background_color=(0.8, 0.2, 0.2, 1)
        )
        delete_all_btn.bind(on_press=self.confirm_delete_all)
        action_box.add_widget(delete_all_btn)
        
        main_layout.add_widget(action_box)
        
        # Statistiques
        self.stats_label = Label(
            text="Total: 0 produit(s)",
            size_hint_y=0.04,
            font_size='14sp',
            color=(0.4, 0.4, 0.4, 1)
        )
        main_layout.add_widget(self.stats_label)
        
        # Mettre à jour l'affichage
        self.update_display()
        
        return main_layout
    
    def open_scanner(self, instance):
        popup = ScannerPopup(callback=self.on_scan_complete)
        popup.open()
    
    def on_scan_complete(self, ean_code):
        self.ean.text = ean_code
        self.show_message("Scan réussi", f"Code EAN scanné: {ean_code}")
    
    def add_product(self, instance):
        # Récupérer les valeurs
        name = self.product_name.text.strip()
        qty = self.quantity.text.strip()
        serial = self.serial.text.strip()
        ean = self.ean.text.strip()
        
        # Validation
        if not name:
            self.show_message("Erreur", "Le nom du produit est obligatoire")
            return
        
        if not qty:
            qty = "1"
        
        try:
            qty_int = int(qty)
            if qty_int <= 0:
                raise ValueError
        except ValueError:
            self.show_message("Erreur", "La quantité doit être un nombre positif")
            return
        
        # Créer l'entrée
        product = {
            'id': len(self.inventory) + 1,
            'name': name,
            'quantity': qty_int,
            'serial': serial,
            'ean': ean,
            'date': datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        
        # Ajouter à l'inventaire
        self.inventory.append(product)
        
        # Sauvegarder
        self.save_data()
        
        # Mettre à jour l'affichage
        self.update_display()
        self.clear_form()
        
        self.show_message("Succès", f"'{name}' ajouté au stock")
    
    def clear_form(self, instance=None):
        self.product_name.text = ""
        self.quantity.text = ""
        self.serial.text = ""
        self.ean.text = ""
    
    def update_display(self):
        # Vider la liste
        self.product_list.clear_widgets()
        
        if not self.inventory:
            empty_msg = Label(
                text="Aucun produit enregistré.\nCommencez par ajouter un produit.",
                size_hint_y=None,
                height=80,
                halign='center',
                color=(0.6, 0.6, 0.6, 1)
            )
            self.product_list.add_widget(empty_msg)
        else:
            # Afficher les produits (du plus récent au plus ancien)
            for product in reversed(self.inventory[-20:]):  # Limiter à 20 produits
                # Créer un conteneur pour chaque produit
                item_box = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=60,
                    padding=5,
                    spacing=10
                )
                
                # Informations du produit
                info_text = (
                    f"[b]{product['name']}[/b]\n"
                    f"Quantité: {product['quantity']} | "
                )
                
                if product['ean']:
                    info_text += f"EAN: {product['ean']} | "
                if product['serial']:
                    info_text += f"S/N: {product['serial']}"
                
                info_label = Label(
                    text=info_text,
                    size_hint_x=0.8,
                    markup=True,
                    halign='left',
                    valign='middle'
                )
                info_label.bind(size=info_label.setter('text_size'))
                item_box.add_widget(info_label)
                
                # Bouton de suppression
                delete_btn = Button(
                    text="✕",
                    size_hint_x=0.2,
                    font_size='18sp',
                    background_color=(0.9, 0.3, 0.3, 1)
                )
                delete_btn.product_id = product['id']
                delete_btn.bind(on_press=self.delete_product)
                item_box.add_widget(delete_btn)
                
                self.product_list.add_widget(item_box)
        
        # Mettre à jour les statistiques
        total_items = len(self.inventory)
        total_qty = sum(p['quantity'] for p in self.inventory)
        self.stats_label.text = f"Total: {total_items} produit(s) | {total_qty} unité(s)"
    
    def delete_product(self, instance):
        product_id = instance.product_id
        self.inventory = [p for p in self.inventory if p['id'] != product_id]
        self.save_data()
        self.update_display()
        self.show_message("Succès", "Produit supprimé")
    
    def confirm_delete_all(self, instance):
        if not self.inventory:
            self.show_message("Information", "L'inventaire est déjà vide")
            return
        
        # Popup de confirmation
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        content.add_widget(Label(
            text="Êtes-vous sûr de vouloir\nsupprimer TOUS les produits?",
            halign='center'
        ))
        
        btn_box = BoxLayout(spacing=10)
        
        yes_btn = Button(
            text="OUI, supprimer tout",
            background_color=(0.9, 0.2, 0.2, 1)
        )
        
        no_btn = Button(
            text="NON, annuler",
            background_color=(0.4, 0.6, 0.9, 1)
        )
        
        popup = Popup(
            title="⚠️ Confirmation",
            content=content,
            size_hint=(0.8, 0.4)
        )
        
        def confirm(btn):
            self.inventory = []
            self.save_data()
            self.update_display()
            popup.dismiss()
            self.show_message("Succès", "Tous les produits ont été supprimés")
        
        def cancel(btn):
            popup.dismiss()
        
        yes_btn.bind(on_press=confirm)
        no_btn.bind(on_press=cancel)
        
        btn_box.add_widget(yes_btn)
        btn_box.add_widget(no_btn)
        content.add_widget(btn_box)
        popup.open()
    
    def export_data(self, instance):
        if not self.inventory:
            self.show_message("Erreur", "Aucune donnée à exporter")
            return
        
        try:
            # Créer un nom de fichier avec date
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"inventory_export_{timestamp}.json"
            
            # Exporter les données
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.inventory, f, indent=2, ensure_ascii=False)
            
            self.show_message("Succès", f"Données exportées dans:\n{filename}")
        except Exception as e:
            self.show_message("Erreur", f"Échec de l'export:\n{str(e)}")
    
    def show_message(self, title, message):
        content = Label(text=message, halign='center')
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.7, 0.4)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)
    
    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.inventory, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur de sauvegarde: {e}")
    
    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.inventory = json.load(f)
        except Exception as e:
            print(f"Erreur de chargement: {e}")
            self.inventory = []
    
    def on_stop(self):
        self.save_data()


if __name__ == '__main__':
    InventoryApp().run()