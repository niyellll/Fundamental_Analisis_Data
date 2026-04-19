# Analisis Kualitas Udara – Stasiun Changping, Beijing (2013–2017)

Proyek Akhir Analisis Data oleh **Nathaniel Krisnahadi P**

## Struktur Direktori
```
submission/
├── dashboard/
│   ├── main_data.csv
│   └── dashboard.py
├── data/
│   └── PRSA_Data_Changping_20130301-20170228.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

##  Pertanyaan Bisnis
1. Bagaimana tren dan pola musiman konsentrasi PM2.5?  
2. Bagaimana pengaruh cuaca (angin, suhu, tekanan udara) terhadap PM2.5?

##  Hasil Temuan
- Musim dingin paling berbahaya, rata-rata PM2.5 jauh di atas ambang aman WHO.  
- Musim panas paling bersih, berkat hujan dan angin.  
- Angin lemah membuat polusi menumpuk, angin kencang menurunkan PM2.5.  
- Puncak polusi harian sering terjadi malam hari (21:00–23:00).  
- Lebih dari 40% data masuk kategori *Unhealthy* atau lebih buruk.  

## Cara Menjalankan Dashboard
```bash
pip install -r requirements.txt
streamlit run dashboard/dashboard.py
```
Dashboard akan terbuka di `http://localhost:8501`
