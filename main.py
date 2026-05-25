import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

from model import PowerCalculator
from graphic_funtion import create_vector_plot

# Налаштовуємо заголовки
header = st.container()
fields = st.container()
writer = st.container()
current_cotainer=st.container()
graf = st.container()


with header:
    # Використовуємо стандартний заголовок без зайвих параметрів
    st.title("⚡ Калькулятор потужності")
    st.markdown("---")

with fields:
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            radio_transform=st.radio(
                label="Вид обліку електроенергії:",
                options=("Лічильник прямого включення",
                         "Лічильник трансформаторного включення")
            )
        with col2:
            # Перевіряємо умову: якщо лічильник трансформаторний, то ПОКАЗУЄМО поле для введення
            if radio_transform == "Лічильник трансформаторного включення":
                coef_input = st.number_input("Коефіцієнт обліку", value=30, min_value=30, step=10)
                coef = coef_input  # Беремо значення, яке ввів користувач
            else:
                # Якщо лічильник прямого включення, поле НЕ МАЛЮЄТЬСЯ,
                # але ми створюємо приховану змінну в коді, щоб розрахунки не зламалися
                coef = 1
                st.write("ℹ️ *Коефіцієнт обліку для прямого включення дорівнює 1*")
    st.markdown("---")

    # Розміщуємо поля введення в три колонки для зручності
    col1, col2, col3 = st.columns(3)

    with col1:
        u_input = st.text_input("Напруга (В)", "220, 220, 220")

    with col2:
        i_input = st.text_input("Струм (А)", "3.5, 2.5, 4.5")

    with col3:
        angel_input = st.text_input("Кути (градуси)", "10, 10, 10")

# Одна кнопка для всіх обчислень
if st.button("Розрахувати", use_container_width=True):
    try:
        # Парсимо числа, замінюючи кому на крапку для підтримки обох форматів
        def parse_input(text):
            # Спочатку спробуємо розділити за комами
            parts = [x.strip() for x in text.split(',') if x.strip()]
            # Якщо частин мало, можливо використано крапку з комою або пробіл
            if len(parts) <= 1:
                parts = [x.strip() for x in text.replace(';', ' ').split() if x.strip()]
            
            # Перетворюємо на числа, замінюючи десяткову кому на крапку, якщо вона там залишилась
            return np.array([float(x.replace(',', '.')) for x in parts])

        voltage = parse_input(u_input)
        current = parse_input(i_input)
        angles = parse_input(angel_input)

    except ValueError:
        st.warning("Будь ласка, введіть дійсні числа, розділені комами або пробілами.")
        st.stop()

    # Перевірка на однакову довжину масивів
    if len(voltage) == len(current) == len(angles) and len(voltage) > 0:
        calculator = PowerCalculator(voltage, current, angles)
        
        # Обчислюємо дані
        active_p = calculator.calculate_active_power()
        reactive_p = calculator.calculate_reactive_power()
        apparent_p = calculator.calculate_apparent_power()

        # Вивід результатів у контейнер writer
        with writer:
            st.subheader("Результати", divider="orange")
            col1, col2, col3 = st.columns(3)
            with col1:
                for idx, p in enumerate(active_p):
                    st.metric(label=f"Активна потужність L{idx + 1}", value=f"{p:.2f} кВт")
            with col2:
                for idx, p in enumerate(reactive_p):
                    st.metric(label=f"Реактивна потужність L{idx + 1}", value=f"{p:.2f} кВАр")

            with col3:
                st.metric(label=f"Загальна активна потужність", value=f"{active_p.sum():.2f} кВт")
                st.metric(label=f"Загальна реактивна потужність", value=f"{reactive_p.sum():.2f} кВАр")
                total_active = active_p.sum()
                total_apparent = apparent_p.sum()
                st.metric(label=f"Загальна повна потужність", value=f"{total_apparent:.2f} кВА")

                if total_apparent != 0:
                    st.metric(label=f"Коефіцієнт потужності (cos φ)", value=f"{total_active/total_apparent:.3f}", width= "content")
        if radio_transform == "Лічильник трансформаторного включення":
            with current_cotainer:
                st.subheader("Струми (Первинний / Вторинний)", divider="blue")

                # Створюємо 3 колонки, щоб метрики струмів красиво встали в один ряд, як і решта результатів
                col_i1, col_i2, col_i3 = st.columns(3)

                # Використовуємо вже розпарсений числовий масив 'current', а не текстовий 'i_input'
                for idx, i in enumerate(current):
                    # Розраховуємо первинний струм (струм трансформатора), множачи на коефіцієнт
                    i_primary = i * coef

                    # Розподіляємо вивід по трьох створених колонках динамічно
                    if idx == 0:
                        with col_i1:
                            st.metric(label=f"Струм L1 (Іпр / Івтр)", value=f"{i_primary:.2f} / {i:.2f} А")
                    elif idx == 1:
                        with col_i2:
                            st.metric(label=f"Струм L2 (Іпр / Івтр)", value=f"{i_primary:.2f} / {i:.2f} А")
                    elif idx == 2:
                        with col_i3:
                            st.metric(label=f"Струм L3 (Іпр / Івтр)", value=f"{i_primary:.2f} / {i:.2f} А")
        # Вивід графіка у контейнер graf
        with graf:
            st.markdown("---")
            st.subheader("Vector diagram", text_alignment="center")
            fig_to_show = create_vector_plot(voltage, current, angles)
            st.pyplot(fig_to_show)
            # col_text, col_plot = st.columns([1, 2])
            #
            # # with col_text:
            # #     st.subheader("Векторна діаграма")
            # #     st.write("Цей графік відображає взаємне розташування векторів напруги та струму для кожної фази.")
            #
            # with col_plot:
            #     # ОСНОВНА КОМАНДА ДЛЯ ВИВОДУ:
            #     fig_to_show = create_vector_plot(voltage, current, angles)
            #     st.pyplot(fig_to_show)

    elif len(voltage) == 0:
        st.info("Будь ласка, введіть дані для розрахунку.")
    else:
        st.error("Помилка: Усі поля повинні мати однакову кількість значень!")

