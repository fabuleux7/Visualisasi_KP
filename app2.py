import pickle
from pathlib import Path
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import gdown

st.set_page_config(page_title='Harmonisasi Regulasi PBI–PADG', page_icon='📚', layout='wide')

# ============================================================
# ISI LINK SHARE GOOGLE DRIVE DI SINI
# ============================================================
DRIVE_FILES = {
    'pbi_pdf': 'https://drive.google.com/file/d/19EGNR6rI9tLoyEHN2md1ONbAZMKxQ246/view?usp=drive_link',
    'padg_pdf': 'https://drive.google.com/file/d/1xPY1NxVDCkBD8K6ElImVi8MDFaE6YiBm/view?usp=drive_link',
    'segmented': 'https://drive.google.com/file/d/1sQzuJzFCe7gzajVhCa5GJs7_hNdAZuBX/view?usp=drive_link',
    'hierarchy': 'https://drive.google.com/file/d/1PVPml2rkgLdjD3wT01FCLhHlfjGKiNQl/view?usp=drive_link',
    'normalized': 'https://drive.google.com/file/d/1CzwNq4PCv1BubxkgXJToq5UsP7Q_6JHi/view?usp=drive_link',
    'glossary': 'https://drive.google.com/file/d/1AfAN1I2IKwjtnGTqlqxe0DLCwV0p8LNF/view?usp=drive_link',
    'knowledge_base': 'https://drive.google.com/file/d/1ObIuc0wsrYxicuwtFLYc81r6hRecxMrk/view?usp=drive_link',
    'embeddings': 'https://drive.google.com/file/d/13GoSMTYmcKMaXVQtbGN9d6HY8z4qnOJM/view?usp=drive_link',
    'similarity': 'https://drive.google.com/file/d/1LTg992JkB67yfZCkxhgHIZjVsOwlj_UT/view?usp=drive_link',
    'topk_candidates': 'https://drive.google.com/file/d/1y3tRMKcJn8Cxrbyjj4kBV5sAJydrGcyY/view?usp=drive_link',
    'filtered_candidates': 'https://drive.google.com/file/d/1QBggQ5lvj1qC0f28m_1BWKpolAkkf0Zk/view?usp=drive_link',
    'llm_checkpoint': 'https://drive.google.com/file/d/1PEaW6fUh2H0BF-MKjYsOE18-Ab7wdEq3/view?usp=drive_link',
    'final_candidate_with_llm': 'https://drive.google.com/file/d/1EDRDrzFiYpuXRZEzGnn95GOTt5WpPByd/view?usp=drive_link',
    'final_mapping': 'https://drive.google.com/file/d/1-DTaEioomXoB-5t3Scl8lz_KeLoCOysh/view?usp=drive_link',
    'final_validation': 'https://drive.google.com/file/d/1HBYd7XZTiBhYQ8KCyyawu2In631FcJqW/view?usp=drive_link',
    'analysis_summary': 'https://drive.google.com/file/d/1NlpcxAe4Tq8HXirgTzXd3TTI36zLbrk8/view?usp=drive_link',
    'manual_evaluation': 'https://drive.google.com/file/d/1JlXVqkjpJuGmUaCQ20S5f58kUAK3pD67/view?usp=drive_link',
}

CACHE = Path('.streamlit_cache')
CACHE.mkdir(exist_ok=True)

def drive_id(x):
    if not x:
        return None
    if 'drive.google.com' not in x:
        return x.strip()
    if '/file/d/' in x:
        return x.split('/file/d/')[1].split('/')[0]
    if 'id=' in x:
        return x.split('id=')[1].split('&')[0]
    return None


def get_file(url, suffix, force_refresh=False):
    """Download Google Drive file. force_refresh=True forces a new download."""
    fid = drive_id(url)
    if not fid:
        return None

    p = CACHE / f'{fid}{suffix}'

    if force_refresh and p.exists():
        try:
            p.unlink()
        except Exception:
            pass

    if not p.exists() or p.stat().st_size == 0:
        result = gdown.download(
            id=fid,
            output=str(p),
            quiet=True
        )
        if result is None or not p.exists() or p.stat().st_size == 0:
            return None

    return str(p)


