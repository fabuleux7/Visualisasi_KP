# Streamlit Harmonisasi Regulasi PBI–PADG

1. Buka `app.py`.
2. Isi `DRIVE_FILES` dengan link share Google Drive untuk PDF, CSV, dan PKL hasil pipeline.
3. Pastikan file Drive dapat diakses oleh environment Streamlit.
4. Install dependency:

```bash
pip install -r requirements.txt
```

5. Jalankan:

```bash
streamlit run app.py
```

Aplikasi hanya membaca hasil yang sudah ada; tidak menjalankan ulang embedding, similarity, filtering, atau LLM.

Untuk deployment publik dengan data privat, gunakan authentication/Google Drive API, bukan membuat data sensitif public.
