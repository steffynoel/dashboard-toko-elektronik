
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# Lokasi file penyimpanan data produk
DATA_FILE = Path(__file__).parent / "products.json"


# Membuat aplikasi FastAPI
app = FastAPI(
    title="API Dashboard Toko Elektronik",
    description=(
        "API untuk melihat, menambah, mengubah, "
        "dan menghapus data produk elektronik."
    ),
    version="1.0.0",
)


# Mengizinkan frontend Vue mengakses backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Skema data untuk menerima produk baru
class ProductCreate(BaseModel):
    nama_produk: str = Field(
        min_length=1,
        max_length=100,
        description="Nama produk elektronik",
    )
    kategori: str = Field(
        min_length=1,
        max_length=50,
        description="Kategori produk",
    )
    stok: int = Field(
        ge=0,
        description="Jumlah stok, minimal 0 unit",
    )
    harga: int = Field(
        gt=0,
        description="Harga produk dalam rupiah, harus lebih dari 0",
    )


# Skema data untuk memperbarui produk
class ProductUpdate(ProductCreate):
    pass


# Skema respons produk
class Product(ProductCreate):
    id: int = Field(
        gt=0,
        description="ID unik produk",
    )


# Membaca data dari file JSON
def load_products() -> list[dict]:
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("Data produk harus berbentuk list.")

        return data

    except FileNotFoundError:
        raise RuntimeError(
            f"File data tidak ditemukan: {DATA_FILE}"
        )
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Format JSON tidak valid: {exc}"
        )


# Menyimpan perubahan ke file JSON
def save_products(products: list[dict]) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            products,
            file,
            ensure_ascii=False,
            indent=2,
        )


# Data awal dibaca dari products.json
products = load_products()


# Memastikan ID data awal valid dan tidak duplikat
initial_ids = [item.get("id") for item in products]

if (
    any(type(product_id) is not int or product_id <= 0
        for product_id in initial_ids)
    or len(initial_ids) != len(set(initial_ids))
):
    raise RuntimeError(
        "Setiap produk harus memiliki ID positif yang unik."
    )


@app.get("/", tags=["Umum"])
def halaman_utama():
    """Memeriksa apakah API berjalan."""
    return {
        "pesan": "Backend Dashboard Toko Elektronik berhasil berjalan!"
    }


@app.get(
    "/products",
    response_model=list[Product],
    tags=["Produk"],
    summary="Mengambil semua produk",
)
def get_products():
    """Mengembalikan seluruh produk elektronik."""
    return products


@app.post(
    "/products",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    tags=["Produk"],
    summary="Menambahkan produk",
)
def create_product(product: ProductCreate):
    """Menambahkan produk baru dan menyimpannya ke JSON."""
    next_id = max(
        (item["id"] for item in products),
        default=0,
    ) + 1

    new_product = {
        "id": next_id,
        **product.model_dump(),
    }

    products.append(new_product)

    try:
        save_products(products)
    except OSError as exc:
        products.pop()
        raise HTTPException(
            status_code=500,
            detail="Gagal menyimpan produk ke file JSON.",
        ) from exc

    return new_product


@app.put(
    "/products/{product_id}",
    response_model=Product,
    tags=["Produk"],
    summary="Memperbarui produk",
)
def update_product(
    product_id: int,
    product: ProductUpdate,
):
    """Mengganti data produk berdasarkan ID."""
    for index, item in enumerate(products):
        if item["id"] == product_id:
            updated_product = {
                "id": product_id,
                **product.model_dump(),
            }

            old_product = products[index]
            products[index] = updated_product

            try:
                save_products(products)
            except OSError as exc:
                products[index] = old_product
                raise HTTPException(
                    status_code=500,
                    detail="Gagal menyimpan perubahan produk.",
                ) from exc

            return updated_product

    raise HTTPException(
        status_code=404,
        detail="Produk tidak ditemukan.",
    )


@app.delete(
    "/products/{product_id}",
    tags=["Produk"],
    summary="Menghapus produk",
)
def delete_product(product_id: int):
    """Menghapus produk berdasarkan ID dan menyimpan perubahan."""
    for index, item in enumerate(products):
        if item["id"] == product_id:
            deleted_product = products.pop(index)

            try:
                save_products(products)
            except OSError as exc:
                products.insert(index, deleted_product)
                raise HTTPException(
                    status_code=500,
                    detail="Gagal menyimpan penghapusan produk.",
                ) from exc

            return {
                "pesan": "Produk berhasil dihapus.",
                "produk": deleted_product,
            }

    raise HTTPException(
        status_code=404,
        detail="Produk tidak ditemukan.",
    )