def clear_all_cache():
    """Clear local downloaded files and Streamlit data cache."""
    deleted = 0

    if CACHE.exists():
        for p in CACHE.iterdir():
            if p.is_file():
                try:
                    p.unlink()
                    deleted += 1
                except Exception:
                    pass

    st.cache_data.clear()
    return deleted


def csv(key, force_refresh=False):
    u = DRIVE_FILES.get(key, '')
    if not u:
        return None

    path = get_file(u, '.csv', force_refresh=force_refresh)

    if not path:
        raise FileNotFoundError(
            f'File Google Drive untuk {key} tidak dapat diunduh. '
            'Pastikan file dibagikan sebagai Anyone with the link / Viewer.'
        )

    return pd.read_csv(path)


def pkl(key, force_refresh=False):
    u = DRIVE_FILES.get(key, '')
    if not u:
        return None

    path = get_file(u, '.pkl', force_refresh=force_refresh)

    if not path:
        raise FileNotFoundError(
            f'File Google Drive untuk {key} tidak dapat diunduh. '
            'Pastikan file dibagikan sebagai Anyone with the link / Viewer.'
        )

    with open(path, 'rb') as f:
        return pickle.load(f)


def pdf(key, force_refresh=False):
    u = DRIVE_FILES.get(key, '')
    if not u:
        return None

    path = get_file(u, '.pdf', force_refresh=force_refresh)

    if not path:
        raise FileNotFoundError(
            f'PDF Google Drive untuk {key} tidak dapat diunduh. '
            'Pastikan file dibagikan sebagai Anyone with the link / Viewer.'
        )

    return Path(path).read_bytes()


def load(key):
    """Load CSV and refresh each requested key once after the refresh button is clicked."""
    refreshed_keys = st.session_state.setdefault('refreshed_keys', set())
    force_all = st.session_state.get('refresh_drive', False)
    force = force_all and key not in refreshed_keys

    try:
        result = csv(key, force_refresh=force)
        if force_all:
            refreshed_keys.add(key)
        return result
    except Exception as e:
        st.error(f'Gagal memuat {key}: {e}')
        return None

def metrics(items):
    c=st.columns(len(items))
    for col,(a,b) in zip(c,items): col.metric(a,b)

def table(df, n=100):
    if df is not None: st.dataframe(df.head(n), use_container_width=True, height=500)

def download(df,name):
    if df is not None: st.download_button('⬇️ Download CSV',df.to_csv(index=False).encode(),name,'text/csv')

def pdf_view(key):
    """Tampilkan dokumen tanpa iframe Google Drive/PDF."""
    url = DRIVE_FILES.get(key, '')
    refreshed_keys = st.session_state.setdefault('refreshed_keys', set())
    force_all = st.session_state.get('refresh_drive', False)
    force = force_all and key not in refreshed_keys

    try:
        b = pdf(key, force_refresh=force)
        if force_all:
            refreshed_keys.add(key)
    except Exception as e:
        b = None
        st.warning(f'PDF belum dapat dimuat: {e}')

    if not url:
        st.warning(f'Link {key} belum diisi pada DRIVE_FILES.')
        return

    c1, c2 = st.columns(2)
    with c1:
        st.link_button('🔗 Buka Dokumen di Google Drive', url, use_container_width=True)
    with c2:
        if b:
            st.download_button(
                '⬇️ Download PDF', b, f'{key}.pdf', 'application/pdf',
                use_container_width=True
            )

    st.info(
        'Preview PDF di dalam iframe sengaja tidak digunakan karena Chrome dapat '
        'memblokir embedded PDF. Gunakan tombol di atas untuk membuka dokumen langsung.'
    )

st.markdown('# 📚 Harmonisasi Regulasi PBI–PADG')
st.caption('Interactive Regulatory Analysis Pipeline — membaca hasil yang sudah diproses, tanpa menjalankan ulang LLM/embedding.')

pages={
'🏠 Overview':'overview','1. Dokumen Regulasi':'documents',
'3. Regulatory Segmentation':'segmentation','4. Regulatory Hierarchy':'hierarchy','5. Knowledge Base':'knowledge',
'6. Embedding':'embedding','7. Similarity Matching':'similarity','8. Candidate Filtering':'filtering',
'9. LLM Regulatory Judgment':'llm','10. Final Regulatory Matching':'matching','11. Final Validation':'validation',
'12. Manual Evaluation':'manual','📊 Final Results':'results','⚠️ Keterbatasan': 'limitations'}
page=pages[st.sidebar.radio('Tahapan',list(pages))]
st.sidebar.divider()
st.sidebar.caption('Data source: Google Drive')

