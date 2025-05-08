import streamlit as st
import requests
from decimal import Decimal, InvalidOperation
import datetime

API_BASE_URL = "http://127.0.0.1:8000/api"
SERVER_BASE_URL = (
    "http://127.0.0.1:8000"
)

AUTHORS_URL = f"{API_BASE_URL}/authors/"
CATEGORIES_URL = f"{API_BASE_URL}/categories/"
BOOKS_URL = f"{API_BASE_URL}/books/"
TOKEN_URL = f"{API_BASE_URL}/token/"

BOOK_FORMAT_CHOICES_FRONTEND = [
    ("", "---"),
    ("HB", "Hardback"),
    ("PB", "Paperback"),
    ("EB", "Ebook"),
]
BOOK_FORMAT_CODES = [code for code, name in BOOK_FORMAT_CHOICES_FRONTEND]

if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "selected_book_data" not in st.session_state:
    st.session_state.selected_book_data = None


def get_auth_headers():
    if st.session_state.auth_token:
        return {"Authorization": f"Bearer {st.session_state.auth_token}"}
    return {}


def login(username, password):
    try:
        response = requests.post(
            TOKEN_URL, data={"username": username, "password": password}
        )
        response.raise_for_status()
        tokens = response.json()
        st.session_state.auth_token = tokens.get("access")
        st.session_state.refresh_token = tokens.get("refresh")
        st.session_state.user_info = username
        st.session_state.selected_book_data = None
        st.success("Zalogowano pomyślnie!")
        st.rerun()
    except requests.exceptions.RequestException as e:
        st.error(f"Błąd logowania: {e}")
        st.error(
            f"Odpowiedź serwera: {e.response.json() if e.response and e.response.content else 'Brak/Nieprawidłowa odpowiedź'}"
        )
    except Exception as e:
        st.error(f"Nieoczekiwany błąd podczas logowania: {e}")


def logout():
    st.session_state.auth_token = None
    st.session_state.refresh_token = None
    st.session_state.user_info = None
    st.session_state.selected_book_data = None
    st.rerun()


def fetch_data(url, params=None):
    try:
        response = requests.get(url, headers=get_auth_headers(), params=params)
        response.raise_for_status()
        data = response.json()
        results = []
        if isinstance(data, dict) and "results" in data:
            results.extend(data["results"])
            next_url = data.get("next")
            while next_url:
                response = requests.get(next_url, headers=get_auth_headers())
                response.raise_for_status()
                data = response.json()
                results.extend(data["results"])
                next_url = data.get("next")
            return results
        elif isinstance(data, list):
            return data
        else:
            st.warning(f"Nieoczekiwany format danych z {url}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Błąd pobierania danych z {url}: {e}")
        st.error(
            f"Odpowiedź serwera: {e.response.text if e.response else 'Brak odpowiedzi'}"
        )
        return None
    except Exception as e:
        st.error(f"Nieoczekiwany błąd podczas pobierania danych: {e}")
        return None


