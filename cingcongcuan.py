import customtkinter as ctk
from pymongo import MongoClient
from tkinter import messagebox, Scrollbar, Canvas, Frame, simpledialog
from PIL import Image, ImageTk

# Membuat koneksi ke MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["Warung_CingCongCuan"]
collection_user = db["User"]
collection_makanan = db["Makanan"]
collection_minuman = db["Minuman"]
collection_keranjang = db["Keranjang"]
collection_pesanan = db["Pesanan"]
collection_history = db["Riwayat Pemesanan"]

# Fungsi untuk menambah item ke keranjang
def add_to_cart(item, price, buyer_name):
    collection_keranjang.insert_one({"buyer_name": buyer_name, "item": item, "price": price})
    messagebox.showinfo("Keranjang", f"{item} telah ditambahkan ke keranjang.")

def delete_item_from_cart(item_id):
    collection_keranjang.delete_one({"_id": item_id})
    messagebox.showinfo("Keranjang", "Item telah dihapus dari keranjang.")

# Fungsi untuk menempatkan pesanan
def place_order(previous_window, buyer_name):
    cart_items = list(collection_keranjang.find())

    if cart_items:
        for item in cart_items:
            # Tambahkan item ke koleksi history
            collection_history.insert_one({"item": item['item'], "price": item['price']})

            # Tambahkan item ke koleksi pesanan
            collection_pesanan.insert_one({"item": item['item'], "price": item['price']})
        
            collection_keranjang.delete_many({"item": item['item'], "price": item['price']})

        messagebox.showinfo("Pesan", "Pesanan Anda telah diterima!")
    else:
        messagebox.showwarning("Keranjang Kosong", "Keranjang Anda kosong, tidak ada yang bisa dipesan.")

    # Kembali ke menu pembeli
    open_buyer_window(buyer_name, previous_window)

def edit_item(collection, item_name):
    new_name = simpledialog.askstring("Input", "Masukkan nama baru:", initialvalue=item_name)
    new_price = simpledialog.askinteger("Input", "Masukkan harga baru:")
    new_category = simpledialog.askstring("Input", "Masukkan kategori baru:")

    if new_name and new_price and new_category:
        collection.update_one(
            {"Nama": item_name},
            {"$set": {"Nama": new_name, "Harga": new_price, "Kategori": new_category}}
        )
        print(f"Item {item_name} berhasil diperbarui.")
    else:
        print("Pembatalan pembaruan item.")

def add_item(collection):
    new_name = simpledialog.askstring("Input", "Masukkan nama item:")
    new_price = simpledialog.askinteger("Input", "Masukkan harga item:")
    new_category = simpledialog.askstring("Input", "Masukkan kategori item:")

    if new_name and new_price and new_category:
        collection.insert_one(
            {"Nama": new_name, "Harga": new_price, "Kategori": new_category}
        )
        print(f"Item {new_name} berhasil ditambahkan.")
    else:
        print("Pembatalan penambahan item.")

def delete_item(collection):
    item_name = simpledialog.askstring("Input", "Masukkan nama item yang akan dihapus:")

    if item_name:
        result = collection.delete_one({"Nama": item_name})
        if result.deleted_count > 0:
            print(f"Item {item_name} berhasil dihapus.")
        else:
            print(f"Item {item_name} tidak ditemukan.")
    else:
        print("Pembatalan penghapusan item.")

def validate_seller(username, password):
    seller = collection_user.find_one({"username": username, "password": password})
    return seller is not None

# Fungsi untuk login sebagai penjual
def login_seller(previous_window):
    previous_window.destroy()
    login_seller_window()

# Fungsi untuk login sebagai pembeli
def login_buyer(previous_window):
    previous_window.destroy()
    name_prompt_window()

def save_username(name):
    user_data = {"name": name}
    collection_user.insert_one(user_data)

def back_to_main(current_window):
    current_window.destroy()
    open_main_window()

# Fungsi untuk menambahkan pesanan ke riwayat
def add_order_to_history(cart_items):  
    for item in cart_items:
        collection_history.insert_one({
            "item": item['item'],
            "price": item['price'] 
        })

