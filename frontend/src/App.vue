
<script setup>
import { ref, computed, onMounted } from 'vue'

const API_URL = 'http://127.0.0.1:8000'

const products = ref([])
const loading = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const searchQuery = ref('')
const sortOrder = ref('asc')
const editingId = ref(null)

const form = ref({
  nama_produk: '',
  kategori: '',
  stok: 0,
  harga: 1,
})

async function loadProducts() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await fetch(`${API_URL}/products`)

    if (!response.ok) {
      throw new Error('Gagal mengambil data produk dari server.')
    }

    products.value = await response.json()
  } catch (error) {
    errorMessage.value =
      'Data produk belum dapat dimuat. Pastikan backend FastAPI sedang berjalan.'
    console.error('Kesalahan mengambil produk:', error)
  } finally {
    loading.value = false
  }
}

// Mencari produk berdasarkan nama atau kategori.
const filteredProducts = computed(() => {
  const keyword = searchQuery.value.trim().toLowerCase()

  return products.value.filter((product) => {
    return (
      product.nama_produk.toLowerCase().includes(keyword) ||
      product.kategori.toLowerCase().includes(keyword)
    )
  })
})

// Mengurutkan hasil pencarian berdasarkan nama produk.
const sortedProducts = computed(() => {
  return [...filteredProducts.value].sort((a, b) => {
    const comparison = a.nama_produk.localeCompare(b.nama_produk, 'id')
    return sortOrder.value === 'asc' ? comparison : -comparison
  })
})

// Empat kartu ringkasan dashboard.
const totalProducts = computed(() => products.value.length)

const lowStockProducts = computed(() =>
  products.value.filter((product) => product.stok <= 5).length
)

const totalCategories = computed(() =>
  new Set(products.value.map((product) => product.kategori)).size
)

const totalStockUnits = computed(() =>
  products.value.reduce((total, product) => total + product.stok, 0)
)

// Menghitung jumlah stok untuk setiap kategori.
const categoryStocks = computed(() => {
  const totals = products.value.reduce((result, product) => {
    result[product.kategori] =
      (result[product.kategori] || 0) + product.stok
    return result
  }, {})

  return Object.entries(totals)
    .map(([kategori, stok]) => ({ kategori, stok }))
    .sort((a, b) => b.stok - a.stok)
})

const maxCategoryStock = computed(() =>
  Math.max(...categoryStocks.value.map((item) => item.stok), 1)
)

function stockStatus(stok) {
  if (stok === 0) return 'habis'
  if (stok <= 5) return 'menipis'
  return 'tersedia'
}

function stockLabel(stok) {
  if (stok === 0) return 'Habis'
  if (stok <= 5) return 'Menipis'
  return 'Tersedia'
}

function formatRupiah(value) {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    maximumFractionDigits: 0,
  }).format(value)
}

function resetForm() {
  editingId.value = null
  form.value = {
    nama_produk: '',
    kategori: '',
    stok: 0,
    harga: 1,
  }
}

function startEdit(product) {
  editingId.value = product.id
  form.value = {
    nama_produk: product.nama_produk,
    kategori: product.kategori,
    stok: product.stok,
    harga: product.harga,
  }
  successMessage.value = ''
  errorMessage.value = ''

  // Memindahkan tampilan ke formulir agar mudah diedit.
  document.getElementById('product-form')?.scrollIntoView({
    behavior: 'smooth',
    block: 'start',
  })
}

