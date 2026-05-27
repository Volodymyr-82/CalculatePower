import numpy as np
import streamlit as st
import matplotlib.pyplot as plt


from model import PowerCalculator
from graphic_funtion import create_vector_plot

# Налаштовуємо заголовки
header = st.container()
fields = st.container()
scalar_container=st.container()
writer = st.container()
current_cotainer=st.container()
graf = st.container()


with header:
    # Використовуємо стандартний заголовок без зайвих параметрів
    st.title("⚡ Калькулятор потужності")
    st.markdown("---")

with fields:
    with st.container():
        col1, col2, col3 = st.columns([0.8,1,1],gap="xxsmall")
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
                st.write("ℹ️ *Коефіцієнт обліку дорівнює 1*")
        with col3:
            check_box=st.checkbox("Перевірка похибки лічильника")
            if check_box:
                sec_input=st.number_input("Час (сек)", value=10.0, min_value=0.01, step=0.01)
                imp_input=st.number_input("Передаточне число (imp/кВт*год)", value=1600, min_value=10, step=50)

                count_input = st.number_input("Кількість імпульсів (imp)", value=10, min_value=1, step=1)
    st.markdown("---")

    # Розміщуємо поля введення в три колонки для зручності
    col1, col2, col3 = st.columns(3)

    with col1:
        u_input = st.text_input("Напруга (В)", "230, 230, 230")

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
        total_active = active_p.sum()/1000
        total_reactive = reactive_p.sum() / 1000
        total_apparent = apparent_p.sum()/1000
        # Вивід результатів у контейнер writer
        with writer:
            st.subheader("Результати", divider="orange")
            col1, col2, col3 = st.columns(3)
            with col1:
                for idx, p in enumerate(active_p):
                    st.metric(label=f"Активна потужність L{idx + 1}", value=f"{p:.2f} Вт")

            with col2:
                for idx, p in enumerate(reactive_p):
                    st.metric(label=f"Реактивна потужність L{idx + 1}", value=f"{p:.2f} ВАр")

            with col3:
                for idx, p in enumerate(apparent_p):
                    st.metric(label=f"Повна потужність L{idx + 1}", value=f"{p:.2f} ВА")

            with st.container():
                st.subheader("Загальні виміри", divider="green")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(label=f"Загальна активна потужність", value=f"{total_active:.3f} кВт")
                    if check_box:
                        counter_error=((total_active*sec_input*imp_input)/(count_input*3600)-1)*100
                        st.metric(label=f"Похибка лічильника", value=f"{counter_error:.3f} %")

                with col2:
                    st.metric(label=f"Загальна реактивна потужність", value=f"{total_reactive:.3f} кВАр")

                with col3:

                    st.metric(label=f"Загальна повна потужність", value=f"{total_apparent:.3f} кВА")
                    if total_apparent != 0:
                        st.metric(label=f"Коефіцієнт потужності (cos φ)", value=f"{total_active / total_apparent:.3f}",
                                  width="content")


        if radio_transform == "Лічильник трансформаторного включення":
            with current_cotainer:
                st.subheader("Струми (Первинний / Вторинний)", divider="blue")

                # Створюємо 3 колонки, щоб метрики струмів красиво встали в один ряд, як і решта результатів
                col_i1, col_i2, col_i3 = st.columns(3, gap="xxsmall")

                # Використовуємо вже розпарсений числовий масив 'current', а не текстовий 'i_input'
                for idx, i in enumerate(current):
                    # Розраховуємо первинний струм (струм трансформатора), множачи на коефіцієнт
                    i_primary = i * coef

                    # Розподіляємо вивід по трьох створених колонках динамічно
                    if idx == 0:
                        with col_i1:
                            st.metric(label=f"Струм L1 (Іпр / Івтр)", value=f"{i_primary:.2f} / {i:.2f} А")
                            st.metric(label=f"Активна потужність L1 (Pпр / Pвтр)", value=f"{active_p[0]*coef:.0f} / {active_p[0]:.0f} Вт")
                    elif idx == 1:
                        with col_i2:
                            st.metric(label=f"Струм L2 (Іпр / Івтр)", value=f"{i_primary:.2f} / {i:.2f} А")
                            st.metric(label=f"Активна потужність L2 (Pпр / Pвтр)",
                                      value=f"{active_p[1] * coef:.0f} / {active_p[1]:.0f} Вт")
                    elif idx == 2:
                        with col_i3:
                            st.metric(label=f"Струм L3 (Іпр / Івтр)", value=f"{i_primary:.2f} / {i:.2f} А")
                            st.metric(label=f"Активна потужність L3 (Pпр / Pвтр)",
                                      value=f"{active_p[2] * coef:.0f} / {active_p[2]:.0f} Вт")
        # Вивід графіка у контейнер graf
        with graf:
            st.markdown("---")
            st.subheader("Vector diagram", text_alignment="center")
            fig_to_show = create_vector_plot(voltage, current, angles, coef)
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

