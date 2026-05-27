import matplotlib.pyplot as plt
import numpy as np


def create_vector_plot(U, I, angles_deg, scalar):
    # 1. Якщо коефіцієнт обліку дорівнює 1 (пряме включення),
    # штучно збільшуємо масштаб векторів струму до 30, щоб їх було видно на графіку поруч із напругою 220В.
    if scalar == 1:
        scalar = 30

    fig, ax = plt.subplots(figsize=(10, 10))

    # Твоя логіка осей
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.axis('equal')

    # Налаштування для 3-х фаз
    phase_angles = [90, -30, -150]  # Фази A, B, C
    colors = ['#FFD700', 'green', 'red']  # Золотистий замість жовтого (краще видно)

    for i in range(len(U)):
        # Напруга (суцільна лінія)
        u_rad = np.radians(phase_angles[i])
        u_x = U[i] * np.cos(u_rad)
        u_y = U[i] * np.sin(u_rad)

        if U[i] > 0:
            ax.quiver(0, 0, u_x, u_y,
                      angles='xy', scale_units='xy', scale=1, color=colors[i],
                      label=f'U{i + 1}', width=0.005)

        # Струм (пунктирна лінія)
        i_rad = np.radians(phase_angles[i] - angles_deg[i])
        i_x = I[i] * scalar * np.cos(i_rad)
        i_y = I[i] * scalar * np.sin(i_rad)

        if I[i] > 0:
            # Малюємо пунктирну лінію для тіла вектора
            ax.plot([0, i_x], [0, i_y], color=colors[i], linestyle='--',
                    alpha=0.8, linewidth=1.5)
            # Додаємо стрілку в кінці без пунктиру
            ax.quiver(0, 0, i_x, i_y,
                      angles='xy', scale_units='xy', scale=1, color=colors[i],
                      width=0.007, label=f'I{i + 1}')

    ax.legend()

    # 2. Додаємо інформаційний напис у лівий верхній куток графіка (2% від лівого краю, 95% від нижнього)
    ax.text(
        0.02, 0.95,
        f"Масштаб струму: х{scalar}",
        transform=ax.transAxes,  # Використовуємо систему координат вікна (від 0 до 1)
        fontsize=12,  # Розмір шрифту
        weight='bold',  # Жирне накреслення
        color='#333333',  # Темно-сірий колір тексту
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray', boxstyle='round,pad=0.5')  # Акуратна рамка
    )

    ax.set_xlim(ax.get_xlim()[0] - 200, ax.get_xlim()[1] + 200)
    ax.set_ylim(ax.get_ylim()[0] - 150, ax.get_ylim()[1] + 250)
    ax.grid(True, linestyle=':', alpha=0.5)
    return fig