def fulfill_order(order_id):
    collection_pesanan.delete_one({"_id": order_id})
    messagebox.showinfo("Pesanan", "Pesanan telah diproses.")

# Fungsi untuk membuka window keranjang
def open_cart_window(previous_window, buyer_name):
    previous_window.destroy()
    cart_window = ctk.CTk()
    cart_window.title("Keranjang")
    cart_window.geometry("360x640")

    main_frame = ctk.CTkFrame(cart_window, fg_color="white")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    welcome_label = ctk.CTkLabel(main_frame, text="Keranjang Anda", font=("Arial", 16, "bold"), text_color="black")
    welcome_label.pack(pady=10)

    # Ambil data keranjang dari database atau sumber lainnya
    cart_items = collection_keranjang.find()  # Query mengambil data dari MongoDB
    total_price = 0  # Inisialisasi total harga

    # Tampilkan setiap item-menu dalam keranjang
    for item in cart_items:
        # Buat frame untuk setiap item-menu
        item_frame = ctk.CTkFrame(main_frame, fg_color="white")
        item_frame.pack(fill="x", pady=5)

        # Tampilkan nama menu dan harga
        item_label = ctk.CTkLabel(item_frame, text=f"{item['item']} - Rp{item['price']}", text_color="black")
        item_label.pack(side="left", padx=10)

        # Tambahkan harga item ke total harga
        total_price += item['price']

        # Buat tombol "hapus" untuk menghapus item-menu
        delete_button = ctk.CTkButton(item_frame, text="Hapus", fg_color="#469173", hover_color="#345d4b", text_color="white", command=lambda item_id=item['_id']: delete_item_from_cart(item_id))
        delete_button.pack(side="right", padx=10)

    # Tampilkan total harga di bagian bawah
    total_label = ctk.CTkLabel(main_frame, text=f"Total Harga: Rp{total_price}", font=("Arial", 14, "bold"), text_color="black", bg_color="white")
    total_label.pack(pady=20)

    order_button = ctk.CTkButton(main_frame, text="Pesan", width=200, height=40, fg_color="#469173", hover_color="#345d4b", text_color="white", command=lambda: place_order(cart_window, buyer_name))
    order_button.pack(pady=20)

    back_button = ctk.CTkButton(main_frame, text="Kembali", width=200, height=40, fg_color="#469173", hover_color="#345d4b", text_color="white", command=lambda: open_buyer_window("User", cart_window))
    back_button.pack(pady=10)

    cart_window.mainloop()