def fetch_single_data(url):
    try:
        response = requests.get(url, headers=get_auth_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Błąd pobierania danych z {url}: {e}")
        st.error(
            f"Odpowiedź serwera: {e.response.text if e.response else 'Brak odpowiedzi'}"
        )
        return None
    except Exception as e:
        st.error(f"Nieoczekiwany błąd podczas pobierania danych: {e}")
        return None


def create_data(url, data):
    headers = get_auth_headers()
    if not headers:
        st.warning("Musisz być zalogowany.")
        return None
    headers["Content-Type"] = "application/json"
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        st.success("Dane dodane pomyślnie!")
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Błąd dodawania danych (JSON) do {url}: {e}")
        try:
            error_details = e.response.json()
            st.error(f"Odpowiedź serwera: {error_details}")
        except:
            st.error(
                f"Odpowiedź serwera (nie JSON): {e.response.text if e.response else 'Brak odpowiedzi'}"
            )
        return None
    except Exception as e:
        st.error(f"Nieoczekiwany błąd: {e}")
        return None


def create_data_with_file(url, data, files):
    headers = get_auth_headers()
    if not headers:
        st.warning("Musisz być zalogowany.")
        return None
    try:
        response = requests.post(url, headers=headers, data=data, files=files)
        response.raise_for_status()
        st.success("Dane i plik dodane pomyślnie!")
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Błąd dodawania danych (multipart) do {url}: {e}")
        try:
            error_details = e.response.json()
            st.error(f"Odpowiedź serwera: {error_details}")
        except:
            st.error(
                f"Odpowiedź serwera (nie JSON): {e.response.text if e.response else 'Brak odpowiedzi'}"
            )
        return None
    except Exception as e:
        st.error(f"Nieoczekiwany błąd: {e}")
        return None


def update_data(url, data):
    headers = get_auth_headers()
    if not headers:
        st.warning("Musisz być zalogowany.")
        return None
    headers["Content-Type"] = "application/json"
    try:
        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()
        st.success("Dane zaktualizowane pomyślnie!")
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Błąd aktualizacji danych w {url}: {e}")
        try:
            error_details = e.response.json()
            st.error(f"Odpowiedź serwera: {error_details}")
        except:
            st.error(
                f"Odpowiedź serwera (nie JSON): {e.response.text if e.response else 'Brak odpowiedzi'}"
            )
        return None
    except Exception as e:
        st.error(f"Nieoczekiwany błąd: {e}")
        return None


def delete_data(url):
    headers = get_auth_headers()
    if not headers:
        st.warning("Musisz być zalogowany.")
        return False
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        st.success("Dane usunięte pomyślnie!")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Błąd usuwania danych z {url}: {e}")
        st.error(
            f"Odpowiedź serwera: {e.response.text if e.response else 'Brak odpowiedzi'}"
        )
        return False
    except Exception as e:
        st.error(f"Nieoczekiwany błąd: {e}")
        return False


st.set_page_config(layout="wide")
st.title("📚 Biblioteka")

st.sidebar.header("Logowanie")
if not st.session_state.auth_token:
    with st.sidebar.form("login_form"):
        username = st.text_input("Nazwa użytkownika")
        password = st.text_input("Hasło", type="password")
        submitted = st.form_submit_button("Zaloguj")
        if submitted:
            if username and password:
                login(username, password)
            else:
                st.warning("Podaj nazwę użytkownika i hasło.")
else:
    st.sidebar.success(f"Zalogowano jako: {st.session_state.user_info}")
    if st.sidebar.button("Wyloguj"):
        logout()

tab_authors, tab_categories, tab_books = st.tabs(["Autorzy", "Kategorie", "Książki"])

with tab_authors:
    st.header("Zarządzanie Autorami")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Lista Autorów")
        if st.button("Odśwież Autorów"):
            st.rerun()
        authors = fetch_data(AUTHORS_URL)
        if authors:
            authors_display = [
                {
                    "ID": a.get("id"),
                    "Imię": a.get("first_name"),
                    "Nazwisko": a.get("last_name"),
                }
                for a in authors
            ]
            st.dataframe(authors_display, use_container_width=True)
        else:
            st.info("Brak autorów do wyświetlenia lub błąd pobierania.")

        st.subheader("Operacje na Autorze")
        if authors:
            author_options = {
                f"{a['first_name']} {a['last_name']} (ID: {a['id']})": a["id"]
                for a in authors
            }
            selected_author_display = st.selectbox(
                "Wybierz autora do edycji/usunięcia",
                options=["-- Wybierz --"] + list(author_options.keys()),
                key="author_select",
            )
            if selected_author_display != "-- Wybierz --":
                selected_author_id = author_options[selected_author_display]
                confirm_delete_author = st.checkbox(
                    f"Potwierdź usunięcie autora ID: {selected_author_id}",
                    key=f"del_auth_confirm_{selected_author_id}",
                )
                if st.button(
                    f"Usuń wybranego autora",
                    type="primary",
                    key=f"del_auth_btn_{selected_author_id}",
                ):
                    if confirm_delete_author:
                        url_del = f"{AUTHORS_URL}{selected_author_id}/"
                        if delete_data(url_del):
                            st.rerun()
                    else:
                        st.warning("Zaznacz pole potwierdzenia, aby usunąć.")

                with st.form(f"update_author_{selected_author_id}"):
                    st.write(f"Edytuj autora: {selected_author_display}")
                    current_author_data = next(
                        (a for a in authors if a["id"] == selected_author_id), None
                    )
                    first_name_update = st.text_input(
                        "Nowe imię",
                        value=current_author_data["first_name"]
                        if current_author_data
                        else "",
                        key=f"fn_upd_{selected_author_id}",
                    )
                    last_name_update = st.text_input(
                        "Nowe nazwisko",
                        value=current_author_data["last_name"]
                        if current_author_data
                        else "",
                        key=f"ln_upd_{selected_author_id}",
                    )
                    submitted_update = st.form_submit_button("Zaktualizuj Autora")
                    if submitted_update:
                        update_payload = {}
                        if first_name_update and first_name_update != (
                            current_author_data["first_name"]
                            if current_author_data
                            else ""
                        ):
                            update_payload["first_name"] = first_name_update
                        if last_name_update and last_name_update != (
                            current_author_data["last_name"]
                            if current_author_data
                            else ""
                        ):
                            update_payload["last_name"] = last_name_update
                        if update_payload:
                            url_upd = f"{AUTHORS_URL}{selected_author_id}/"
                            if update_data(url_upd, update_payload):
                                st.rerun()
                        else:
                            st.info("Nie wprowadzono zmian.")
    with col2:
        st.subheader("Dodaj Nowego Autora")
        with st.form("new_author_form", clear_on_submit=True):
            first_name_new = st.text_input("Imię*")
            last_name_new = st.text_input("Nazwisko*")
            submitted_new = st.form_submit_button("Dodaj Autora")
            if submitted_new:
                if first_name_new and last_name_new:
                    author_data = {
                        "first_name": first_name_new,
                        "last_name": last_name_new,
                    }
                    if create_data(AUTHORS_URL, author_data):
                        st.rerun()
                else:
                    st.warning("Wypełnij imię i nazwisko.")

with tab_categories:
    st.header("Zarządzanie Kategoriami")
    col1_cat, col2_cat = st.columns(2)
    with col1_cat:
        st.subheader("Lista Kategorii")
        if st.button("Odśwież Kategorie"):
            st.rerun()
        categories = fetch_data(CATEGORIES_URL)
        if categories:
            cat_display = [
                {
                    "ID": c.get("id"),
                    "Nazwa": c.get("name"),
                    "Opis": c.get("description", ""),
                }
                for c in categories
            ]
            st.dataframe(cat_display, use_container_width=True)
        else:
            st.info("Brak kategorii do wyświetlenia lub błąd pobierania.")

        st.subheader("Operacje na Kategorii")
        if categories:
            cat_options = {f"{c['name']} (ID: {c['id']})": c["id"] for c in categories}
            selected_cat_display = st.selectbox(
                "Wybierz kategorię do edycji/usunięcia",
                options=["-- Wybierz --"] + list(cat_options.keys()),
                key="cat_select",
            )
            if selected_cat_display != "-- Wybierz --":
                selected_cat_id = cat_options[selected_cat_display]
                confirm_delete_cat = st.checkbox(
                    f"Potwierdź usunięcie kategorii ID: {selected_cat_id}",
                    key=f"del_cat_confirm_{selected_cat_id}",
                )
                if st.button(
                    f"Usuń wybraną kategorię",
                    type="primary",
                    key=f"del_cat_btn_{selected_cat_id}",
                ):
                    if confirm_delete_cat:
                        url_del_cat = f"{CATEGORIES_URL}{selected_cat_id}/"
                        if delete_data(url_del_cat):
                            st.rerun()
                    else:
                        st.warning("Zaznacz pole potwierdzenia, aby usunąć.")

                with st.form(f"update_category_{selected_cat_id}"):
                    st.write(f"Edytuj kategorię: {selected_cat_display}")
                    current_cat_data = next(
                        (c for c in categories if c["id"] == selected_cat_id), None
                    )
                    name_update = st.text_input(
                        "Nowa nazwa",
                        value=current_cat_data["name"] if current_cat_data else "",
                        key=f"name_upd_{selected_cat_id}",
                    )
                    desc_update = st.text_area(
                        "Nowy opis",
                        value=current_cat_data.get("description", "")
                        if current_cat_data
                        else "",
                        key=f"desc_upd_{selected_cat_id}",
                    )
                    submitted_update_cat = st.form_submit_button(
                        "Zaktualizuj Kategorię"
                    )
                    if submitted_update_cat:
                        update_payload_cat = {}
                        if name_update and name_update != (
                            current_cat_data["name"] if current_cat_data else ""
                        ):
                            update_payload_cat["name"] = name_update
                        if desc_update != (
                            current_cat_data.get("description", "")
                            if current_cat_data
                            else ""
                        ):
                            update_payload_cat["description"] = desc_update
                        if update_payload_cat:
                            url_upd_cat = f"{CATEGORIES_URL}{selected_cat_id}/"
                            if update_data(url_upd_cat, update_payload_cat):
                                st.rerun()
                        else:
                            st.info("Nie wprowadzono zmian.")
    with col2_cat:
        st.subheader("Dodaj Nową Kategorię")
        with st.form("new_category_form", clear_on_submit=True):
            name_new = st.text_input("Nazwa*")
            desc_new = st.text_area("Opis")
            submitted_new_cat = st.form_submit_button("Dodaj Kategorię")
            if submitted_new_cat:
                if name_new:
                    category_data = {"name": name_new, "description": desc_new}
                    if create_data(CATEGORIES_URL, category_data):
                        st.rerun()
                else:
                    st.warning("Podaj nazwę kategorii.")

with tab_books:
    st.header("Zarządzanie Książkami")

    all_authors = fetch_data(AUTHORS_URL)
    all_categories = fetch_data(CATEGORIES_URL)

    author_map = (
        {f"{a['first_name']} {a['last_name']}": a["id"] for a in all_authors}
        if all_authors
        else {}
    )
    author_map_rev = {v: k for k, v in author_map.items()}
    category_map = (
        {c["name"]: c["id"] for c in all_categories} if all_categories else {}
    )
    category_map_rev = {v: k for k, v in category_map.items()}

    col1_book, col2_book = st.columns([3, 2])

    with col1_book:
        st.subheader("Lista Książek")
        if st.button("Odśwież Książki"):
            st.rerun()
        books = fetch_data(BOOKS_URL)
        if books:
            st.markdown("---")
            cols_per_row = 4
            for i, b in enumerate(books):
                if i % cols_per_row == 0:
                    cols = st.columns(cols_per_row)
                col_index = i % cols_per_row
                with cols[col_index]:
                    cover_url = b.get("cover_image")
                    details = b.get("details", {})

                    if cover_url:
                        if cover_url.startswith(
                            "/media"
                        ):
                            cover_url = f"{SERVER_BASE_URL}{cover_url}"
                        st.image(
                            cover_url, caption=f"ID: {b.get('id')}", width=100
                        )
                    else:
                        st.caption(f"ID: {b.get('id')} (brak okładki)")

                    st.markdown(f"**{b.get('title')}**")
                    st.caption(f"Autor: {b.get('author_name')}")
                    st.caption(f"Kategorie: {', '.join(b.get('category_names', []))}")
                    st.caption(
                        f"Cena: {b.get('price', '')} | Data: {b.get('publication_date', '')} | Format: {b.get('book_format', '')}"
                    )
                    if details:
                        st.caption(
                            f"ISBN: {details.get('isbn', '-')} | Stron: {details.get('number_of_pages', '-')}"
                        )

                    st.markdown("---")
        else:
            st.info("Brak książek do wyświetlenia lub błąd pobierania.")

        st.subheader("Operacje na Książce")
        if books:
            book_options = {
                f"{b['title']} ({b['author_name']}) (ID: {b['id']})": b["id"]
                for b in books
            }
            selected_book_display = st.selectbox(
                "Wybierz książkę do edycji/usunięcia",
                options=["-- Wybierz --"] + list(book_options.keys()),
                key="book_select",
            )

            if selected_book_display != "-- Wybierz --":
                selected_book_id = book_options[selected_book_display]
                if (
                    st.session_state.selected_book_data is None
                    or st.session_state.selected_book_data.get("id") != selected_book_id
                ):
                    st.session_state.selected_book_data = fetch_single_data(
                        f"{BOOKS_URL}{selected_book_id}/"
                    )

                if st.session_state.selected_book_data:
                    current_book = st.session_state.selected_book_data
                    current_details = current_book.get("details", {}) or {}

                    st.markdown("###")
                    st.subheader(f"Edytuj / Usuń: {current_book.get('title')}")

                    current_cover_url = current_book.get("cover_image")
                    if current_cover_url:
                        if current_cover_url.startswith("/media"):
                            current_cover_url = f"{SERVER_BASE_URL}{current_cover_url}"
                        st.image(
                            current_cover_url, caption="Aktualna okładka", width=150
                        )
                    else:
                        st.caption("Brak aktualnej okładki.")

                    confirm_delete_book = st.checkbox(
                        f"Potwierdź usunięcie książki ID: {selected_book_id}",
                        key=f"del_book_confirm_{selected_book_id}",
                    )
                    if st.button(
                        f"Usuń wybraną książkę",
                        type="primary",
                        key=f"del_book_btn_{selected_book_id}",
                    ):
                        if confirm_delete_book:
                            url_del_book = f"{BOOKS_URL}{selected_book_id}/"
                            if delete_data(url_del_book):
                                st.session_state.selected_book_data = None
                                st.rerun()
                        else:
                            st.warning("Zaznacz pole potwierdzenia, aby usunąć.")

                    with st.form(
                        f"update_book_{selected_book_id}", clear_on_submit=False
                    ):
                        st.write(
                            "Wprowadź nowe wartości (pozostaw puste, aby nie zmieniać):"
                        )
                        title_upd = st.text_input(
                            "Tytuł", value=current_book.get("title", "")
                        )
                        desc_upd = st.text_area(
                            "Opis", value=current_book.get("description", "")
                        )
                        price_str_upd = st.text_input(
                            "Cena", value=str(current_book.get("price", ""))
                        )
                        current_pub_date = current_book.get("publication_date")
                        pub_date_upd_obj = None
                        if current_pub_date:
                            try:
                                pub_date_upd_obj = datetime.datetime.strptime(
                                    current_pub_date, "%Y-%m-%d"
                                ).date()
                            except ValueError:
                                pub_date_upd_obj = None
                        pub_date_upd = st.date_input(
                            "Data publikacji", value=pub_date_upd_obj
                        )

                        current_format = current_book.get("book_format", "")
                        try:
                            format_index = BOOK_FORMAT_CODES.index(current_format)
                        except ValueError:
                            format_index = 0
                        format_upd = st.selectbox(
                            "Format",
                            options=BOOK_FORMAT_CODES,
                            index=format_index,
                            key=f"fmt_upd_{selected_book_id}",
                        )

                        author_options_list = list(author_map.keys())
                        current_author_id = current_book.get("author")
                        current_author_name = author_map_rev.get(current_author_id)
                        author_index = (
                            author_options_list.index(current_author_name)
                            if current_author_name in author_options_list
                            else 0
                        )
                        selected_author_name_upd = st.selectbox(
                            "Autor", options=author_options_list, index=author_index
                        )

                        category_options_list = list(category_map.keys())
                        current_category_ids = current_book.get("categories", [])
                        current_category_names = [
                            category_map_rev.get(cid)
                            for cid in current_category_ids
                            if category_map_rev.get(cid)
                        ]
                        selected_category_names_upd = st.multiselect(
                            "Kategorie",
                            options=category_options_list,
                            default=current_category_names,
                        )

                        with st.expander("Szczegóły książki (opcjonalne)"):
                            isbn_upd = st.text_input(
                                "ISBN", value=current_details.get("isbn", "") or ""
                            )
                            pages_upd_str = st.text_input(
                                "Liczba stron",
                                value=str(current_details.get("number_of_pages", ""))
                                if current_details.get("number_of_pages") is not None
                                else "",
                            )
                            lang_upd = st.text_input(
                                "Język", value=current_details.get("language", "") or ""
                            )
                            pub_upd = st.text_input(
                                "Wydawca",
                                value=current_details.get("publisher", "") or "",
                            )

                        submitted_update_book = st.form_submit_button(
                            "Zaktualizuj Książkę"
                        )

                        if submitted_update_book:
                            update_payload_book = {}
                            if title_upd != current_book.get("title", ""):
                                update_payload_book["title"] = title_upd
                            if desc_upd != current_book.get("description", ""):
                                update_payload_book["description"] = desc_upd
                            try:
                                price_upd_dec = (
                                    Decimal(price_str_upd) if price_str_upd else None
                                )
                                current_price_dec = (
                                    Decimal(current_book.get("price"))
                                    if current_book.get("price")
                                    else None
                                )
                                if price_upd_dec != current_price_dec:
                                    update_payload_book["price"] = (
                                        price_str_upd
                                        if price_upd_dec is not None
                                        else None
                                    )
                            except InvalidOperation:
                                st.warning("Nieprawidłowy format ceny.")
                            pub_date_str_upd = (
                                pub_date_upd.isoformat() if pub_date_upd else None
                            )
                            if pub_date_str_upd != current_book.get("publication_date"):
                                update_payload_book[
                                    "publication_date"
                                ] = pub_date_str_upd
                            if format_upd != current_book.get("book_format", ""):
                                update_payload_book["book_format"] = (
                                    format_upd if format_upd else None
                                )

                            selected_author_id_upd = author_map.get(
                                selected_author_name_upd
                            )
                            if selected_author_id_upd != current_book.get("author"):
                                update_payload_book["author"] = selected_author_id_upd

                            selected_category_ids_upd = [
                                category_map.get(name)
                                for name in selected_category_names_upd
                                if category_map.get(name)
                            ]
                            if set(selected_category_ids_upd) != set(
                                current_book.get("categories", [])
                            ):
                                update_payload_book[
                                    "categories"
                                ] = selected_category_ids_upd

                            details_payload = {}
                            if isbn_upd != (current_details.get("isbn", "") or ""):
                                details_payload["isbn"] = isbn_upd if isbn_upd else None
                            try:
                                pages_upd_int = (
                                    int(pages_upd_str) if pages_upd_str else None
                                )
                                current_pages = current_details.get("number_of_pages")
                                if pages_upd_int != current_pages:
                                    details_payload["number_of_pages"] = pages_upd_int
                            except ValueError:
                                st.warning("Nieprawidłowa liczba stron.")
                            if lang_upd != (current_details.get("language", "") or ""):
                                details_payload["language"] = (
                                    lang_upd if lang_upd else None
                                )
                            if pub_upd != (current_details.get("publisher", "") or ""):
                                details_payload["publisher"] = (
                                    pub_upd if pub_upd else None
                                )

                            if details_payload:
                                update_payload_book["details"] = details_payload

                            if update_payload_book:
                                url_upd_book = f"{BOOKS_URL}{selected_book_id}/"
                                if update_data(url_upd_book, update_payload_book):
                                    st.session_state.selected_book_data = None
                                    st.rerun()
                            else:
                                st.info("Nie wprowadzono żadnych zmian.")
                else:
                    st.warning("Nie udało się pobrać danych wybranej książki.")

    with col2_book:
        st.subheader("Dodaj Nową Książkę")
        if not all_authors or not all_categories:
            st.warning("Nie można dodać książki - najpierw dodaj autorów i kategorie.")
        else:
            with st.form("new_book_form", clear_on_submit=True):
                title_new = st.text_input("Tytuł*", key="new_title")
                desc_new = st.text_area("Opis", key="new_desc")
                price_str_new = st.text_input("Cena*", key="new_price")
                pub_date_new = st.date_input(
                    "Data publikacji*", key="new_pub_date", value=datetime.date.today()
                )
                format_new = st.selectbox(
                    "Format", options=BOOK_FORMAT_CODES, key="new_format"
                )
                author_options_list = ["-- Wybierz autora --"] + list(author_map.keys())
                selected_author_name_new = st.selectbox(
                    "Autor*", options=author_options_list, key="new_author"
                )
                category_options_list = list(category_map.keys())
                selected_category_names_new = st.multiselect(
                    "Kategorie*", options=category_options_list, key="new_categories"
                )

                cover_image_file = st.file_uploader(
                    "Okładka (opcjonalnie)",
                    type=["jpg", "png", "jpeg"],
                    key="new_cover",
                )

                with st.expander("Szczegóły książki (opcjonalne)"):
                    isbn_new = st.text_input("ISBN", key="new_isbn")
                    pages_new_str = st.text_input("Liczba stron", key="new_pages")
                    lang_new = st.text_input("Język", key="new_lang")
                    pub_new = st.text_input("Wydawca", key="new_pub")

                submitted_new_book = st.form_submit_button("Dodaj Książkę")

                if submitted_new_book:
                    errors = []
                    if not title_new:
                        errors.append("Tytuł jest wymagany.")
                    if not price_str_new:
                        errors.append("Cena jest wymagana.")
                    if selected_author_name_new == "-- Wybierz autora --":
                        errors.append("Autor jest wymagany.")
                    if not selected_category_names_new:
                        errors.append("Przynajmniej jedna kategoria jest wymagana.")
                    if not pub_date_new:
                        errors.append("Data publikacji jest wymagana.")

                    price_new_dec = None
                    pages_new_int = None
                    try:
                        if price_str_new:
                            price_new_dec = Decimal(price_str_new)
                    except InvalidOperation:
                        errors.append("Nieprawidłowy format ceny.")
                    try:
                        if pages_new_str:
                            pages_new_int = int(pages_new_str)
                    except ValueError:
                        errors.append(
                            "Nieprawidłowa liczba stron (musi być liczbą całkowitą)."
                        )

                    if errors:
                        for error in errors:
                            st.warning(error)
                    else:
                        if cover_image_file is not None:
                            multipart_data_payload = {
                                "title": title_new,
                                "author": author_map[selected_author_name_new],
                                "price": price_str_new,
                                "publication_date": pub_date_new.isoformat(),
                                "description": desc_new,
                                "book_format": format_new if format_new else "",
                            }
                            for i, name in enumerate(
                                selected_category_names_new
                            ):
                                multipart_data_payload[
                                    f"categories[{i}]"
                                ] = category_map[name]

                            files_payload = {
                                "cover_image": (
                                    cover_image_file.name,
                                    cover_image_file,
                                    cover_image_file.type,
                                )
                            }

                            if create_data_with_file(
                                BOOKS_URL,
                                data=multipart_data_payload,
                                files=files_payload,
                            ):
                                st.session_state.selected_book_data = None
                                st.rerun()
                        else:
                            json_payload = {
                                "title": title_new,
                                "author": author_map[selected_author_name_new],
                                "categories": [
                                    category_map[name]
                                    for name in selected_category_names_new
                                ],
                                "price": price_str_new,
                                "publication_date": pub_date_new.isoformat(),
                                "description": desc_new,
                                "book_format": format_new if format_new else None,
                            }
                            details_payload_new = {}
                            if isbn_new:
                                details_payload_new["isbn"] = isbn_new
                            if pages_new_int is not None:
                                details_payload_new["number_of_pages"] = pages_new_int
                            if lang_new:
                                details_payload_new["language"] = lang_new
                            if pub_new:
                                details_payload_new["publisher"] = pub_new
                            if details_payload_new:
                                json_payload["details"] = details_payload_new

                            if create_data(BOOKS_URL, json_payload):
                                st.session_state.selected_book_data = None
                                st.rerun()