async function submitForm() {
  successMessage.value = ''
  errorMessage.value = ''

  if (
    !form.value.nama_produk.trim() ||
    !form.value.kategori.trim() ||
    Number(form.value.stok) < 0 ||
    Number(form.value.harga) <= 0
  ) {
    errorMessage.value =
      'Lengkapi nama dan kategori. Stok tidak boleh negatif dan harga harus lebih dari 0.'
    return
  }

  saving.value = true

  const payload = {
    nama_produk: form.value.nama_produk.trim(),
    kategori: form.value.kategori.trim(),
    stok: Number(form.value.stok),
    harga: Number(form.value.harga),
  }

  const isEditing = editingId.value !== null
  const url = isEditing
    ? `${API_URL}/products/${editingId.value}`
    : `${API_URL}/products`

  try {
    const response = await fetch(url, {
      method: isEditing ? 'PUT' : 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const result = await response.json()
      throw new Error(
        result.detail
          ? JSON.stringify(result.detail)
          : 'Gagal menyimpan produk.'
      )
    }

    await loadProducts()
    resetForm()
    successMessage.value = isEditing
      ? 'Data produk berhasil diperbarui.'
      : 'Produk baru berhasil ditambahkan.'
  } catch (error) {
    errorMessage.value = `Gagal menyimpan data. ${error.message}`
    console.error('Kesalahan menyimpan produk:', error)
  } finally {
    saving.value = false
  }
}

async function deleteProduct(product) {
  const confirmed = window.confirm(
    `Yakin ingin menghapus ${product.nama_produk}?`
  )

  if (!confirmed) return

  successMessage.value = ''
  errorMessage.value = ''

  try {
    const response = await fetch(`${API_URL}/products/${product.id}`, {
      method: 'DELETE',
    })

    if (!response.ok) {
      const result = await response.json()
      throw new Error(result.detail || 'Gagal menghapus produk.')
    }

    await loadProducts()
    successMessage.value = 'Produk berhasil dihapus.'

    if (editingId.value === product.id) {
      resetForm()
    }
  } catch (error) {
    errorMessage.value = `Gagal menghapus produk. ${error.message}`
    console.error('Kesalahan menghapus produk:', error)
  }
}

onMounted(loadProducts)
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <a class="brand" href="#" aria-label="Dashboard Toko Elektronik">
        <span class="brand-icon">E</span>
        <span>
          <strong>Electro<span>Hub</span></strong>
          <small>INVENTORY DASHBOARD</small>
        </span>
      </a>

      <div class="topbar-right">
        <span class="connection-dot"></span>
        <span>Dashboard Inventaris</span>
      </div>
    </header>

    <main class="dashboard">
      <section class="page-heading">
        <div>
          <p class="eyebrow">RINGKASAN INVENTARIS</p>
          <h1>Dashboard Toko Elektronik</h1>
          <p class="subtitle">
            Pantau produk, ketersediaan stok, dan data inventaris toko.
          </p>
        </div>

        <button class="button button-secondary" @click="loadProducts">
          ↻ Muat Ulang Data
        </button>
      </section>

      <div v-if="errorMessage" class="notice notice-error" role="alert">
        <strong>Terjadi kendala</strong>
        <span>{{ errorMessage }}</span>
      </div>

      <div
        v-if="successMessage"
        class="notice notice-success"
        role="status"
      >
        <strong>Berhasil</strong>
        <span>{{ successMessage }}</span>
      </div>

      <section class="summary-grid" aria-label="Ringkasan produk">
        <article class="summary-card">
          <div class="summary-top">
            <span>Total Produk</span>
            <span class="summary-icon icon-blue">▤</span>
          </div>
          <strong class="summary-value">{{ totalProducts }}</strong>
          <span class="summary-foot">Jenis produk terdaftar</span>
        </article>

        <article class="summary-card">
          <div class="summary-top">
            <span>Stok Menipis + Habis</span>
            <span class="summary-icon icon-orange">!</span>
          </div>
          <strong class="summary-value">{{ lowStockProducts }}</strong>
          <span class="summary-foot">Produk dengan stok 5 atau kurang</span>
        </article>

        <article class="summary-card">
          <div class="summary-top">
            <span>Jumlah Kategori</span>
            <span class="summary-icon icon-purple">▦</span>
          </div>
          <strong class="summary-value">{{ totalCategories }}</strong>
          <span class="summary-foot">Kategori produk berbeda</span>
        </article>

        <article class="summary-card">
          <div class="summary-top">
            <span>Total Unit Stok</span>
            <span class="summary-icon icon-green">▥</span>
          </div>
          <strong class="summary-value">{{ totalStockUnits }}</strong>
          <span class="summary-foot">Unit dari seluruh produk</span>
        </article>
      </section>

      <section class="content-grid">
        <article class="panel inventory-panel">
          <div class="panel-heading">
            <div>
              <h2>Daftar Produk</h2>
              <p>Data inventaris toko elektronik</p>
            </div>
            <span class="count-pill">{{ sortedProducts.length }} produk</span>
          </div>

          <div class="table-toolbar">
            <label class="search-box">
              <span aria-hidden="true">⌕</span>
              <input
                v-model="searchQuery"
                type="search"
                placeholder="Cari nama atau kategori..."
                aria-label="Cari nama atau kategori produk"
              />
            </label>

            <button
              class="button button-secondary sort-button"
              @click="sortOrder = sortOrder === 'asc' ? 'desc' : 'asc'"
              :aria-label="
                sortOrder === 'asc'
                  ? 'Ubah urutan menjadi Z ke A'
                  : 'Ubah urutan menjadi A ke Z'
              "
            >
              {{ sortOrder === 'asc' ? '↑ A–Z' : '↓ Z–A' }}
            </button>
          </div>

          <div v-if="loading" class="state-message">
            <span class="spinner"></span>
            <p>Sedang memuat data produk...</p>
          </div>

          <div v-else-if="sortedProducts.length === 0" class="state-message">
            <span class="empty-icon">⌕</span>
            <h3>Produk tidak ditemukan</h3>
            <p>
              {{
                searchQuery
                  ? 'Coba kata kunci lain.'
                  : 'Belum ada data produk untuk ditampilkan.'
              }}
            </p>
          </div>

          <div v-else class="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>PRODUK</th>
                  <th>KATEGORI</th>
                  <th>STOK</th>
                  <th>HARGA</th>
                  <th>STATUS</th>
                  <th>AKSI</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="product in sortedProducts" :key="product.id">
                  <td>
                    <div class="product-cell">
                      <span class="product-avatar">
                        {{ product.nama_produk.charAt(0).toUpperCase() }}
                      </span>
                      <div>
                        <strong>{{ product.nama_produk }}</strong>
                        <small>ID #{{ product.id }}</small>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span class="category-label">{{ product.kategori }}</span>
                  </td>
                  <td>
                    <strong>{{ product.stok }}</strong>
                    <span class="unit-label"> unit</span>
                  </td>
                  <td class="price-cell">{{ formatRupiah(product.harga) }}</td>
                  <td>
                    <span
                      class="status-badge"
                      :class="`status-${stockStatus(product.stok)}`"
                    >
                      {{ stockLabel(product.stok) }}
                    </span>
                  </td>
                  <td>
                    <div class="action-buttons">
                      <button
                        class="action-button edit-action"
                        @click="startEdit(product)"
                        :aria-label="`Edit ${product.nama_produk}`"
                        title="Edit produk"
                      >
                        ✎
                      </button>
                      <button
                        class="action-button delete-action"
                        @click="deleteProduct(product)"
                        :aria-label="`Hapus ${product.nama_produk}`"
                        title="Hapus produk"
                      >
                        ×
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="table-footer">
            <span>Menampilkan {{ sortedProducts.length }} dari {{ totalProducts }} produk</span>
            <span>Data tersimpan melalui FastAPI</span>
          </div>
        </article>

        <aside class="side-column">
          <article class="panel chart-panel">
            <div class="panel-heading">
              <div>
                <h2>Stok per Kategori</h2>
                <p>Jumlah unit tersedia</p>
              </div>
            </div>

            <div v-if="categoryStocks.length === 0" class="small-empty">
              Belum ada data stok.
            </div>

            <div v-else class="chart-list">
              <div
                v-for="item in categoryStocks"
                :key="item.kategori"
                class="chart-item"
              >
                <div class="chart-labels">
                  <span>{{ item.kategori }}</span>
                  <strong>{{ item.stok }}</strong>
                </div>
                <div
                  class="bar-track"
                  role="progressbar"
                  :aria-label="`Stok kategori ${item.kategori}`"
                  :aria-valuenow="item.stok"
                  :aria-valuemin="0"
                  :aria-valuemax="maxCategoryStock"
                >
                  <div
                    class="bar-fill"
                    :style="{
                      width: `${(item.stok / maxCategoryStock) * 100}%`,
                    }"
                  ></div>
                </div>
              </div>
            </div>

            <p class="chart-note">
              Grafik menyesuaikan data produk yang tersimpan.
            </p>
          </article>

          <article id="product-form" class="panel form-panel">
            <div class="panel-heading">
              <div>
                <h2>{{ editingId !== null ? 'Edit Produk' : 'Tambah Produk' }}</h2>
                <p>
                  {{
                    editingId !== null
                      ? 'Perbarui informasi produk'
                      : 'Masukkan produk ke inventaris'
                  }}
                </p>
              </div>
              <span class="form-plus">{{ editingId !== null ? '✎' : '+' }}</span>
            </div>

            <form @submit.prevent="submitForm">
              <label class="form-field">
                <span>Nama Produk</span>
                <input
                  v-model="form.nama_produk"
                  type="text"
                  maxlength="100"
                  placeholder="Contoh: Samsung Galaxy"
                  required
                />
              </label>

              <label class="form-field">
                <span>Kategori</span>
                <input
                  v-model="form.kategori"
                  type="text"
                  maxlength="50"
                  placeholder="Contoh: Smartphone"
                  required
                />
              </label>

              <div class="form-row">
                <label class="form-field">
                  <span>Jumlah Stok</span>
                  <input
                    v-model.number="form.stok"
                    type="number"
                    min="0"
                    step="1"
                    required
                  />
                </label>

                <label class="form-field">
                  <span>Harga (Rp)</span>
                  <input
                    v-model.number="form.harga"
                    type="number"
                    min="1"
                    step="1"
                    required
                  />
                </label>
              </div>

              <button class="button button-primary submit-button" type="submit" :disabled="saving">
                {{ saving ? 'Menyimpan...' : editingId !== null ? 'Simpan Perubahan' : '+ Tambah Produk' }}
              </button>

              <button
                v-if="editingId !== null"
                class="button cancel-button"
                type="button"
                @click="resetForm"
              >
                Batal Edit
              </button>
            </form>

            <p class="form-note">
              Perubahan data disimpan ke backend dan file JSON.
            </p>
          </article>
        </aside>
      </section>

      <footer class="page-footer">
        <span>ElectroHub · Dashboard Inventaris</span>
        <span>Vue 3 + FastAPI</span>
      </footer>
    </main>
  </div>
</template>
