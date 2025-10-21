import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import io
import base64

# =========================
# DATABASE SETUP
# =========================
conn = sqlite3.connect('crochet_shop.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price REAL,
    description TEXT,
    category TEXT,
    image BLOB
)''')
conn.commit()

# =========================
# HELPER FUNCTIONS
# =========================
def insert_product(name, price, description, category, image_bytes):
    c.execute("INSERT INTO products (name, price, description, category, image) VALUES (?, ?, ?, ?, ?)",
              (name, price, description, category, image_bytes))
    conn.commit()

def get_products():
    c.execute("SELECT * FROM products")
    return c.fetchall()

def delete_product(product_id):
    c.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()

def update_product(product_id, name, price, description, category):
    c.execute("UPDATE products SET name=?, price=?, description=?, category=? WHERE id=?",
              (name, price, description, category, product_id))
    conn.commit()

def image_to_base64(image_bytes):
    return base64.b64encode(image_bytes).decode()

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="KnitCraft Store 🧶", layout="wide")

# =========================
# NAVIGATION MENU
# =========================
st.sidebar.title("🧵 KnitCraft Admin")
menu = st.sidebar.radio("Navigate", ["🏠 Home", "➕ Add Product", "📋 View Products", "✏️ Update / Delete"])

st.markdown(
    """
    <style>
    body {
        background-color: #f6f8fa;
    }
    .stApp {
        background-color: #fefefe;
    }
    h1, h2, h3 {
        color: #b56576;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# HOME PAGE
# =========================
if menu == "🏠 Home":
    st.title("🧶 Welcome to KnitCraft Store")
    st.subheader("Beautiful Handmade Crochet & Knitting Items")
    st.markdown("Explore unique handmade products — scarves, sweaters, toys, and more!")

    products = get_products()
    if products:
        cols = st.columns(3)
        for i, product in enumerate(products):
            with cols[i % 3]:
                st.markdown(f"### {product[1]}")
                st.write(f"💰 ₹{product[2]}")
                st.write(f"🧵 {product[4]}")
                if product[5]:
                    img = Image.open(io.BytesIO(product[5]))
                    st.image(img, width=200)
                st.write(product[3])
                st.button("🛒 Add to Cart", key=f"cart_{product[0]}")
    else:
        st.info("No products available yet! Please add items from the admin panel.")

# =========================
# ADD PRODUCT
# =========================
elif menu == "➕ Add Product":
    st.title("➕ Add a New Product")

    with st.form("add_form"):
        name = st.text_input("Product Name")
        price = st.number_input("Price (₹)", min_value=0.0, step=10.0)
        description = st.text_area("Description")
        category = st.selectbox("Category", ["Scarf", "Sweater", "Toy", "Accessory", "Other"])
        image_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

        submitted = st.form_submit_button("Add Product")

        if submitted:
            if name and price and description and image_file:
                image_bytes = image_file.read()
                insert_product(name, price, description, category, image_bytes)
                st.success(f"✅ {name} added successfully!")
            else:
                st.error("Please fill all fields and upload an image.")

# =========================
# VIEW PRODUCTS
# =========================
elif menu == "📋 View Products":
    st.title("📦 Product Catalog")

    data = get_products()
    if data:
        df = pd.DataFrame(data, columns=["ID", "Name", "Price", "Description", "Category", "Image"])
        st.dataframe(df[["ID", "Name", "Price", "Category"]])
    else:
        st.info("No products found.")

# =========================
# UPDATE / DELETE PRODUCTS
# =========================
elif menu == "✏️ Update / Delete":
    st.title("✏️ Update or Delete Products")

    data = get_products()
    if data:
        product_names = [f"{row[1]} (₹{row[2]})" for row in data]
        selected = st.selectbox("Select Product", product_names)
        selected_row = data[product_names.index(selected)]
        product_id = selected_row[0]

        st.subheader("Edit Product Details")
        name = st.text_input("Product Name", selected_row[1])
        price = st.number_input("Price (₹)", value=selected_row[2], step=10.0)
        description = st.text_area("Description", selected_row[3])
        category = st.text_input("Category", selected_row[4])

        if st.button("Update"):
            update_product(product_id, name, price, description, category)
            st.success("✅ Product updated successfully!")

        if st.button("Delete"):
            delete_product(product_id)
            st.warning("🗑️ Product deleted.")
    else:
        st.info("No products to edit.")