if st.sidebar.button('🔄 Refresh Data dari Google Drive', use_container_width=True):
    deleted = clear_all_cache()
    st.session_state['refresh_drive'] = True
    st.session_state['refreshed_keys'] = set()
    st.sidebar.success(f'Cache dibersihkan ({deleted} file). Memuat data terbaru...')
    st.rerun()

if st.session_state.get('refresh_drive', False):
    st.sidebar.info('Mode refresh aktif: file yang dimuat akan diambil ulang dari Google Drive.')

 
if page=='overview':
    st.header('Harmonisasi Regulasi di Bank Indonesia')

    st.markdown("""
    Regulatory Reform di Bank Indonesia dilakukan secara berkelanjutan untuk memastikan
    regulasi tetap selaras dan adaptif terhadap perubahan lingkungan strategis. Dalam
    prosesnya, setiap Petunjuk Teknis (Juknis) perlu selaras dengan ketentuan yang lebih
    tinggi, seperti PBI, PDG, PADG, dan PERBI.
    """)

    st.markdown("""
    Proses harmonisasi yang masih dilakukan secara manual mengharuskan reviewer
    membandingkan berbagai dokumen regulasi, sehingga membutuhkan waktu dan berisiko
    terhadap terlewatnya perbedaan istilah maupun substansi.
    """)

    st.markdown("""
    **Pemanfaatan AI** dikembangkan untuk membantu mengidentifikasi keterkaitan dan
    potensi ketidaksesuaian antar ketentuan secara lebih cepat, konsisten, dan sistematis,
    sehingga dapat menjadi **early warning** sekaligus mendukung proses review oleh reviewer.
    """)

    st.markdown("### Tujuan Pengembangan AI")

    st.markdown("""
    Mendukung proses harmonisasi dengan menganalisis kesesuaian ketentuan dan
    mengidentifikasi potensi ketidaksesuaian sebagai bahan pendukung proses review.
    """)

    st.divider()

    st.subheader('Tahapan Analisis')

    stages = [
        'Dokumen Regulasi',
        'Regulatory Segmentation',
        'Regulatory Hierarchy',
        'Knowledge Base',
        'Embedding',
        'Similarity Matching',
        'Candidate Filtering',
        'LLM Regulatory Judgment',
        'Final Regulatory Matching',
        'Final Validation',
        'Manual Evaluation'
    ]

    for i, s in enumerate(stages, 1):
        st.markdown(
            f'**{i}. {s}**  →  hasil tahap dapat dibuka melalui sidebar'
        )

    df = load('final_mapping')

    if df is not None:
        pc = next(
            (c for c in ['pbi_node_id', 'node_id'] if c in df),
            None
        )

        metrics([
            ('Final Mapping', f'{len(df):,}'),
            ('Unique PBI', f'{df[pc].nunique():,}' if pc else '-'),
            ('Columns', len(df.columns))
        ])

    
elif page=='documents':
    st.header('1. Dokumen Regulasi')
    a,b=st.tabs(['📄 PBI 10/2024','📄 PADG 15/2025'])
    with a: pdf_view('pbi_pdf')
    with b: pdf_view('padg_pdf')


elif page=='segmentation':
    st.header('2. Regulatory Segmentation'); df=load('segmented')
    if df is not None:
        metrics([('Total Nodes',f'{len(df):,}'),('Structure Types',df['structure_type'].nunique() if 'structure_type' in df else '-')])
        if 'structure_type' in df: st.bar_chart(df['structure_type'].value_counts())
        table(df,100); download(df,'segmented_regulations.csv')

elif page=='hierarchy':
    st.header('3. Regulatory Hierarchy'); df=load('hierarchy')
    if df is not None:
        metrics([('Nodes',f'{len(df):,}'),('Parent Types',df['parent_type'].nunique() if 'parent_type' in df else '-')])
        table(df,100)

elif page=='knowledge':
    st.header('4. Regulatory Knowledge Base'); df=load('knowledge_base')
    if df is not None:
        metrics([('Rows',f'{len(df):,}'),('Columns',len(df.columns))])
        if 'structure_type' in df: st.bar_chart(df['structure_type'].value_counts())
        table(df,100); download(df,'regulatory_knowledge_base.csv')

