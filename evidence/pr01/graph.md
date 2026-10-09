# Исследование графа ROS 2 и изоляции доменов (ПР01)

## 1. Штатный режим (до сбоя)

Эксперимент проводится в домене `ROS_DOMAIN_ID=16`.
Запущены две ноды:
- `/turtlesim` (пакет `turtlesim`, бинарник `turtlesim_node`) — симулятор движения робота.
- `/teleop_turtle` (пакет `turtlesim`, бинарник `turtle_teleop_key`) — узел телеуправления с клавиатуры.

### Список активных нод
Команда:
```bash
ros2 node list --no-daemon --spin-time 2
```
Вывод:
```text
/teleop_turtle
/turtlesim
```

### Список топиков и их типы
Команда:
```bash
ros2 topic list -t
```
Вывод:
```text
/parameter_events [rcl_interfaces/msg/ParameterEvent]
/rosout [rcl_interfaces/msg/Log]
/turtle1/cmd_vel [geometry_msgs/msg/Twist]
/turtle1/color_sensor [turtlesim_msgs/msg/Color]
/turtle1/pose [turtlesim_msgs/msg/Pose]
```

### Инспекция ноды /turtlesim
Команда:
```bash
ros2 node info /turtlesim
```
Вывод:
```text
/turtlesim
  Subscribers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /turtle1/cmd_vel: geometry_msgs/msg/Twist
  Publishers:
    /parameter_events: rcl_interfaces/msg/ParameterEvent
    /rosout: rcl_interfaces/msg/Log
    /turtle1/color_sensor: turtlesim_msgs/msg/Color
    /turtle1/pose: turtlesim_msgs/msg/Pose
  Service Servers:
    /clear: std_srvs/srv/Empty
    /kill: turtlesim_msgs/srv/Kill
    /reset: std_srvs/srv/Empty
    /spawn: turtlesim_msgs/srv/Spawn
    /turtle1/set_pen: turtlesim_msgs/srv/SetPen
    /turtle1/teleport_absolute: turtlesim_msgs/srv/TeleportAbsolute
    /turtle1/teleport_relative: turtlesim_msgs/srv/TeleportRelative
    /turtlesim/describe_parameters: rcl_interfaces/srv/DescribeParameters
    /turtlesim/get_parameter_types: rcl_interfaces/srv/GetParameterTypes
    /turtlesim/get_parameters: rcl_interfaces/srv/GetParameters
    /turtlesim/list_parameters: rcl_interfaces/srv/ListParameters
    /turtlesim/set_parameters: rcl_interfaces/srv/SetParameters
    /turtlesim/set_parameters_atomically: rcl_interfaces/srv/SetParametersAtomically
  Service Clients:

  Action Servers:
    /turtle1/rotate_absolute: turtlesim_msgs/action/RotateAbsolute
  Action Clients:
```

Нода `/turtlesim` подписывается на топик скорости `/turtle1/cmd_vel` (`geometry_msgs/msg/Twist`) и публикует текущую позу в топик `/turtle1/pose` (`turtlesim_msgs/msg/Pose`). Нода `/teleop_turtle` публикует команды в `/turtle1/cmd_vel`.

### Снимок позы робота
Команда:
```bash
ros2 topic echo /turtle1/pose --once
```
Вывод:
```text
x: 5.362162113189697
y: 5.2627973556518555
theta: -2.369555950164795
linear_velocity: 0.0
angular_velocity: 0.0
---
```

### Замер частоты публикации топика /turtle1/pose
Команда:
```bash
ros2 topic hz /turtle1/pose
```
Фрагмент вывода:
```text
average rate: 62.484
        min: 0.008s max: 0.025s std dev: 0.00220s window: 1001
average rate: 62.483
        min: 0.003s max: 0.029s std dev: 0.00228s window: 1063
average rate: 62.495
        min: 0.003s max: 0.029s std dev: 0.00226s window: 1126
```

Параметры замера:
- Средняя частота: 62.495 Гц (соответствует ожидаемым ~62.5 Гц).
- Размер окна наблюдений: 1126 сообщений.
- Длительность замера: 1126 / 62.495 ≈ 18.02 с (требование `>= 10 с` выполнено).

---

## 2. Воспроизведение сбоя (разрыв домена)

Нода симулятора `/turtlesim` остаётся работать в домене `ROS_DOMAIN_ID=16`.
Нода управления `/teleop_turtle` перезапущена в домене `ROS_DOMAIN_ID=17`.
В терминале наблюдения также установлен домен 17:
```bash
export ROS_DOMAIN_ID=17
```

### Список нод в домене 17
Команда:
```bash
ros2 node list --no-daemon --spin-time 2
```
Вывод:
```text
/teleop_turtle
```
Нода `/turtlesim` в списке отсутствует, так как DDS discovery изолирует трафик между разными доменами.

### Инструментальное измерение сбоя
Команда:
```bash
timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > evidence/pr01/pose-broken.txt 2>&1
printf 'exit=%s\n' "$?"
```
Результат:
```text
exit=124
```
Файл `evidence/pr01/pose-broken.txt` пустой (0 байт). По истечении 5 секунд утилита была принудительно остановлена по таймауту, не получив ни одного сообщения.

---

## 3. Восстановление связи и доказательство исправления

Нода `/teleop_turtle` перезапущена с возвратом в исходный домен `ROS_DOMAIN_ID=16`.
В терминале наблюдения также возвращён домен 16:
```bash
export ROS_DOMAIN_ID=16
```

### Инструментальное измерение восстановления
Команда:
```bash
timeout 5s ros2 topic echo /turtle1/pose "$POSE_TYPE" --once > evidence/pr01/pose-fixed.txt 2>&1
printf 'exit=%s\n' "$?"
```
Результат:
```text
exit=0
```
Вывод из `evidence/pr01/pose-fixed.txt`:
```text
x: 0.0
y: 0.0
theta: -2.049556016921997
linear_velocity: 0.0
angular_velocity: 0.0
---
```

---

## 4. Сравнительный анализ и обоснование

### Сводная таблица состояний

| Параметр | 1. Штатный режим | 2. Сбой сети | 3. Восстановление |
| :--- | :--- | :--- | :--- |
| Домен симулятора (`/turtlesim`) | 16 | 16 | 16 |
| Домен управления (`/teleop_turtle`) | 16 | 17 | 16 |
| Домен наблюдателя | 16 | 17 | 16 |
| Видимые ноды наблюдателю | `/turtlesim`, `/teleop_turtle` | `/teleop_turtle` | `/turtlesim`, `/teleop_turtle` |
| Результат проверки `/turtle1/pose` | Сообщение получено | Таймаут 5 с | Сообщение получено |
| Код возврата (`exit code`) | 0 | 124 | 0 |

### Почему потребовался только перезапуск teleop, а симулятор и систему менять не нужно
1. Причина сбоя заключалась исключительно в несовпадении сетевого домена (`ROS_DOMAIN_ID`) у процесса `turtle_teleop_key` относительно симулятора.
2. Сам симулятор `/turtlesim` на протяжении всего эксперимента продолжал работать штатно и публиковать позу в домене 16.
3. Процессы в Linux считывают переменные окружения только один раз — в момент старта. Поэтому для изменения рабочего домена teleop было достаточно завершить процесс и запустить его заново с `ROS_DOMAIN_ID=16`.
4. Никаких изменений в конфигурацию операционной системы, бинарные пакеты или код симулятора вносить не требовалось, так как сбой носил чисто конфигурационный характер на уровне окружения конкретного процесса.
