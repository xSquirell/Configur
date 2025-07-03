import streamlit as st
import pandas as pd

# --- CSV-ссылки Google Sheets ---
CPU_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQRyUL7uhyh1AFer0Q1f8my16H5XZHYWT_HwYXn59TreT19xQxSwBNp3Epy7baaAiR0KlLwiREiR5zu/pub?gid=1883998508&single=true&output=csv"
MB_URL  = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQRyUL7uhyh1AFer0Q1f8my16H5XZHYWT_HwYXn59TreT19xQxSwBNp3Epy7baaAiR0KlLwiREiR5zu/pub?gid=0&single=true&output=csv"
CH_URL  = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQRyUL7uhyh1AFer0Q1f8my16H5XZHYWT_HwYXn59TreT19xQxSwBNp3Epy7baaAiR0KlLwiREiR5zu/pub?gid=73405903&single=true&output=csv"

# --- Загрузка данных ---
cpu_df = pd.read_csv(CPU_URL)
mb_df  = pd.read_csv(MB_URL)
ch_df  = pd.read_csv(CH_URL)

# --- Определяем ключевые столбцы ---
# CPU
code_col  = 'Code'           # Part Number
proc_col  = 'Model'
sock_col  = 'Socket'
cores_col = 'C'
thr_col   = 'T'
freq_col  = 'Base frequency'
price_cpu_col = [c for c in cpu_df.columns if 'price' in c.lower() or 'цена' in c.lower()][0]
# MB
mb_code_col  = 'PN'
mb_name_col  = 'Model'
mb_sock_col  = 'Socket'
mb_cpu_count = 'CPUS'
mb_form_col  = 'MB FF'
price_mb_col = [c for c in mb_df.columns if 'price' in c.lower() or 'цена' in c.lower()][0]
# CH
ch_code_col    = 'PN'
ch_name_col    = 'Model'
ch_dims_col    = 'Dimensions (W x D x H)'
ch_ff_col      = 'FF'
ch_support_col = 'MB FF'
front_bays     = 'Front Bays'
type_fb        = 'Type front bays'
ff_fb          = 'form factor front bays'
inner_bays     = 'Inner bays'
ff_ib          = 'form factor inner bays'
rear_bays      = 'rear bays'
type_rb        = 'type rear bays'
ff_rb          = 'form factor rear bays'
price_ch_col   = [c for c in ch_df.columns if 'price' in c.lower() or 'цена' in c.lower()][0]

# --- Проверка наличия столбцов ---
def ensure(col, df, name):
    if col not in df.columns:
        st.error(f"Column '{col}' not found in {name} sheet")
        st.stop()
for col,name,df in [
    (code_col,'CPU',cpu_df),(proc_col,'CPU',cpu_df),(sock_col,'CPU',cpu_df),
    (cores_col,'CPU',cpu_df),(thr_col,'CPU',cpu_df),(freq_col,'CPU',cpu_df),(price_cpu_col,'CPU',cpu_df),
    (mb_code_col,'MB',mb_df),(mb_name_col,'MB',mb_df),(mb_sock_col,'MB',mb_df),
    (mb_cpu_count,'MB',mb_df),(mb_form_col,'MB',mb_df),(price_mb_col,'MB',mb_df),
    (ch_code_col,'CH',ch_df),(ch_name_col,'CH',ch_df),(ch_dims_col,'CH',ch_df),
    (ch_ff_col,'CH',ch_df),(ch_support_col,'CH',ch_df),(front_bays,'CH',ch_df),
    (type_fb,'CH',ch_df),(ff_fb,'CH',ch_df),(inner_bays,'CH',ch_df),(ff_ib,'CH',ch_df),
    (rear_bays,'CH',ch_df),(type_rb,'CH',ch_df),(ff_rb,'CH',ch_df),(price_ch_col,'CH',ch_df)
]:
    ensure(col, df, name)

# --- Нормализация сокета ---
cpu_df['sock_norm'] = cpu_df[sock_col].astype(str).str.strip().str.lower().str.replace(' ',' ').str.replace('-', '-')
mb_df['sock_norm']  = mb_df[mb_sock_col].astype(str).str.strip().str.lower().str.replace(' ',' ').str.replace('-', '-')