elif page=='embedding':
    st.header('5. Embedding')
    kb=load('knowledge_base'); emb=None
    try: emb=pkl('embeddings')
    except Exception as e: st.error(f'Gagal memuat embedding: {e}')
    if kb is not None: st.metric('Knowledge Base Nodes',f'{len(kb):,}')
    if emb is not None:
        st.success('✓ Embedding berhasil dimuat dari Drive.')
        if hasattr(emb,'shape'): st.metric('Embedding Shape',str(emb.shape))
        elif isinstance(emb,(dict,list,tuple)): st.metric('Embedding Objects',f'{len(emb):,}')

elif page=='similarity':
    st.header('6. Similarity Matching'); df=load('topk_candidates')
    if df is None:
        try: sim=pkl('similarity'); st.success('Similarity object berhasil dimuat.')
        except Exception as e: st.error(f'Gagal memuat similarity: {e}')
    else:
        pc='pbi_node_id' if 'pbi_node_id' in df else None
        metrics([('Candidate Rows',f'{len(df):,}'),('Unique PBI',f'{df[pc].nunique():,}' if pc else '-')]); table(df,100)

elif page=='filtering':
    st.header('7. Candidate Filtering'); df=load('filtered_candidates')
    if df is not None:
        pc=next((c for c in ['pbi_node_id','node_id'] if c in df),None)
        metrics([('Filtered Candidates',f'{len(df):,}'),('Unique PBI',f'{df[pc].nunique():,}' if pc else '-')])
        if 'similarity_score' in df: st.metric('Average Similarity',f"{df['similarity_score'].mean():.4f}")
        table(df,100); download(df,'pbi_padg_filtered_candidates.csv')

elif page=='llm':
    st.header('8. LLM Regulatory Judgment')
    df = load('final_candidate_with_llm')
    if df is None:
        df = load('llm_checkpoint')
    if df is not None:
        lc=next((c for c in ['llm_label','label','llm_judgment','final_label'] if c in df),None)
        metrics([('Candidates',f'{len(df):,}'),('Judged',f'{df[lc].notna().sum():,}' if lc else '-'),('Empty',f'{df[lc].isna().sum():,}' if lc else '-')])
        if lc:
            counts=df[lc].fillna('EMPTY').value_counts(); st.bar_chart(counts)
            sel=st.multiselect('Filter label',list(counts.index),default=list(counts.index)); df=df[df[lc].fillna('EMPTY').isin(sel)]
        table(df,100)

elif page=='matching':
    st.header('9. Final Regulatory Matching'); df=load('final_mapping')
    if df is not None:
        pc=next((c for c in ['pbi_node_id','node_id'] if c in df),None); dc='padg_node_id' if 'padg_node_id' in df else None
        lc=next((c for c in ['llm_label','final_label','label','judgment'] if c in df),None)
        metrics([('Mapping Rows',f'{len(df):,}'),('Unique PBI',f'{df[pc].nunique():,}' if pc else '-'),('Unique PADG',f'{df[dc].nunique():,}' if dc else '-')])
        if lc: st.bar_chart(df[lc].fillna('EMPTY').value_counts())
        table(df,200); download(df,'final_pbi_padg_mapping.csv')

elif page=='validation':
    st.header('10. Final Validation'); s=load('final_validation'); df=load('final_mapping')
    if s is not None: st.subheader('Validation Summary'); table(s,50)
    if df is not None:
        pc=next((c for c in ['pbi_node_id','node_id'] if c in df),None)
        if pc: st.metric('Unique PBI pada Final Mapping',f'{df[pc].nunique():,}')
        st.success('✓ Hasil final validation tersedia.')

elif page=='manual':
    st.header('11. Manual Evaluation')
    st.info('human_label, human_confidence, dan human_reason tidak diisi otomatis. Pengisian dilakukan oleh pihak yang memiliki kewenangan.')
    df=load('manual_evaluation')
    if df is not None:
        for c in ['human_label','human_confidence','human_reason']:
            if c in df:
                empty=df[c].isna() | (df[c].astype(str).str.strip()=='')
                st.metric(f'{c} kosong',f'{empty.sum():,}')
        table(df,100); download(df,'manual_evaluation_sample.csv')

