import streamlit as st
import os
from owlready2 import get_ontology
import traceback

st.set_page_config(page_title="Skincare Recommender (Ontology)", page_icon="🧴", layout="centered")
st.title("Skincare Recommender — Ontology-driven")

def find_owl_file():
  or name in os.listdir(os.getcwd()):
        if name.lower().endswith(".owl"):
            return os.path.join(os.getcwd(), skincare_recom (5))
    return None

owl_path = find_owl_file()
if not owl_path:
    st.error("File ontologi (.owl) tidak ditemukan di folder aplikasi. Pastikan file .owl ada di root repo.")
    st.stop()

try:
    onto = get_ontology(f"file://{owl_path}").load()
except Exception as e:
    st.error("Gagal load ontology: " + str(e))
    st.stop()

# --- helper: collect metadata ---
classes = sorted([c.name for c in onto.classes()])
obj_props = sorted([p.name for p in onto.object_properties()])
data_props = sorted([p.name for p in onto.data_properties()])
individuals = sorted([i.name for i in onto.individuals()])

# --- inspector (expandable) ---
with st.expander("🔎 Ontology inspector (classes / properties / individuals)"):
    st.write("Jumlah class:", len(classes))
    st.write("Beberapa class (contoh):", classes[:80])
    st.write("Object properties:", obj_props)
    st.write("Data properties:", data_props)
    st.write("Sample individuals (contoh):", individuals[:80])

# --- Mapping UI ---
st.subheader("🧩 Mapping Ontology")
produk_class = st.selectbox("Pilih Class yang mewakili produk (produk class):", classes, index=0)
prop_options = ["(none)"] + obj_props + data_props
jenis_kulit_prop = st.selectbox("Property untuk 'jenis kulit' pada produk (jenis kulit property):", prop_options, index=0)
masalah_kulit_prop = st.selectbox("Property untuk 'masalah kulit' pada produk (masalah kulit property):", prop_options, index=0)


def collect_values_for_property(prop_name):
    vals = set()
    if prop_name == "(none)":
        return []
    if not hasattr(onto, prop_name):
        return []
    prop = getattr(onto, prop_name)
    for ind in onto.individuals():
        if hasattr(ind, prop_name):
            try:
                for v in getattr(ind, prop_name):
                    if hasattr(v, "name"):
                        vals.add(v.name)
                    else:
                        # try to parse IRI-like strings
                        s = str(v)
                        if "." in s:
                            vals.add(s.split(".")[-1])
                        elif "#" in s:
                            vals.add(s.split("#")[-1])
                        else:
                            vals.add(s)
            except Exception:
                pass
    return sorted(vals)


    jenis_kulit_options = collect_values_for_property(jenis_kulit_prop)
if jenis_kulit_options:
    jenis_kulit = st.selectbox("Pilih jenis kulit (nilai dari ontology):", ["(manual input)"] + jenis_kulit_options)
    if jenis_kulit == "(manual input)":
        jenis_kulit = st.text_input("Masukkan jenis kulit (manual):", value="")
else:
    jenis_kulit = st.text_input("Masukkan jenis kulit:", value="")

masalah_kulit_options = collect_values_for_property(masalah_kulit_prop)
if masalah_kulit_options:
    masalah_kulit = st.multiselect("Pilih masalah kulit (nilai dari ontology):", masalah_kulit_options)
else:
    masalah_kulit = st.multiselect("Pilih masalah kulit (ketik manual jika perlu):",
                                   ["Jerawat","Flek Hitam","Kulit Kusam","Penuaan Dini","Bekas Jerawat"])
    

def clean_value(v):
    s = str(v)
    if "." in s:
        return s.split(".")[-1]
    if "#" in s:
        return s.split("#")[-1]
    return s

    # --- recommendation engine (knowledge-base style using assertions) ---

def recommend(produk_class_name, jenis_kulit_value, masalah_kulit_values):
    out = []
    try:
        produkclass = getattr(onto, produk_class_name)
    except Exception:
        return out
    for p in produkclass.instances():
        ok = True

# cek skin type

   if jenis_kulit_prop != "(none)" and jenis_kulit_value:
            if hasattr(p, jenis_kulit_prop):
                vals = [clean_value(x) for x in getattr(p, jenis_kulit_prop)]
                if jenis_kulit_value not in vals:
                    ok = False

 # cek masalah kulit (any match)

  if masalah_kulit_prop != "(none)" and masalah_kulit_values:
            if hasattr(p, masalah_kulit_prop):
                vals = [clean_value(x) for x in getattr(p, masalah_kulit_prop)]
                if not any(pr in vals for pr in masalah_kulit_values):
                    ok = False

  if ok:
            # prefer label if available
            try:
                lbl = p.label.first() if hasattr(p, "label") and p.label else None
                out.append(str(lbl) if lbl else p.name)
            except Exception:
                out.append(p.name)
    return out

# --- run recommendation ---

st.subheader("🎯 Input Pengguna")
st.write("Masukkan/ pilih preferensi lalu tekan tombol untuk melihat rekomendasi.")
if st.button("🔍 Cari Rekomendasi"):
    results = recommend(produk_class, jenis_kulit, masalah_kulit)
    if results:
        st.success(f"Ditemukan {len(results)} produk yang cocok:")
        for r in results:
            st.write("- " + r)
    else:
        st.info("Tidak ditemukan produk yang cocok. Coba ubah mapping atau periksa isi ontologi.")