# --- Streamlit UI ---
st.set_page_config(page_title='Configurator', layout='wide')
st.title('Конфигуратор сервера')

# 1) Выбор CPU
t_c = cpu_df[proc_col].tolist()
selected_cpu = st.selectbox('Процессор', t_c)
cpu_row = cpu_df[cpu_df[proc_col]==selected_cpu].iloc[0]
# 2) Выбор MB
compatible_mb = mb_df[mb_df['sock_norm']==cpu_row['sock_norm']]
if compatible_mb.empty:
    st.error('Нет совместимых материнских плат для выбранного процессора.')
    st.stop()
selected_mb = st.selectbox('Материнская плата', compatible_mb[mb_name_col].tolist())
mb_row = compatible_mb[compatible_mb[mb_name_col]==selected_mb].iloc[0]
# 3) Кол-во CPU
n_cpu = int(mb_row[mb_cpu_count] or 1)
if n_cpu > 1:
    cpu_count = st.slider('Кол-во CPU', min_value=1, max_value=n_cpu, value=1)
else:
    st.write('Количество процессоров: 1')
    cpu_count = 1
# 4) Выбор корпуса
compatible_ch = ch_df[ch_df[ch_support_col].str.contains(mb_row[mb_form_col], na=False)]
selected_ch = st.selectbox('Корпус', compatible_ch[ch_name_col].tolist())
ch_row = compatible_ch[compatible_ch[ch_name_col]==selected_ch].iloc[0]

# --- Сборка итогового DataFrame ---
# Расчет цен
price_cpu = float(cpu_row[price_cpu_col]) * cpu_count
price_mb  = float(mb_row[price_mb_col])
price_ch  = float(ch_row[price_ch_col])
total_price = price_cpu + price_mb + price_ch

# Спецификации
spec_cpu = f"{cpu_row[sock_col]}, {int(cpu_row[cores_col])}/{int(cpu_row[thr_col])}, @{cpu_row[freq_col]}GHz"
spec_mb  = f"{mb_row[mb_sock_col]}, {mb_row[mb_cpu_count]} CPU, {mb_row[mb_form_col]}"
# Корпус specs
# Функция безопасного преобразования в int
import math

def to_int(val):
    try:
        if pd.isna(val): return 0
        # строковые числа вроде '0', '2'
        return int(float(val))
    except:
        return 0

fb = to_int(ch_row[front_bays])
ib = to_int(ch_row[inner_bays])
rb = to_int(ch_row[rear_bays])
# Подробности корзин с типом и форм-фактором
front_detail = f"{fb}×({ch_row[type_fb]}, {ch_row[ff_fb]})" if fb > 0 else "0"
inner_detail = f"{ib}×({ch_row[type_fb]}, {ch_row[ff_ib]})" if ib > 0 else "0"
rear_detail  = f"{rb}×({ch_row[type_rb]}, {ch_row[ff_rb]})" if rb > 0 else "0"
spec_ch = (
    f"{ch_row[ch_dims_col]}, FF {ch_row[ch_ff_col]}, корзины: "
    f"фронтальная {front_detail}; "
    f"внутренняя {inner_detail}; "
    f"задняя {rear_detail}"
)

# DataFrame с дополнительным полем Count
records = [
    {
        'Партномер': cpu_row[code_col],
        'Тип': 'CPU',
        'Наименонование': cpu_row[proc_col],
        'Характеристики': spec_cpu,
        'Количество': cpu_count,
        'Цена': price_cpu
    },
    {
        'Партномер': mb_row[mb_code_col],
        'Тип': 'MB',
        'Наименонование': mb_row[mb_name_col],
        'Характеристики': spec_mb,
        'Количество': 1,
        'Цена': price_mb
    },
    {
        'Партномер': ch_row[ch_code_col],
        'Тип': 'CH',
        'Наименонование': ch_row[ch_name_col],
        'Характеристики': spec_ch + f", PSU: {ch_row['PSU']} {ch_row['PSU power']}W",
        'Количество': 1,
        'Цена': price_ch
    }
]
# Вывод таблицы без индекса и с колонкой Count
st.table(records)
# Итоговая цена
st.markdown(f"**Итого:** {total_price}")

st.info('Версия с гугл-доками.')('Версия с гугл-доками.')