# Function to open the food window
def open_food_window_seller(previous_window):
    previous_window.destroy()
    food_window = ctk.CTk()
    food_window.title("Makanan")
    food_window.geometry("360x640")

    canvas = Canvas(food_window, bg="white")
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = Scrollbar(food_window, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    scrollable_frame = Frame(canvas, bg="white")
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    back_button = ctk.CTkButton(scrollable_frame, text="<", width=40, height=40, fg_color="#469173", hover_color="#345d4b", text_color="white", command=lambda: open_seller_window(food_window))
    back_button.pack(pady=10, anchor="w")

    logo_frame = ctk.CTkFrame(scrollable_frame, fg_color="white")
    logo_frame.pack(pady=10)

    # Memuat gambar menggunakan PIL
    image_path = "logo.png"  # Ganti dengan path ke gambar Anda
    image = Image.open(image_path)
    image = image.resize((200, 200), Image.LANCZOS)
    logo_image = ImageTk.PhotoImage(image)

    logo_label = ctk.CTkLabel(logo_frame, image=logo_image, text="", width=100, height=100, fg_color="white", bg_color="white")
    logo_label.image = logo_image  # Simpan referensi ke gambar untuk mencegah garbage collection
    logo_label.pack()

    # Ambil data dari MongoDB
    foods = collection_makanan.find()

    food_categories = {}
    for food in foods:
        category = food.get('Kategori', 'Lainnya')
        if category not in food_categories:
            food_categories[category] = []
        food_categories[category].append(food)
    
    for category, items in food_categories.items():
        category_label = ctk.CTkLabel(scrollable_frame, text=category, font=("Arial", 14, "bold"), text_color="black")
        category_label.pack(anchor="w", padx=10, pady=5)

        for food in items:
            if 'Nama' in food and 'Harga' in food:
                item_frame = ctk.CTkFrame(scrollable_frame, fg_color="white")
                item_frame.pack(fill="x", pady=5)

                food_label = ctk.CTkLabel(item_frame, text=f"{food['Nama']} - Rp{food['Harga']}", text_color="black")
                food_label.pack(side="left", padx=10)

                edit_button = ctk.CTkButton(item_frame, text="Edit", width=60, height=30, fg_color="#469173", hover_color="#345d4b", text_color="white", command=lambda food_name=food['Nama']: edit_item(collection_makanan, food_name))
                edit_button.pack(side="right", padx=10)
            else:
                print("Invalid food structure:", food)

    control_frame = ctk.CTkFrame(scrollable_frame, fg_color="white")
    control_frame.pack(fill="x", pady=10)

    add_button = ctk.CTkButton(control_frame, text="Tambah", fg_color="#469173", hover_color="#345d4b", text_color="white", width=100, height=30, command=lambda: add_item(collection_makanan))
    add_button.pack(side="left", padx=5, pady=5)

    remove_button = ctk.CTkButton(control_frame, text="Hapus", fg_color="#469173", hover_color="#345d4b", text_color="white", width=100, height=30, command=lambda: delete_item(collection_makanan))
    remove_button.pack(side="left", padx=5, pady=5)

    food_window.mainloop()

# Function to open the food window
def open_drink_window_seller(previous_window):
    previous_window.destroy()
    drink_window = ctk.CTk()
    drink_window.title("Minuman")
    drink_window.geometry("360x640")

    canvas = Canvas(drink_window, bg="white")
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = Scrollbar(drink_window, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    scrollable_frame = Frame(canvas, bg="white")
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    back_button = ctk.CTkButton(scrollable_frame, text="<", width=40, height=40, fg_color="#469173", hover_color="#345d4b", text_color="white", command=lambda: open_seller_window(drink_window))
    back_button.pack(pady=10, anchor="w")

    logo_frame = ctk.CTkFrame(scrollable_frame, fg_color="white")
    logo_frame.pack(pady=10)

    # Memuat gambar menggunakan PIL
    image_path = "logo.png"  # Ganti dengan path ke gambar Anda
    image = Image.open(image_path)
    image = image.resize((200, 200), Image.LANCZOS)
    logo_image = ImageTk.PhotoImage(image)

    logo_label = ctk.CTkLabel(logo_frame, image=logo_image, text="", width=100, height=100, fg_color="white", bg_color="white")
    logo_label.image = logo_image  # Simpan referensi ke gambar untuk mencegah garbage collection
    logo_label.pack()

    # Ambil data dari MongoDB
    drinks = collection_minuman.find()

    # Group drinks by category
    drink_categories = {}
    for drink in drinks:
        category = drink.get('Kategori', 'Lainnya') 
        if category not in drink_categories:
            drink_categories[category] = []
        drink_categories[category].append(drink)
    
    # Display drinks grouped by category
    for category, items in drink_categories.items():
        category_label = ctk.CTkLabel(scrollable_frame, text=category, font=("Arial", 14, "bold"), text_color="black")
        category_label.pack(anchor="w", padx=10, pady=5)

        for drink in items:
            if 'Nama' in drink and 'Harga' in drink:
                item_frame = ctk.CTkFrame(scrollable_frame, fg_color="white")
                item_frame.pack(fill="x", pady=5)

                drink_label = ctk.CTkLabel(item_frame, text=f"{drink['Nama']} - Rp{drink['Harga']}", text_color="black")
                drink_label.pack(side="left", padx=10)

                edit_button = ctk.CTkButton(item_frame, text="Edit", width=60, height=30, fg_color="#469173", hover_color="#345d4b", text_color="white", command=lambda drink_name=drink['Nama']: edit_item(collection_minuman, drink_name))
                edit_button.pack(side="right", padx=10)
            else:
                print("Invalid drink structure:", drink)

    control_frame = ctk.CTkFrame(scrollable_frame, fg_color="white")
    control_frame.pack(fill="x", pady=10)

    add_button = ctk.CTkButton(control_frame, text="Tambah", fg_color="#469173", hover_color="#345d4b", text_color="white", width=100, height=30, command=lambda: add_item(collection_minuman))
    add_button.pack(side="left", padx=5, pady=5)

    remove_button = ctk.CTkButton(control_frame, text="Hapus", fg_color="#469173", hover_color="#345d4b", text_color="white", width=100, height=30, command=lambda: delete_item(collection_minuman))
    remove_button.pack(side="left", padx=5, pady=5)

    drink_window.mainloop()

# Fungsi untuk membuka window penjual
def open_seller_window(previous_window):
    previous_window.destroy()
    seller_window = ctk.CTk()
    seller_window.title("Penjual")
    seller_window.geometry("360x640")

    main_frame = ctk.CTkFrame(seller_window, fg_color="white", bg_color="white")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    back_button = ctk.CTkButton(main_frame, text="<", width=40, height=40, fg_color="#469173", hover_color="#345d4b", text_color="white", command=lambda: login_seller_window())
    back_button.pack(pady=10, anchor="w")

    welcome_label = ctk.CTkLabel(main_frame, text=f"Penjual", font=("Arial", 16, "bold"), text_color="black", bg_color="white")
    welcome_label.pack(pady=10)

    logo_frame = ctk.CTkFrame(main_frame, fg_color="white", bg_color="white")
    logo_frame.pack(pady=10)

    # Memuat gambar menggunakan PIL
    image_path = "logo.png" 
    image = Image.open(image_path)
    image = image.resize((200, 200), Image.LANCZOS)
    logo_image = ImageTk.PhotoImage(image)

    logo_label = ctk.CTkLabel(logo_frame, image=logo_image, text="", width=100, height=100, fg_color="white", bg_color="white")
    logo_label.image = logo_image 
    logo_label.pack()

    info_label = ctk.CTkLabel(main_frame, text="Silahkan pilih item yang ingin anda edit", font=("Arial", 12), text_color="black", bg_color="white")
    info_label.pack(pady=10)

    button_frame = ctk.CTkFrame(main_frame, fg_color="white", bg_color="white")
    button_frame.pack(pady=10)

    food_button = ctk.CTkButton(button_frame, text="Makanan", width=120, height=60, fg_color="#469173", hover_color="#345d4b", text_color="white", corner_radius=8, command=lambda: open_food_window_seller(seller_window))
    food_button.grid(row=0, column=0, padx=10)

    drink_button = ctk.CTkButton(button_frame, text="Minuman", width=120, height=60, fg_color="#469173", hover_color="#345d4b", text_color="white", corner_radius=8, command=lambda: open_drink_window_seller(seller_window))
    drink_button.grid(row=0, column=1, padx=10)

    cart_button = ctk.CTkButton(main_frame, text="Pesanan Masuk", width=200, height=40, fg_color="#469173", hover_color="#345d4b", text_color="white", command=lambda: open_pesanan_window(seller_window))
    cart_button.pack(pady=20)

    seller_window.mainloop()

# Fungsi untuk membuka window login penjual
def login_seller_window():
    seller_window = ctk.CTk()
    seller_window.title("Login Penjual")
    seller_window.geometry("360x640")

    main_frame = ctk.CTkFrame(seller_window, fg_color="white", bg_color="white")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    back_button = ctk.CTkButton(main_frame, text="<", width=40, height=40, fg_color="#469173", hover_color="#345d4b", text_color="white", command=lambda: back_to_main(seller_window))
    back_button.pack(pady=10, anchor="w")

    title_label = ctk.CTkLabel(main_frame, text="Penjual", font=("Arial", 18, "bold"), text_color="black", bg_color="white")
    title_label.pack(pady=10)

    logo_frame = ctk.CTkFrame(main_frame, fg_color="white", bg_color="white")
    logo_frame.pack(pady=10)

    # Memuat gambar menggunakan PIL
    image_path = "logo.png" 
    image = Image.open(image_path)
    image = image.resize((200, 200), Image.LANCZOS)
    logo_image = ImageTk.PhotoImage(image)

    logo_label = ctk.CTkLabel(logo_frame, image=logo_image, text="", width=100, height=100, fg_color="white", bg_color="white")
    logo_label.image = logo_image 
    logo_label.pack()

    username_entry = ctk.CTkEntry(main_frame, width=200, placeholder_text="Username", fg_color="#d3d3d3", placeholder_text_color="grey", bg_color="white", text_color="black")
    username_entry.pack(pady=(20, 10))

    password_entry = ctk.CTkEntry(main_frame, show="*", width=200, placeholder_text="Password", fg_color="#d3d3d3", placeholder_text_color="grey", bg_color="white", text_color="black")
    password_entry.pack(pady=10)

    def login():
        username = username_entry.get()
        password = password_entry.get()
        if validate_seller(username, password):
            messagebox.showinfo("Login Berhasil", "Login penjual berhasil!")
            open_seller_window(seller_window)
        else:
            messagebox.showerror("Login Gagal", "Username atau password salah.")

    login_button = ctk.CTkButton(main_frame, text="Login", width=200, height=40, fg_color="#469173", hover_color="#345d4b", text_color="white", command=login)
    login_button.pack(pady=20)

    seller_window.mainloop()

# Fungsi untuk membuka window prompt nama
def name_prompt_window():
    name_window = ctk.CTk()
    name_window.title("Masukkan Nama")
    name_window.geometry("360x640")

    main_frame = ctk.CTkFrame(name_window, fg_color="white", bg_color="white")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    back_button = ctk.CTkButton(main_frame, text="<", width=40, height=40, fg_color="#469173", hover_color="#345d4b", text_color="white", command=lambda: back_to_main(name_window))
    back_button.pack(pady=10, anchor="w")

    name_label = ctk.CTkLabel(main_frame, text="Masukkan Nama Anda", text_color="black", bg_color="white")
    name_label.pack(pady=20)

    name_entry = ctk.CTkEntry(main_frame, width=200, placeholder_text="Nama", fg_color="#d3d3d3", placeholder_text_color="grey", bg_color="white", text_color="black")
    name_entry.pack(pady=10)

    continue_button = ctk.CTkButton(main_frame, text="Lanjutkan", width=200, height=35, fg_color="#469173", hover_color="#345d4b", text_color="white", command=lambda: open_buyer_window(name_entry.get(), name_window))
    continue_button.pack(pady=20)

    name_window.mainloop()

# Fungsi untuk membuka jendela riwayat pemesanan
def open_order_history_window():
    history_window = ctk.CTk()
    history_window.title("Riwayat Pemesanan")
    history_window.geometry("360x640")

    main_frame = ctk.CTkFrame(history_window, fg_color="white", bg_color="white")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    title_label = ctk.CTkLabel(main_frame, text="Riwayat Pemesanan", font=("Arial", 16, "bold"), text_color="black", bg_color="white")
    title_label.pack(pady=10)

    order_history = list(collection_history.find())
    
    if not order_history:
        empty_label = ctk.CTkLabel(main_frame, text="Belum ada riwayat pemesanan.", font=("Arial", 12), text_color="black", bg_color="white")
        empty_label.pack(pady=10)
    else:
        for order in order_history:
            user = None
            if 'user_id' in order:
                user = collection_user.find_one({"_id": order['user_id']})  # Menemukan pengguna berdasarkan user_id pada riwayat pesanan
            
            separator = ctk.CTkLabel(main_frame, text="Pesanan", font=("Arial", 14, "bold"), text_color="black", bg_color="white")
            separator.pack(anchor="w", pady=10, padx=10)

            buyer_name = user['name'] if user else 'Tidak Diketahui'
            buyer_name_label = ctk.CTkLabel(main_frame, text=f"Pembeli: {buyer_name}", font=("Arial", 12), text_color="black", bg_color="white")
            buyer_name_label.pack(anchor="w", pady=2, padx=10)

            order_label = ctk.CTkLabel(main_frame, text=f"{order['item']} - Rp{order['price']}", font=("Arial", 12), text_color="black", bg_color="white")
            order_label.pack(anchor="w", pady=2, padx=20)

    back_button = ctk.CTkButton(main_frame, text="Kembali", width=200, height=40, text_color="white", fg_color="#469173", hover_color="#345d4b", command=history_window.destroy)
    back_button.pack(pady=20)

    history_window.mainloop()

def open_pesanan_window(previous_window):
    previous_window.destroy()
    pesanan_window = ctk.CTk()
    pesanan_window.title("Pesanan Masuk")
    pesanan_window.geometry("360x640")

    main_frame = ctk.CTkFrame(pesanan_window, fg_color="white", bg_color="white")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    title_label = ctk.CTkLabel(main_frame, text="Pesanan Masuk", font=("Arial", 16, "bold"), text_color="black", bg_color="white")
    title_label.pack(pady=10)

    orders = collection_pesanan.find()

    for order in orders:
        order_frame = ctk.CTkFrame(main_frame, fg_color="white")
        order_frame.pack(fill="x", pady=5)

        order_label = ctk.CTkLabel(order_frame, text=f"{order['item']} - Rp{order['price']}", text_color="black")
        order_label.pack(side="left", padx=10)

        fulfill_button = ctk.CTkButton(order_frame, text="Proses", fg_color="#469173", hover_color="#345d4b", text_color="white", command=lambda order_id=order['_id']: fulfill_order(order_id))
        fulfill_button.pack(side="right", padx=10)

    back_button = ctk.CTkButton(main_frame, text="Kembali", width=200, height=40, fg_color="#469173", hover_color="#345d4b", text_color="white", command=lambda: open_seller_window(pesanan_window))
    back_button.pack(pady=10)

    pesanan_window.mainloop()

# Fungsi untuk membuka window pembeli
def open_buyer_window(name, previous_window):
    save_username(name)
    previous_window.destroy()
    buyer_window = ctk.CTk()
    buyer_window.title("Pembeli")
    buyer_window.geometry("360x640")

    main_frame = ctk.CTkFrame(buyer_window, fg_color="white", bg_color="white")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    back_button = ctk.CTkButton(main_frame, text="<", width=40, height=40, fg_color="#469173", hover_color="#345d4b", text_color="white", command=lambda: back_to_main(buyer_window))
    back_button.pack(pady=10, anchor="w")

    welcome_label = ctk.CTkLabel(main_frame, text=f"Hai {name}, mau makan apa?", font=("Arial", 16, "bold"), text_color="black", bg_color="white")
    welcome_label.pack(pady=10)

    logo_frame = ctk.CTkFrame(main_frame, fg_color="white", bg_color="white")
    logo_frame.pack(pady=10)

    # Memuat gambar menggunakan PIL
    image_path = "logo.png"  # Ganti dengan path ke gambar Anda
    image = Image.open(image_path)
    image = image.resize((200, 200), Image.LANCZOS)
    logo_image = ImageTk.PhotoImage(image)

    logo_label = ctk.CTkLabel(logo_frame, image=logo_image, text="", width=100, height=100, fg_color="white", bg_color="white")
    logo_label.image = logo_image  # Simpan referensi ke gambar untuk mencegah garbage collection
    logo_label.pack()

    info_label = ctk.CTkLabel(main_frame, text="Silahkan pilih item yang ingin anda pesan", font=("Arial", 12), text_color="black", bg_color="white")
    info_label.pack(pady=10)

    button_frame = ctk.CTkFrame(main_frame, fg_color="white", bg_color="white")
    button_frame.pack(pady=10)

    food_button = ctk.CTkButton(button_frame, text="Makanan", width=120, height=60, fg_color="#469173", hover_color="#345d4b", text_color="white", corner_radius=8, command=lambda: open_food_window(buyer_window, buyer_name=name))
    food_button.grid(row=0, column=0, padx=10)

    drink_button = ctk.CTkButton(button_frame, text="Minuman", width=120, height=60, fg_color="#469173", hover_color="#345d4b", text_color="white", corner_radius=8, command=lambda: open_drink_window(buyer_window, buyer_name=name))
    drink_button.grid(row=0, column=1, padx=10)

    cart_button = ctk.CTkButton(main_frame, text="Lihat Keranjang", width=200, height=40, fg_color="#469173", hover_color="#345d4b", text_color="white", command=lambda: open_cart_window(buyer_window, name))
    cart_button.pack(pady=20)

    # Tombol Riwayat Pemesanan
    history_button = ctk.CTkButton(main_frame, text="Riwayat Pemesanan", width=200, height=40, fg_color="#469173", hover_color="#345d4b", text_color="white", command=open_order_history_window)
    history_button.pack(pady=10)

    buyer_window.mainloop()

# Fungsi untuk membuka window daftar minuman
def open_drink_window(previous_window, buyer_name):
    previous_window.destroy()
    drink_window = ctk.CTk()
    drink_window.title("Minuman")
    drink_window.geometry("360x640")

    canvas = Canvas(drink_window, bg="white")
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = Scrollbar(drink_window, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    scrollable_frame = Frame(canvas, bg="white")
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    back_button = ctk.CTkButton(scrollable_frame, text="<", width=40, height=40, fg_color="#469173", hover_color="#345d4b", text_color="white", command=lambda: open_buyer_window(buyer_name, drink_window))
    back_button.pack(pady=10, anchor="w")

    logo_frame = ctk.CTkFrame(scrollable_frame, fg_color="white", bg_color="white")
    logo_frame.pack(pady=10)

    # Memuat gambar menggunakan PIL
    image_path = "logo.png"  # Ganti dengan path ke gambar Anda
    image = Image.open(image_path)
    image = image.resize((200, 200), Image.LANCZOS)
    logo_image = ImageTk.PhotoImage(image)

    logo_label = ctk.CTkLabel(logo_frame, image=logo_image, text="", width=100, height=100, fg_color="white", bg_color="white")
    logo_label.image = logo_image  # Simpan referensi ke gambar untuk mencegah garbage collection
    logo_label.pack()

    # Fetch data from MongoDB
    drinks = collection_minuman.find()

    # Group drinks by category
    drink_categories = {}
    for drink in drinks:
        category = drink.get('Kategori', 'Lainnya')  # Default to 'Lainnya' if no category found
        if category not in drink_categories:
            drink_categories[category] = []
        drink_categories[category].append(drink)
    
    # Display drinks grouped by category
    for category, items in drink_categories.items():
        category_label = ctk.CTkLabel(scrollable_frame, text=category, font=("Arial", 14, "bold"), text_color="black")
        category_label.pack(anchor="w", padx=10, pady=5)

        for drink in items:
            if 'Nama' in drink and 'Harga' in drink:
                item_frame = ctk.CTkFrame(scrollable_frame, fg_color="white")
                item_frame.pack(fill="x", pady=5)

                drink_label = ctk.CTkLabel(item_frame, text=f"{drink['Nama']} - Rp{drink['Harga']}", text_color="black")
                drink_label.pack(side="left", padx=10)

                add_button = ctk.CTkButton(item_frame, text="+", width=40, height=40, fg_color="#469173", hover_color="#345d4b", text_color="white", corner_radius=100, command=lambda drink_name=drink['Nama'], price=drink['Harga']: add_to_cart(drink_name, price, buyer_name))
                add_button.pack(side="right", padx=10)
            else:
                print("Invalid drink structure:", drink)

    drink_window.mainloop()

# Fungsi untuk membuka window daftar makanan
def open_food_window(previous_window, buyer_name):
    previous_window.destroy()
    food_window = ctk.CTk()
    food_window.title("Makanan")
    food_window.geometry("360x640")

    canvas = Canvas(food_window, bg="white")
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = Scrollbar(food_window, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    scrollable_frame = Frame(canvas, bg="white")
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    back_button = ctk.CTkButton(scrollable_frame, text="<", width=40, height=40, fg_color="#469173", hover_color="#345d4b", text_color="white", command=lambda: open_buyer_window(buyer_name, food_window))
    back_button.pack(pady=10, anchor="w")

    logo_frame = ctk.CTkFrame(scrollable_frame, fg_color="white", bg_color="white")
    logo_frame.pack(pady=10)

    # Memuat gambar menggunakan PIL
    image_path = "logo.png"  # Ganti dengan path ke gambar Anda
    image = Image.open(image_path)
    image = image.resize((200, 200), Image.LANCZOS)
    logo_image = ImageTk.PhotoImage(image)

    logo_label = ctk.CTkLabel(logo_frame, image=logo_image, text="", width=100, height=100, fg_color="white", bg_color="white")
    logo_label.image = logo_image  # Simpan referensi ke gambar untuk mencegah garbage collection
    logo_label.pack()

    foods = collection_makanan.find()

    food_categories = {}
    for food in foods:
        category = food.get('Kategori', 'Lainnya')
        if category not in food_categories:
            food_categories[category] = []
        food_categories[category].append(food)
    
    for category, items in food_categories.items():
        category_label = ctk.CTkLabel(scrollable_frame, text=category, font=("Arial", 14, "bold"), text_color="black")
        category_label.pack(anchor="w", padx=10, pady=5)

        for food in items:
            if 'Nama' in food and 'Harga' in food:
                item_frame = ctk.CTkFrame(scrollable_frame, fg_color="white")
                item_frame.pack(fill="x", pady=5)

                food_label = ctk.CTkLabel(item_frame, text=f"{food['Nama']} - Rp{food['Harga']}", text_color="black")
                food_label.pack(side="left", padx=10)

                add_button = ctk.CTkButton(item_frame, text="+", width=40, height=40, fg_color="#469173", hover_color="#345d4b", text_color="white", corner_radius=100, command=lambda food=food['Nama'], price=food['Harga']: add_to_cart(food, price, buyer_name))
                add_button.pack(side="right", padx=10)
            else:
                print("Invalid food structure:", food)

    food_window.mainloop()

def open_main_window():
    # Membuat window utama
    root = ctk.CTk()
    root.title("Halaman Login")
    root.geometry("360x640")

    # Membuat frame utama
    main_frame = ctk.CTkFrame(root, fg_color="white", bg_color="white")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    title_label = ctk.CTkLabel(main_frame, text="Warung CingCong Cuan", font=("Arial", 18, "bold"), text_color="black", bg_color="white")
    title_label.pack(pady=10)

    # Menambahkan logo (gambar kotak)
    logo_frame = ctk.CTkFrame(main_frame, fg_color="white", bg_color="white")
    logo_frame.pack(pady=50)

    # Memuat gambar menggunakan PIL
    image_path = "logo.png"  # Ganti dengan path ke gambar Anda
    image = Image.open(image_path)
    image = image.resize((200, 200), Image.LANCZOS)
    logo_image = ImageTk.PhotoImage(image)

    logo_label = ctk.CTkLabel(logo_frame, image=logo_image, text="", width=100, height=100, fg_color="white", bg_color="white")
    logo_label.image = logo_image  # Simpan referensi ke gambar untuk mencegah garbage collection
    logo_label.pack()

    login_label = ctk.CTkLabel(main_frame, text="Login sebagai:", font=("Arial", 14), text_color="black", bg_color="white")
    login_label.pack(pady=10)

    # Menambahkan tombol login sebagai penjual
    seller_button = ctk.CTkButton(main_frame, text="Penjual", command=lambda: login_seller(root), width=200, height=40, fg_color="#469173", text_color="white", hover_color="#345d4b")
    seller_button.pack(pady=10)

    # Menambahkan tombol login sebagai pembeli
    buyer_button = ctk.CTkButton(main_frame, text="Pembeli", command=lambda: login_buyer(root), width=200, height=40, fg_color="#469173", text_color="white", hover_color="#345d4b")
    buyer_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    open_main_window()