elif page=='results':
    st.header('📊 Final Report'); df=load('final_mapping'); s=load('analysis_summary')
    if s is not None: st.subheader('Analysis Summary'); table(s,50)
    if df is not None:
        pc=next((c for c in ['pbi_node_id','node_id'] if c in df),None); lc=next((c for c in ['llm_label','final_label','label','judgment'] if c in df),None)
        metrics([('Final Mapping',f'{len(df):,}'),('Unique PBI',f'{df[pc].nunique():,}' if pc else '-'),('LLM Label Terisi',f'{df[lc].notna().sum():,}' if lc else '-')])
        if lc:
            counts=df[lc].fillna('EMPTY').value_counts(); fig,ax=plt.subplots(figsize=(8,4)); counts.plot(kind='bar',ax=ax); ax.set_ylabel('Count'); ax.set_xlabel('Label'); ax.set_title('PBI–PADG Regulatory Relationship'); plt.xticks(rotation=30,ha='right'); plt.tight_layout(); st.pyplot(fig); plt.close(fig)
        table(df,200); download(df,'final_pbi_padg_mapping.csv')
    st.warning('Hasil yang masih memerlukan human_label/human_confidence/human_reason belum merupakan expert-validated final result.')


elif page == 'limitations':
    st.header('⚠️ Keterbatasan Eksperimen')

    st.markdown("""
    Eksperimen ini merupakan **proof of concept** untuk menguji pemanfaatan
    Artificial Intelligence dalam mendukung proses harmonisasi regulasi.
    Oleh karena itu, terdapat beberapa keterbatasan yang perlu diperhatikan
    dalam interpretasi hasil.
    """)

    st.subheader('1. Keterbatasan Hardware')

    st.markdown("""
    Proses embedding dan terutama inferensi Large Language Model (LLM)
    membutuhkan sumber daya komputasi yang cukup besar. Keterbatasan
    kapasitas GPU dan memory menyebabkan eksperimen ini dibatasi pada
    **dua dokumen regulasi**, yaitu **PBI 10/2024** dan **PADG 15/2025**.

    Pembatasan tersebut dilakukan agar seluruh tahapan, khususnya proses
    LLM Regulatory Judgment, tetap dapat dijalankan dalam resource
    komputasi yang tersedia.
    """)

    st.subheader('2. Keterbatasan Model AI')

    st.markdown("""
    Eksperimen menggunakan **BAAI/bge-m3** sebagai embedding model dan
    **Qwen2.5-7B-Instruct** sebagai Large Language Model (LLM).

    Model tersebut digunakan dalam kondisi tanpa fine-tuning khusus terhadap
    terminologi dan karakteristik regulasi Bank Indonesia. Oleh karena itu,
    semantic similarity dan judgment yang dihasilkan masih memiliki kemungkinan
    mengandung kesalahan atau kurang menangkap konteks regulasi tertentu.
    """)

    st.subheader('3. Keterbatasan Dataset')

    st.markdown("""
    Eksperimen menggunakan pasangan regulasi **PBI 10/2024 dan PADG 15/2025**
    sebagai objek utama. Dengan demikian, hasil eksperimen belum dapat
    digunakan untuk menyimpulkan performa sistem pada seluruh regulasi
    Bank Indonesia.
    """)

    st.subheader('4. Keterbatasan Validasi')

    st.markdown("""
    Hasil AI masih berfungsi sebagai **pendukung proses review**, bukan sebagai
    keputusan regulasi. Beberapa hubungan antar ketentuan dapat memerlukan
    interpretasi hukum dan pemahaman konteks yang lebih mendalam.

    Oleh karena itu, hasil akhir tetap memerlukan **validasi oleh reviewer
    atau pihak yang memiliki kewenangan**.
    """)

    st.subheader('5. Keterbatasan Skalabilitas')

    st.markdown("""
    Ketika jumlah dokumen dan ketentuan regulasi meningkat secara signifikan,
    kebutuhan computational resource, waktu pemrosesan, serta kapasitas
    penyimpanan embedding dan hasil intermediate juga akan meningkat.

    Pengembangan lebih lanjut diperlukan agar sistem dapat menangani
    jumlah regulasi yang lebih besar secara efisien.
    """)

    st.divider()

    st.info(
        'Keterbatasan tersebut merupakan batasan pada tahap eksperimen dan '
        'proof of concept, bukan batasan konseptual dari pendekatan AI yang dikembangkan.'
    )